@echo off
REM --- Make sure Python is installed and added to PATH ---

REM Upgrade pip
python -m ensurepip --upgrade
python -m pip install --upgrade pip

REM Install required packages
python -m pip install pythonnet
python -m pip install opencv-python
python -m pip install numpy
python -m pip install pywin32
python -m pip install mss
python -m pip install pystray pillow

pause
