# Pack large media for ECS (tar.gz keeps UTF-8 Chinese paths; zip from Windows garbles names)
# Usage: .\deploy\scripts\pack-media.ps1
# Upload media.tar.gz to /var/www/cyinc/ on ECS, then:
#   cd /var/www/cyinc && rm -rf img/BA Music && tar -xzf media.tar.gz

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $Root

$Archive = Join-Path $Root "media.tar.gz"
if (Test-Path $Archive) { Remove-Item $Archive -Force }

$items = @()
if (Test-Path "img/BA") { $items += "img/BA" }
if (Test-Path "Music") { $items += "Music" }

if ($items.Count -lt 1) {
  throw "Nothing to pack: need img/BA and/or Music/"
}

Write-Host "==> tar.gz packing: $($items -join ', ')"
& tar -czf $Archive @items
if ($LASTEXITCODE -ne 0) { throw "tar failed" }

Write-Host "Done: $Archive ($([math]::Round((Get-Item $Archive).Length / 1MB, 1)) MB)"
Write-Host "ECS:"
Write-Host "  rm -rf img/BA Music"
Write-Host "  tar -xzf media.tar.gz"
Write-Host "  ls img/BA/R/日奈/ | head"
