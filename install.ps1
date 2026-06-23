# Imperator Installer for Windows
# Requires PowerShell 5.1+, Git, and Python 3.8+

$ErrorActionPreference = "Stop"
$REPO = if ($env:IMPERATOR_REPO) { $env:IMPERATOR_REPO } else { "https://github.com/MyGenX/Imperator" }
$IMPERATOR_DIR = if ($env:IMPERATOR_DIR) { $env:IMPERATOR_DIR } else { "$HOME\.imperator" }

Write-Host ""
Write-Host "Imperator Installer" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "--------------------------------" -ForegroundColor Blue
Write-Host ""

function Check-Command($cmd) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "x $cmd is required but not installed." -ForegroundColor Red
        Write-Host "  Please install it and re-run this script." -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "-> Checking dependencies..." -ForegroundColor Cyan
Check-Command "git"
Check-Command "python"
Check-Command "pip"
Write-Host "OK All dependencies found" -ForegroundColor Green
Write-Host ""

if (Test-Path "$IMPERATOR_DIR\.git") {
    Write-Host "-> Imperator already installed. Updating..." -ForegroundColor Yellow
    git -C $IMPERATOR_DIR pull --quiet
    Write-Host "OK Updated to latest version" -ForegroundColor Green
} else {
    Write-Host "-> Cloning Imperator..." -ForegroundColor Cyan
    git clone --quiet $REPO $IMPERATOR_DIR
    Write-Host "OK Cloned to $IMPERATOR_DIR" -ForegroundColor Green
}
Write-Host ""

Write-Host "-> Installing Python CLI..." -ForegroundColor Cyan
pip install -e "$IMPERATOR_DIR\cli" --quiet
Write-Host "OK CLI installed (entry point: imperator)" -ForegroundColor Green
Write-Host ""

Write-Host "OK Imperator installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "  Run 'imperator init' in your project to get started" -ForegroundColor White
Write-Host "  Docs: $REPO" -ForegroundColor Cyan
Write-Host ""
