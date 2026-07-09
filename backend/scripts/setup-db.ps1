# 用 mysql 命令行初始化 cyinc 库并生成 backend/.env
# 用法: .\scripts\setup-db.ps1 -Password "你的root密码"
param(
    [Parameter(Mandatory = $true)]
    [string]$Password
)

$ErrorActionPreference = "Stop"
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$backend = Join-Path $root "backend"

$mysqlCandidates = @(
    "D:\phpstudy\phpstudy_pro\Extensions\MySQL5.7.26\bin\mysql.exe",
    "D:\phpstudy\phpstudy_pro\Extensions\MySQL8.0.12\bin\mysql.exe"
)
$mysql = $mysqlCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $mysql) {
    $mysql = (Get-Command mysql -ErrorAction SilentlyContinue).Source
}
if (-not $mysql) {
    Write-Error "找不到 mysql.exe。请确认 phpstudy MySQL 已启动，或把 mysql 加入 PATH。"
}

Write-Host "使用: $mysql"
Write-Host "创建数据库 cyinc ..."

& $mysql -uroot "-p$Password" --default-character-set=utf8mb4 -e "CREATE DATABASE IF NOT EXISTS cyinc CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; SHOW DATABASES LIKE 'cyinc';"
if ($LASTEXITCODE -ne 0) {
    Write-Error "mysql 连接失败。请到 phpstudy 首页 -> 数据库 查看/重置 root 密码后重试。"
}

$envFile = Join-Path $backend ".env"
$dbUrl = "mysql+pymysql://root:$Password@127.0.0.1:3306/cyinc"

@"
DATABASE_URL=$dbUrl
SECRET_KEY=dev-$(New-Guid)
ACCESS_TOKEN_EXPIRE_MINUTES=10080
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
API_PREFIX=/api/v1
"@ | Set-Content -Path $envFile -Encoding UTF8

Write-Host "已写入 $envFile"
Write-Host "下一步: cd backend; .\.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
