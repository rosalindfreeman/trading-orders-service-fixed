$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
    $pythonCommand = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $pythonCommand) {
    throw "Python 3.12+ was not found. Install it with: winget install --id Python.Python.3.12 -e"
}

$pythonArguments = @()
if ($pythonCommand.Name -eq "py.exe" -or $pythonCommand.Name -eq "py") {
    $pythonArguments = @("-3.12")
}

& $pythonCommand.Source @pythonArguments -c "import sys; assert sys.version_info >= (3, 12), 'Python 3.12 or newer is required'"
if ($LASTEXITCODE -ne 0) { throw "Python 3.12 or newer is required." }

if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
    & $pythonCommand.Source @pythonArguments -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Could not create the virtual environment." }
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Could not upgrade pip." }

& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Could not install application dependencies." }

& ".\.venv\Scripts\python.exe" -c "import fastapi, sqlalchemy, jwt, structlog; print('Dependencies verified successfully. SQLAlchemy', sqlalchemy.__version__)"
if ($LASTEXITCODE -ne 0) { throw "Dependency verification failed." }

Write-Host "Setup complete. Start the API with: .\run-windows.ps1"

