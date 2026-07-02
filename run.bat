@echo off
:: Устанавливаем рабочую директорию на папку, где лежит этот .bat файл
cd /d "%~dp0"

title Discord Orbs Earner Setup
echo ===================================
echo   Discord Orbs Earner Setup ^& Run
echo ===================================
echo.

:: Check for python
py --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=py
) else (
    python --version >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set PYTHON_CMD=python
    ) else (
        echo [ERROR] Python is not installed or not added to PATH!
        echo Please install Python 3.10+ from python.org and ensure "Add to PATH" is checked.
        pause
        exit /b 1
    )
)

:: Create venv
if not exist venv (
    echo [INFO] Creating virtual environment...
    %PYTHON_CMD% -m venv venv
)

:: Activate venv
call venv\Scripts\activate.bat

:: Install requirements
echo [INFO] Installing required packages...
if exist requirements.txt (
    pip install -r requirements.txt -q
) else (
    echo [ERROR] requirements.txt not found! Make sure it is in the same folder as run.bat.
    pause
    exit /b 1
)

:: Run app
echo [INFO] Launching Application...
cd src
python app.py

:: If crashed, pause to let user read the error
if %ERRORLEVEL% neq 0 (
    echo.
    echo [FATAL ERROR] The application crashed unexpectedly.
    echo Please check crash_report.txt and crash_report_imports.txt in the src folder.
    pause
)
