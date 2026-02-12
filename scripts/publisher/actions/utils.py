import re
import os
from typing import List

def sanitize_content_links(text: str, for_quartz: bool = True) -> str:
    """
    清理 Logseq 內容中的連結格式問題：
    1. 移除 [["Title"]] 內部的多餘引號，避免 404
    2. 如果 for_quartz=True: 將空格轉為 - 以符合 Quartz Slug 邏輯
    """
    if not text:
        return text

    def clean_link_content(match):
        content = match.group(1)
        # 移除標題內的引號
        content = content.replace('"', '').replace("'", "").strip()
        
        if for_quartz:
            # Quartz 輸出時將空格轉為 -
            # 注意：管道符號理論上已經不存在，但為了保險起見仍做替換
            content = content.replace('|', '-').replace('｜', '-').replace(' ', '-')
        
        return f'[[{content}]]'

    # 使用 Regex 匹配所有 [[...]] 並清理其內容
    text = re.sub(r'\[\[(.*?)\]\]', clean_link_content, text)
    
    return text

def get_safe_path_elements(title: str, categories: str):
    """
    統一生成檔案路徑與目標連結的邏輯。
    """
    if not categories:
        categories = "Uncategorized"
    primary_cat = categories.split(",")[0].strip() if "," in categories else categories.strip()
    
    # 處理分類
    if primary_cat == ".":
        safe_cat = ""
    else:
        safe_cat = primary_cat.replace("/", "-").replace(" ", "-")
    
    # 處理標題 (移除 /, :, |, ｜, 並將空格轉為 -)
    safe_title = title.replace("/", "-").replace(":", "-").replace("|", "-").replace("｜", "-").replace(" ", "-").strip().lstrip("#").strip()
    
    return safe_cat, safe_title

def clean_tags(tags: List[str]) -> List[str]:
    """
    集中清理標籤邏輯 (Ported from fix_tags_source.py)
    """
    if not tags:
        return []
    
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
    
    for tag in tags:
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
