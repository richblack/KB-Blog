import requests
import os
import re
import html2text
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import hashlib

# --- 配置區 ---
SITE_URL = "https://uncle6.me"
KB_DIR = "./KB"
OUTPUT_DIR = os.path.join(KB_DIR, "pages")
ASSETS_DIR = os.path.join(KB_DIR, "assets")
PER_PAGE = 20  # 每次抓取幾篇

def ensure_dirs():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)

def download_image(img_url):
    """下載圖片並存入 assets，回傳相對路徑名稱 (例如 ../assets/abc.jpg)"""
    try:
        # 簡單過濾掉非 http 開頭的 (例如 data:image)
        if not img_url.startswith('http'):
            return img_url

        # 產生唯一檔名，避免重複或過長
        # 使用 MD5 hash 確保同一個網址的圖片存成同一份
        file_ext = os.path.splitext(urlparse(img_url).path)[1]
        if not file_ext or len(file_ext) > 5:
            file_ext = ".jpg" # 預設 fallback
            
        hash_name = hashlib.md5(img_url.encode('utf-8')).hexdigest()
        filename = f"{hash_name}{file_ext}"
        filepath = os.path.join(ASSETS_DIR, filename)

        # 如果檔案已經存在，就不用重抓
        if not os.path.exists(filepath):
            # 偽裝 User-Agent 避免被擋
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(img_url, headers=headers, stream=True, timeout=10)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
            else:
                print(f"  ⚠️  圖片下載失敗 (Status {r.status_code}): {img_url}")
                return img_url # 下載失敗則維持原網址
        
        # 使用相對路徑 ../assets/，配合分類子資料夾結構
        return f"../assets/{filename}"

    except Exception as e:
        print(f"  ⚠️  圖片下載錯誤: {e} - {img_url}")
        return img_url

def process_html_images(html_content):
    """使用 BeautifulSoup 解析 HTML，下載圖片並替換 src"""
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 找尋所有圖片標籤
    imgs = soup.find_all('img')
    if imgs:
        print(f"  Found {len(imgs)} images, downloading...")
        for img in imgs:
            src = img.get('src')
            if src:
                new_src = download_image(src)
                img['src'] = new_src
                # 移除 srcset 避免 Logseq/瀏覽器優先使用舊的 CDN 連結
                if img.has_attr('srcset'):
                    del img['srcset']
    
    return str(soup)

def convert_to_outliner(html_content):
    # 1. 先處理圖片下載
    processed_html = process_html_images(html_content)

    # 2. 轉為 Markdown
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 0 
    h.ignore_images = False 
    markdown = h.handle(processed_html)
    
    # 3. 解析並轉為 Logseq Outliner 格式
    lines = markdown.split('\n')
    
    parsed_items = [] # 儲存 {type, content, level, original_is_list, ...}
    min_header_level = 999
    
    # 預處理：解析每一行的類型
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 過濾雜訊
        if line == "本文目錄" or line == "Toggle" or line == "Table of Contents": 
            i += 1
            continue
            
        # 更加寬鬆的 TOC 連結判斷 (支援 * 或 - 開頭，且允許縮排)
        stripped_line = line.strip()
        if (stripped_line.startswith("- [") or stripped_line.startswith("* [")) and "](" in line and "#" in line and "uncle6.me" in line:
            i += 1
            continue

        # 移除 Footer ("- 讓我們保持聯繫" 之後的內容)
        # 支援 * 或 - 開頭，或是粗體
        if "讓我們保持聯繫" in line:
            break
            
        if not line.strip(): # 空行
            i += 1
            continue

        item = {'content': line, 'type': 'text'}
        
        # --- Table Detection ---
        # 檢查下一行是否為分隔線 (---|---|...)
        if i + 1 < len(lines):
            next_line = lines[i+1].strip()
            # 分隔線特徵：包含 |，且只由 - : | 空白 組成，且至少有一個 -
            if "|" in next_line and "-" in next_line and re.match(r'^[\s\-:|]+$', next_line):
                # 發現表格！
                table_lines = [line] # Header
                table_lines.append(lines[i+1]) # Separator
                
                # 繼續往下抓取表格內容
                k = i + 2
                while k < len(lines):
                    curr = lines[k].strip()
                    # 簡單判斷：只要這行有 | 且不是空行，就視為表格的一部分
                    # (這可能誤判，但在一般 html2text 輸出中通常是連續的)
                    if "|" in curr:
                         table_lines.append(lines[k])
                         k += 1
                    else:
                         break
                
                item['type'] = 'table'
                item['content'] = table_lines #List of strings
                parsed_items.append(item)
                i = k
                continue

        # 1. Header
        if line.startswith('#'):
            level = line.count('#')
            content = line.replace('#', '').strip()
            # 移除粗體與前綴
            if content.startswith("**") and content.endswith("**"):
                content = content[2:-2].strip()
            content = clean_text_prefixes(content)
            
            if level < min_header_level:
                min_header_level = level
                
            item['type'] = 'header'
            item['level'] = level
            item['content'] = content
            parsed_items.append(item)
            i += 1
            continue
            
        # 2. Blockquote
        if line.startswith('>'):
            item['type'] = 'quote'
            item['content'] = line
            parsed_items.append(item)
            i += 1
            continue

        # 3. 預處理：解析縮排與移除列表符號
        # 計算來源縮排 (解決「假內縮」問題) - 假設 2 空格 = 1 層
        stripped_line = line.lstrip()
        indent_spaces = len(line) - len(stripped_line)
        indent_level = indent_spaces // 2 
        item['indent_level'] = indent_level

        clean_line = stripped_line
        is_list = False
        
        # 判斷是否為列表項目 (支援 *, -, + 和 1. 2. 等)
        # 使用 Regex 偵測並移除符號，避免 Logseq 出現「雙重 bullet」或「bullet + 數字」
        match_ul = re.match(r'^[*+-]\s+(.*)', stripped_line)
        match_ol = re.match(r'^(\d+)\.\s+(.*)', stripped_line)

        if match_ul:
            clean_line = match_ul.group(1).strip()
            is_list = True
        elif match_ol:
            clean_line = match_ol.group(2).strip()
            is_list = True
        
        # 特殊處理：若開頭是圖片格式 ![...](...)，則不應被切斷
        # 下方第 4 步會處理 image，這裡只需確保 clean_line 乾淨即可

        # 4. Image 判斷 (包含 list 內的 image)
        if clean_line.startswith('!['):
            # 檢查是否有後續文字作為 Image Caption
            match = re.match(r'^(!\[.*?\]\(.*?\))\s*(.*)', clean_line)
            if match:
                img_part = match.group(1)
                caption_part = match.group(2)
                
                item['type'] = 'image'
                item['content'] = img_part
                parsed_items.append(item)
                
                if caption_part:
                    caption_item = {
                        'type': 'caption',
                        'content': caption_part
                    }
                    parsed_items.append(caption_item)
            else:
                item['type'] = 'image'
                item['content'] = clean_line
                parsed_items.append(item)
            i += 1
            continue

        # 5. List Item or Paragraph
        item['content'] = clean_line
        if is_list:
             item['type'] = 'list_item'
        else:
             item['type'] = 'paragraph'
        
        parsed_items.append(item)
        i += 1

    # 計算 Header 位移量 (讓最小 Header 變成 H2)
    if min_header_level == 999:
        header_offset = 0
    else:
        header_offset = 2 - min_header_level
    
    # 重組 Outliner，處理縮排邏輯
    outliner_lines = []
    
    current_header_indent = "" 
    list_indent_level = 0  # 額外的列表縮排層級
    previous_item_type = None
    previous_content = ""
    
    # 狀態：是否處於「冒號後的列表區塊」
    in_colon_list_group = False
    
    for item in parsed_items:
        # 1. Header 處理：重設所有縮排狀態
        if item['type'] == 'header':
            in_colon_list_group = False
            list_indent_level = 0
            
            new_level = max(2, item['level'] + header_offset)
            indent_level = max(0, new_level - 2)
            current_header_indent = "  " * indent_level
            
            hashes = "#" * new_level
            outliner_lines.append(f"{current_header_indent}- {hashes} {item['content']}")
            
            # Header 下的內容預設縮排 + 1
            current_body_indent = "  " * (indent_level + 1)
            
        # 2. Table 處理
        elif item['type'] == 'table':
            in_colon_list_group = False # 表格中斷列表
            final_indent = current_body_indent if 'current_body_indent' in locals() else ""
            
            # table_lines 是一個 list
            table_lines = item['content']
            if table_lines:
                # 第一行帶 bullet
                outliner_lines.append(f"{final_indent}- {table_lines[0]}")
                # 後續行縮排對齊文字 (Enter in Logseq block)
                # 縮排 = indent + 2 spaces
                sub_indent = final_indent + "  "
                for t_line in table_lines[1:]:
                    outliner_lines.append(f"{sub_indent}{t_line}")

        # 3. 列表項目處理
        elif item['type'] == 'list_item':
            # 判斷是否進入冒號後的列表群組
            if previous_item_type == 'paragraph' and (previous_content.endswith('：') or previous_content.endswith(':')):
                in_colon_list_group = True
            
            # 如果是 Header 之後直接接列表，通常要重設群組
            if previous_item_type == 'header':
                in_colon_list_group = False

            # 決定縮排
            final_indent = current_body_indent if 'current_body_indent' in locals() else ""
            
            # 加入來源縮排 (from indentation detection)
            source_indent = "  " * item.get('indent_level', 0)
            final_indent += source_indent

            if in_colon_list_group:
                final_indent += "  " # 增加一層縮排
            else:
                pass # 維持標準 body 縮排
                
            outliner_lines.append(f"{final_indent}- {item['content']}")
            
        # 4. Caption 處理
        elif item['type'] == 'caption':
            # Caption 縮排比 body 多一層
            final_indent = current_body_indent if 'current_body_indent' in locals() else ""
            outliner_lines.append(f"{final_indent}  - {item['content']}")

        # 5. 其他內容 (Paragraph, Quote, Image)
        else:
            # 遇到非列表項目，通常會中斷列表群組
            if item['type'] == 'paragraph':
                 in_colon_list_group = False
            
            final_indent = current_body_indent if 'current_body_indent' in locals() else ""
            
            # 加入來源縮排
            source_indent = "  " * item.get('indent_level', 0)
            final_indent += source_indent

            if item['type'] == 'quote':
                 # 若上一行是縮排列表，引用是否該跟著縮？
                 # 簡單起見，引用跟隨基本 body 縮排，再加一層 Logseq 引用縮排
                 outliner_lines.append(f"{final_indent}  - {item['content']}")
            else:
                 outliner_lines.append(f"{final_indent}- {item['content']}")
        
        previous_item_type = item['type']
        # content 可能是 list (table)，轉字串以便 check
        if isinstance(item['content'], list):
            previous_content = str(item['content'][0])
        else:
            previous_content = item['content']
            
    return '\n'.join(outliner_lines)

# 新增輔助函式
def clean_text_prefixes(text):
    import re
    # 對應 refine_notes.py 的移除清單
    prefixes = [
        "【六叔唯物解】", "【simpro】", "simpro-", "Simpro-"
    ]
    
    # 嘗試 URL decode
    try:
        import urllib.parse
        decoded = urllib.parse.unquote(text)
        if decoded != text:
             text = decoded
    except:
        pass

    for prefix in prefixes:
        if text.lower().startswith(prefix.lower()):
            text = re.sub(f"^{re.escape(prefix)}", "", text, flags=re.IGNORECASE).strip()
            
    return text.strip()

def fetch_posts():
    ensure_dirs()
    
    page = 1
    total_count = 0
    redirects = []  # 收集重定向規則
    
    print(f"🚀 開始從 {SITE_URL} 抓取文章 (含圖片)...")

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}

    while True:
        api_url = f"{SITE_URL}/wp-json/wp/v2/posts?page={page}&per_page={PER_PAGE}&_embed"
        
        # Retry mechanism
        max_retries = 3
        
        response = None
        for attempt in range(max_retries):
            try:
                print(f"  正在請求 API (頁面 {page}, 嘗試 {attempt+1}/{max_retries})...")
                response = requests.get(api_url, headers=headers, timeout=30)
                if response.status_code == 200:
                    break
                elif response.status_code in [400, 404]:
                    break
                else:
                    print(f"  ⚠️  API 回傳非 200 狀態: {response.status_code}")
            except Exception as e:
                print(f"  ⚠️  連線嘗試失敗: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)
        
        if not response:
            print("❌ 放棄此頁面，無法連線。")
            break

        if response.status_code == 400 or response.status_code == 404:
            print("✅ 已抵達最後一頁或無內容。")
            break 
            
        if response.status_code != 200:
            print(f"❌ 錯誤: 無法連結 API (Status: {response.status_code})")
            break

        try:
            posts = response.json()
        except:
            print("❌ 回傳資料非 JSON 格式")
            break
            
        if not posts:
            print("✅ 無更多文章。")
            break

        for post in posts:
            raw_title = post['title']['rendered']
            title = clean_text_prefixes(raw_title) # 清理標題
            
            slug = post['slug']
            content_html = post['content']['rendered']
            date = post['date']
            link = post['link']
            
            print(f"正在處理: {title}")

            # 取得標籤與分類
            tags = []
            categories = []
            if '_embedded' in post and 'wp:term' in post['_embedded']:
                terms = post['_embedded']['wp:term']
                for term_group in terms:
                    for term in term_group:
                        if term['taxonomy'] == 'post_tag':
                            tags.append(term['name'])
                        elif term['taxonomy'] == 'category':
                            categories.append(term['name'])
            
            # 將分類合併至標籤，以便在 Quartz 標籤頁面顯示
            # 排除 'Uncategorized'
            for cat in categories:
                if cat != "Uncategorized":
                    tags.append(cat)

            # 轉換內容
            logseq_body = convert_to_outliner(content_html)
            
            # 預設為公開 (draft: false)，但若分類包含「私密」，則設為草稿 (draft: true) 以便 Quartz 過濾
            is_draft = "false"
            for cat in categories:
                if "私密" in cat:
                    is_draft = "true"
                    break

            # 組合 Logseq Page (扁平結構，使用 frontmatter 指定分類)
            # 出版時由 logseq_publish.py 依據 categories 組織到子資料夾
            header = f"""---
title: "{title}"
date: {date}
tags: {', '.join(tags)}
categories: {', '.join(categories)}
original_url: "{link}"
draft: {is_draft}
---

"""
            # 解碼檔名並清理前綴
            try:
                import urllib.parse
                decoded_slug = urllib.parse.unquote(slug)
            except:
                decoded_slug = slug
            
            clean_slug = clean_text_prefixes(decoded_slug) # 清理檔名
            safe_filename = clean_slug.replace("/", "-").replace(":", "-")
            filename = f"{safe_filename}.md"
            
            # 寫入至 Pages 資料夾 (扁平結構，配合 Logseq)
            target_path = os.path.join(OUTPUT_DIR, filename)
            abs_path = os.path.abspath(target_path)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(header + logseq_body)
            
            total_count += 1
            print(f"✅ [{total_count}] 已儲存: {abs_path}")

        page += 1

    print(f"\n🎉 抓取完成！總共轉換 {total_count} 篇文章。")
    
    # 注意：_redirects 檔案現在由 logseq_publish.py 產生

if __name__ == "__main__":
    fetch_posts()