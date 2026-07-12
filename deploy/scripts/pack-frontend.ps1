# Pack frontend build for ECS upload
# Usage: .\deploy\scripts\pack-frontend.ps1
# Upload frontend.zip to /var/www/cyinc/ then unzip on ECS

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $Root

if (-not (Test-Path ".env.production")) {
  Copy-Item ".env.production.example" ".env.production"
  Write-Host "Created .env.production (VITE_API_BASE_URL=/api/v1)"
}

Write-Host "==> npm run build"
npm run build
if ($LASTEXITCODE -ne 0) { throw "build failed" }

Write-Host "==> copy Content/*.html into docs/Content"
Remove-Item "docs\Content" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "docs\Content" | Out-Null
Copy-Item "Content\*.html" "docs\Content\" -Force

if (-not (Test-Path "docs\index.html")) { throw "missing docs/index.html" }
$htmlCount = @(Get-ChildItem "docs\Content\*.html").Count
if ($htmlCount -lt 1) { throw "missing docs/Content html files" }
Write-Host "Content articles: $htmlCount"

$Zip = Join-Path $Root "frontend.zip"
if (Test-Path $Zip) { Remove-Item $Zip -Force }

Write-Host "==> zip docs/* -> frontend.zip"
Write-Host "Tip: on ECS after unzip run: cp /var/www/cyinc/Content/*.html /var/www/cyinc/myweb/Content/"
Compress-Archive -Path "docs\*" -DestinationPath $Zip -Force
Write-Host "Done: $Zip"
Write-Host "Upload to ECS /var/www/cyinc/ then: cd myweb && unzip -o ../frontend.zip"
