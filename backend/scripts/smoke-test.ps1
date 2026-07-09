# M1 冒烟测试：健康检查 + 注册 + 登录 + /auth/me
param(
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"
$user = "test_" + (Get-Random -Maximum 999999)
$pass = "test123456"
$body = @{ username = $user; email = "$user@example.com"; password = $pass } | ConvertTo-Json

Write-Host "GET $BaseUrl/api/health"
$h = Invoke-RestMethod "$BaseUrl/api/health"
if ($h.data.status -ne "ok") { throw "health failed" }
Write-Host "  OK"

Write-Host "POST /api/v1/auth/register ($user)"
$r = Invoke-RestMethod "$BaseUrl/api/v1/auth/register" -Method Post -Body $body -ContentType "application/json; charset=utf-8"
if ($r.code -ne 0) { throw "register failed: $($r.message)" }
Write-Host "  OK"

Write-Host "POST /api/v1/auth/login"
$login = @{ username = $user; password = $pass } | ConvertTo-Json
$l = Invoke-RestMethod "$BaseUrl/api/v1/auth/login" -Method Post -Body $login -ContentType "application/json; charset=utf-8"
$token = $l.data.access_token
if (-not $token) { throw "login failed" }
Write-Host "  OK token=$($token.Substring(0, [Math]::Min(20, $token.Length)))..."

Write-Host "GET /api/v1/auth/me"
$me = Invoke-RestMethod "$BaseUrl/api/v1/auth/me" -Headers @{ Authorization = "Bearer $token" }
if ($me.data.username -ne $user) { throw "me failed" }
Write-Host "  OK username=$($me.data.username)"
Write-Host "M1 smoke test passed."
