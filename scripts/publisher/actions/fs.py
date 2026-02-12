import os
import shutil
from pathlib import Path
from typing import List, Set
from ..contracts.types import Article, PublisherConfig
from ..actions.generator import generate_quartz_frontmatter, generate_related_articles, process_body_content

def prepare_output_directories(config: PublisherConfig):
    os.makedirs(config.quartz_content_dir, exist_ok=True)

def write_article(article: Article, config: PublisherConfig, tag_index: dict) -> bool:
    """
    Writes the article to the target file. Returns True if updated, False if skipped.
    """
    if not article.filename:
        return False
        
    target_dir = os.path.join(config.quartz_content_dir, article.target_dir)
    os.makedirs(target_dir, exist_ok=True)
    
    target_path = os.path.join(target_dir, article.filename)
    
    # Generate content
    fm_str = generate_quartz_frontmatter(article, config.logseq_dir)
    related_str = generate_related_articles(article, tag_index)
    body_str = process_body_content(article.body)
    
    final_content = f"{fm_str}\n\n{body_str}{related_str}"
    
    # Smart Write Check
    if os.path.exists(target_path):
        with open(target_path, "r", encoding="utf-8") as f:
            existing_content = f.read()
        if existing_content == final_content:
            return False
            
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(final_content)
    
    return True

def clean_output_directory(config: PublisherConfig, expected_files: Set[str]):
    """
    Removes files in quartz/content that are not in expected_files.
    """
    print("🧹 執行同步清理 (移除已刪除或更名的文章)...")
    if os.path.exists(config.quartz_content_dir):
        for root, dirs, files in os.walk(config.quartz_content_dir):
            for file in files:
                # Keep list
                if file in ["index.md", "assets", "404.md", "robots.txt", "CNAME", "_redirects"]:
                    continue
                if file.startswith("."): 
                    continue
                
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, config.quartz_content_dir)
                
                if file.endswith(".md"):
                    if rel_path not in expected_files:
                        print(f"  🗑️  刪除過期檔案: {rel_path}")
                        os.remove(abs_path)
                        
        # Clean empty dirs
        for root, dirs, files in os.walk(config.quartz_content_dir, topdown=False):
            for name in dirs:
                if name == "assets": continue
                path = os.path.join(root, name)
                if not os.listdir(path):
                    print(f"  🗑️  移除空資料夾: {os.path.relpath(path, config.quartz_content_dir)}")
                    os.rmdir(path)

def copy_assets(config: PublisherConfig):
    assets_src = os.path.join(config.logseq_dir, "assets")
    assets_dest = os.path.join(config.quartz_content_dir, "assets")
    
    if os.path.islink(assets_dest):
        os.remove(assets_dest)
    if os.path.isdir(assets_dest):
        shutil.rmtree(assets_dest)
    
    def ignore_large_files(directory, files):
        ignored = []
        for f in files:
            filepath = os.path.join(directory, f)
            if os.path.isfile(filepath):
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                if size_mb > config.max_asset_size_mb:
                    print(f"  ⚠️ 跳過大檔案 ({size_mb:.1f}MB > {config.max_asset_size_mb}MB): {f}")
                    ignored.append(f)
        return ignored
    
    if os.path.exists(assets_src) and not os.path.exists(assets_dest):
        shutil.copytree(assets_src, assets_dest, ignore=ignore_large_files)
        print(f"  📦 已複製 Assets 資料夾 ({len(os.listdir(assets_dest))} 個檔案)")
