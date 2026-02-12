import re
import os
from datetime import datetime
from typing import Dict
from ..contracts.types import Article
from .utils import clean_tags

def load_uuid_tags_map(logseq_dir: str) -> Dict[str, str]:
    """Load TagsBlock.md for UUID resolution"""
    uuid_tags_map = {}
    tags_block_path = os.path.join(logseq_dir, "pages", "TagsBlock.md")
    if os.path.exists(tags_block_path):
        try:
            with open(tags_block_path, 'r', encoding='utf-8') as f:
                lines_tb = f.readlines()
                current_tag = None
                for line in lines_tb:
                    tag_match = re.match(r'^\s*-\s*\+\+(.+)$', line)
                    if tag_match:
                        current_tag = tag_match.group(1).strip().lstrip('/')
                        continue
                    id_match = re.match(r'^\s*id::\s*([a-zA-Z0-9-]+)', line)
                    if id_match and current_tag:
                        uuid = id_match.group(1).strip()
                        uuid_tags_map[uuid] = current_tag
        except Exception: pass
    return uuid_tags_map

def enrich_article_metadata(article: Article, uuid_tags_map: Dict[str, str]):
    """Enrich article frontmatter with inferred Date, consolidated Tags, and Slug"""
    fm = article.frontmatter
    
    # 1. Date Inference
    if "date" not in fm:
        source_file = article.source_file
        date_match = re.match(r'^(\d{4})_(\d{2})_(\d{2})\.md$', source_file)
        if date_match:
             fm["date"] = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
        else:
             fm["date"] = datetime.now().strftime("%Y-%m-%d")
    date = fm["date"]
    # [Fix] Enforce YYYY-MM-DD format to match legacy behavior and consistency
    article.date = str(date)[:10]

    # 2. Extract Inline Tags from Body
    inline_tags_found = []
    if article.body:
        matches = re.findall(r'\+\+/([a-zA-Z0-9_\u4e00-\u9fa5-]+)', article.body)
        
        ignored_tags = {"tag1", "my_new_tag", "tag", "logseq"} 
        if matches: 
            valid_matches = [t for t in matches if t.lower() not in ignored_tags]
            inline_tags_found.extend(valid_matches)
        
        uuid_matches = re.findall(r'\(\(([a-zA-Z0-9-]+)\)\)', article.body)
        for uuid in uuid_matches:
            if uuid in uuid_tags_map:
                inline_tags_found.append(uuid_tags_map[uuid])

    # 3. Consolidate Tags
    raw_tags_input = []
    if "tags" in fm:
        rt = fm["tags"]
        if isinstance(rt, list):
            def flatten(lst):
                 res = []
                 for item in lst:
                     if isinstance(item, list): res.extend(flatten(item))
                     else: res.append(str(item)) 
                 return res
            raw_tags_input.extend(flatten(rt))
        else:
             cleaned_str = str(rt).replace("[", "").replace("]", "").replace("'", "")
             raw_tags_input.extend([t.strip() for t in cleaned_str.split(",") if t.strip()])

    raw_tags_input.extend(inline_tags_found)
    
    # 4. Resolve UUIDs & Clean
    final_tags = []
    for t in raw_tags_input:
        t_str = str(t).strip()
        clean_t = t_str.replace("((", "").replace("))", "").strip()
        
        if re.match(r'^[a-z0-9-]{36}$', clean_t, re.IGNORECASE):
             if clean_t in uuid_tags_map:
                 final_tags.append(uuid_tags_map[clean_t])
        else:
             final_tags.append(t_str)
    
    final_tags = [t for t in final_tags if t.lower() not in {"tag1", "my_new_tag"}]
    
    try:
        final_tags = clean_tags(final_tags)
    except Exception as e:
        print(f"⚠️ Clean Tags Error: {e}")
        final_tags = list(set(final_tags)) 
    
    if final_tags:
        fm["tags"] = final_tags
        article.tags = final_tags

    # 5. Categories
    article.categories = fm.get("categories", "Uncategorized")

    # 6. Slug Inference
    if "slug" not in fm or not fm["slug"]:
        raw_title = fm.get("title", article.title)
        title = str(raw_title).strip().lstrip("#").strip()
        
        def slugify(text):
            text = re.sub(r'[#：:｜|–—「」『』【】《》\?\!&\s]+', '-', text)
            text = re.sub(r'[-]+', '-', text)
            text = text.strip('-')
            return text[:80]
        
        date_part = str(date)[:10] if date else datetime.now().strftime("%Y-%m-%d")
        title_part = slugify(title)
        fm["slug"] = f"{date_part}-{title_part}"
    
    article.slug = fm["slug"]
