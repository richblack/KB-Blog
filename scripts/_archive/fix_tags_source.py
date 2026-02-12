#!/usr/bin/env python3
"""
scripts/fix_tags_source.py
功能：一次性掃描 KB 目錄下的所有 .md 檔案，解析 Frontmatter 並清理 Tags
使用方式：
    python3 scripts/fix_tags_source.py
"""

import os
import re
from pathlib import Path

KB_DIR = "./KB"

def clean_tags(tags_list):
    """
    清洗、正規化、合併標籤
    """
    if not tags_list: return []
    
    # 1. Blacklist (全小寫比對)
    BLACKLIST = {
        "#", "注意看這行", "這行可以不寫", "", 
        "h1", "ul", "ol", "listtotable", "centered", "right", "justified", 
        "outline", "nospace", "imagecaption", "tablecaption", "book100",
        "simpro", "fusionflow", "日本", "長篇小說", "現實主義", "東京", 
        "20世紀", "愛情", "精神官能症", "曾改編電影"
    }
    
    # 2. Renames (Canonical Mapping)
    RENAMES = {
        "product manager 產品經理": "PM",
        "product plan 產品企劃": "PM",
        "product manager": "PM",
        "product plan": "PM",
        "remnote教學": "RemNote", 
    }
    
    cleaned = []
    seen = set()
    
    for tag in tags_list:
        t = str(tag).strip()
        if not t: continue
        
        # 移除開頭 #
        t = t.lstrip("#")
        
        # basic check
        if t.lower() in BLACKLIST:
            continue
        
        # 3. Splitting (Atomic Tags: Prefix-based)
        # 複合標籤拆分: Logseq筆記法 -> Logseq, 筆記法
        PREFIXES = [
            "GraphRAG", "Heptabase", "Logseq", "Notion", "RemNote", "Obsidian", "AI"
        ]
        
        split_tags = [t]
        
        for p in PREFIXES:
            # Case-insensitive prefix match
            # 如果標籤以 Prefix 開頭，且長度大於 Prefix (表示有 Suffix)
            if t.lower().startswith(p.lower()) and len(t) > len(p):
                suffix = t[len(p):]
                # 簡單清理 Suffix 開頭的連接符 (例如 Logseq-custom -> custom)
                # 但因為之前的步驟移除了連字號? 不，這裡 t 是原始 tag
                # 如果 suffix 是 "-abc", lstrip 變成 "abc"
                suffix = suffix.lstrip("- _")
                
                if suffix:
                   split_tags = [p, suffix]
                   break # 只拆分一次，避免多重拆分邏輯過於複雜
            
        for sub_tag in split_tags:
            st = sub_tag.strip()
            if not st: continue
            
            # Check Rename
            if st.lower() in RENAMES:
                st = RENAMES[st.lower()]
            
            # 4. Normalization (CamelCase & English-Chinese mixed)
            # CamelCase 處理：將 - 或 空格 分割的字首大寫
            parts = re.split(r'[- ]+', st)
            normalized_parts = []
            for p in parts:
                if re.match(r'^[a-zA-Z0-9]+$', p): # 純英文/數字部分
                    if p.islower():
                        normalized_parts.append(p.capitalize())
                    else:
                        normalized_parts.append(p)
                else:
                    normalized_parts.append(p) # 中文或其他
            
            final_tag = "".join(normalized_parts)
            
            # Final check
            if final_tag.lower() not in BLACKLIST and final_tag not in seen:
                cleaned.append(final_tag)
                seen.add(final_tag)
                
    return cleaned

def parse_tags_from_string(val):
    """解析 tags 字串，支援 list "[a, b]" 或 comma string "a, b" """
    val = val.strip()
    if val.startswith("[") and val.endswith("]"):
        clean = val.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
        return [t.strip() for t in clean.split(",") if t.strip()]
    else:
        return [t.strip() for t in val.split(",") if t.strip()]

def process_file(filepath):
    """讀取並修改檔案中的 tags"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"⚠️ 無法讀取 {filepath}: {e}")
        return False

    modified = False
    new_lines = []
    
    i = 0
    in_yaml = False
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 簡單判定 YAML 區塊 (僅在檔案開頭)
        if i == 0 and stripped == "---":
            in_yaml = True
            new_lines.append(line)
            i += 1
            continue
        if in_yaml and stripped == "---":
            in_yaml = False
            new_lines.append(line)
            i += 1
            continue
            
        # 判斷是否為 Tags 行
        # 支援格式:
        # 1. tags: [a, b]  (YAML)
        # 2. tags: a, b    (YAML)
        # 3. tags:: a, b   (Logseq Page Property)
        # 4. - tags: a, b  (Logseq Block Property)
        # 5.   tags:: a, b (Logseq Indented Property)
        
        # Regex: 
        # ^\s*       :開頭空白
        # (?:[-*]\s*)+ :可選的 "- " 或 "* " 或 "-- " (non-capturing group, one or more times)
        # tags       :關鍵字
        # (:|::)     :分隔符
        # \s+(.*)    :內容
        
        # Modified to handle "-- tags" or "- - tags" typos
        match = re.match(r'^(\s*)((?:[-*]+\s*)+)?tags(:{1,2})\s+(.*)', line)
        
        if match:
            indent = match.group(1)
            dash = match.group(2) or ""
            sep = match.group(3)
            val = match.group(4)
            
            # 解析
            current_tags = parse_tags_from_string(val)
            cleaned_tags = clean_tags(current_tags)
            
            # 重組
            # 如果是 List 格式 ['a', 'b']，原樣保留 List 格式比較安全?
            # 但為了統一，若原本是 List 字串，我們重組成 List 字串
            # 若原本是逗號分隔，則維持逗號分隔
            
            is_bracket_list = val.strip().startswith("[") and val.strip().endswith("]")
            
            if is_bracket_list:
                # 轉回 ['a', 'b'] 格式
                # 注意: Logseq 有時用雙引號，有時單引號
                # 這裡統一用單引號
                quoted_tags = [f"'{t}'" for t in cleaned_tags]
                new_val_str = "[" + ", ".join(quoted_tags) + "]"
            else:
                new_val_str = ", ".join(cleaned_tags)
                
            new_line_content = f"{indent}{dash}tags{sep} {new_val_str}\n"
            
            if sorted(current_tags) != sorted(cleaned_tags):
                print(f"  ✨ [Fixed] {filepath.name}: {val.strip()} -> {new_val_str}")
                modified = True
                new_lines.append(new_line_content)
            else:
                new_lines.append(line)
                
        else:
            new_lines.append(line)
            
        i += 1

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    return False

def main():
    print("🚀 開始清理 Logseq 原始檔中的 Tags ...")
    count = 0
    for root, dirs, files in os.walk(KB_DIR):
        for file in files:
            if file.endswith(".md"):
                path = os.path.join(root, file)
                if process_file(Path(path)):
                    count += 1
    
    print(f"\n✅ 清理完成！共修改了 {count} 個檔案。")

if __name__ == "__main__":
    main()
