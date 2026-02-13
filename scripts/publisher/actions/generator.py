import re
import os
import hashlib
from datetime import datetime
from typing import List, Dict
from ..contracts.types import Article
from .utils import get_safe_path_elements, sanitize_content_links

def generate_quartz_frontmatter(article: Article, logseq_dir: str) -> str:
    fm = article.frontmatter
    lines = ["---"]
    
    # Title
    raw_title = fm.get("title", article.title)
    title = str(raw_title).strip().lstrip("#").strip()
    title = title.replace("**", "").replace("__", "")  # Strip markdown bold
    lines.append(f'title: "{title}"')
    
    # Date
    date = article.date if article.date else datetime.now().strftime("%Y-%m-%d")
    lines.append(f'date: {date}')
    
    # Image
    image = fm.get("socialImage") or fm.get("image") or fm.get("featured_image")
    if not image:
        img_match = re.search(r'!\[.*?\]\((.*?)\)', article.body)
        if img_match:
            image = img_match.group(1)
            if image.startswith("../assets/"):
                image = image.replace("../assets/", "/assets/")
            asset_filename = os.path.basename(image)
            name_part, ext_part = os.path.splitext(asset_filename)
            optimized_filename = f"{name_part}_optimized.jpg"
            optimized_path = os.path.join(logseq_dir, "assets", optimized_filename)
            if os.path.exists(optimized_path):
                image = f"/assets/{optimized_filename}"
    
    if image:
        lines.append(f'image: "{image}"')
        lines.append(f'socialImage: "{image}"')

    # Tags
    if article.tags:
        lines.append(f"tags: [{', '.join(article.tags)}]")

    if "categories" in fm:
        lines.append(f'categories: {fm["categories"]}')
    
    if "template" in fm:
        lines.append(f'template: {fm["template"]}')

    if article.slug:
         lines.append(f'slug: {article.slug}')
    
    # Short URL
    short_hash = hashlib.md5(f"{title}{date}".encode()).hexdigest()[:6]
    short_url = f"/p/{short_hash}"
    lines.append(f'short_url: "{short_url}"')
    
    if "original_url" in fm:
        lines.append(f'original_url: "{fm["original_url"]}"')
        
    lines.append('draft: false')
    lines.append("---")
    return "\n".join(lines)

def generate_related_articles(article: Article, tag_index: Dict[str, List[Article]], category_index: Dict[str, List[Article]] = None, max_related=5) -> str:
    current_tags = set(article.tags)
    candidates = {}
    
    # 1. Tag Matching (High Score)
    if current_tags:
        for tag in current_tags:
            for related_art in tag_index.get(tag, []):
                if related_art.title == article.title:
                    continue
                
                title = related_art.title
                if title not in candidates:
                    candidates[title] = {
                        "score": 0,
                        "art": related_art
                    }
                candidates[title]["score"] += 3  # Tag Match = 3 points

    # 2. Category Matching (Low Score)
    if category_index and article.categories:
        # Support comma separated categories
        cats = [c.strip() for c in str(article.categories).split(',')]
        for cat in cats:
            for related_art in category_index.get(cat, []):
                 if related_art.title == article.title:
                    continue
                 
                 title = related_art.title
                 if title not in candidates:
                    candidates[title] = {
                        "score": 0,
                        "art": related_art
                    }
                 candidates[title]["score"] += 1 # Category Match = 1 point

    if not candidates:
        return ""
        
    sorted_candidates = sorted(
        candidates.values(), 
        key=lambda x: (x["score"], str(x["art"].date)), 
        reverse=True
    )
    
    selected = [x["art"] for x in sorted_candidates[:max_related]]

    lines = ["\n\n---\n## 📚 相關文章\n"]
    for art in selected:
        safe_cat, safe_title = get_safe_path_elements(art.title, art.categories)
        
        if "關於我" in art.title and "About" in art.title:
            link_path = "about"
        else:
            link_path = safe_title
        
        lines.append(f"- [[{link_path}|{art.title}]]")
    
    return "\n".join(lines)

def process_body_content(body: str) -> str:
    """清理和處理 Body 內容"""
    
    # 處理分隔線及其後的縮排內容
    def fix_separator_section(text):
        lines = text.split('\n')
        result = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if re.match(r'^\s*-\s*\*\s+\*\s*$', line):
                result.append('')
                result.append('---')
                result.append('')
                i += 1
                if i < len(lines):
                    next_line = lines[i]
                    indent_match = re.match(r'^(\t+)', next_line)
                    if indent_match:
                        base_indent = indent_match.group(1)
                        while i < len(lines):
                            if lines[i].startswith(base_indent):
                                result.append(lines[i][1:] if lines[i].startswith('\t') else lines[i])
                            elif lines[i].strip() == '':
                                result.append(lines[i])
                            else:
                                break
                            i += 1
                        continue
            else:
                result.append(line)
                i += 1
        return '\n'.join(result)
    
    body = fix_separator_section(body)
    
    # 修正臺灣引號在粗體標記內的問題
    body = re.sub(r'\*\*「([^」]+)」\*\*', r'「**\1**」', body)
    body = re.sub(r'\*\*『([^』]+)』\*\*', r'『**\1**』', body)
    
    # 確保 Legacy Mode 或其它來源的 body 也有做連結清理
    body = sanitize_content_links(body, for_quartz=True)
    
    return body
