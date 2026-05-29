@echo off
REM Setup FraudIA - Instala todas las dependencias

setlocal enabledelayedexpansion

echo ========================================
echo FraudIA - Setup Completo
echo ========================================
echo.

REM Python correcto en AppData
set "PYTHON=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python3.12.exe"

if not exist "%PYTHON%" (
    echo [ERROR] Python no encontrado en: %PYTHON%
    echo.
    echo Soluciones:
    echo 1. Instala Python 3.12+ desde https://www.python.org/downloads/
    echo 2. Asegúrate de marcar "Add Python to PATH" durante la instalación
    echo 3. Reinicia PowerShell
    echo.
    pause
    exit /b 1
)

echo Python encontrado: %PYTHON%
"%PYTHON%" --version
echo.

REM Verificar pip
echo Verificando pip...
"%PYTHON%" -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip no está disponible
    echo Reinstala Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Instalando dependencias Python...
echo (Esto puede tomar 2-3 minutos la primera vez)
echo.

"%PYTHON%" -m pip install --upgrade pip setuptools wheel --quiet
"%PYTHON%" -m pip install fastapi uvicorn python-multipart pandas scikit-learn groq python-dotenv supabase-py --quiet

if errorlevel 1 (
    echo [ERROR] Fallo la instalación de dependencias
    pause
    exit /b 1
)

echo.
echo ✓ Dependencias Python instaladas
echo.

REM Node/npm
where npm >nul 2>&1
if errorlevel 1 (
    echo [ADVERTENCIA] npm no encontrado
    echo Instala Node.js desde: https://nodejs.org/
    echo.
) else (
    echo ✓ Node.js encontrado
    node --version
    echo.

    if exist "frontend\node_modules" (
        echo ✓ Dependencias npm ya instaladas
    ) else (
        echo Instalando dependencias npm...
        cd frontend
        call npm install --silent
        cd ..
        echo ✓ Dependencias npm instaladas
    )
)

echo.
echo ========================================
echo ✓ Setup completado exitosamente
echo ========================================
echo.
echo Ahora abre 2 PowerShell nuevas y ejecuta:
echo.
echo Terminal 1 (Backend):
echo   cd c:\Users\guano\OneDrive\Documentos\Reto_aseguradora
echo   python src/app/main.py
echo.
echo Terminal 2 (Frontend):
echo   cd c:\Users\guano\OneDrive\Documentos\Reto_aseguradora\frontend
echo   npm run dev
echo.
echo Luego abre: http://localhost:3000
echo.
pause
