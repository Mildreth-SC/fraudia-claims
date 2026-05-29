@echo off
title FraudIA - Instalar dependencias Python
cd /d "%~dp0"

set PY=C:\Users\guano\AppData\Local\Programs\Python\Python312\python.exe

if not exist "%PY%" (
  echo No se encontro Python 3.12 en:
  echo %PY%
  echo Instale Python 3.12 desde https://www.python.org/downloads/
  pause
  exit /b 1
)

echo Instalando dependencias demo...
"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install -r requirements-demo.txt

echo.
echo Listo. Ahora ejecute:
echo   "%PY%" src\app\main_local_test.py
echo o doble clic en INICIAR_DEMO.bat
echo.
pause
