#!/usr/bin/env python3
"""
patch_original_url.py

從 WordPress API 抓取文章的 original_url，
並更新到現有 KB/pages/ 檔案的 frontmatter 中，
不會覆蓋文章內容。
"""

import requests
import os
import re
import yaml
from pathlib import Path

# --- 配置區 ---
SITE_URL = "https://uncle6.me"
KB_DIR = "./KB"
PAGES_DIR = os.path.join(KB_DIR, "pages")
PER_PAGE = 100  # 每次抓取幾篇

def fetch_all_posts():
    """從 WordPress API 抓取所有文章的 title 和 link"""
    posts = []
    page = 1
    
    while True:
        url = f"{SITE_URL}/wp-json/wp/v2/posts"
        params = {
            'per_page': PER_PAGE,
            'page': page,
            '_fields': 'id,title,link,slug'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 400:
                break  # 沒有更多頁面
            response.raise_for_status()
            
            batch = response.json()
            if not batch:
                break
                
            for post in batch:
                posts.append({
                    'id': post['id'],
                    'title': post['title']['rendered'],
                    'link': post['link'],
                    'slug': post['slug']
                })
            
            print(f"  📥 已抓取 {len(posts)} 篇文章...")
            page += 1
            
        except Exception as e:
            print(f"  ⚠️  API 錯誤: {e}")
            break
    
    return posts

def normalize_title(title):
    """正規化標題以便比對"""
    import html
    title = html.unescape(title)
    # 移除特殊字元
    title = re.sub(r'[：:｜|–—]', '', title)
    title = re.sub(r'\s+', '', title)
    return title.lower()

def find_matching_file(title, files_map):
    """用正規化標題比對檔案"""
    normalized = normalize_title(title)
    return files_map.get(normalized)

def update_frontmatter(filepath, original_url):
    """更新檔案的 frontmatter，加入 original_url"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查是否已有 original_url
    if 'original_url:' in content:
        return False  # 已存在，跳過
    
    # 找到 frontmatter 結束位置
    if not content.startswith('---'):
        return False
    
    end_marker = content.find('---', 3)
    if end_marker == -1:
        return False
    
    # 在 draft: 行後面插入 original_url
    frontmatter = content[:end_marker]
    body = content[end_marker:]
    
    # 找到 draft 行並在其前插入
    if 'draft:' in frontmatter:
        frontmatter = frontmatter.replace('draft:', f'original_url: "{original_url}"\ndraft:')
    else:
        # 沒有 draft 行，就在 --- 前插入
        frontmatter = frontmatter.rstrip() + f'\noriginal_url: "{original_url}"\n'
    
    new_content = frontmatter + body
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    print("🔗 正在從 WordPress 抓取文章 URL 對照表...")
    
    # 1. 抓取所有文章
    posts = fetch_all_posts()
    print(f"📊 共抓取 {len(posts)} 篇文章")
    
    if not posts:
        print("⚠️  無法抓取文章，請檢查網路連線或 WordPress API")
        return
    
    # 2. 建立本地檔案對照表
    files_map = {}
    for root, dirs, files in os.walk(PAGES_DIR):
        for f in files:
            if f.endswith('.md'):
                filepath = os.path.join(root, f)
                # 從檔案讀取標題
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read()
                        match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
                        if match:
                            title = match.group(1).strip('"\'')
                            normalized = normalize_title(title)
                            files_map[normalized] = filepath
                except:
                    pass
    
    print(f"📂 本地共有 {len(files_map)} 個檔案")
    
    # 3. 比對並更新
    updated = 0
    skipped = 0
    not_found = 0
    
    for post in posts:
        filepath = find_matching_file(post['title'], files_map)
        
        if filepath:
            if update_frontmatter(filepath, post['link']):
                updated += 1
                print(f"  ✅ 更新: {os.path.basename(filepath)}")
            else:
                skipped += 1
        else:
            not_found += 1
    
    print(f"\n📊 結果: 更新 {updated} 篇, 跳過 {skipped} 篇 (已存在), 未找到 {not_found} 篇")
    print("🎉 完成！請執行 logseq_publish_agent.py 重新生成 _redirects")

if __name__ == "__main__":
    main()
