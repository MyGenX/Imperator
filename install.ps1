# Imperator Installer for Windows
# Thin wrapper around cli/imperator/installer.py.

$ErrorActionPreference = "Stop"

$Repo = if ($env:IMPERATOR_REPO) { $env:IMPERATOR_REPO } else { "https://github.com/MyGenX/Imperator" }
$RawInstaller = if ($env:IMPERATOR_INSTALLER_URL) {
    $env:IMPERATOR_INSTALLER_URL
} else {
    "https://raw.githubusercontent.com/MyGenX/Imperator/main/cli/imperator/installer.py"
}

function Find-Python {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return "python"
    }
    if (Get-Command python3 -ErrorAction SilentlyContinue) {
        return "python3"
    }
    throw "python or python3 is required."
}

$Python = Find-Python
$LocalInstaller = Join-Path $PSScriptRoot "cli\imperator\installer.py"

if ($PSScriptRoot -and (Test-Path $LocalInstaller)) {
    & $Python $LocalInstaller @args
    exit $LASTEXITCODE
}

$TmpInstaller = Join-Path ([System.IO.Path]::GetTempPath()) ("imperator-installer-" + [System.Guid]::NewGuid().ToString() + ".py")
try {
    Invoke-WebRequest -Uri $RawInstaller -OutFile $TmpInstaller -UseBasicParsing
    $env:IMPERATOR_REPO = $Repo
    & $Python $TmpInstaller @args
    exit $LASTEXITCODE
}
finally {
    Remove-Item -Force -ErrorAction SilentlyContinue $TmpInstaller
}
