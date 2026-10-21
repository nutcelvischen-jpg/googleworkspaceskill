# 🎓 Google Workspace one-click authorization skill (google-easy-auth)

[繁體中文](https://github.com/nutcelvischen-jpg/googleworkspaceskill/tree/main) | **English**

Lets students connect their Google account (Drive, Sheets, Docs, Slides, Gmail, Calendar, Apps Script) to an AI assistant **in one step**.
The student only clicks a link → ticks boxes → clicks Continue. The AI does the rest.

---

## 🚀 The one step students do

Copy this **whole message** and paste it into Antigravity, Claude Code or Codex:

```text
Install https://github.com/nutcelvischen-jpg/googleworkspaceskill (branch: en) as a skill (google-easy-auth)
and follow its SKILL.md to authorize my Google Workspace account.
```

The AI will:
1. Download the skill and check Python
2. Post a **tick-box permission checklist** and the authorization link in chat
3. Open your browser and wait for you
4. Check nothing was left unticked, and tell you exactly what is missing if so
5. Write the credentials and the MCP config

On Google's screens you only:
- [ ] Choose a personal **@gmail.com** account
- [ ] If you see "not verified" → click **Advanced** → **Go to … (unsafe)**
- [ ] On the permissions page click [**Select all**] → **Continue**

> ⚠️ Before you start, turn on the [Apps Script API switch](https://script.google.com/home/usersettings) (set it to On).

---

## ⚠️ Not fully automatic: what students still do themselves

The AI runs everything it can, but Google does not allow the steps below to be done for the student, and a few situations can stop the flow.

**Students must do these themselves**
1. Turn on the [Apps Script API switch](https://script.google.com/home/usersettings) (set it to On)
2. Choose an account; if you see "not verified" → click **Advanced** → **Go to … (unsafe)**
3. On the permissions page click [**Select all**] → **Continue**
4. After authorizing, **restart the AI tool** so the Google tools appear

**Where it can get stuck**
| Situation | What to do |
|---|---|
| The AI asks permission before running a command | Click "Allow" |
| Python isn't installed and the installer asks for admin rights | Click "Yes"; if a school computer blocks installs, use your own computer |
| A school account (e.g. @mail.edu.tw) shows "Access blocked" | Use a personal @gmail.com account |
| "This app is blocked" appears (no Advanced option) | Try a different personal Gmail account |
| Using ChatGPT / Claude **in a web browser** | Not supported; use Antigravity, Claude Code or Codex |

If a permission is left unticked or the API switch is Off, the wizard and health check point it out and the AI walks you through fixing it.

> 🧑‍🏫 For teachers: before class, run the whole flow once on a Windows and a Mac computer, each with a fresh personal Gmail account.

---

## Supported AI tools

| Tool | One step? | Notes |
|---|---|---|
| Google Antigravity | ✅ | Writes `~/.gemini/config/mcp_config.json` |
| Claude Code / Claude desktop (can run local commands) | ✅ | Wizard with `--claude` registers it in Claude Code |
| OpenAI Codex | ✅ | Wizard with `--codex` writes `~/.codex/config.toml` |
| ChatGPT / Claude **in a web browser** | ❌ | Cannot run programs on your computer; can only explain the steps |

## Manual install (teachers or advanced users)

```bash
# Antigravity
git clone -b en https://github.com/nutcelvischen-jpg/googleworkspaceskill ~/.gemini/skills/google-easy-auth
# Claude Code
git clone -b en https://github.com/nutcelvischen-jpg/googleworkspaceskill ~/.claude/skills/google-easy-auth
# Codex
git clone -b en https://github.com/nutcelvischen-jpg/googleworkspaceskill ~/.codex/skills/google-easy-auth
```
For the Traditional Chinese version, leave out `-b en`.

Run directly (Windows / macOS / Linux, Python 3.8+ only):
```bash
python scripts/easy_auth.py          # authorize
python scripts/check_status.py       # health check (creates nothing in your account)
```

| Flag | Purpose |
|---|---|
| `--print-url` | Only print the checklist and link |
| `--claude` / `--codex` | Also register in Claude Code / Codex |
| `--port 54322` | Use another port if 54321 is busy |
| `--lang zh` | Traditional Chinese output |

---

## 📂 Structure

```text
googleworkspaceskill/
├── SKILL.md                              # Rules and chat template for the AI
├── README.md                             # This file
├── references/student_oauth_cheatsheet.md # The 4 screens + error table
└── scripts/
    ├── easy_auth.py                      # One-click authorization wizard
    └── check_status.py                   # Authorization health check
```

## 🔒 Security
- Uses the public OAuth client of Google's open-source `@google/clasp` tool; no personal keys are included.
- Tokens stay on your own computer (`~/.clasprc.json`, MCP config) and are never uploaded.
- Remove access any time: [myaccount.google.com/permissions](https://myaccount.google.com/permissions).
- The repo's `.gitignore` excludes credential files; never add them to git.

## Related
- Publish an Apps Script web app (clock-in system, etc.) after authorizing: [appscript_skill](https://github.com/nutcelvischen-jpg/appscript_skill/tree/en)
- MCP server: [google-workspace-mcp](https://pypi.org/project/google-workspace-mcp/) (Arclio, MIT)

## License
Apache 2.0. Schools and universities are welcome to use it for IT courses and project teaching.
