@echo off
rem Creates/updates the .venv that start.bat runs against - run this once,
rem and again any time requirements.txt changes.
setlocal

cd /d "%~dp0"

if not exist .venv (
    python -m venv .venv
    if errorlevel 1 exit /b 1
)

call .venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo Setup complete - run start.bat to launch tune.py
