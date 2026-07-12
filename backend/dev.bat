@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] 未找到 .venv，请先: python -m venv .venv ^& pip install -r requirements.txt
  exit /b 1
)
echo ==^> CYINC API  http://127.0.0.1:8000
".venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
