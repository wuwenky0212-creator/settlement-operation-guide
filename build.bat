@echo off
echo ==========================================
echo Building Settlement Operation Guide
echo ==========================================
echo.

echo Step 1: Installing root dependencies...
call npm install
if errorlevel 1 goto error

echo.
echo Step 2: Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 goto error

echo.
echo Step 3: Building frontend...
call npm run build
if errorlevel 1 goto error

echo.
echo Step 4: Verifying build...
cd ..
if exist "frontend\dist" (
    echo [32m✓ Frontend build successful![0m
    echo [32m✓ Files in frontend/dist:[0m
    dir frontend\dist
) else (
    echo [31m✗ Frontend build failed - dist directory not found![0m
    goto error
)

echo.
echo ==========================================
echo Build completed successfully!
echo ==========================================
goto end

:error
echo.
echo [31m==========================================
echo Build failed!
echo ==========================================[0m
exit /b 1

:end
