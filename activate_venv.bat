@echo off
echo Activating Python virtual environment...

REM Set variables
set VENV_NAME=venv
set PROJ_ROOT=%~dp0

REM Check if virtual environment exists
if not exist "%PROJ_ROOT%\%VENV_NAME%" (
    echo Virtual environment not found at %PROJ_ROOT%\%VENV_NAME%
    echo Please create it first using create_venv.bat
    exit /b 1
)

REM Activate the virtual environment
call "%PROJ_ROOT%\%VENV_NAME%\Scripts\activate.bat"
if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment
    exit /b 1
)

echo Virtual environment activated successfully
echo.
echo You can now run Python commands with the virtual environment
echo To deactivate, type 'deactivate'

REM Keep the command prompt open with the activated environment
cmd /k