import os
import re
import urllib.parse

PAGES_DIR = "./KB/pages"

PREFIXES_TO_REMOVE = [
    "【六叔唯物解】",
    "【simpro】",
    "【Simpro】",
    "simpro-",
    "Simpro-",
    "【六叔唯物論】",
    "【六叔觀察站】",
    "【跨能致勝】", # Optional, but based on pattern
    "【學生zk】",    # Optional
]

# User specifically asked for: 【六叔唯物解】, 【simpro】, simpro-
# I will stick to these strictly first, plus case variants.
TARGET_PREFIXES = [
    "【六叔唯物解】",
    "【simpro】",
    "simpro-",
    "Simpro-"
]

def clean_text(text):
    original = text
    # 1. 解碼 (以防有漏網之魚)
    try:
        decoded = urllib.parse.unquote(text)
        if decoded != text:
             text = decoded
    except:
        pass
        
    # 2. 移除前綴
    for prefix in TARGET_PREFIXES:
        if text.lower().startswith(prefix.lower()): # Case insensitive check for the prefix text
            # Slicing with len(prefix) might be wrong if case differs
            # Use regex for robust replacement at start
            pattern = re.compile(f"^{re.escape(prefix)}", re.IGNORECASE)
            text = pattern.sub("", text)
            
    # 3. 移除前後空格
    text = text.strip()
    
    return text

def refine_notes():
    if not os.path.exists(PAGES_DIR):
        print("❌ 目錄不存在")
        return

    print("🚀 開始優化筆記 (移除前綴、修復標題)...")
    
    renamed_count = 0
    refined_content_count = 0
    
    # 先做檔名重命名 (先收集，避免 iterator 失效)
    files = [f for f in os.listdir(PAGES_DIR) if f.endswith(".md")]
    
    # 建立 file map 以便後續處理內容時知道新檔名
    file_map = {f: f for f in files} 
    
    for filename in files:
        # 解碼檔名 (有些可能還是 encoded)
        try:
            decoded_filename = urllib.parse.unquote(filename)
        except:
            decoded_filename = filename
            
        clean_name = decoded_filename
        
        # 移除前綴
        for prefix in TARGET_PREFIXES:
            if clean_name.lower().startswith(prefix.lower()):
                 clean_name = re.sub(f"^{re.escape(prefix)}", "", clean_name, flags=re.IGNORECASE).strip()
        
        # 如果檔名有變
        if clean_name != decoded_filename or decoded_filename != filename:
            # 確保副檔名
            if not clean_name.endswith(".md"): 
                 clean_name += ".md"
            
            src = os.path.join(PAGES_DIR, filename)
            dst = os.path.join(PAGES_DIR, clean_name)
            
            if src != dst:
                if os.path.exists(dst):
                    print(f"⚠️  跳過重命名，目標已存在: {clean_name}")
                else:
                    try:
                        os.rename(src, dst)
                        print(f"Dg 重新命名: {filename} -> {clean_name}")
                        renamed_count += 1
                        file_map[filename] = clean_name # Update map
                    except OSError as e:
                        print(f"❌ 重命名失敗 {filename}: {e}")

    # 現在處理內容 (使用 logseq 屬性更新 & Header 修復)
    # 重新掃描目錄確保正確
    files = [f for f in os.listdir(PAGES_DIR) if f.endswith(".md")]
    
    for filename in files:
        filepath = os.path.join(PAGES_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        new_lines = []
        modified = False
        
        for line in lines:
            original_line = line
            stripped = line.strip()
            
            # A. 處理 title:: 屬性
            if stripped.startswith("title::"):
                key, val = line.split("::", 1)
                new_val = clean_text(val.strip())
                if new_val != val.strip():
                    line = f"{key}:: {new_val}\n"
                    modified = True
            
            # B. 處理 Headers
            # 檢查是否為 header 行 (包含縮排的情況?)
            # Logseq outliner header 通常是 "- # Title" 或 "- ## Title"
            # 下載腳本目前產出的格式是 "- ## **Title**"
            
            # 定義 Regex 抓取 Header
            # 容許縮排, dash, spaces, hash symbols
            header_match = re.search(r"^(\s*-\s*)(#+)\s*(.*)", line)
            
            if header_match:
                prefix_dash = header_match.group(1) # "  - "
                hashes = header_match.group(2)      # "##"
                content = header_match.group(3)     # "**Title**"
                
                # B1. 移除 Bold (**...**)
                # 只有當整行為 bold 時才移除？或者移除所有 bold？
                # 用户說 "如果已經用 header，就不要再用 ** 來包覆"
                # 所以移除外層的 **
                if content.strip().startswith("**") and content.strip().endswith("**"):
                    content = content.strip()[2:-2].strip()
                    modified = True
                
                # B2. 移除前綴 (內容標題)
                new_content = clean_text(content)
                if new_content != content:
                    content = new_content
                    modified = True
                    
                # B3. 解碼可能的亂碼 (再做一次確保)
                try:
                    decoded = urllib.parse.unquote(content)
                    if decoded != content:
                        content = decoded
                        modified = True
                except:
                    pass
                
                # 重組
                if modified:
                    line = f"{prefix_dash}{hashes} {content}\n"
            
            new_lines.append(line)
            
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            refined_content_count += 1
            # print(f"  ✨ 優化內容: {filename}")

    print(f"\n🎉 優化完成！")
    print(f"  - 重新命名 {renamed_count} 個檔案")
    print(f"  - 修正 {refined_content_count} 個檔案的內容 (Title前綴/Header粗體)")

if __name__ == "__main__":
    refine_notes()
