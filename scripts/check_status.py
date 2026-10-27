#!/usr/bin/env python3
"""
授權健康檢查 / Authorization health check (read-only, creates nothing in your Google account)

  python check_status.py            # Chinese
  python check_status.py --lang en  # English
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from easy_auth import SCOPES, DEFAULT_LANG, label  # noqa: E402

M = {
    "zh": {
        "no_clasp": "❌ 找不到 ~/.clasprc.json → 請先執行 easy_auth.py",
        "clasp_ok": "✅ 找到憑證：{p}（有 Refresh Token：{r}）",
        "refreshed": "✅ Access Token 已過期，已自動更新",
        "refresh_fail": "❌ 無法更新 Token（可能已被撤銷）→ 請重新執行 easy_auth.py：{e}",
        "scopes_ok": "✅ 所有權限都已授權",
        "scopes_missing": "⚠️ 缺少以下權限 → 重新執行 easy_auth.py 並按【全選】：",
        "mcp_ok": "✅ Antigravity MCP（google-workspace）已設定 Refresh Token",
        "mcp_missing": "⚠️ Antigravity MCP 設定中沒有 google-workspace → 請執行 easy_auth.py",
        "api_ok": "✅ Apps Script API 開關為 On",
        "api_off": "❌ Apps Script API 開關是 Off → 到 https://script.google.com/home/usersettings 切換為 On",
        "api_other": "⚠️ Apps Script API 回應：{e}",
    },
    "en": {
        "no_clasp": "❌ ~/.clasprc.json not found → run easy_auth.py first",
        "clasp_ok": "✅ Credentials found: {p} (has refresh token: {r})",
        "refreshed": "✅ Access token had expired and was refreshed",
        "refresh_fail": "❌ Could not refresh the token (maybe revoked) → run easy_auth.py again: {e}",
        "scopes_ok": "✅ Every permission is granted",
        "scopes_missing": "⚠️ Missing permissions → run easy_auth.py again and click [Select all]:",
        "mcp_ok": "✅ Antigravity MCP (google-workspace) has a refresh token",
        "mcp_missing": "⚠️ No google-workspace server in Antigravity MCP config → run easy_auth.py",
        "api_ok": "✅ Apps Script API switch is On",
        "api_off": "❌ Apps Script API switch is Off → turn it On at https://script.google.com/home/usersettings",
        "api_other": "⚠️ Apps Script API response: {e}",
    },
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["zh", "en"], default=DEFAULT_LANG)
    a = ap.parse_args()
    m = M[a.lang]
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    cp = Path.home() / ".clasprc.json"
    if not cp.exists():
        print(m["no_clasp"])
        sys.exit(1)
    c = json.loads(cp.read_text(encoding="utf-8-sig"))
    tok = c["token"]
    print(m["clasp_ok"].format(p=cp, r=bool(tok.get("refresh_token"))))

    if time.time() * 1000 >= (tok.get("expiry_date") or 0) - 60000:
        s = c["oauth2ClientSettings"]
        try:
            data = urllib.parse.urlencode({
                "client_id": s["clientId"], "client_secret": s["clientSecret"],
                "refresh_token": tok["refresh_token"], "grant_type": "refresh_token",
            }).encode()
            with urllib.request.urlopen("https://oauth2.googleapis.com/token", data=data, timeout=30) as r:
                nt = json.loads(r.read().decode())
            tok["access_token"] = nt["access_token"]
            tok["expiry_date"] = int(time.time() * 1000) + int(nt["expires_in"]) * 1000
            cp.write_text(json.dumps(c, indent=2), encoding="utf-8")
            print(m["refreshed"])
        except Exception as e:
            print(m["refresh_fail"].format(e=e))
            sys.exit(1)

    # granted scopes
    try:
        with urllib.request.urlopen("https://oauth2.googleapis.com/tokeninfo?access_token=" + tok["access_token"], timeout=30) as r:
            granted = set(json.loads(r.read().decode()).get("scope", "").split())
        miss = [s for s in SCOPES if s[3] and s[0] not in granted]
        if miss:
            print(m["scopes_missing"])
            for s in miss:
                print("   [ ] " + label(s, a.lang))
        else:
            print(m["scopes_ok"])
    except Exception:
        pass

    mp = Path.home() / ".gemini" / "config" / "mcp_config.json"
    try:
        gw = json.loads(mp.read_text(encoding="utf-8-sig"))["mcpServers"]["google-workspace"]
        print(m["mcp_ok"] if gw["env"].get("GOOGLE_WORKSPACE_REFRESH_TOKEN") else m["mcp_missing"])
    except Exception:
        print(m["mcp_missing"])

    # read-only ping: list recent script processes
    req = urllib.request.Request("https://script.googleapis.com/v1/processes?pageSize=1",
                                 headers={"Authorization": "Bearer " + tok["access_token"]})
    try:
        urllib.request.urlopen(req, timeout=30).read()
        print(m["api_ok"])
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")
        if "disabled" in body or "has not been used" in body or "User has not enabled" in body:
            print(m["api_off"])
        elif "ACCESS_TOKEN_SCOPE_INSUFFICIENT" in body or "insufficient authentication scopes" in body:
            print("⚠️ Apps Script API 權限未包含在 Token 中（授權時漏勾 Apps Script 相關項目，請按【全選】重新授權）" if a.lang == "zh" else "⚠️ Token lacks Apps Script scopes. Please re-run and click [Select all].")
        else:
            print(m["api_other"].format(e=f"{e.code} {body[:200]}"))


if __name__ == "__main__":
    main()
