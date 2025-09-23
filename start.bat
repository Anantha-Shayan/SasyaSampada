@echo off
echo 🌱 Starting Agrigrow Application...

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ first.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Install React dependencies if node_modules doesn't exist
cd frontend
if not exist "node_modules" (
    echo �� Installing React dependencies...
    npm install
)

REM Install Python dependencies if not installed
if not exist "node_modules" (
    echo 📦 Installing React dependencies...
    npm install
)

REM Install Python dependencies if not installed
if not exist "backend\venv" (
    echo 🐍 Setting up Python virtual environment...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    cd ..
)

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating environment file...
    copy env.example .env
    echo ⚠️  Please edit .env file with your API keys before running the application.
)

echo ✅ Setup complete!
echo.
echo 🚀 To start the application:
echo 1. Edit .env file with your API keys
echo 2. Run: npm start (for React frontend)
echo 3. Run: cd backend ^&^& python main.py (for FastAPI backend)
echo.
echo 📱 Frontend will be available at: http://localhost:3000
echo 🔧 Backend API will be available at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
pause
