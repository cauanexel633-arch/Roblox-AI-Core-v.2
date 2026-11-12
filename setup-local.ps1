$ErrorActionPreference = "Stop"
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
Write-Host "Instalacao concluida. Edite .env e execute: .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload"
