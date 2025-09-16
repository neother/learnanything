@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo  Starting Learn Anything Development
echo ========================================
echo.

REM Stop processes running on ports 3000 and 8000
echo Checking for existing processes on ports 3000 and 8000
for %%P in (8000) do (
    echo Checking port %%P...
    for /f "tokens=5" %%i in ('netstat -aon 2^>nul ^| findstr :%%P ^| findstr LISTENING 2^>nul') do (
        if not "%%i"=="0" if not "%%i"=="" (
            echo   Found process using port %%P (PID: %%i)
            taskkill /F /PID %%i >nul 2>&1
            if !errorlevel! equ 0 (
                echo   [SUCCESS] Killed process %%i
            ) else (
                echo   [WARNING] Could not kill process %%i
            )
        )
    )
)

REM Additional cleanup - kill any remaining python processes that might be using our ports
echo Cleaning up any remaining Python processes...
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV /NH 2^>nul ^| findstr /V "INFO:"') do (
    set "pid=%%i"
    set "pid=!pid:"=!"
    if not "!pid!"=="" if not "!pid!"=="PID" (
        echo   Checking Python process !pid!...
        netstat -aon 2>nul | findstr "!pid!" | findstr ":3000\|:8000" >nul
        if !errorlevel! equ 0 (
            echo   [CLEANUP] Killing Python process !pid! using our ports
            taskkill /F /PID !pid! >nul 2>&1
        )
    )
)

echo.
echo Starting backend (FastAPI with uvicorn)
cd backend\backend

REM Install requirements if needed
if not exist "requirements_installed.txt" (
    echo Installing Python requirements...
    python -m pip install -r requirements.txt
    echo Requirements installed > requirements_installed.txt
) else (
    echo Python requirements already installed
)

REM Start the backend with built-in logging
echo Starting backend server (logs will appear in console and backend.log)
echo Log file location: %CD%\..\..\backend.log
echo Backend uses Python logging module for proper UTF-8 log file output
echo.

REM Start Python with built-in logging (no additional redirection needed)
python main.py

REM Backend will run in foreground with logs visible
echo.
echo Backend is starting - you will see logs below and in backend.log
echo Press Ctrl+C to stop the server.
echo.
echo ========================================
