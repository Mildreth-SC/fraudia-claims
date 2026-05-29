@echo off
REM Run FraudIA Backend
REM This script installs dependencies and runs the FastAPI server

setlocal
cd /d "%~dp0"

echo ========================================
echo FraudIA Backend Launcher
echo ========================================

REM Try to find Python - prefer AppData path
set PYTHON=
if exist "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python3.12.exe" (
    set "PYTHON=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python3.12.exe"
) else (
    for /f "delims=" %%i in ('where python 2^>nul') do set PYTHON=%%i
)

if "%PYTHON%"=="" (
    echo Error: Python no encontrado en PATH
    echo Por favor instala Python 3.12+ desde python.org
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Usando: %PYTHON%
"%PYTHON%" --version

echo.
echo Instalando dependencias...
"%PYTHON%" -m pip install --upgrade pip -q 2>nul
"%PYTHON%" -m pip install fastapi uvicorn python-multipart pandas scikit-learn groq python-dotenv supabase-py -q

echo.
echo Iniciando backend en http://127.0.0.1:8000
echo.

"%PYTHON%" src/app/main.py

