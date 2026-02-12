import os
import urllib.parse

PAGES_DIR = "./KB/pages"

def rename_files():
    if not os.path.exists(PAGES_DIR):
        print(f"❌ {PAGES_DIR} 不存在")
        return

    print("🚀 開始將檔名解碼為中文...")
    
    count = 0
    
    for filename in os.listdir(PAGES_DIR):
        if not filename.endswith(".md"):
            continue
            
        # 嘗試解碼
        # 若 filename 本身沒有 % 編碼，unquote 會回傳原字串，不會有副作用
        decoded_name = urllib.parse.unquote(filename)
        
        if decoded_name != filename:
            # 處理可能的不合法字元 (雖然 slug 通常已經避開了，但解碼後可能會有特殊的)
            # Mac 系統通常只討厭 / 和 : (雖由系統底層轉譯)
            safe_name = decoded_name.replace("/", "-").replace(":", "-")
            
            src = os.path.join(PAGES_DIR, filename)
            dst = os.path.join(PAGES_DIR, safe_name)
            
            try:
                os.rename(src, dst)
                print(f"✅ Renamed: {filename[:20]}... -> {safe_name}")
                count += 1
            except OSError as e:
                print(f"❌ 重新命名失敗 {filename}: {e}")

    print(f"\n🎉 完成！共重新命名 {count} 個檔案。")

if __name__ == "__main__":
    rename_files()
