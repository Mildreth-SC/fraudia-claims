@echo off
REM Run FraudIA Backend - con ruta correcta de Python

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ========================================
echo FraudIA Backend
echo ========================================
echo.

REM Usar la versión correcta de Python de AppData
set "PYTHON=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python3.12.exe"

if not exist "%PYTHON%" (
    echo [ERROR] Python no encontrado
    echo Ejecuta primero: setup.bat
    pause
    exit /b 1
)

echo Usando: %PYTHON%
"%PYTHON%" --version
echo.

REM Instalar si falta FastAPI
"%PYTHON%" -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias faltantes...
    "%PYTHON%" -m pip install fastapi uvicorn python-multipart pandas scikit-learn groq python-dotenv supabase-py --quiet
)

echo.
echo Iniciando servidor en http://127.0.0.1:8000
echo Presiona Ctrl+C para detener
echo.

"%PYTHON%" src/app/main.py
