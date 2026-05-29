@echo off
REM Run FraudIA Frontend
REM This script runs the Vite development server on port 3000

setlocal
cd /d "%~dp0\frontend"

echo ========================================
echo FraudIA Frontend Launcher
echo ========================================

REM Check if node_modules exists
if not exist "node_modules" (
    echo Instalando dependencias npm...
    call npm install
)

echo.
echo Iniciando frontend en http://127.0.0.1:3000
echo.

call npm run dev
