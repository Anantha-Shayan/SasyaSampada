# 🚀 Quick Start Guide - Agrigrow React App

## Option 1: Simple Setup (Recommended for Demo)

### 1. Install React Dependencies
```bash
npm install
```

### 2. Install Python Dependencies (Simple Version)
```bash
cd backend
pip install -r requirements-simple.txt
cd ..
```

### 3. Start the Application
```bash
# Terminal 1: Start React frontend
npm start

# Terminal 2: Start FastAPI backend (simple version)
cd backend
python main-simple.py
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Option 2: Full Setup (With ML Models)

### 1. Install React Dependencies
```bash
npm install
```

### 2. Install Python Dependencies (Full Version)
```bash
cd backend
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
cd ..
```

### 3. Set up Environment Variables
```bash
# Create .env file
echo REACT_APP_API_URL=http://localhost:8000 > .env
echo OPENWEATHER_API_KEY=your_api_key_here >> .env
echo MANDI_PRICE_KEY=your_api_key_here >> .env
echo HUGGINGFACEHUB_API_KEY=your_api_key_here >> .env
```

### 4. Start the Application
```bash
# Terminal 1: Start React frontend
npm start

# Terminal 2: Start FastAPI backend (full version)
cd backend
python main.py
```

## 🎯 What You'll Get

### ✅ Working Features (Simple Version)
- **React Frontend**: All 5 pages with mobile-first design
- **API Integration**: Mock data for demonstration
- **Crop Recommendations**: Basic logic-based recommendations
- **Weather Display**: Mock weather data
- **Market Prices**: Sample market prices
- **Chat Interface**: Simple keyword-based responses

### ✅ Working Features (Full Version)
- **ML Integration**: Real crop recommendation models
- **Weather API**: Real weather data from OpenWeatherMap
- **Market API**: Real market prices from Agmarknet
- **AI Chat**: LangChain-powered agricultural assistant
- **Data Processing**: ICRISAT district crop mapping

## 🐛 Troubleshooting

### Python Installation Issues
If you get Python dependency errors:

1. **Use Simple Version**: Run `python main-simple.py` instead of `main.py`
2. **Update pip**: `pip install --upgrade pip setuptools wheel`
3. **Use virtual environment**: 
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements-simple.txt
   ```

### Node.js Issues
If React doesn't start:

1. **Clear cache**: `npm cache clean --force`
2. **Delete node_modules**: `rm -rf node_modules` (or delete folder)
3. **Reinstall**: `npm install`

### Port Issues
If ports 3000 or 8000 are busy:

1. **Kill processes**: 
   ```bash
   # Windows
   netstat -ano | findstr :3000
   taskkill /PID <PID> /F
   ```
2. **Use different ports**: 
   ```bash
   # React
   set PORT=3001 && npm start
   
   # FastAPI
   uvicorn main:app --port 8001
   ```

## 📱 Testing the App

### 1. Home Page
- Weather display
- Quick advisory cards
- Mandi prices ticker

### 2. Advisory Page
- Fill soil parameters
- Submit form
- View recommendations

### 3. Weather Page
- Weather forecast
- Risk alerts
- Spraying conditions

### 4. Market Page
- Crop prices
- Search functionality
- Price trends

### 5. Pest Detection
- Image upload interface
- Detection results
- Treatment recommendations

## 🔧 Development Tips

### Frontend Development
```bash
npm start          # Start development server
npm run build      # Build for production
npm test           # Run tests
```

### Backend Development
```bash
cd backend
python main-simple.py     # Simple version
python main.py            # Full version with ML
uvicorn main:app --reload # Development with auto-reload
```

### API Testing
- Visit http://localhost:8000/docs for interactive API documentation
- Use Postman or curl to test endpoints
- Check browser console for API errors

## 🎨 Customization

### Styling
- Edit `src/index.css` for global styles
- Modify Tailwind config in `tailwind.config.js`
- Update component styles in individual files

### API Integration
- Modify `src/services/api.js` for API calls
- Update backend endpoints in `backend/main.py`
- Add new features in respective page components

## 📞 Support

If you encounter issues:
1. Check the console for error messages
2. Verify all dependencies are installed
3. Ensure ports 3000 and 8000 are available
4. Try the simple version first, then upgrade to full version

Happy farming! 🌱
