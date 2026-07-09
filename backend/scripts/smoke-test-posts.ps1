# M2：登录后创建/发布/列表/删除文章
param(
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"
$user = "post_" + (Get-Random -Maximum 999999)
$pass = "Test123456"
$reg = @{ username = $user; email = "$user@example.com"; password = $pass } | ConvertTo-Json
Invoke-RestMethod "$BaseUrl/api/v1/auth/register" -Method Post -Body $reg -ContentType "application/json; charset=utf-8" | Out-Null
$login = @{ username = $user; password = $pass } | ConvertTo-Json
$token = (Invoke-RestMethod "$BaseUrl/api/v1/auth/login" -Method Post -Body $login -ContentType "application/json; charset=utf-8").data.access_token
$headers = @{ Authorization = "Bearer $token" }

$post = @{
    title = "M2 Test Post"
    content = "Hello CYINC M2"
    category = "测试"
    tags = @("FastAPI", "M2")
    status = "published"
} | ConvertTo-Json
$created = Invoke-RestMethod "$BaseUrl/api/v1/posts" -Method Post -Body $post -ContentType "application/json; charset=utf-8" -Headers $headers
$id = $created.data.id
Write-Host "POST /posts -> id=$id"

$list = Invoke-RestMethod "$BaseUrl/api/v1/posts?status=published"
if ($list.data.total -lt 1) { throw "list empty" }
Write-Host "GET /posts -> total=$($list.data.total)"

$detail = Invoke-RestMethod "$BaseUrl/api/v1/posts/$id"
Write-Host "GET /posts/$id -> $($detail.data.title)"

Invoke-RestMethod "$BaseUrl/api/v1/posts/$id" -Method Delete -Headers $headers | Out-Null
Write-Host "DELETE /posts/$id OK"
Write-Host "M2 posts smoke test passed."
