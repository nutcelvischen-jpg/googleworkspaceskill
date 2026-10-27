[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ClaspPath = Join-Path $HOME ".clasprc.json"
if (-not (Test-Path $ClaspPath)) {
  Write-Host "❌ 找不到 ~/.clasprc.json 憑證 → 請先執行 easy_auth.ps1 進行授權！" -ForegroundColor Red
  exit 1
}

$Clasp = Get-Content -Raw -Encoding UTF8 $ClaspPath | ConvertFrom-Json
$Tok = $Clasp.token
$HasRefresh = (![string]::IsNullOrEmpty($Tok.refresh_token))

Write-Host "✅ 找到本機憑證：$ClaspPath（包含 Refresh Token: $HasRefresh）" -ForegroundColor Green

# 檢查 Token 是否過期需要刷新
$NowMs = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
if ($Tok.expiry_date -and ($NowMs -ge ($Tok.expiry_date - 60000))) {
  Write-Host "🔄 Access Token 已過期，正在自動更新..." -ForegroundColor Gray
  $Settings = $Clasp.oauth2ClientSettings
  $RefreshBody = @{
    client_id = $Settings.clientId
    client_secret = $Settings.clientSecret
    refresh_token = $Tok.refresh_token
    grant_type = "refresh_token"
  }
  try {
    $RefRes = Invoke-RestMethod -Uri "https://oauth2.googleapis.com/token" -Method Post -Body $RefreshBody
    $Tok.access_token = $RefRes.access_token
    $Tok.expiry_date = $NowMs + ($RefRes.expires_in * 1000)
    $Clasp | ConvertTo-Json -Depth 5 | Set-Content -Path $ClaspPath -Encoding UTF8
    Write-Host "✅ Access Token 已自動更新成功！" -ForegroundColor Green
  } catch {
    Write-Host "❌ 無法自動更新 Token（可能已被撤銷），請重新授權：$($_.Exception.Message)" -ForegroundColor Red
    exit 1
  }
}

# 檢查已授權的 Scope
$ScopeLabels = @{
  "https://www.googleapis.com/auth/drive" = "查看、編輯、建立及刪除您所有的 Google 雲端硬碟檔案"
  "https://www.googleapis.com/auth/spreadsheets" = "查看、編輯、建立及刪除您所有的 Google 試算表"
  "https://www.googleapis.com/auth/calendar" = "查看、編輯、共用及刪除您的 Google 日曆"
  "https://www.googleapis.com/auth/gmail.modify" = "讀取、撰寫及傳送您 Gmail 中的電子郵件"
  "https://www.googleapis.com/auth/script.projects" = "建立及更新 Google Apps Script 專案"
  "https://www.googleapis.com/auth/script.deployments" = "建立及更新 Google Apps Script 部署作業"
  "https://www.googleapis.com/auth/script.webapp.deploy" = "將指令碼部署為網頁應用程式"
  "https://www.googleapis.com/auth/cloud-platform" = "查看、編輯及設定您的 Google Cloud 資料"
}

try {
  $TokenInfo = Invoke-RestMethod -Uri ("https://oauth2.googleapis.com/tokeninfo?access_token=" + $Tok.access_token) -TimeoutSec 10
  $Granted = ($TokenInfo.scope -split " ") | ForEach-Object { $_.Trim() }
  $Missing = @()
  foreach ($k in $ScopeLabels.Keys) {
    if ($Granted -notcontains $k) {
      $Missing += $ScopeLabels[$k]
    }
  }

  if ($Missing.Count -gt 0) {
    Write-Host "⚠️ 缺少以下權限（授權時可能漏勾）→ 請重新授權並在畫面點【全選】：`n" -ForegroundColor Yellow
    foreach ($m in $Missing) {
      Write-Host "   [ ] $m" -ForegroundColor Red
    }
  } else {
    Write-Host "✅ 所有必要權限皆已完整授權！" -ForegroundColor Green
  }
} catch {
  Write-Host "⚠️ 查詢 Token 權限清單失敗：$($_.Exception.Message)" -ForegroundColor Gray
}

# 檢查 Antigravity MCP 設定
$McpPath = Join-Path $HOME ".gemini\config\mcp_config.json"
if (Test-Path $McpPath) {
  try {
    $McpCfg = Get-Content -Raw -Encoding UTF8 $McpPath | ConvertFrom-Json
    if ($McpCfg.mcpServers."google-workspace".env.GOOGLE_WORKSPACE_REFRESH_TOKEN) {
      Write-Host "✅ Antigravity MCP（google-workspace）已正確配置 Refresh Token！" -ForegroundColor Green
    } else {
      Write-Host "⚠️ Antigravity MCP 設定中尚未包含 google-workspace" -ForegroundColor Yellow
    }
  } catch {
    Write-Host "⚠️ 讀取 MCP 設定失敗：$($_.Exception.Message)" -ForegroundColor Gray
  }
}

# 檢查 Apps Script API 開關狀態
$Headers = @{ Authorization = "Bearer $($Tok.access_token)" }
try {
  $Ping = Invoke-RestMethod -Uri "https://script.googleapis.com/v1/processes?pageSize=1" -Headers $Headers -TimeoutSec 10
  Write-Host "✅ Apps Script API 開關為：開啟 (On)！" -ForegroundColor Green
} catch {
  $ErrDetail = $_.ErrorDetails.Message
  if ($ErrDetail -match "disabled|not been used|not enabled") {
    Write-Host "❌ Apps Script API 開關目前是【關閉 (Off)】！" -ForegroundColor Red
    Write-Host "👉 請前往 https://script.google.com/home/usersettings 切換為 On" -ForegroundColor Yellow
  } elseif ($ErrDetail -match "insufficient authentication scopes|ACCESS_TOKEN_SCOPE_INSUFFICIENT") {
    Write-Host "⚠️ Apps Script API 權限未包含在 Token 中（授權時漏勾 Apps Script 相關項目，請重新授權並按【全選】）" -ForegroundColor Yellow
  } else {
    Write-Host "⚠️ Apps Script API 回應：$($_.Exception.Response.StatusCode.value__) $ErrDetail" -ForegroundColor Gray
  }
}
