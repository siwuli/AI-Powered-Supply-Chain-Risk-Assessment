@echo off
:: Force path to current directory
cd /d "%~dp0"

echo ==========================================
echo       SYSTEM STARTUP (SAFE MODE)
echo ==========================================
echo.

:: 1. Check Python
echo [1/4] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! 
    echo Please install Python and check "Add to PATH".
    pause
    exit
)

:: 2. Check Node.js
echo [2/4] Checking Node.js...
call node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found!
    echo Please install Node.js from nodejs.org
    pause
    exit
)

:: 3. Setup Backend
echo.
echo [3/4] Starting Backend...
if not exist "backend" (
    echo [ERROR] Folder 'backend' missing!
    pause
    exit
)
cd backend
if not exist venv (
    echo Creating venv...
    python -m venv venv
)
echo Installing libraries...
:: Use python -m pip to avoid path issues
call venv\Scripts\activate
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
start "Backend_Server" cmd /k "python main.py"
cd ..

:: 4. Setup Frontend
echo.
echo [4/4] Starting Frontend...
if not exist "frontend" (
    echo [ERROR] Folder 'frontend' missing!
    pause
    exit
)
cd frontend
echo Installing frontend dependencies (Vite)...
:: Force install to fix missing vite
call npm install --registry=https://registry.npmmirror.com
start "Frontend_UI" cmd /k "npm run dev"
cd ..

:: 5. Finish
echo.
echo ==========================================
echo       DONE! Opening Browser...
echo ==========================================
timeout /t 5 >nul
start http://localhost:5173

pause