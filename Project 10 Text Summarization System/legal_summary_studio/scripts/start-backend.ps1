$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..\backend')
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    throw 'Set up backend/.venv using the README first.'
}
& '.\.venv\Scripts\python.exe' run.py
if ($LASTEXITCODE -ne 0) { throw 'Backend exited with an error.' }
