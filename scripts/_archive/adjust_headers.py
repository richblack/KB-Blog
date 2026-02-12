import os
import re

PAGES_DIR = "./KB/pages"

def adjust_headers():
    if not os.path.exists(PAGES_DIR):
        print("❌ 目錄不存在")
        return

    print("🚀 開始調整標題層級 (H2 起始, 補 H1)...")
    
    files = [f for f in os.listdir(PAGES_DIR) if f.endswith(".md")]
    count = 0
    
    for filename in files:
        filepath = os.path.join(PAGES_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        new_lines = []
        
        # 1. 抓取 Meta 中的 Title
        title = ""
        meta_end_index = -1
        
        for i, line in enumerate(lines):
            if line.strip().startswith("title::"):
                title = line.split("::", 1)[1].strip()
            if line.strip() == "" and i > 0 and i < 10: # 假設 meta block 在前 10 行內結束
                # 簡單判斷 meta 區塊結束 (通常是第一個空行，但也可能沒有)
                # 我們假設 meta block 之後接著正文
                pass
        
        # 尋找正文開始處 (跳過 meta)
        body_start_index = 0
        if lines and lines[0].strip().startswith("meta:"):
            for i, line in enumerate(lines):
                if i == 0: continue
                # 如果遇到空行或非縮排內容，可能是正文開始
                # 但 Logseq meta 通常是連續的屬性
                # 直到遇到第一個 `-` 或 `#` 或空行
                if line.strip() == "":
                    body_start_index = i + 1
                    break
        
        meta_lines = lines[:body_start_index]
        body_lines = lines[body_start_index:]
        
        # 2. 掃描 Body 中的最小 Header Level
        min_level = 999
        header_indices = []
        
        for i, line in enumerate(body_lines):
            # 匹配 Logseq 標題格式: "- #...", "- ##...", "  - ###..."
            # Regex: 縮排 + "- " + 一個以上 "#" + 空白
            match = re.search(r"^(\s*-\s*)(#+)\s", line)
            if match:
                level = len(match.group(2))
                if level < min_level:
                    min_level = level
                header_indices.append((i, level))
        
        # 如果找不到任何標題，min_level 保持 999
        if min_level == 999:
            min_level = 2 # 預設不調整
            
        # 計算偏移量：目標是讓最小 level 變成 2 (H2)
        # 例如 min=3 (H3), offset = 2 - 3 = -1.  H3 + (-1) = H2
        # 例如 min=1 (H1), offset = 2 - 1 = +1.  H1 + 1 = H2 (雖然 H1 應該保留給大標題，但這裡我們統一 body 結構)
        # Wait, if H1 exists in body, it might be the title?
        # User implies body headers should be H2+.
        # Let's target min_level -> 2.
        
        offset = 2 - min_level
        
        # 3. 調整 Body Headers
        if offset != 0:
            for idx, level in header_indices:
                line = body_lines[idx]
                match = re.search(r"^(\s*-\s*)(#+)(\s.*)", line)
                if match:
                    prefix = match.group(1)
                    old_hashes = match.group(2)
                    content = match.group(3)
                    
                    new_level = max(2, len(old_hashes) + offset) # 最少 H2
                    new_hashes = "#" * new_level
                    
                    # 同時調整縮排? 
                    # 原本邏輯: H2 indent 0, H3 indent 1...
                    # indent_level = max(0, new_level - 2)
                    # new_indent = "  " * indent_level
                    # prefix 包含 "- "，我們只替換 indent 部分
                    
                    # 重新建構 prefix
                    # Logseq 原本: indent + "- "
                    indent_level = max(0, new_level - 2)
                    new_prefix = ("  " * indent_level) + "- "
                    
                    body_lines[idx] = f"{new_prefix}{new_hashes}{content}\n"
                    
        # 4. 檢查是否已有 H1 Title (檢查 body 第一個 block)
        has_h1 = False
        if len(body_lines) > 0:
            first_line = body_lines[0].strip()
            # 檢查是否是 "- # Title" 格式
            if re.search(r"^\s*-\s*#\s", first_line):
                has_h1 = True
        
        # 如果沒有 H1 且有抓到 title，則插入
        # 只有當 body 不為空時才插入，或者是空檔也插入？
        if not has_h1 and title:
            # 確保 H1 格式: "- # Title"
            h1_line = f"- # {title}\n"
            body_lines.insert(0, h1_line)
            
        # 5. 寫回檔案
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(meta_lines + body_lines)
            
        count += 1
        
    print(f"🎉 完成！共調整 {count} 個檔案。")

if __name__ == "__main__":
    adjust_headers()
