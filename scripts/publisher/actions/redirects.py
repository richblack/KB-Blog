import os
import urllib.parse
import hashlib
import re
from typing import List
from ..contracts.types import Article, PublisherConfig
from ..actions.utils import get_safe_path_elements

def generate_redirects(articles: List[Article], config: PublisherConfig):
    """
    生成 Cloudflare Pages _redirects 檔案
    """
    redirects = []
    short_redirects = []
    
    for art in articles:
        fm = art.frontmatter
        title = art.title
        original_url = fm.get("original_url", "")
        
        # New Path Calculation
        safe_cat, safe_title = get_safe_path_elements(title, art.categories)
        if "關於我" in title and "About" in title:
            new_path = "/about"
        elif safe_cat:
            new_path = f"/{safe_cat}/{safe_title}"
        else:
            new_path = f"/{safe_title}"
            
        new_path_encoded = urllib.parse.quote(new_path, safe='/')

        # 1. Old URL Redirects
        if original_url:
            try:
                parsed = urllib.parse.urlparse(original_url)
                old_path = parsed.path.rstrip("/")
                if old_path and old_path != "/" and old_path != new_path_encoded:
                    redirects.append(f"{old_path} {new_path_encoded} 301")
            except Exception as e:
                print(f"  ⚠️ 轉址解析錯誤 {original_url}: {e}")

        # 2. Short URL Redirects
        date = str(art.date)
        short_hash = hashlib.md5(f"{title}{date}".encode()).hexdigest()[:6]
        short_path = f"/p/{short_hash}"
        short_redirects.append(f"{short_path} {new_path_encoded} 301")

        # 3. Slug Redirects
        if art.slug:
            slug_encoded = urllib.parse.quote(art.slug)
            slug_path = f"/{slug_encoded}"
            if slug_path != new_path_encoded:
                short_redirects.append(f"{slug_path} {new_path_encoded} 301")
    
    all_redirects = redirects + short_redirects
    
    redirects_path = os.path.join(config.quartz_content_dir, "..", "static", "_redirects")
    # Resolve relative path from config.quartz_content_dir which is likely ./quartz/content
    # So .. -> ./quartz -> static -> ./quartz/static/_redirects
    # However config.quartz_content_dir is a string path.
    # Safe construction:
    static_dir = os.path.abspath(os.path.join(config.quartz_content_dir, "..", "static"))
    os.makedirs(static_dir, exist_ok=True)
    redirects_file = os.path.join(static_dir, "_redirects")
    
    if all_redirects:
        with open(redirects_file, "w", encoding="utf-8") as f:
            f.write("# Auto-generated redirects\n")
            f.write("\n".join(all_redirects))
        print(f"  🔗 已生成 _redirects: {len(redirects)} 條舊文轉址 + {len(short_redirects)} 條短網址")
    else:
        print("  ℹ️  無需生成 _redirects")
