@echo off
REM J-Quants API Data Inspector - Windows Batch File

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    exit /b 1
)

REM Change to project root directory
cd /d "%~dp0.."

REM Execute Python script with all arguments
python scripts\inspect_data.py %*

REM Pause to see results
pause 