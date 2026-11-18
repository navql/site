# NavQL installer for Windows (PowerShell).
#
#   irm https://navql.com/install.ps1 | iex
#
# Downloads the latest NavQL installer and runs it silently, for the current user (no administrator
# rights): NavQL goes to the Start menu and updates itself afterwards. Run it again to reinstall;
# uninstall with
#
#   & ([scriptblock]::Create((irm https://navql.com/install.ps1))) -Uninstall
#
# By installing NavQL you agree to its Terms of Use (https://navql.com/terms.html) and
# Privacy Policy (https://navql.com/privacy.html).
param([switch]$Uninstall)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue' # Invoke-WebRequest is much faster without the progress bar
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

function Get-NavQLInstall {
  $keys = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*', 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*'
  Get-ItemProperty $keys -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -like 'NavQL*' } | Select-Object -First 1
}

function Split-Command([string]$command) {
  # "C:\...\Uninstall NavQL.exe" /currentuser  ->  path, arguments
  if ($command -match '^\s*"([^"]+)"\s*(.*)$') { return $Matches[1], $Matches[2] }
  return $command, ''
}

if ($Uninstall) {
  $app = Get-NavQLInstall
  if (-not $app) { Write-Host 'NavQL is not installed.'; return }
  $exe, $arguments = Split-Command $app.UninstallString
  Start-Process -FilePath $exe -ArgumentList (($arguments, '/S') -join ' ').Trim() -Wait
  Write-Host 'NavQL uninstalled. Your connections and settings are still in' (Join-Path $env:APPDATA 'NavQL') '(delete that folder to remove them).'
  return
}

if (-not [Environment]::Is64BitOperatingSystem) {
  throw 'NavQL for Windows needs a 64-bit Windows 10 or 11.'
}

Write-Host 'Finding the latest NavQL...'
$release = Invoke-RestMethod -Uri 'https://api.github.com/repos/navql/releases/releases/latest' -Headers @{ 'User-Agent' = 'navql-install' }
$asset = $release.assets | Where-Object { $_.name -match '^NavQL-Setup-.*\.exe$' } | Select-Object -First 1
if (-not $asset) { throw 'Could not find the Windows installer in the latest release (https://github.com/navql/releases/releases).' }
$version = $release.tag_name -replace '^v', ''

$installer = Join-Path ([IO.Path]::GetTempPath()) $asset.name
Write-Host "Downloading NavQL $version..."
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $installer -UseBasicParsing -Headers @{ 'User-Agent' = 'navql-install' }

Write-Host 'Installing...'
try {
  $process = Start-Process -FilePath $installer -ArgumentList '/S' -Wait -PassThru
  if ($process.ExitCode -ne 0) { throw "The installer stopped with code $($process.ExitCode)." }
} finally {
  Remove-Item $installer -Force -ErrorAction SilentlyContinue
}

$app = Get-NavQLInstall
Write-Host ''
if ($app) {
  Write-Host "NavQL $version is installed: open it from the Start menu."
} else {
  Write-Host "NavQL $version was installed; open it from the Start menu."
}
Write-Host ''
Write-Host 'By installing NavQL you agree to its Terms of Use (https://navql.com/terms.html) and Privacy Policy (https://navql.com/privacy.html).'
