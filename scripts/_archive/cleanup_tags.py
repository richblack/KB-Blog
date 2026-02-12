#!/usr/bin/env python3
"""
cleanup_tags.py
清理 KB/pages 下 markdown 檔案中 tags 欄位過多的括號。
例如: tags: [[[[[[['Tag A', 'Tag B']]]]]]] -> tags: ['Tag A', 'Tag B']
"""

import os
import re
from pathlib import Path

# 設定
KB_PAGES_DIR = "./KB/pages"

def clean_tags_in_file(filepath):
    """
    讀取檔案，檢查 tags 欄位是否有過多括號，若有則替換。
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"⚠️ 無法讀取 {filepath}: {e}")
        return False

    modified = False
    new_lines = []
    
    # Regex 說明:
    # ^tags:\s*        -> 以 tags: 開頭，後面接空白
    # \[+              -> 一個或多個 [
    # (.*?)            -> 捕捉內容 (Group 1)，非貪婪匹配
    # \]+              -> 一個或多個 ]
    # \s*$             -> 結尾空白
    #
    # 注意：這裡假設 tags 都在同一行。
    # 針對像 [[[[[[['A', 'B']]]]]]] 這種結構，我們要提取其中的 'A', 'B' 部分，
    # 但為了單純化，我們可以用簡單的字串取代把它們變回一層括號。
    
    # 更穩健的做法：
    # 只要看到 tags: 且包含 [[，我們就嘗試解析出最內層的內容，然後包回 ['...']
    
    for line in lines:
        if line.startswith("tags:") and "[[" in line:
            # 嘗試提取內容
            original_line = line.strip()
            
            # 使用 regex 抓取最內層的 list content
            # 假設內容是單引號包起來的字串列表，中間有逗號分隔
            # 我們先把所有 [ 和 ] 去掉，然後補回前後各一個
            
            content_part = line.split("tags:", 1)[1].strip()
            
            # 檢查是否真的有很多括號
            if content_part.startswith("[["):
                # 去除所有的 [ 和 ]
                clean_content = content_part.replace("[", "").replace("]", "")
                
                # 重新組合
                new_line = f"tags: [{clean_content}]\n"
                
                if new_line != line:
                    new_lines.append(new_line)
                    modified = True
                    # print(f"   Fixing: {original_line[:50]}... -> {new_line.strip()}")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    if modified:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            return True
        except Exception as e:
            print(f"⚠️ 無法寫入 {filepath}: {e}")
            return False
    
    return False

def main():
    print("🚀 開始清理 tags 多餘括號...")
    
    pages_path = Path(KB_PAGES_DIR)
    if not pages_path.exists():
        print(f"❌ 目錄不存在: {KB_PAGES_DIR}")
        return

    md_files = list(pages_path.rglob("*.md"))
    count = 0
    
    for md_file in md_files:
        if clean_tags_in_file(md_file):
            print(f"✅ 已修復: {md_file.name}")
            count += 1
            
    print(f"\n🎉 完成！共修復了 {count} 個檔案。")

if __name__ == "__main__":
    main()
