@echo off
REM FraudIA Railway Deployment Script for Windows
REM Automates the deployment to Railway platform

setlocal enabledelayedexpansion

echo ==================================
echo FraudIA Railway Deployment
echo ==================================

REM Check prerequisites
echo.
echo Checking prerequisites...

where git >nul 2>nul
if errorlevel 1 (
    echo ERROR: Git not found. Install from https://git-scm.com/download/win
    exit /b 1
)

echo OK: Git found

REM Push to GitHub
echo.
echo Preparing repository...
set /p GITHUB_READY="Have you created a GitHub repository? (y/n): "

if /i not "!GITHUB_READY!"=="y" (
    echo.
    echo Please create a GitHub repository first and push your code
    echo Then run this script again.
    exit /b 0
)

set /p COMMIT_MSG="Commit message (default: 'Deploy FraudIA to Railway'): "
if "!COMMIT_MSG!"=="" set COMMIT_MSG=Deploy FraudIA to Railway

git add -A
git commit -m "!COMMIT_MSG!" >nul 2>nul || echo No changes to commit
git push origin main
if errorlevel 1 git push origin master

echo OK: Code pushed to GitHub

REM Get Supabase credentials
echo.
echo Setting up environment variables...
set /p SUPABASE_URL="Supabase URL (https://your-project.supabase.co): "
set /p SUPABASE_KEY="Supabase API Key: "

if "!SUPABASE_URL!"=="" (
    echo ERROR: Supabase credentials required
    exit /b 1
)

REM Instructions for Railway
echo.
echo ==================================
echo Railway Deployment Instructions
echo ==================================
echo.
echo 1. Go to https://railway.app
echo 2. Sign in with GitHub
echo 3. Click 'New Project' ^> 'Deploy from GitHub repo'
echo 4. Select your 'fraudia-claims' repository
echo 5. Railway will auto-detect settings
echo 6. Add these environment variables:
echo    SUPABASE_URL=!SUPABASE_URL!
echo    SUPABASE_KEY=!SUPABASE_KEY!
echo 7. Click 'Deploy'
echo 8. Wait for deployment to complete
echo 9. Copy public URL from 'Networking' tab
echo 10. Update frontend VITE_API_URL
echo.
echo NOTE: Railway auto-redeploys on git push to main
echo.

set /p OPEN_BROWSER="Open Railway in browser? (y/n): "
if /i "!OPEN_BROWSER!"=="y" (
    start https://railway.app/dashboard
)

echo.
echo Deployment setup complete!
echo.
