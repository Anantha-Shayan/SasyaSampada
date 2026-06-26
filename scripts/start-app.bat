@echo off
echo 🌱 Starting Agrigrow Full-Stack Application...

echo.
echo 📦 Starting React Frontend...
start "React Frontend" cmd /k "cd frontend && npm start"

echo.
echo 🤖 Starting ML-Integrated Backend...
start "ML Backend" cmd /k "cd backend && uvicorn app.main:app --reload"

echo.
echo ✅ Both servers are starting...
echo 📱 Frontend will be available at: http://localhost:3000
echo 🔧 Backend will be available at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs

echo.
echo 🎉 Your Agrigrow app is starting up!
echo 💡 Close the terminal windows to stop the servers.

pause
