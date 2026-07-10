# 打包前端完整产物（含 Content/、content/ 预渲染、assets）
# 用法（PowerShell，项目根目录）：
#   .\deploy\scripts\pack-frontend.ps1
# 生成 frontend.zip 后上传到 ECS /var/www/cyinc/myweb/ 并 unzip

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $Root

if (-not (Test-Path ".env.production")) {
  Copy-Item ".env.production.example" ".env.production"
  Write-Host "已创建 .env.production（VITE_API_BASE_URL=/api/v1）"
}

Write-Host "==> npm run build"
npm run build
if ($LASTEXITCODE -ne 0) { throw "build failed" }

# Windows 下 docs/content 与 docs/Content 同目录，预渲染会污染 Content；用源码目录覆盖
Write-Host "==> 清理并复制 Content/*.html（避免乱码子目录）"
Remove-Item "docs\Content" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "docs\Content" | Out-Null
Copy-Item "Content\*.html" "docs\Content\" -Force

if (-not (Test-Path "docs\index.html")) { throw "docs/index.html 不存在" }
$htmlCount = (Get-ChildItem "docs\Content\*.html").Count
if ($htmlCount -lt 1) { throw "docs/Content 无 .html 文件" }
Write-Host "Content 文章数: $htmlCount"

$Zip = Join-Path $Root "frontend.zip"
if (Test-Path $Zip) { Remove-Item $Zip -Force }

Write-Host "==> 打包 docs/* -> frontend.zip"
Write-Host "提示: 若 ECS 上中文文件名乱码，请直接在 ECS 执行: cp /var/www/cyinc/Content/*.html /var/www/cyinc/myweb/Content/"
Compress-Archive -Path "docs\*" -DestinationPath $Zip -Force
Write-Host "完成: $Zip"
Write-Host "上传到 ECS: /var/www/cyinc/myweb/ 后执行 unzip -o frontend.zip"
Write-Host "媒体文件（不打包）: 确保 ECS 存在 /var/www/cyinc/img/ 与 /var/www/cyinc/Music/，并配置 Nginx alias"
