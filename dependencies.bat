@echo off
REM -------------------------------
REM FrameKeep Dependency Installer
REM -------------------------------

REM --- License / Source Notice ---
echo FrameKeep - (C) 2025 Tanner Lucier
echo Licensed under GPLv3 - see LICENSE file for details
echo.

REM --- Check if Python is installed ---
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is NOT installed or not in PATH.
    echo Please install Python before running this script.
    pause
    exit /b
) ELSE (
    echo Python is installed.
    echo Installing required packages...
    echo.
)

REM --- Install Python packages ---
python -m pip install pythonnet
python -m pip install opencv-python
python -m pip install numpy
python -m pip install pywin32
python -m pip install mss
python -m pip install pystray
python -m pip install pillow

echo.
echo All dependencies installed successfully.
pause
