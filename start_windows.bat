@echo off
REM Windows PowerShell Startup Script for OpenFlow Simulation
REM This script helps you start the simulation correctly on Windows with WSL

echo ========================================
echo OpenFlow Simulation - Windows Startup
echo ========================================
echo.

echo [Step 1] Cleaning previous Mininet instances...
wsl sudo mn -c

echo [Step 2] Checking if controller is running...
wsl pgrep -f ryu-manager >nul 2>&1
if %errorlevel% equ 0 (
    echo WARNING: Ryu controller is already running!
    echo Killing previous instance...
    wsl sudo pkill -f ryu-manager
    timeout /t 2 >nul
)

echo.
echo ========================================
echo Ready to start simulation!
echo ========================================
echo.
echo Please open TWO PowerShell windows:
echo.
echo Window 1 - Controller:
echo   wsl ryu-manager controller.py --verbose
echo.
echo Wait for "instantiating app" message, then:
echo.
echo Window 2 - Mininet:
echo   wsl sudo python3 topology.py
echo.
echo In Mininet CLI, wait 5 seconds, then:
echo   mininet^> pingall
echo.
echo Expected result: 50%% dropped (h1 blocked, others work)
echo ========================================
pause
