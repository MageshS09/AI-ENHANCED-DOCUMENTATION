Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) {
    $env:GIT_PYTHON_GIT_EXECUTABLE = $git.Source
}

Set-Location "$PSScriptRoot\..\backend"

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created backend\.env. Add OPENAI_API_KEY before generating documentation."
}

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
