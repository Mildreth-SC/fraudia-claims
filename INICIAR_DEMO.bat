@echo off
title FraudIA - Demo local
cd /d "%~dp0"

echo ============================================
echo  FraudIA - Iniciar backend + frontend
echo ============================================
echo.

echo [1/2] Backend API en http://127.0.0.1:8000
start "FraudIA API" cmd /k ""C:\Users\guano\AppData\Local\Programs\Python\Python312\python.exe" src\app\main_local_test.py"

timeout /t 3 /nobreak >nul

echo [2/2] Frontend en http://127.0.0.1:3000
cd frontend
start "FraudIA Frontend" cmd /k "npm run dev"

echo.
echo Listo. Abre http://127.0.0.1:3000
echo API: http://127.0.0.1:8000
echo.
pause
