@echo off
:: VedicRecon Framework - Windows Setup Utility
:: Version: 1.0.0-alpha

echo --- [ VedicRecon Setup: Windows ] ---

:: 1. Check for Admin Privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [+] Administrative permissions confirmed.
) else (
    echo [!] Please run this script as Administrator.
    pause
    exit /b 1
)

:: important creation of reports and output directory
md "output" "reports"
:: 2. Check for Go and Python
where go >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Go is not installed. Please install from https://go.dev/dl/
    pause
    exit /b 1
)

:: 3. Setup Python Environment
echo [*] Setting up Python virtual environment...
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install pandas requests google-generativeai python-dotenv

:: 4. Compile Go Muscle
echo [*] Compiling Go core binaries for Windows...
if not exist "bin" mkdir bin
cd core
go build -o ../bin/vr_core_win.exe .
cd ..

:: 5. Initialize Directory Structure
echo [*] Creating workspace folders...
if not exist "output" mkdir output
if not exist "reports" mkdir reports
if not exist ".runtime_integrity" mkdir .runtime_integrity

echo --------------------------------------------------
echo [+] Setup Complete! 
echo [+] To start: call venv\Scripts\activate ^& python main.py
echo --------------------------------------------------
pause