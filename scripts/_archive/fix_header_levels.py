#!/usr/bin/env python3
"""
fix_header_levels.py
掃描並修正 Logseq markdown 檔案中的標題層級
確保最小標題層級為 H2 (##)，同時調整整體階層關係

使用方式:
    cd /Users/youlinhsieh/Documents/knowledge_worker
    .venv/bin/python3 fix_header_levels.py

規則:
    - 掃描所有 H3 及以上的標題
    - 如果沒有 H2，將最小層級 (如 H3) 提升為 H2
    - 其他層級跟著調整，保持相對關係
    - H4 → H3, H5 → H4, 依此類推
"""

import os
import re
from pathlib import Path

# 設定 - 可以處理扁平或分類資料夾結構
PAGES_DIR = "./KB/pages"

def find_header_levels(content):
    """找出內容中所有 header 的層級，排除 footer 區塊"""
    # 匹配 Logseq outliner 格式的 header: "- ## Title" 或 "  - ### Title"
    pattern = r'^(\s*-\s*)(#{2,6})\s+(.+)$'
    levels = []
    
    # Footer 關鍵字 - 這些 header 不計入層級判斷
    footer_keywords = ['註釋', '參考', '附錄', '引用', '備註', 'References', 'Notes', 'Footnotes']
    
    for line in content.split('\n'):
        match = re.match(pattern, line)
        if match:
            hashes = match.group(2)
            title = match.group(3).strip()
            level = len(hashes)
            
            # 檢查是否為 footer section
            is_footer = any(kw in title for kw in footer_keywords)
            
            if not is_footer:
                levels.append(level)
    
    return set(levels) if levels else set()

def fix_headers(content, min_current_level):
    """調整 header 層級"""
    if min_current_level <= 2:
        return content, 0  # 已經正確，無需調整
    
    # 計算需要提升的層級數
    offset = min_current_level - 2
    
    lines = content.split('\n')
    fixed_lines = []
    fixes_count = 0
    
    pattern = r'^(\s*-\s*)(#{2,6})(\s+.+)$'
    
    for line in lines:
        match = re.match(pattern, line)
        if match:
            prefix = match.group(1)  # "  - " 之類的
            hashes = match.group(2)
            rest = match.group(3)    # " Title"
            
            current_level = len(hashes)
            new_level = max(2, current_level - offset)
            new_hashes = '#' * new_level
            
            if new_level != current_level:
                fixes_count += 1
            
            fixed_lines.append(f"{prefix}{new_hashes}{rest}")
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), fixes_count

def process_file(filepath):
    """處理單一檔案"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"讀取錯誤: {e}"
    
    # 找出當前最小 header 層級
    levels = find_header_levels(content)
    
    if not levels:
        return False, "無 header"
    
    min_level = min(levels)
    
    if min_level <= 2:
        return False, "已正確 (H2)"
    
    # 修正 headers
    fixed_content, fixes_count = fix_headers(content, min_level)
    
    if fixes_count == 0:
        return False, "無需修正"
    
    # 寫回檔案
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        return True, f"修正 {fixes_count} 個 header (H{min_level}→H2)"
    except Exception as e:
        return False, f"寫入錯誤: {e}"

def main():
    print("🔧 開始修正 Header 層級...")
    print(f"📁 掃描目錄: {PAGES_DIR}")
    print()
    
    pages_path = Path(PAGES_DIR)
    
    # 支援扁平和分類資料夾結構
    md_files = list(pages_path.glob("**/*.md"))
    
    fixed_count = 0
    skipped_count = 0
    error_count = 0
    
    for md_file in sorted(md_files):
        relative_path = md_file.relative_to(pages_path)
        
        # 跳過 index.md
        if md_file.name == "index.md":
            continue
        
        success, message = process_file(md_file)
        
        if success:
            print(f"✅ {relative_path}: {message}")
            fixed_count += 1
        elif "錯誤" in message:
            print(f"❌ {relative_path}: {message}")
            error_count += 1
        else:
            # 靜默跳過無需修正的檔案
            skipped_count += 1
    
    print()
    print(f"🎉 完成！")
    print(f"   ✅ 已修正: {fixed_count} 篇")
    print(f"   ⏭️ 跳過: {skipped_count} 篇 (無 header 或已正確)")
    print(f"   ❌ 錯誤: {error_count} 篇")

if __name__ == "__main__":
    main()
