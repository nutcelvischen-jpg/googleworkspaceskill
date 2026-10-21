# 🎓 Google Workspace 一鍵授權技能（google-easy-auth）

**繁體中文** | [English](https://github.com/nutcelvischen-jpg/googleworkspaceskill/tree/en)

讓學生**一步**把 Google 帳號（Drive、Sheets、Docs、Slides、Gmail、Calendar、Apps Script）連到 AI 助手。
學生只要「點連結 → 打勾 → 按繼續」，其餘交給 AI。

---

## 🚀 學生只要做這一步

把下面這段話**整段複製**，貼給 Antigravity、Claude Code 或 Codex：

```text
請把 https://github.com/nutcelvischen-jpg/googleworkspaceskill 安裝成技能（google-easy-auth），
照 SKILL.md 幫我完成 Google Workspace 授權。
```

AI 會：
1. 下載技能並檢查 Python
2. 在聊天中貼出**只需要打勾的授權清單**和授權連結
3. 自動開瀏覽器，等你按完
4. 檢查有沒有漏勾，漏了會告訴你缺哪幾項
5. 寫好憑證與 MCP 設定

你在 Google 畫面上只要：
- [ ] 選個人 **@gmail.com** 帳號
- [ ] 看到「尚未驗證」→ 點 **進階** → **前往…（不安全）**
- [ ] 權限頁點【**全選**】→ **繼續**

> ⚠️ 授權前先打開 [Apps Script API 開關](https://script.google.com/home/usersettings)（切到 On）。

---

## 支援的 AI 工具

| 工具 | 可以一步完成？ | 說明 |
|---|---|---|
| Google Antigravity | ✅ | 寫入 `~/.gemini/config/mcp_config.json` |
| Claude Code / Claude 桌面版（可執行本機指令） | ✅ | 精靈加 `--claude`，註冊到 Claude Code |
| OpenAI Codex | ✅ | 精靈加 `--codex`，寫入 `~/.codex/config.toml` |
| ChatGPT / Claude **網頁版** | ❌ | 無法在你的電腦執行程式，只能看步驟說明 |

## 手動安裝（老師或進階使用者）

```bash
# Antigravity
git clone https://github.com/nutcelvischen-jpg/googleworkspaceskill ~/.gemini/skills/google-easy-auth
# Claude Code
git clone https://github.com/nutcelvischen-jpg/googleworkspaceskill ~/.claude/skills/google-easy-auth
# Codex
git clone https://github.com/nutcelvischen-jpg/googleworkspaceskill ~/.codex/skills/google-easy-auth
```
英文版：在 `git clone` 後加 `-b en`。

直接執行（Windows / macOS / Linux 都可，只需 Python 3.8+）：
```bash
python scripts/easy_auth.py          # 授權
python scripts/check_status.py       # 健康檢查（不會在你的帳號建立任何東西）
```

| 參數 | 用途 |
|---|---|
| `--print-url` | 只印出授權清單與連結 |
| `--claude` / `--codex` | 同時註冊到 Claude Code / Codex |
| `--port 54322` | 54321 被佔用時改用 |
| `--lang en` | 英文輸出 |

---

## 📂 檔案結構

```text
googleworkspaceskill/
├── SKILL.md                              # 給 AI 的操作規則與聊天輸出範本
├── README.md                             # 本說明
├── references/student_oauth_cheatsheet.md # 4 個畫面圖解 + 錯誤對照表
└── scripts/
    ├── easy_auth.py                      # 一鍵授權精靈
    └── check_status.py                   # 授權健康檢查
```

## 🔒 安全說明
- 使用 Google 開源工具 `@google/clasp` 的公開 OAuth Client，不含任何個人金鑰。
- Token 只存在你自己的電腦（`~/.clasprc.json`、MCP 設定），不會上傳。
- 取消授權：[myaccount.google.com/permissions](https://myaccount.google.com/permissions)。
- 本 repo 的 `.gitignore` 已排除憑證檔，請勿把它們加進 git。

## 相關技能
- 授權完成後要用 Apps Script 發布網頁（打卡系統等）：[appscript_skill](https://github.com/nutcelvischen-jpg/appscript_skill)
- MCP 伺服器：[google-workspace-mcp](https://pypi.org/project/google-workspace-mcp/)（Arclio，MIT）

## 授權
Apache 2.0。歡迎各級學校用於資訊課程與專題教學。
