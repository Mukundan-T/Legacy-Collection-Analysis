@echo off
REM ===============================================
REM Run Python script from CMD
REM Author: Mukundan Thanigaivelan
REM ===============================================

REM Optional: Set project root (script directory)
set "APP_DIR=%~dp0"
@REM set "ROOT_DIR=%APP_DIR%.." changed below
for %%i in ("%APP_DIR%\..") do set "ROOT_DIR=%%~fi"

REM Path to .venv
set "VENV_DIR=%ROOT_DIR%\.venv"

REM Activate the virtual environment (commented)
@REM call "%VENV_DIR%\Scripts\activate.bat"

REM Run the Python script (changed from python)
"%VENV_DIR%\Scripts\python.exe" "%APP_DIR%\src\main.py"