Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location "$PSScriptRoot\..\frontend"

if (-not (Test-Path ".env.local")) {
    Copy-Item ".env.example" ".env.local"
}

npm.cmd install
npm.cmd run dev
