import os
import sys
from pathlib import Path
from ..contracts.types import PublisherConfig
from ..actions.utils import get_safe_path_elements
from ..actions.parser import parse_logseq_file
from ..actions.enricher import load_uuid_tags_map, enrich_article_metadata
from ..actions.fs import prepare_output_directories, write_article, clean_output_directory, copy_assets
from ..actions.dashboard import generate_dashboard
from ..actions.archive import generate_archive, generate_tags_page
from ..actions.redirects import generate_redirects

def main():
    print("🚀 啟動 Logseq Block-Publish Agent (Atomic V2)...")
    config = PublisherConfig()
    
    prepare_output_directories(config)
    
    search_dirs = [Path(config.logseq_dir) / "journals", Path(config.logseq_dir) / "pages"]
    all_md_files = []
    
    for d in search_dirs:
        if d.exists():
            for f in d.rglob("*.md"):
                if "Uncategorized" in f.parts: continue
                if len(f.name) > 100: continue
                if f.name.startswith(">") or f.name.startswith("!"): continue
                all_md_files.append(f)
                
    print(f"📂 掃描 {len(all_md_files)} 個檔案...")
    
    uuid_map = load_uuid_tags_map(config.logseq_dir)
    articles_to_publish = []
    expected_output_files = set()
    
    # Parse & Enrich Plan
    for f in all_md_files:
        found_articles = parse_logseq_file(f, config)
        for art in found_articles:
            enrich_article_metadata(art, uuid_map)
            
            # Draft check
            is_draft = str(art.frontmatter.get("draft", "false")).lower() == "true"
            if is_draft: continue
            
            # Path Logic
            safe_cat, safe_title = get_safe_path_elements(art.title, art.categories)
            filename = f"{safe_title}.md"
            
            if "關於我" in art.title and "About" in art.title:
                filename = "about.md"
                safe_cat = ""
                
            art.target_dir = safe_cat
            art.filename = filename
            
            articles_to_publish.append(art)
            expected_output_files.add(os.path.join(safe_cat, filename))
            
    print(f"📝 準備發佈 {len(articles_to_publish)} 篇文章...")
    
    # Build Tag Index
    tag_index = {}
    for art in articles_to_publish:
        for t in art.tags:
            if t not in tag_index: tag_index[t] = []
            tag_index[t].append(art)
            
    # Write Content
    updated_count = 0
    skipped_count = 0
    for art in articles_to_publish:
        if write_article(art, config, tag_index):
            updated_count += 1
        else:
            skipped_count += 1
            
    print(f"✅ 完成同步: 更新 {updated_count} 篇, 跳過 {skipped_count} 篇")
    
    clean_output_directory(config, expected_output_files)
    copy_assets(config)
    
    generate_dashboard(articles_to_publish, config)
    generate_archive(articles_to_publish, config)
    generate_tags_page(articles_to_publish, config)
    generate_redirects(articles_to_publish, config)
    
    print("\n🎉 同步完成 (Atomic V2)！")

if __name__ == "__main__":
    main()
