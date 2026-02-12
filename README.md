# Logseq AI Publisher (Quartz Edition) 🚀

> **把你的 Logseq 筆記變成一個精美、高效的網站。**
> *專為 WordPress 移民和喜歡寫作多於寫程式的人設計。*

![Quartz Logo](https://raw.githubusercontent.com/jackyzha0/quartz/v4/quartz/static/icon.png)

## 為什麼選擇這個？

如果你來自 **WordPress**，或者只是想要一個個人的知識花園，這套設定結合了兩者的優點：

1.  **在 Logseq 中寫作**：使用你喜歡的工具，不需學習新的 CMS。
2.  **AI 輔助發佈**：複雜的工作（如 SEO、標籤整理、格式調整）都由內建的腳本和 AI 代理人（Agent）自動處理。
3.  **擁有你的數據**：你的內容以 Markdown 檔案儲存，而不是被鎖在資料庫裡。

## 核心功能

### 🤖 AI 優先的工作流
這個引擎是專為與 AI Coding Agents（如 Gemini, Cline, Cursor）合作而設計的。
-   **內建腳本**：我們在 `scripts/` 中提供了 Python 腳本來處理繁重的工作。
-   **自動格式化**：系統會自動將 Logseq 特有的語法清理成適合網頁的格式。

### 📝 Logseq 深度整合
-   **區塊級發佈 (Block Publishing)**：在 Logseq 中對任何區塊加上標籤（例如 `#public`），它就會自動變成一篇獨立的文章。
-   **圖譜同步**：你的內部連結、反向連結 (Backlinks) 和標籤在網頁上都能完美運作。

### 🗂️ 自動化整理
-   **日期歸檔**：內容會自動按年份/月份歸檔。
-   **標籤索引**：點擊標籤即可查看所有相關文章。
-   **"關於我" 頁面**：輕鬆自定義個人介紹頁面。

## 如何開始

### 1. 下載這個引擎 (Clone)
這是你的 **網站引擎**，包含建置網站所需的所有程式碼。
```bash
git clone https://github.com/richblack/KB-Blog.git my-website
cd my-website
```

### 2. 加入你的內容
將你的 Logseq `pages` 和 `journals` 資料夾複製到 `content` 資料夾中。
*(或者讓 AI Agent 幫你同步！)*

### 3. 自定義
-   **設定**：打開 `quartz.config.ts` 修改你的網站名稱和網址。
-   **Logo**：將 `quartz/static/logo.png` 替換成你自己的圖片。

### 4. 建置與預覽
```bash
npx quartz build --serve
```
打開瀏覽器訪問 `http://localhost:8080` 即可看到你的網站！

## 給開發者（或 AI Agents）
-   **Scripts**：查看 `scripts/` 資料夾，這裡是 Python 發佈邏輯的核心。
-   **Layout**：`quartz.layout.ts` 定義了網站的外觀和感覺。
-   **Styles**：`quartz/styles/custom.scss` 可以讓你調整顏色和字體。

---
*Powered by [Quartz v4](https://quartz.jzhao.xyz/) and Logseq.*
