@echo off
REM FraudIA Cloud Run Deployment Script for Windows
REM Automates the deployment process to Google Cloud Run

setlocal enabledelayedexpansion

echo ==================================
echo FraudIA Cloud Run Deployment
echo ==================================

REM Check prerequisites
echo.
echo Checking prerequisites...

where gcloud >nul 2>nul
if errorlevel 1 (
    echo ERROR: gcloud CLI not found.
    echo Install it from: https://cloud.google.com/sdk/docs/install
    exit /b 1
)

where docker >nul 2>nul
if errorlevel 1 (
    echo ERROR: Docker not found.
    echo Install it from: https://www.docker.com/products/docker-desktop
    exit /b 1
)

echo OK: Prerequisites satisfied

REM Get project ID
echo.
set /p PROJECT_ID="Enter your Google Cloud Project ID: "

if "!PROJECT_ID!"=="" (
    echo ERROR: Project ID cannot be empty
    exit /b 1
)

REM Set gcloud configuration
echo.
echo Configuring gcloud...
call gcloud config set project !PROJECT_ID!
call gcloud auth application-default login

REM Get Supabase credentials
echo.
echo Setting up environment variables...
set /p SUPABASE_URL="Enter Supabase URL (https://your-project.supabase.co): "
set /p SUPABASE_KEY="Enter Supabase API Key: "

if "!SUPABASE_URL!"=="" (
    echo WARNING: Supabase credentials not provided. You can set them after deployment.
)

REM Build Docker image locally (optional)
echo.
set /p BUILD_LOCAL="Build Docker image locally first? (y/n): "
if /i "!BUILD_LOCAL!"=="y" (
    echo.
    echo Building Docker image...
    call docker build -t fraudia-api:latest .
    echo OK: Docker image built
)

REM Deploy to Cloud Run
echo.
echo Deploying to Cloud Run...

set SERVICE_NAME=fraudia-api
set REGION=us-central1

if "!SUPABASE_URL!"=="" (
    call gcloud run deploy !SERVICE_NAME! ^
      --source . ^
      --platform managed ^
      --region !REGION! ^
      --allow-unauthenticated ^
      --memory 2Gi ^
      --cpu 2 ^
      --timeout 60 ^
      --max-instances 100
) else (
    call gcloud run deploy !SERVICE_NAME! ^
      --source . ^
      --platform managed ^
      --region !REGION! ^
      --allow-unauthenticated ^
      --memory 2Gi ^
      --cpu 2 ^
      --timeout 60 ^
      --max-instances 100 ^
      --set-env-vars SUPABASE_URL=!SUPABASE_URL! ^
      --set-env-vars SUPABASE_KEY=!SUPABASE_KEY!
)

echo OK: Deployment initiated

REM Get service URL
echo.
echo Retrieving service URL...
for /f "tokens=*" %%A in ('gcloud run services describe !SERVICE_NAME! --region !REGION! --format "value(status.url)"') do set SERVICE_URL=%%A

echo.
echo ==================================
echo Deployment Successful!
echo ==================================
echo Service: !SERVICE_NAME!
echo Region: !REGION!
echo URL: !SERVICE_URL!

REM Test the endpoint
echo.
echo Testing endpoint...
call curl -s "!SERVICE_URL!/"
echo.

REM Update frontend configuration
echo.
set /p UPDATE_FRONTEND="Update frontend .env with API URL? (y/n): "
if /i "!UPDATE_FRONTEND!"=="y" (
    if exist "frontend\.env" (
        for /f "tokens=*" %%A in (frontend\.env) do (
            echo %%A | find "VITE_API_URL=" >nul
            if errorlevel 1 (
                echo %%A >> frontend\.env.tmp
            )
        )
        echo VITE_API_URL=!SERVICE_URL! >> frontend\.env.tmp
        move /y frontend\.env.tmp frontend\.env >nul
        echo OK: Frontend .env updated
    ) else (
        echo VITE_API_URL=!SERVICE_URL! > frontend\.env
        echo OK: Created frontend\.env
    )
)

REM View logs
echo.
set /p VIEW_LOGS="View deployment logs? (y/n): "
if /i "!VIEW_LOGS!"=="y" (
    call gcloud run logs read !SERVICE_NAME! --region !REGION! --limit 50
)

echo.
echo Deployment Complete!
echo.
echo Next steps:
echo 1. Set environment variables if not done during deployment
echo 2. Monitor logs: gcloud run logs read !SERVICE_NAME! --region !REGION!
echo 3. Test the API: curl !SERVICE_URL!/
echo 4. Update frontend with API URL: !SERVICE_URL!
echo.
