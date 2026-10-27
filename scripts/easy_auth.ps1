param(
  [int]$Port = 54321,
  [int]$Timeout = 300,
  [switch]$PrintUrl,
  [switch]$NoBrowser
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ClientId = "1072944905499-vm2v2i5dvn0a0d2o4ca36i1vge8cvbn0.apps.googleusercontent.com"
$ClientSecret = "v6V3fKV_zWU7iw1DrpO1rknX"
$RedirectUri = "http://localhost:$Port"

$ScopeList = @(
  @{ Scope = "https://www.googleapis.com/auth/drive"; Label = "查看、編輯、建立及刪除您所有的 Google 雲端硬碟檔案"; Required = $true },
  @{ Scope = "https://www.googleapis.com/auth/spreadsheets"; Label = "查看、編輯、建立及刪除您所有的 Google 試算表"; Required = $true },
  @{ Scope = "https://www.googleapis.com/auth/calendar"; Label = "查看、編輯、共用及刪除您的 Google 日曆"; Required = $true },
  @{ Scope = "https://www.googleapis.com/auth/gmail.modify"; Label = "讀取、撰寫及傳送您 Gmail 中的電子郵件"; Required = $true },
  @{ Scope = "https://www.googleapis.com/auth/script.projects"; Label = "建立及更新 Google Apps Script 專案"; Required = $true },
  @{ Scope = "https://www.googleapis.com/auth/script.deployments"; Label = "建立及更新 Google Apps Script 部署作業"; Required = $true },
  @{ Scope = "https://www.googleapis.com/auth/script.webapp.deploy"; Label = "將指令碼部署為網頁應用程式"; Required = $true },
  @{ Scope = "https://www.googleapis.com/auth/cloud-platform"; Label = "查看、編輯及設定您的 Google Cloud 資料"; Required = $true },
  @{ Scope = "https://www.googleapis.com/auth/userinfo.email"; Label = "查看您的電子郵件地址"; Required = $false },
  @{ Scope = "https://www.googleapis.com/auth/userinfo.profile"; Label = "查看您的個人資訊"; Required = $false }
)

$AllScopesString = ($ScopeList | ForEach-Object { $_.Scope }) -join " "
$EscapedScopes = [System.Uri]::EscapeDataString($AllScopesString)
$EscapedRedirect = [System.Uri]::EscapeDataString($RedirectUri)

$AuthUrl = "https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent&response_type=code&client_id=$ClientId&redirect_uri=$EscapedRedirect&scope=$EscapedScopes"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " 🎓 Google Workspace 一鍵授權精靈 (Windows 原生免 Python 版) " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "【授權通關四字訣：個 ➔ 進 ➔ 全 ➔ 續】" -ForegroundColor Yellow
Write-Host " 1.【個】選個人 @gmail.com（❌ 勿用學校 @*.edu.tw 帳號，通常會被封鎖）"
Write-Host " 2.【進】看到「Google 尚未驗證這個應用程式」➔ 點左下「進階」➔「前往…（不安全）」"
Write-Host " 3.【全】🚨 最致命關鍵！務必點擊最頂部的【全選 (Select All)】！" -ForegroundColor Red
Write-Host "        （Google 預設全部方框皆未打勾，必須每格都是藍色打勾才有效！）" -ForegroundColor Red
Write-Host " 4.【續】確認全部打勾後，再點最下方的「繼續」按鈕。"
Write-Host ""
Write-Host "👉 授權連結（瀏覽器未自動開啟時請複製手動開啟）：" -ForegroundColor Cyan
Write-Host $AuthUrl -ForegroundColor White
Write-Host ""

if ($PrintUrl) {
  exit 0
}

function Open-InChrome {
  param([string]$Url)
  $chromeCandidates = @(
    (Join-Path $env:ProgramFiles "Google\Chrome\Application\chrome.exe"),
    (Join-Path ${env:ProgramFiles(x86)} "Google\Chrome\Application\chrome.exe"),
    (Join-Path $env:LOCALAPPDATA "Google\Chrome\Application\chrome.exe")
  )
  foreach ($p in $chromeCandidates) {
    if ($p -and (Test-Path $p)) {
      Start-Process -FilePath $p -ArgumentList @("--new-window", $Url)
      Write-Host "🌐 已於獨立 Google Chrome 視窗開啟授權頁面..." -ForegroundColor Cyan
      return
    }
  }
  try {
    $cmd = Get-Command chrome.exe -ErrorAction SilentlyContinue
    if ($cmd) {
      Start-Process "chrome.exe" -ArgumentList @("--new-window", $Url)
      Write-Host "🌐 已於 Google Chrome 開啟授權頁面..." -ForegroundColor Cyan
      return
    }
  } catch {}

  # 若未安裝 Chrome 則回退至系統預設瀏覽器
  Start-Process $Url
  Write-Host "🌐 已開啟預設瀏覽器授權頁面..." -ForegroundColor Cyan
}

# 啟動本機 HTTP 監聽器
$Listener = New-Object System.Net.HttpListener
try {
  $Listener.Prefixes.Add("$RedirectUri/")
  $Listener.Start()
} catch {
  Write-Host "❌ 連接埠 $Port 疑似被佔用或無法啟動！錯誤：$($_.Exception.Message)" -ForegroundColor Red
  Write-Host "💡 提示：若之前有未完成的視窗，請先關閉，或稍候 5 秒重試。" -ForegroundColor Yellow
  exit 1
}

Write-Host "⏳ 正在等待瀏覽器完成授權（最多等待 $Timeout 秒）..." -ForegroundColor Green
if (-not $NoBrowser) {
  Open-InChrome $AuthUrl
}

$AsyncResult = $Listener.BeginGetContext($null, $null)
$Signaled = $AsyncResult.AsyncWaitHandle.WaitOne($Timeout * 1000)

if (-not $Signaled) {
  $Listener.Stop()
  Write-Host "❌ 授權逾時（超過 $Timeout 秒），請重新執行一次。" -ForegroundColor Red
  exit 1
}

$Context = $Listener.EndGetContext($AsyncResult)
$Request = $Context.Request
$Response = $Context.Response

$Code = $Request.QueryString["code"]
$ErrorParam = $Request.QueryString["error"]

$SuccessHtml = @"
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>授權已順利完成！</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f1f5f9; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }
    .card { background: #fff; max-width: 500px; padding: 40px 30px; border-radius: 20px; text-align: center; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.08); }
    .badge { display: inline-block; background: #dcfce7; color: #15803d; font-weight: 700; padding: 6px 16px; border-radius: 999px; font-size: 14px; margin-bottom: 12px; }
    h2 { color: #0f172a; margin: 10px 0; }
    p { color: #64748b; line-height: 1.6; font-size: 15px; }
    .btn-box { margin-top: 24px; padding-top: 20px; border-top: 1px solid #e2e8f0; }
    .btn { display: inline-block; background: #2563eb; color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 10px; font-size: 14px; font-weight: 600; }
  </style>
</head>
<body>
  <div class="card">
    <div style="font-size: 56px;">🎉</div>
    <div class="badge">Google 帳號連線成功</div>
    <h2>授權已順利完成！</h2>
    <p>您可以關閉這個分頁，回到 AI 助手聊天視窗了。</p>
    <div class="btn-box">
      <p style="font-size: 13px; color: #64748b; margin-bottom: 10px;">⚠️ 若後續需要發布 Apps Script 打卡網頁，請確保開關為 On：</p>
      <a class="btn" href="https://script.google.com/home/usersettings" target="_blank">檢查 Apps Script API 開關 ↗</a>
    </div>
  </div>
</body>
</html>
"@

if ($Code) {
  $Buffer = [System.Text.Encoding]::UTF8.GetBytes($SuccessHtml)
  $Response.ContentLength64 = $Buffer.Length
  $Response.ContentType = "text/html; charset=utf-8"
  $Response.OutputStream.Write($Buffer, 0, $Buffer.Length)
  $Response.OutputStream.Close()
  $Listener.Stop()

  Write-Host "✅ 已收到 Google 授權碼，正在換取金鑰..." -ForegroundColor Green

  # 向 Google 換取 Token
  $TokenBody = @{
    code = $Code
    client_id = $ClientId
    client_secret = $ClientSecret
    redirect_uri = $RedirectUri
    grant_type = "authorization_code"
  }

  try {
    $TokenRes = Invoke-RestMethod -Uri "https://oauth2.googleapis.com/token" -Method Post -Body $TokenBody
  } catch {
    Write-Host "❌ 換取 Token 失敗：$($_.Exception.Message)" -ForegroundColor Red
    exit 1
  }

  $GrantedScopes = ($TokenRes.scope -split " ") | ForEach-Object { $_.Trim() }

  # 檢查是否有漏勾權限
  $MissingScopes = @()
  foreach ($item in $ScopeList) {
    if ($item.Required -and ($GrantedScopes -notcontains $item.Scope)) {
      $MissingScopes += $item
    }
  }

  if ($MissingScopes.Count -gt 0) {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host "⚠️ 警告：您在授權頁面漏勾了必要權限！" -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host "原因：在 Google 權限畫面時，直接按了藍色「繼續」，沒有勾選方框。" -ForegroundColor Yellow
    Write-Host "缺少以下權限：" -ForegroundColor Yellow
    foreach ($m in $MissingScopes) {
      Write-Host "   [ ] $($m.Label)" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "👉 解法：請重新執行一次授權，並在畫面中務必點選【全選】！" -ForegroundColor Cyan
    Write-Host ""
  } else {
    Write-Host "✅ 恭喜！所有必要權限皆已完整勾選！" -ForegroundColor Green
  }

  # 儲存 ~/.clasprc.json
  $ClaspRc = @{
    token = @{
      access_token = $TokenRes.access_token
      refresh_token = $TokenRes.refresh_token
      scope = $TokenRes.scope
      token_type = $TokenRes.token_type
      expiry_date = ([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() + ($TokenRes.expires_in * 1000))
    }
    oauth2ClientSettings = @{
      clientId = $ClientId
      clientSecret = $ClientSecret
      redirectUri = $RedirectUri
    }
    isLocalCreds = $false
  }

  $ClaspPath = Join-Path $HOME ".clasprc.json"
  $ClaspRc | ConvertTo-Json -Depth 5 | Set-Content -Path $ClaspPath -Encoding UTF8
  Write-Host "✅ 已儲存 Apps Script 憑證：$ClaspPath" -ForegroundColor Green

  # 合併寫入 Antigravity MCP 設定 (~/.gemini/config/mcp_config.json)
  $McpDir = Join-Path $HOME ".gemini\config"
  if (-not (Test-Path $McpDir)) {
    New-Item -ItemType Directory -Force -Path $McpDir | Out-Null
  }
  $McpPath = Join-Path $McpDir "mcp_config.json"
  $McpCfg = @{ mcpServers = @{} }
  if (Test-Path $McpPath) {
    try {
      $Existing = Get-Content -Raw -Encoding UTF8 $McpPath | ConvertFrom-Json
      if ($Existing.mcpServers) {
        $McpCfg = $Existing
      }
    } catch {
      $McpCfg = @{ mcpServers = @{} }
    }
    # 備份原檔
    Copy-Item $McpPath "$McpPath.bak" -Force
  }

  # 探測 Python 路徑供 MCP 呼叫（若有）
  $PyExe = "python"
  $CandidatePy = @(
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"),
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"),
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python310\python.exe")
  )
  foreach ($cp in $CandidatePy) {
    if (Test-Path $cp) {
      $PyExe = $cp
      break
    }
  }

  $McpEntry = [ordered]@{
    command = $PyExe
    args = @("-m", "google_workspace_mcp")
    env = [ordered]@{
      GOOGLE_WORKSPACE_CLIENT_ID = $ClientId
      GOOGLE_WORKSPACE_CLIENT_SECRET = $ClientSecret
      GOOGLE_WORKSPACE_REFRESH_TOKEN = $TokenRes.refresh_token
      GOOGLE_WORKSPACE_ENABLED_CAPABILITIES = '["drive", "docs", "sheets", "slides", "gmail", "calendar"]'
    }
  }

  if (-not $McpCfg.mcpServers) {
    $McpCfg | Add-Member -MemberType NoteProperty -Name "mcpServers" -Value @{}
  }
  $McpCfg.mcpServers | Add-Member -MemberType NoteProperty -Name "google-workspace" -Value $McpEntry -Force

  $McpCfg | ConvertTo-Json -Depth 6 | Set-Content -Path $McpPath -Encoding UTF8
  Write-Host "✅ 已合併寫入 Antigravity MCP 設定：$McpPath" -ForegroundColor Green

  # 測試 Apps Script API 開關狀態
  Write-Host "🔍 正在檢查 Apps Script API 開關狀態..." -ForegroundColor Gray
  $Headers = @{ Authorization = "Bearer $($TokenRes.access_token)" }
  try {
    $Ping = Invoke-RestMethod -Uri "https://script.googleapis.com/v1/processes?pageSize=1" -Headers $Headers -TimeoutSec 10
    Write-Host "✅ Apps Script API 開關為：開啟 (On)！" -ForegroundColor Green
  } catch {
    $ErrDetail = $_.ErrorDetails.Message
    if ($ErrDetail -match "disabled|not been used|not enabled") {
      Write-Host "⚠️ 注意：您的 Apps Script API 開關目前是【關閉 (Off)】！" -ForegroundColor Red
      Write-Host "👉 請立刻開啟此網址切換為 On：https://script.google.com/home/usersettings" -ForegroundColor Yellow
    }
  }

  Write-Host ""
  Write-Host "================================================================" -ForegroundColor Green
  Write-Host " 🎉 授權大功告成！" -ForegroundColor Green
  Write-Host "================================================================" -ForegroundColor Green
  Write-Host "🔒 憑證已安全儲存於本機。若日後欲撤銷授權可至：https://myaccount.google.com/permissions"
  Write-Host ""
  Write-Host "💡【下一步】如果您要建立員工打卡系統或 Web App，請直接告訴 AI：" -ForegroundColor Cyan
  Write-Host "   「請幫我用 appscript_skill 建立員工打卡系統並發布成 Web App！」" -ForegroundColor Yellow
  Write-Host ""

  if ($MissingScopes.Count -gt 0) {
    exit 2
  }
  exit 0

} else {
  $Listener.Stop()
  Write-Host "❌ 授權取消或失敗：$ErrorParam" -ForegroundColor Red
  exit 1
}
