$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
    throw "The virtual environment is missing. Run .\setup-windows.ps1 first."
}

& ".\.venv\Scripts\python.exe" -c "import sqlalchemy" 2>$null
if ($LASTEXITCODE -ne 0) {
    throw "Dependencies are missing from this virtual environment. Run .\setup-windows.ps1 again."
}

& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

