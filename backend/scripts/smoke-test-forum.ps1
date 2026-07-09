# M5.5 论坛冒烟：板块列表 → 登录发帖 → 回帖
param(
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"
$user = "forum_" + (Get-Random -Maximum 999999)
$pass = "Test123456"
$reg = @{ username = $user; email = "$user@example.com"; password = $pass } | ConvertTo-Json
Invoke-RestMethod "$BaseUrl/api/v1/auth/register" -Method Post -Body $reg -ContentType "application/json; charset=utf-8" | Out-Null
$login = @{ username = $user; password = $pass } | ConvertTo-Json
$token = (Invoke-RestMethod "$BaseUrl/api/v1/auth/login" -Method Post -Body $login -ContentType "application/json; charset=utf-8").data.access_token
$headers = @{ Authorization = "Bearer $token" }

Write-Host "GET /api/v1/forum/categories"
$cats = Invoke-RestMethod "$BaseUrl/api/v1/forum/categories"
if (-not $cats.data.Count) { throw "no categories" }
$catId = $cats.data[0].id
$slug = $cats.data[0].slug
Write-Host "  OK id=$catId slug=$slug"

$post = @{
    category_id = $catId
    title = "Forum smoke test"
    content = "Hello from smoke-test-forum.ps1"
} | ConvertTo-Json
Write-Host "POST /api/v1/forum/threads"
$thread = Invoke-RestMethod "$BaseUrl/api/v1/forum/threads" -Method Post -Body $post -ContentType "application/json; charset=utf-8" -Headers $headers
$tid = $thread.data.id
Write-Host "  OK thread_id=$tid"

$reply = @{ content = "First reply" } | ConvertTo-Json
Write-Host "POST /api/v1/forum/threads/$tid/replies"
Invoke-RestMethod "$BaseUrl/api/v1/forum/threads/$tid/replies" -Method Post -Body $reply -ContentType "application/json; charset=utf-8" -Headers $headers | Out-Null
Write-Host "  OK"

$detail = Invoke-RestMethod "$BaseUrl/api/v1/forum/threads/$tid"
if ($detail.data.reply_count -lt 1) { throw "reply_count expected >= 1" }
Write-Host "GET /api/v1/forum/threads/$tid -> replies=$($detail.data.reply_count)"
Write-Host "Forum smoke test passed."
