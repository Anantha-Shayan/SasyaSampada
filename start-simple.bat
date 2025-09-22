@echo off
echo 🌱 Starting Agrigrow Application (Simple Version)...

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
    echo 📦 Installing React dependencies...
    npm install
)

REM Install Python dependencies with simple requirements
echo 🐍 Installing Python dependencies (simple version)...
cd backend
pip install -r requirements-simple.txt
cd ..

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating environment file...
    echo REACT_APP_API_URL=http://localhost:8000 > .env
    echo OPENWEATHER_API_KEY=your_openweather_api_key_here >> .env
    echo MANDI_PRICE_KEY=your_mandi_price_api_key_here >> .env
    echo HUGGINGFACEHUB_API_KEY=your_huggingface_api_key_here >> .env
    echo HF_REPO=tiiuae/falcon-7b-instruct >> .env
    echo ⚠️  Please edit .env file with your API keys before running the application.
)

echo ✅ Setup complete!
echo.
echo 🚀 To start the application:
echo 1. Edit .env file with your API keys (optional for demo)
echo 2. Run: npm start (for React frontend)
echo 3. Run: cd backend ^&^& python main-simple.py (for FastAPI backend)
echo.
echo 📱 Frontend will be available at: http://localhost:3000
echo 🔧 Backend API will be available at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo.
echo 💡 This is a simplified version that works without ML models for demo purposes.
pause
