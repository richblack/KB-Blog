import os
import urllib.parse

PAGES_DIR = "./KB/pages"

def cleanup_duplicates():
    if not os.path.exists(PAGES_DIR):
        print("❌ 目錄不存在")
        return

    print("🚀 開始清理重複的 URL 編碼檔案...")
    
    files = [f for f in os.listdir(PAGES_DIR) if f.endswith(".md")]
    
    removed_count = 0
    renamed_count = 0
    
    for filename in files:
        # 1. 檢查是否經過 URL 編碼 (簡單判斷: 含 %)
        if '%' in filename:
            try:
                decoded_filename = urllib.parse.unquote(filename)
            except:
                continue
            
            # 如果解碼後的檔名跟原檔名不同 (代表真的是 encoded)
            if decoded_filename != filename:
                src = os.path.join(PAGES_DIR, filename)
                dst = os.path.join(PAGES_DIR, decoded_filename)
                
                # 2. 檢查目標 (解碼後) 是否已存在
                if os.path.exists(dst):
                    # 目標已存在，代表這是重複的舊檔 -> 刪除
                    print(f"🗑️  發現重複，刪除編碼版本: {filename}")
                    try:
                        os.remove(src)
                        removed_count += 1
                    except OSError as e:
                        print(f"❌ 刪除失敗: {e}")
                else:
                    # 目標不存在，這可能是漏網之魚 -> 重命名
                    # 但之前 refine_notes 應該做過這步，可能是某些特殊字元導致
                    print(f"🔄 發現未解碼檔案，執行重命名: {filename} -> {decoded_filename}")
                    try:
                        os.rename(src, dst)
                        renamed_count += 1
                    except OSError as e:
                        print(f"❌ 重命名失敗: {e}")

    print(f"\n🎉 清理完成！")
    print(f"  - 刪除 {removed_count} 個重複檔案")
    print(f"  - 重命名 {renamed_count} 個遺留檔案")

if __name__ == "__main__":
    cleanup_duplicates()
