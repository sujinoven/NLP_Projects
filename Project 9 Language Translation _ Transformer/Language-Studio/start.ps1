$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$appPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $appPython)) {
    Write-Host 'Create the virtual environment and install requirements first. See README.md.'
    exit 1
}
& $appPython -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
