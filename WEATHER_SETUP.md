# Weather System Setup Guide

This guide will help you set up the weather functionality in Agrigrow.

## 🔧 Quick Fix Summary

The weather system was not working because:

1. **Static Data**: Weather page was using hardcoded data instead of API calls
2. **Missing API Key**: OpenWeather API key was not properly configured
3. **Path Issues**: Backend couldn't find ML model files
4. **No API Integration**: Frontend wasn't calling the weather API

## ✅ What Was Fixed

### 1. Frontend Weather Page (`src/pages/Weather.js`)
- ✅ Added real API integration with `weatherAPI.getWeather()`
- ✅ Dynamic weather data updates based on location
- ✅ Loading states and error handling
- ✅ Location search functionality
- ✅ Dynamic weather alerts based on conditions
- ✅ Dynamic forecast generation

### 2. Backend API (`backend/main.py`)
- ✅ Fixed ML model path resolution
- ✅ Added proper environment variable loading
- ✅ Better error handling for missing API keys
- ✅ Fallback to mock data when API fails

### 3. ML Model (`ml-model/unified_advice.py`)
- ✅ Fixed file path issues for model loading
- ✅ Proper path resolution for JSON files

### 4. Environment Configuration (`.env`)
- ✅ Fixed API key placeholder values
- ✅ Added proper configuration structure

## 🚀 Setup Instructions

### Step 1: Get OpenWeather API Key

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Get your API key from the dashboard

### Step 2: Configure Environment

Edit your `.env` file:

```bash
# Replace with your actual API key
OPENWEATHER_API_KEY=your_actual_api_key_here
REACT_APP_API_URL=http://localhost:8000
```

### Step 3: Install Dependencies

```bash
# Frontend dependencies
npm install

# Backend dependencies
cd backend
pip install -r requirements.txt
```

### Step 4: Start the Application

```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend
npm start
```

### Step 5: Test the Weather System

```bash
# Run the test script
python test-weather.py
```

## 🧪 Testing

The weather system now includes:

1. **Location Detection**: Automatically detects location (defaults to Bangalore)
2. **Search Functionality**: Type a city name and press Enter or click search
3. **Real-time Data**: Fetches actual weather data from OpenWeather API
4. **Dynamic Alerts**: Generates alerts based on weather conditions:
   - Frost alerts for low temperatures
   - Heat stress warnings for high temperatures
   - High humidity warnings
   - Rainfall alerts
   - Optimal spraying conditions

5. **Fallback System**: Uses mock data when API is unavailable

## 🔍 How It Works Now

1. **User opens Weather page** → Location is auto-detected
2. **API call is made** → `weatherAPI.getWeather(city)` calls backend
3. **Backend processes** → Calls ML model's `get_weather()` function
4. **OpenWeather API** → Fetches real weather data
5. **Data is processed** → Temperature, humidity, rainfall extracted
6. **Frontend updates** → Weather display, forecast, and alerts update
7. **Dynamic content** → Alerts and tips based on actual conditions

## 🐛 Troubleshooting

### Weather not updating?
- Check if backend is running on `http://localhost:8000`
- Verify API key is set correctly in `.env`
- Check browser console for errors

### API errors?
- Verify your OpenWeather API key is valid
- Check if you've exceeded the free tier limits
- Ensure internet connection is working

### ML models not loading?
- Check if all `.pkl` files exist in `ml-model/` directory
- Verify file permissions
- Check backend console for import errors

## 📱 Features Now Working

- ✅ Real-time weather data
- ✅ Location-based weather
- ✅ Search functionality
- ✅ Dynamic weather icons
- ✅ Smart alerts and recommendations
- ✅ 5-day forecast (generated)
- ✅ Loading states
- ✅ Error handling
- ✅ Fallback to mock data

The weather system is now fully integrated and should work seamlessly with the rest of the Agrigrow application!
