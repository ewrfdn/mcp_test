@echo off
echo Creating Python virtual environment...

REM Set variables
set VENV_NAME=venv
set PROJ_ROOT=%~dp0

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python and try again
    exit /b 1
)

REM Check if virtual environment already exists
if exist "%PROJ_ROOT%\%VENV_NAME%" (
    echo Virtual environment already exists at %PROJ_ROOT%\%VENV_NAME%
    echo To recreate it, please delete the existing one first
    exit /b 0
)

REM Create virtual environment
echo Creating virtual environment in %PROJ_ROOT%\%VENV_NAME%
python -m venv "%PROJ_ROOT%\%VENV_NAME%"
if %ERRORLEVEL% neq 0 (
    echo Failed to create virtual environment
    exit /b 1
)

REM Activate the virtual environment and install requirements
echo Activating virtual environment and installing dependencies...
call "%PROJ_ROOT%\%VENV_NAME%\Scripts\activate.bat"
pip install -r "%PROJ_ROOT%\requirements.txt"

echo Virtual environment created and dependencies installed successfully
echo.
echo You can activate it again in the future by running:
echo %PROJ_ROOT%\%VENV_NAME%\Scripts\activate.bat
echo.

exit /b 0