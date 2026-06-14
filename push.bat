@echo off
title EverythingMoe API - Git Push
echo ========================================
echo   EverythingMoe API - Git Push
echo ========================================
echo.

:: Stage all changes
echo [1/3] Staging all changes...
git add .
if %errorlevel% neq 0 (
    echo ERROR: Failed to stage changes.
    pause
    exit /b 1
)
echo       Done.
echo.

:: Prompt for commit message
set /p MSG="[2/3] Enter commit message: "
if "%MSG%"=="" (
    echo ERROR: Commit message cannot be empty.
    pause
    exit /b 1
)

:: Commit
git commit -m "%MSG%"
if %errorlevel% neq 0 (
    echo ERROR: Failed to commit. Nothing to commit or other issue.
    pause
    exit /b 1
)
echo       Committed.
echo.

:: Push
echo [3/3] Pushing to origin main...
git push origin main
if %errorlevel% neq 0 (
    echo ERROR: Push failed. Try pulling first.
    pause
    exit /b 1
)
echo.
echo ========================================
echo   Push successful!
echo ========================================
pause
