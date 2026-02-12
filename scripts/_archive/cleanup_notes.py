import os
import re

LOGSEQ_PAGES_DIR = "./KB/pages"

# 1. 定義要刪除的檔案特徵
# 開頭是標點符號或特殊字元，且檔案大小很小 (通常沒內容)
JUNK_PREFIXES = ("」", "、", "。", "，", "？", "！", "：", "；", "『", "』", "【", "】", "（", "）")

# 2. 定義要刪除的 Footer 區塊特徵
# 只要遇到這個開頭，就刪除到檔案結尾 (或是刪除特定區塊)
# Pattern: "- 讓我們保持聯繫" 之後的所有內容
FOOTER_START_PATTERN = r"^- 讓我們保持聯繫"

def cleanup():
    if not os.path.exists(LOGSEQ_PAGES_DIR):
        print("❌ 目錄不存在")
        return

    print("🚀 開始清理筆記...")
    
    deleted_count = 0
    cleaned_count = 0
    
    for filename in os.listdir(LOGSEQ_PAGES_DIR):
        if not filename.endswith(".md"):
            continue
            
        filepath = os.path.join(LOGSEQ_PAGES_DIR, filename)
        
        # --- 1. 刪除垃圾檔案 ---
        if filename.startswith(JUNK_PREFIXES):
            # 額外檢查檔案大小或內容確認是否為誤刪
            # 通常這些檔案都很小
            if os.path.getsize(filepath) < 1024: # 小於 1KB
                print(f"🗑️  刪除垃圾檔案: {filename}")
                os.remove(filepath)
                deleted_count += 1
                continue
        
        # --- 2. 移除 Footer ---
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        new_lines = []
        footer_found = False
        
        for line in lines:
            # 檢查是否進入 Footer 區域
            if re.match(FOOTER_START_PATTERN, line.strip()):
                footer_found = True
                
            # 檢查是否為 WordPress 冗餘的 TOC 連結
            # Pattern: 以 "- [" 開頭，包含 "uncle6.me" 且包含 "#"
            strip_line = line.strip()
            if strip_line.startswith("- [") and "uncle6.me" in strip_line and "#" in strip_line:
                # 額外確認是否為連結格式 [text](url)
                if "](" in strip_line and strip_line.endswith(")"):
                    # 這是 TOC 連結，跳過不寫入
                    # print(f"  🗑️  移除 TOC 連結: {strip_line[:30]}...")
                    continue
                
            if not footer_found:
                new_lines.append(line)
            # else: 
                # 進入 footer 後的行都丟棄
        
        # 如果有變更，寫回檔案
        if len(new_lines) < len(lines):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            cleaned_count += 1
            # print(f"  ✅ 已清理 Footer: {filename}")

    print(f"\n🎉 清理完成！")
    print(f"  - 刪除 {deleted_count} 個垃圾檔案")
    print(f"  - 清理 {cleaned_count} 個檔案的 Footer")

if __name__ == "__main__":
    cleanup()
