#!/usr/bin/env python3
"""
Check the status of your Agrigrow application
"""
import requests
import time

def check_frontend():
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_backend():
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🔍 Checking Agrigrow Application Status...")
    print("=" * 50)
    
    # Check Frontend
    print("📱 React Frontend (Port 3000):", end=" ")
    if check_frontend():
        print("✅ Running")
    else:
        print("❌ Not Running")
    
    # Check Backend
    print("🔧 FastAPI Backend (Port 8000):", end=" ")
    if check_backend():
        print("✅ Running")
    else:
        print("❌ Not Running")
    
    print("=" * 50)
    
    if check_frontend() and check_backend():
        print("🎉 Your Agrigrow app is fully operational!")
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 Backend: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
    else:
        print("⚠️ Some services are not running.")
        print("💡 Run 'start-app.bat' to start both servers.")

if __name__ == "__main__":
    main()
