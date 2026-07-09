# 留言板 Q&A 冒烟：匿名 POST → GET 列表
param(
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"
$msg = @{
    name = "smoke_test"
    content = "QA smoke " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
} | ConvertTo-Json -Compress

Write-Host "POST /api/v1/qa/messages (anonymous)"
$created = Invoke-RestMethod "$BaseUrl/api/v1/qa/messages" -Method Post -Body $msg -ContentType "application/json; charset=utf-8"
if ($created.code -ne 0) { throw "create failed: $($created.message)" }
Write-Host "  OK id=$($created.data.id)"

Write-Host "GET /api/v1/qa/messages"
$list = Invoke-RestMethod "$BaseUrl/api/v1/qa/messages?limit=5"
if (-not $list.data.Count) { throw "list empty" }
Write-Host "  OK count=$($list.data.Count)"
Write-Host "QA smoke test passed."
