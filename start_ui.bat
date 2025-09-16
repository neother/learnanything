@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo  Starting Learn Anything Development
echo ========================================
echo.

REM Stop processes running on ports 3000 and 8000
echo Checking for existing processes on ports 3000 and 8000
for %%P in (3000) do (
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

echo Starting frontend (npm start)
cd frontend

REM Check if node_modules exists, install if needed
if not exist node_modules (
    echo Installing npm dependencies...
    npm install
    echo.
)

echo Frontend is starting - you will see logs below and in frontend.log
echo Press Ctrl+C to stop the server.
echo Open http://localhost:3000 in your browser
echo Log file location: %CD%\..\frontend.log
echo.
echo ========================================

REM Create fresh log file with timestamp header (override mode)
echo [%date% %time%] Frontend server starting... > ..\frontend.log
echo ================================================================================ >> ..\frontend.log

REM Start npm - output will override the log file each time
REM Using override mode (>) to clear previous sessions
echo NOTE: Frontend logs will override frontend.log on each startup
npm start >> ..\frontend.log 2>&1