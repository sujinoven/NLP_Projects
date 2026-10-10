$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..\frontend')
if (-not (Get-Command flutter -ErrorAction SilentlyContinue)) {
    throw 'Install the Flutter SDK and add flutter/bin to PATH. See README.md.'
}
flutter pub get
if ($LASTEXITCODE -ne 0) { throw 'Flutter dependency installation failed.' }
flutter run -d chrome --web-port=5173 --dart-define=API_BASE_URL=http://127.0.0.1:5001
if ($LASTEXITCODE -ne 0) { throw 'Flutter exited with an error.' }
