---
name: google-easy-auth
description: 學生一步完成 Google Workspace（Drive、Sheets、Docs、Slides、Gmail、Calendar）與 Google Apps Script 的 OAuth 授權。當使用者要連結 Google 帳號、設定 Google Workspace MCP、或要用 Apps Script 發布網頁但尚未授權時使用。會在聊天中產生「只需要打勾」的授權清單，自動開瀏覽器、檢查有沒有漏勾，並寫入 ~/.clasprc.json 與 MCP 設定。支援 Windows 原生 PowerShell（零安裝 Python）與跨平台 Python。
---

# Google Workspace 一鍵授權（google-easy-auth）

給 AI 助手（Antigravity、Claude Code、Codex 等能在本機執行指令的 Agent）的操作規則。
目標：學生只要「點連結 → 打勾 → 按繼續」，其他全部由你完成。

## 你（AI）要做的事，依序執行

### 1. 判斷作業系統（Windows 優先使用原生 PowerShell）
- **Windows（推薦零依賴管道）**：
  直接使用內建 PowerShell，**完全不需要安裝 Python 或 pip**！
  - 檢查狀態：`powershell -ExecutionPolicy Bypass -File <SKILL_DIR>/scripts/check_status.ps1`
  - 啟動授權：`powershell -ExecutionPolicy Bypass -File <SKILL_DIR>/scripts/easy_auth.ps1`
- **macOS / Linux（或 Windows 指定使用 Python）**：
  確認有 Python 3.8 以上（`python3 --version`）。
  - 檢查狀態：`python3 <SKILL_DIR>/scripts/check_status.py`
  - 啟動授權：`python3 <SKILL_DIR>/scripts/easy_auth.py`

`<SKILL_DIR>` 是這份 SKILL.md 所在的資料夾。

### 2. 先做健康檢查
執行上述對應系統的檢查指令：
- 全部都是 ✅ → 告訴學生「已經授權過了，可以直接使用」，並詢問是否要開始使用 Google 工具或發布打卡系統。

### 3. 在聊天中貼出授權清單（必做，不可只丟指令）
直接用下方「聊天輸出範本」回覆學生。連結可用印出的 URL。

### 4. 啟動授權精靈（在背景執行，不要卡住對話）
- **Windows**：
  ```powershell
  powershell -ExecutionPolicy Bypass -File <SKILL_DIR>/scripts/easy_auth.ps1
  ```
- **macOS / Linux**：
  ```bash
  python3 <SKILL_DIR>/scripts/easy_auth.py
  ```
  依你自己的身分加參數：
  - Claude Code → 加 `--claude`
  - Codex → 加 `--codex`
  - Antigravity → 不用加（預設就會寫入 `~/.gemini/config/mcp_config.json`）

精靈會自動開瀏覽器、等學生按完、換取 Token、檢查有沒有漏勾，並：
- 寫入 `~/.clasprc.json`（Apps Script API 用）
- **合併**寫入 MCP 設定（只新增或更新 `google-workspace`，其他 MCP 不動，原檔備份為 `.bak`）
- 檢測 Apps Script API 開關狀態（若未開提示開啟）

### 5. 看結束代碼回報
| 代碼 | 意思 | 你要做的 |
|---|---|---|
| 0 | 成功 | 告知學生授權已成功！請重新啟動 AI 工具載入工具。若要建立打卡系統，無縫引導學生切換至 `appscript_skill` |
| 2 | 有權限沒打勾 | 白話告知學生：「在 Google 權限畫面時，直接按了繼續未勾選。Google 預設全空，必須點最上方的【全選】」，貼上缺少清單並重跑步驟 4 |
| 1 | 逾時 / 取消 / 連接埠被佔用 | 依輸出訊息處理；若連接埠被佔用請關閉先前殘留視窗再重試 |

---

## 聊天輸出範本（照抄，用繁體中文）

````markdown
### 🎓 Google 帳號授權：通關四字訣【個 ➔ 進 ➔ 全 ➔ 續】

瀏覽器已為您自動開啟！沒彈出的話請點這裡 👉 **[開啟 Google 授權頁面](https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent&response_type=code&client_id=1072944905499-vm2v2i5dvn0a0d2o4ca36i1vge8cvbn0.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A54321&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fspreadsheets%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.modify%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fscript.projects%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fscript.deployments%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fscript.webapp.deploy%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile)**

```text
┌─────────────────────────────────────────────────────────────┐
│ 1.【個】選個人 @gmail.com（❌ 勿用學校 @*.edu.tw 會被管理員封鎖） │
│ 2.【進】看到「尚未驗證」➔ 點左下「進階」➔「前往…（不安全）」    │
│ 3.【全】🚨 最重要！一定要先點最頂部的【全選 (Select All)】！    │
│        （Google 預設全部空白，每一格都必須是藍色打勾！）       │
│ 4.【續】確認全部勾選後，再點最下方的「繼續」                   │
└─────────────────────────────────────────────────────────────┘
```

**事前檢查（選填）**：若後續要發布打卡系統等 Web App，請先至 [script.google.com/home/usersettings](https://script.google.com/home/usersettings) 確認「Google Apps Script API」切到 **On**。

看到綠色「🎉 授權已順利完成！」就關掉分頁，回到這裡告訴我，剩下的我來為您處理！
````

---

## 規則
- 不要要求學生自己打指令；所有指令由你執行。
- Windows 環境請優先使用 `easy_auth.ps1`，避免學生陷入 Python / PATH 安裝問題。
- 不要把 `~/.clasprc.json`、Refresh Token 貼到聊天或上傳到任何地方。
- 不要覆寫整個 MCP 設定檔；只用精靈腳本寫入。
- 學生卡關時，依 `references/student_oauth_cheatsheet.md` 的錯誤對照表回答。
- 要用 Apps Script 發布網頁（打卡系統等），授權完成後直接切換使用 [appscript_skill](https://github.com/nutcelvischen-jpg/appscript_skill)。
