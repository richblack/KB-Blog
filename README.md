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

### 3. 個人化設定 (AI 輔助) 🤖

我們提供了一份 **[給 AI 的設定指南 (AI_SETUP.md)](./AI_SETUP.md)**。

**你不需要懂程式碼，只要這樣做：**
1.  打開 `AI_SETUP.md` 檔案。
2.  複製裡面的內容。
3.  貼給 ChatGPT / Claude / Gemini。
4.  AI 就會一步步問你網站叫什麼名字、網址是什麼，然後幫你寫好設定檔！

當然，如果你是開發者，也可以直接編輯 `quartz.config.ts` 和 `quartz.layout.ts`。

### 4. 建置與預覽
```bash
npx quartz build --serve
```
打開瀏覽器訪問 `http://localhost:8080` 即可看到你的網站！

## 🚀 如何將此引擎變成你自己的 (Configuration Guide)

這個引擎已經預裝了許多「六叔」的個人設定 (例如 GA4、網站標題、Logo)。在你使用之前，請務必修改以下檔案。

如果你不懂程式碼，不用擔心！每個項目我都準備了 **「給 AI 的指令 (Prompt)」**，你只要複製貼上給 ChatGPT/Claude/Gemini，它就會教你怎麼改。

### 1. 核心網站設定 (`quartz.config.ts`)
這是網站的控制中心，請修改：
*   **網站標題 (Page Title)**: 目前是 "六叔觀察站"
*   **網址 (Base URL)**: 目前是 "uncle6.me"
*   **分析追蹤 (Analytics)**: 目前是 "G-EL62JF5PED" (請換成你自己的，或刪除)
*   **語言 (Locale)**: 目前是 "zh-TW"

> 🤖 **AI Prompt**:
> "請幫我修改 `quartz.config.ts` 檔案。我要把網站標題改成 '[你的標題]'，網址改成 '[你的網址]'，並且把 Google Analytics ID 換成 '[你的ID]'。"

### 2. 網站外觀與導覽列 (`quartz.layout.ts`)
決定網站 header (導覽列) 和 footer (頁尾) 要顯示什麼連結。
*   **Navbar**: 目前有 "標籤整理"、"日期整理"、"關於我"
*   **Footer**: 目前有 GitHub 和 Discord 連結

> 🤖 **AI Prompt**:
> "請幫我修改 `quartz.layout.ts`。我想要在 header 加入一個連結到 '[你的頁面]'，並且在 footer 加入我的 Email '[你的Email]'。"

### 3. Logseq 編輯體驗 (重要！✨)
為了讓你在 Logseq 寫作時也能看到漂亮的 `++/publish` 標籤樣式，你需要把我們提供的設定檔放進你的 Logseq：

**步驟：**
1.  找到下載下來的 `logseq/` 資料夾。
2.  將裡面的 `custom.css` 和 `custom.js` 複製。
3.  貼到你自己的 Logseq Graph 資料夾中的 `logseq/` 目錄下。
4.  在 Logseq 中按下 `Re-index` 或重啟。

### 4. 網站圖標 (Logo & Favicon)
請準備你自己的圖片，替換掉預設的：
*   **Logo**: `quartz/static/logo.png` (網站左上角圖示)
*   **Favicon**: `quartz/static/icon.png` (瀏覽器分頁小圖示)

> 🤖 **AI Prompt**: 
> "我想更換網站的 Logo，我已經準備好一張圖片了，請問我要把它放在哪個資料夾？檔名需要是什麼？"

### 5. 發佈腳本 (`scripts/`)
這是本引擊的靈魂，通常**不需要修改**。
它負責將你的 Logseq 內容 (`.md`) 轉換成 Quartz 看得懂的格式。

**執行方式 (Mac/Linux)**:
```bash
# 首次執行需安裝
python3 -m venv .venv
.venv/bin/pip install PyYAML

# 每次發佈
.venv/bin/python3 scripts/publish.py
```

---
*Powered by [Quartz v4](https://quartz.jzhao.xyz/) and Logseq.*
