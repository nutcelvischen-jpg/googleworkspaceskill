---
name: google-easy-auth
description: One-step OAuth authorization for Google Workspace (Drive, Sheets, Docs, Slides, Gmail, Calendar) and Google Apps Script, built for students. Use when the user wants to connect a Google account, set up the Google Workspace MCP server, or publish an Apps Script web app without credentials yet. Posts a tick-box permission checklist in chat, opens the browser, checks nothing was left unticked, and writes ~/.clasprc.json and the MCP config.
---

# Google Workspace one-click authorization (google-easy-auth)

Operating rules for the AI assistant (Antigravity, Claude Code, Codex, or any agent that can run commands on the user's computer).
Goal: the student only **clicks a link → ticks boxes → clicks Continue**. You do everything else.

## What you (the AI) do, in order

### 1. Make sure Python 3.8+ is installed
Run `python3 --version` (on Windows `python --version` or `py -3 --version`).
If it is missing, install it for the student:
- Windows: `winget install -e --id Python.Python.3.12`
- macOS: `xcode-select --install` (or `brew install python`)

Below, replace `python` with whichever command works (`python3` / `python` / `py -3`).
`<SKILL_DIR>` is the folder containing this SKILL.md.

### 2. Run the health check first
```bash
python <SKILL_DIR>/scripts/check_status.py
```
All ✅ → tell the student they are already authorized and can start. Stop here.

### 3. Post the checklist in chat (required — never just paste a command)
Reply with the "Chat template" below. The link is the line printed by `python <SKILL_DIR>/scripts/easy_auth.py --print-url` (identical to the template when the default port 54321 is used).

### 4. Start the wizard (in the background, so the chat is not blocked)
```bash
python <SKILL_DIR>/scripts/easy_auth.py
```
Add a flag for the tool you are:
- Claude Code → add `--claude`
- Codex → add `--codex`
- Antigravity → nothing (it always writes `~/.gemini/config/mcp_config.json`)

The wizard opens the browser, waits for the student, exchanges the code for tokens, checks for unticked permissions, and:
- writes `~/.clasprc.json` (for the Apps Script API)
- **merges** the MCP config (adds or updates `google-workspace` only, keeps every other server, backs up the old file as `.bak`)
- runs `pip install google-workspace-mcp` if it is missing

### 5. Report by exit code
| Code | Meaning | What you do |
|---|---|---|
| 0 | Success | Ask the student to restart the AI tool (or reload MCP), then run `check_status.py` to confirm |
| 2 | Some permissions were not ticked | Show the "missing permissions" list it printed, remind them to click [Select all], rerun step 4 |
| 1 | Timeout / cancelled / port in use | Follow the message; if the port is in use add `--port 54322` |

---

## Chat template (copy as is)

````markdown
### 🎓 Connect your Google account in 3 steps

Your browser will open automatically. If it doesn't, click here 👉 **[Open the Google authorization page](https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent&response_type=code&client_id=1072944905499-vm2v2i5dvn0a0d2o4ca36i1vge8cvbn0.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A54321&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fspreadsheets%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.modify%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fscript.projects%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fscript.deployments%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fscript.webapp.deploy%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile)**

**① Turn on the API switch**: open [script.google.com/home/usersettings](https://script.google.com/home/usersettings) and set "Google Apps Script API" to **On**.

**② Choose your account**: use a personal **@gmail.com** account (school accounts are often blocked by the admin).
If you see "Google hasn't verified this app" → click **Advanced** (bottom left) → **Go to … (unsafe)**.

**③ Tick the boxes (most important!)**: click [**Select all**], or make sure every box below is ticked, then click **Continue**:
- [ ] See, edit, create and delete all your Google Drive files
- [ ] See, edit, create and delete all your Google Sheets spreadsheets
- [ ] See, edit, share and delete your Google Calendars
- [ ] Read, compose and send emails from your Gmail account
- [ ] Create and update Google Apps Script projects
- [ ] Create and update Google Apps Script deployments
- [ ] Deploy your script as a web app
- [ ] See, edit and configure your Google Cloud data

(The exact wording on Google's screen may differ slightly — the point is **every box ticked**.)

When you see the green "🎉 Authorization complete!" page, close the tab and come back here. I'll take care of the rest.
````

---

## Rules
- Never ask the student to type commands; you run them.
- Never paste `~/.clasprc.json` or any refresh token into the chat or upload it anywhere.
- Never overwrite the whole MCP config file; only write it through `easy_auth.py`.
- When the student is stuck, answer from the error table in `references/student_oauth_cheatsheet.md`.
- To publish an Apps Script web app (clock-in system, etc.) after authorization, use [appscript_skill](https://github.com/nutcelvischen-jpg/appscript_skill/tree/en).
