# AI 設定助手指南 (AI Setup Guide)

**給 AI 助手 (ChatGPT, Claude, Gemini) 的指令：**

你好！使用者剛剛下載了這個 Logseq + Quartz 的網站發佈引擎。請依照以下步驟，協助使用者完成個人化設定。

## 你的任務

請一步步引導使用者提供資訊，並為他們生成修改後的程式碼。

### 第一步：收集資訊
請詢問使用者以下問題：
1.  **網站標題**：例如「小明的筆記花園」。
2.  **網站網址 (Base URL)**：例如 `notebook.example.com` (如果還沒有，可以先填 `example.com`)。
3.  **Google Analytics ID**：如果有 GA4 追蹤碼 (例如 `G-XXXXXXXX`)，請提供；如果沒有，請詢問是否要關閉追蹤。
4.  **關於我頁面**：是否要建立一個「關於我」的連結？

### 第二步：生成 `quartz.config.ts`
根據使用者提供的資訊，請生成一份完整的 `quartz.config.ts` 設定區塊 (只顯示 `config` 物件部分即可)，並特別標註修改了哪些地方。

*   `pageTitle`: 填入網站標題。
*   `baseUrl`: 填入網址。
*   `analytics`: 填入 ID 或設為 null。

### 第三步：生成 `quartz.layout.ts`
如果使用者想要修改導覽列 (Navbar)，請提供修改建議。默認保留 `Archvie` (歸檔) 和 `Tags` (標籤) 是好的選擇。

### 第四步：提醒 Logseq 設定
請提醒使用者，為了達到最佳寫作體驗，必須將專案中的 `logseq/` 資料夾內容 (custom.css, custom.js) 複製到他們自己的 Logseq Graph 中。

### 第五步：更換 Logo
提醒使用者，如果他們有自己的 Logo，請將圖片命名為 `logo.png` 並放入 `quartz/static/` 資料夾中。

---

**給使用者的提示：**
請將這份文件的內容 (或直接把這個檔案) 貼給 AI，它就會變身為你的專屬設定工程師！
