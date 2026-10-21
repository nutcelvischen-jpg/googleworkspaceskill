#!/usr/bin/env python3
"""
Google Workspace 一鍵授權精靈 / Google Workspace one-click OAuth wizard
(Windows / macOS / Linux, Python 3.8+ standard library only)

What it does
 1. Prints a tick-box checklist of every permission the student will see.
 2. Starts a local listener on http://localhost:<port> and opens Google's consent page.
 3. Exchanges the code for tokens and CHECKS that every permission was ticked.
 4. Saves ~/.clasprc.json (Apps Script API / clasp).
 5. MERGES a "google-workspace" server into ~/.gemini/config/mcp_config.json
    (Antigravity) without touching your other MCP servers.
 6. Optional: --claude registers the same MCP server in Claude Code,
    --codex adds it to ~/.codex/config.toml.

Usage
  python easy_auth.py                 # Chinese output (default on main branch)
  python easy_auth.py --lang en       # English output
  python easy_auth.py --print-url     # only print checklist + URL, do not listen
  python easy_auth.py --claude --codex
"""

import argparse
import http.server
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

DEFAULT_LANG = "zh"

# Public OAuth client of Google's open-source @google/clasp CLI (not a personal secret).
CLIENT_ID = "1072944905499-vm2v2i5dvn0a0d2o4ca36i1vge8cvbn0.apps.googleusercontent.com"
CLIENT_SECRET = "v6V3fKV_zWU7iw1DrpO1rknX"

G = "https://www.googleapis.com/auth/"
# (scope, zh label, en label, shows a checkbox on the consent screen?)
SCOPES = [
    (G + "drive", "查看、編輯、建立及刪除您所有的 Google 雲端硬碟檔案", "See, edit, create and delete all your Google Drive files", True),
    (G + "spreadsheets", "查看、編輯、建立及刪除您所有的 Google 試算表", "See, edit, create and delete all your Google Sheets spreadsheets", True),
    (G + "calendar", "查看、編輯、共用及刪除您的 Google 日曆", "See, edit, share and delete your Google Calendars", True),
    (G + "gmail.modify", "讀取、撰寫及傳送您 Gmail 中的電子郵件", "Read, compose and send emails from your Gmail account", True),
    (G + "script.projects", "建立及更新 Google Apps Script 專案", "Create and update Google Apps Script projects", True),
    (G + "script.deployments", "建立及更新 Google Apps Script 部署作業", "Create and update Google Apps Script deployments", True),
    (G + "script.webapp.deploy", "將指令碼部署為網頁應用程式", "Deploy your script as a web app", True),
    (G + "cloud-platform", "查看、編輯及設定您的 Google Cloud 資料", "See, edit and configure your Google Cloud data", True),
    (G + "userinfo.email", "查看您的電子郵件地址", "See your email address", False),
    (G + "userinfo.profile", "查看您的個人資訊", "See your personal info", False),
]

T = {
    "zh": {
        "title": "🎓 Google Workspace 一鍵授權精靈",
        "step0": "【0】先確認 Apps Script API 開關為 On：https://script.google.com/home/usersettings",
        "step1": "【1】出現「Google 尚未驗證這個應用程式」→ 點左下「進階」→「前往…（不安全）」",
        "step2": "【2】權限頁面請點【全選】，或把下面每一格都打勾，再按「繼續」：",
        "note": "（實際文字以 Google 畫面為準）",
        "link": "👉 授權連結（瀏覽器沒自動打開就點這裡）：",
        "wait": "等待瀏覽器完成授權（最多 {s} 秒）…",
        "port_busy": "❌ 連接埠 {p} 被佔用，請改用：python easy_auth.py --port 54322",
        "timeout": "❌ 授權逾時，請重新執行一次。",
        "denied": "❌ 授權被取消或失敗：{e}",
        "ok_page_t": "授權已順利完成！",
        "ok_page_b": "Google 帳號連線成功",
        "ok_page_p": "可以關閉這個分頁，回到 AI 聊天視窗了。",
        "missing": "⚠️ 以下權限沒有打勾，請重新執行並按【全選】：",
        "all_ok": "✅ 所有權限都已勾選",
        "saved_clasp": "✅ 已儲存 Apps Script 憑證：{p}",
        "saved_mcp": "✅ 已合併寫入 Antigravity MCP 設定（其他 MCP 保留不動）：{p}",
        "backup": "   （原檔已備份為 {p}）",
        "mcp_missing": "ℹ️ 尚未安裝 google-workspace-mcp，正在安裝…",
        "mcp_fail": "⚠️ 自動安裝失敗，請手動執行：{c}",
        "claude_ok": "✅ 已註冊到 Claude Code（user scope）",
        "claude_fail": "⚠️ 找不到 claude 指令，請手動執行：\n{c}",
        "codex_ok": "✅ 已寫入 Codex 設定：{p}",
        "codex_skip": "ℹ️ Codex 設定已有 google-workspace，略過。",
        "done": "🎉 完成！請重新啟動 AI 工具（或重新載入 MCP），就能使用 Drive / Sheets / Docs / Gmail / Calendar。",
        "warn_secret": "🔒 憑證等同你的 Google 鑰匙：不要上傳、不要傳給別人。撤銷：https://myaccount.google.com/permissions",
    },
    "en": {
        "title": "🎓 Google Workspace one-click authorization wizard",
        "step0": "[0] Make sure the Apps Script API switch is On: https://script.google.com/home/usersettings",
        "step1": "[1] If you see \"Google hasn't verified this app\" → click \"Advanced\" (bottom left) → \"Go to … (unsafe)\"",
        "step2": "[2] On the permissions page click [Select all], or tick every box below, then click \"Continue\":",
        "note": "(exact wording may differ slightly on Google's screen)",
        "link": "👉 Authorization link (click if the browser did not open):",
        "wait": "Waiting for you to finish in the browser (up to {s} s)…",
        "port_busy": "❌ Port {p} is in use. Try: python easy_auth.py --port 54322",
        "timeout": "❌ Timed out. Please run the script again.",
        "denied": "❌ Authorization cancelled or failed: {e}",
        "ok_page_t": "Authorization complete!",
        "ok_page_b": "Google account connected",
        "ok_page_p": "You can close this tab and go back to your AI chat.",
        "missing": "⚠️ These permissions were NOT ticked. Run again and click [Select all]:",
        "all_ok": "✅ Every permission was granted",
        "saved_clasp": "✅ Saved Apps Script credentials: {p}",
        "saved_mcp": "✅ Merged into Antigravity MCP config (other servers kept): {p}",
        "backup": "   (previous file backed up as {p})",
        "mcp_missing": "ℹ️ google-workspace-mcp is not installed, installing…",
        "mcp_fail": "⚠️ Automatic install failed. Run manually: {c}",
        "claude_ok": "✅ Registered in Claude Code (user scope)",
        "claude_fail": "⚠️ `claude` command not found. Run manually:\n{c}",
        "codex_ok": "✅ Written to Codex config: {p}",
        "codex_skip": "ℹ️ Codex config already has google-workspace, skipped.",
        "done": "🎉 Done! Restart your AI tool (or reload MCP) to use Drive / Sheets / Docs / Gmail / Calendar.",
        "warn_secret": "🔒 These credentials are a key to your Google account: never upload or share them. Revoke at https://myaccount.google.com/permissions",
    },
}


def label(scope_row, lang):
    return scope_row[1] if lang == "zh" else scope_row[2]


def build_auth_url(redirect_uri):
    q = {
        "access_type": "offline",
        "prompt": "consent",
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": " ".join(s[0] for s in SCOPES),
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(q, quote_via=urllib.parse.quote)


def print_checklist(t, lang, url):
    print("=" * 64)
    print(t["title"])
    print("=" * 64)
    print(t["step0"])
    print(t["step1"])
    print(t["step2"], t["note"])
    for row in SCOPES:
        if row[3]:
            print("   [ ] " + label(row, lang))
    print()
    print(t["link"])
    print(url)
    print()


def success_html(t, lang):
    return f"""<!DOCTYPE html><html lang="{'zh-TW' if lang == 'zh' else 'en'}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{t['ok_page_t']}</title>
<style>body{{font-family:-apple-system,"Segoe UI",sans-serif;background:#f1f5f9;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;padding:20px}}
.c{{background:#fff;max-width:460px;padding:40px 28px;border-radius:20px;text-align:center;box-shadow:0 20px 25px -5px rgba(0,0,0,.08)}}
.b{{display:inline-block;background:#dcfce7;color:#15803d;font-weight:700;padding:6px 16px;border-radius:999px;font-size:13px}}
h2{{color:#0f172a}}p{{color:#64748b;line-height:1.6}}</style></head>
<body><div class="c"><div style="font-size:54px">🎉</div><div class="b">{t['ok_page_b']}</div>
<h2>{t['ok_page_t']}</h2><p>{t['ok_page_p']}</p></div></body></html>"""


def wait_for_code(port, timeout, t, lang):
    result = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if "code" in qs or "error" in qs:
                result["code"] = qs.get("code", [None])[0]
                result["error"] = qs.get("error", [None])[0]
                body = success_html(t, lang) if result["code"] else f"<h2>{result['error']}</h2>"
                data = body.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:  # favicon etc.
                self.send_response(204)
                self.end_headers()

        def log_message(self, *a):
            pass

    try:
        server = http.server.HTTPServer(("localhost", port), Handler)
    except OSError:
        print(t["port_busy"].format(p=port))
        sys.exit(1)
    server.timeout = 1
    deadline = time.time() + timeout
    while "code" not in result and time.time() < deadline:
        server.handle_request()
    server.server_close()
    return result


def post_form(url, fields):
    data = urllib.parse.urlencode(fields).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=30) as r:
        return json.loads(r.read().decode())


def backup(path):
    if path.exists():
        b = path.with_name(path.name + ".bak")
        shutil.copy2(path, b)
        return b
    return None


def ensure_mcp_package(t):
    try:
        import importlib.util
        if importlib.util.find_spec("google_workspace_mcp"):
            return
    except Exception:
        pass
    print(t["mcp_missing"])
    cmd = [sys.executable, "-m", "pip", "install", "--user", "google-workspace-mcp"]
    r = subprocess.run(cmd)
    if r.returncode != 0:
        r = subprocess.run(cmd + ["--break-system-packages"])
    if r.returncode != 0:
        print(t["mcp_fail"].format(c=" ".join(cmd)))


def mcp_server_entry(refresh_token):
    return {
        "command": sys.executable,
        "args": ["-m", "google_workspace_mcp"],
        "env": {
            "GOOGLE_WORKSPACE_CLIENT_ID": CLIENT_ID,
            "GOOGLE_WORKSPACE_CLIENT_SECRET": CLIENT_SECRET,
            "GOOGLE_WORKSPACE_REFRESH_TOKEN": refresh_token,
            "GOOGLE_WORKSPACE_ENABLED_CAPABILITIES": '["drive", "docs", "sheets", "slides", "gmail", "calendar"]',
        },
    }


def write_antigravity(entry, t):
    p = Path.home() / ".gemini" / "config" / "mcp_config.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    cfg = {}
    if p.exists():
        try:
            cfg = json.loads(p.read_text(encoding="utf-8-sig") or "{}")
        except json.JSONDecodeError:
            cfg = {}
    b = backup(p)
    cfg.setdefault("mcpServers", {})["google-workspace"] = entry
    p.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    print(t["saved_mcp"].format(p=p))
    if b:
        print(t["backup"].format(p=b))


def write_claude(entry, t):
    js = json.dumps(entry, ensure_ascii=False)
    cmd = ["claude", "mcp", "add-json", "google-workspace", js, "--scope", "user"]
    exe = shutil.which("claude")
    if exe:
        subprocess.run(["claude", "mcp", "remove", "google-workspace", "--scope", "user"], capture_output=True)
        if subprocess.run([exe] + cmd[1:]).returncode == 0:
            print(t["claude_ok"])
            return
    print(t["claude_fail"].format(c="claude mcp add-json google-workspace '" + js + "' --scope user"))


def write_codex(entry, t):
    p = Path.home() / ".codex" / "config.toml"
    p.parent.mkdir(parents=True, exist_ok=True)
    text = p.read_text(encoding="utf-8") if p.exists() else ""
    if "[mcp_servers.google-workspace]" in text:
        print(t["codex_skip"])
        return
    backup(p)
    env = ", ".join(f'{k} = {json.dumps(v)}' for k, v in entry["env"].items())
    block = (
        "\n[mcp_servers.google-workspace]\n"
        f"command = {json.dumps(entry['command'])}\n"
        f"args = {json.dumps(entry['args'])}\n"
        f"env = {{ {env} }}\n"
    )
    p.write_text(text + block, encoding="utf-8")
    print(t["codex_ok"].format(p=p))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["zh", "en"], default=DEFAULT_LANG)
    ap.add_argument("--port", type=int, default=54321)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--print-url", action="store_true", help="only print checklist and URL")
    ap.add_argument("--claude", action="store_true", help="also register MCP in Claude Code")
    ap.add_argument("--codex", action="store_true", help="also register MCP in Codex")
    ap.add_argument("--skip-mcp-install", action="store_true")
    a = ap.parse_args()
    t = T[a.lang]

    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles
    except Exception:
        pass

    redirect = f"http://localhost:{a.port}"
    url = build_auth_url(redirect)
    print_checklist(t, a.lang, url)
    if a.print_url:
        return

    print(t["wait"].format(s=a.timeout))
    if not a.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    res = wait_for_code(a.port, a.timeout, t, a.lang)
    if "code" not in res:
        print(t["timeout"])
        sys.exit(1)
    if not res.get("code"):
        print(t["denied"].format(e=res.get("error")))
        sys.exit(1)

    try:
        tok = post_form("https://oauth2.googleapis.com/token", {
            "code": res["code"], "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
            "redirect_uri": redirect, "grant_type": "authorization_code",
        })
    except Exception as e:
        detail = e.read().decode(errors="ignore") if hasattr(e, "read") else str(e)
        print(t["denied"].format(e=detail[:300]))
        sys.exit(1)

    granted = set(tok.get("scope", "").split())
    missing = [r for r in SCOPES if r[3] and r[0] not in granted]
    if missing:
        print(t["missing"])
        for r in missing:
            print("   [ ] " + label(r, a.lang))
    else:
        print(t["all_ok"])

    clasp = {
        "token": {
            "access_token": tok.get("access_token"),
            "refresh_token": tok.get("refresh_token"),
            "scope": tok.get("scope"),
            "token_type": tok.get("token_type"),
            "expiry_date": int(time.time() * 1000) + int(tok.get("expires_in", 3600)) * 1000,
        },
        "oauth2ClientSettings": {"clientId": CLIENT_ID, "clientSecret": CLIENT_SECRET, "redirectUri": redirect},
        "isLocalCreds": False,
    }
    cp = Path.home() / ".clasprc.json"
    backup(cp)
    cp.write_text(json.dumps(clasp, indent=2), encoding="utf-8")
    try:
        os.chmod(cp, 0o600)
    except Exception:
        pass
    print(t["saved_clasp"].format(p=cp))

    if not a.skip_mcp_install:
        ensure_mcp_package(t)
    entry = mcp_server_entry(tok.get("refresh_token"))
    write_antigravity(entry, t)
    if a.claude:
        write_claude(entry, t)
    if a.codex:
        write_codex(entry, t)

    print()
    print(t["warn_secret"])
    print(t["done"])
    if missing:
        sys.exit(2)


if __name__ == "__main__":
    main()
