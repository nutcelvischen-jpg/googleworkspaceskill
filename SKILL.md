---
name: google-easy-auth
description: 學生一步完成 Google Workspace（Drive、Sheets、Docs、Slides、Gmail、Calendar）與 Google Apps Script 的 OAuth 授權。當使用者要連結 Google 帳號、設定 Google Workspace MCP、或要用 Apps Script 發布網頁但尚未授權時使用。會在聊天中產生「只需要打勾」的授權清單，自動開瀏覽器、檢查有沒有漏勾，並寫入 ~/.clasprc.json 與 MCP 設定。
---

# Google Workspace 一鍵授權（google-easy-auth）

給 AI 助手（Antigravity、Claude Code、Codex 等能在本機執行指令的 Agent）的操作規則。
目標：學生只要「點連結 → 打勾 → 按繼續」，其他全部由你完成。

## 你（AI）要做的事，依序執行

### 1. 確認有 Python 3.8 以上
執行 `python3 --version`（Windows 用 `python --version` 或 `py -3 --version`）。
沒有的話先幫學生安裝：
- Windows：`winget install -e --id Python.Python.3.12`
- macOS：`xcode-select --install`（或 `brew install python`）

以下指令中的 `python` 請換成實際可用的指令（`python3` / `python` / `py -3`）。
`<SKILL_DIR>` 是這份 SKILL.md 所在的資料夾。

### 2. 先做健康檢查
```bash
python <SKILL_DIR>/scripts/check_status.py
```
全部都是 ✅ → 告訴學生「已經授權過了，可以直接使用」，結束。

### 3. 在聊天中貼出授權清單（必做，不可只丟指令）
直接用下方「聊天輸出範本」回覆學生。連結用 `python <SKILL_DIR>/scripts/easy_auth.py --print-url` 印出的那一行（預設連接埠 54321 時與範本相同）。

### 4. 啟動授權精靈（在背景執行，不要卡住對話）
```bash
python <SKILL_DIR>/scripts/easy_auth.py
```
依你自己的身分加參數：
- Claude Code → 加 `--claude`
- Codex → 加 `--codex`
- Antigravity → 不用加（預設就會寫入 `~/.gemini/config/mcp_config.json`）

精靈會自動開瀏覽器、等學生按完、換取 Token、檢查有沒有漏勾，並：
- 寫入 `~/.clasprc.json`（Apps Script API 用）
- **合併**寫入 MCP 設定（只新增或更新 `google-workspace`，其他 MCP 不動，原檔備份為 `.bak`）
- 沒裝 `google-workspace-mcp` 時自動 `pip install`

### 5. 看結束代碼回報
| 代碼 | 意思 | 你要做的 |
|---|---|---|
| 0 | 成功 | 請學生重新啟動 AI 工具（或重新載入 MCP），然後執行 `check_status.py` 確認 |
| 2 | 有權限沒打勾 | 把輸出的「缺少權限」清單貼給學生，提醒按【全選】，重跑步驟 4 |
| 1 | 逾時 / 取消 / 連接埠被佔用 | 依輸出訊息處理；連接埠被佔用就加 `--port 54322` |

---

## 聊天輸出範本（照抄，用繁體中文）

````markdown
### 🎓 Google 帳號授權：只要 3 步

瀏覽器會自動打開。沒打開的話點這裡 👉 **[開啟 Google 授權頁面](https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent&response_type=code&client_id=1072944905499-vm2v2i5dvn0a0d2o4ca36i1vge8cvbn0.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A54321&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fspreadsheets%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.modify%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fscript.projects%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fscript.deployments%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fscript.webapp.deploy%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile)**

**① 先開 API 開關**：打開 [script.google.com/home/usersettings](https://script.google.com/home/usersettings)，把「Google Apps Script API」切到 **On**。

**② 選帳號**：請用個人 **@gmail.com**（學校帳號常被管理員擋）。
看到「Google 尚未驗證這個應用程式」→ 點左下 **進階** → **前往…（不安全）**。

**③ 打勾（最重要！）**：點【**全選**】，或確認下面每一格都有勾，再按 **繼續**：
- [ ] 查看、編輯、建立及刪除您所有的 Google 雲端硬碟檔案
- [ ] 查看、編輯、建立及刪除您所有的 Google 試算表
- [ ] 查看、編輯、共用及刪除您的 Google 日曆
- [ ] 讀取、撰寫及傳送您 Gmail 中的電子郵件
- [ ] 建立及更新 Google Apps Script 專案
- [ ] 建立及更新 Google Apps Script 部署作業
- [ ] 將指令碼部署為網頁應用程式
- [ ] 查看、編輯及設定您的 Google Cloud 資料

（實際文字以 Google 畫面為準，重點是**每一格都要勾**。）

看到綠色「🎉 授權已順利完成！」就關掉分頁，回來這裡，剩下的我來處理。
````

---

## 規則
- 不要要求學生自己打指令；所有指令由你執行。
- 不要把 `~/.clasprc.json`、Refresh Token 貼到聊天或上傳到任何地方。
- 不要覆寫整個 MCP 設定檔；只用 `easy_auth.py` 寫入。
- 學生卡關時，依 `references/student_oauth_cheatsheet.md` 的錯誤對照表回答。
- 要用 Apps Script 發布網頁（打卡系統等），授權完成後改用 [appscript_skill](https://github.com/nutcelvischen-jpg/appscript_skill)。
