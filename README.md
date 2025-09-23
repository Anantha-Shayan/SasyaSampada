# 🌾 Agrigrow - Smart Crop Advisory System

Agrigrow is a **full-stack React + FastAPI application** that empowers farmers with intelligent crop recommendations, weather forecasts, market price insights, pest detection, and an AI-powered agricultural assistant.

## ✨ Features

- **🌱 Smart Crop Recommendations** – ML-powered suggestions based on soil and location data
- **🌤️ Weather Integration** – Real-time weather validation for crop suitability
- **💰 Market Price Analysis** – Current mandi prices for profitable crop decisions
- **🐛 Pest Detection** – AI-powered pest identification from images
- **🤖 AI Chat Assistant** – LangChain-powered chatbot for agricultural queries
- **📱 Mobile-First Design** – Responsive interface optimized for smartphones
- **🚨 NOTE : There is an one live link but it is just the 50% and the frontend UI part so you can just take mobile view feel to know how it will look but bakcend is yet not functioning**

---

## 🏗️ Project Structure

```

agrigrow-app/
├── src/                        # React frontend
│   ├── components/             # Reusable UI components
│   ├── pages/                  # Page-level components
│   ├── context/                # Global state management
│   ├── services/               # API service layer
│   └── App.js                  # Root app
├── backend/                    # FastAPI backend
│   ├── main.py                 # FastAPI application entrypoint
│   ├── main\_fresh.py           # Chatbot API service
│   ├── langchain\_integration.py# AI chat integration
│   └── requirements.txt        # Python dependencies
├── ml-model/                   # ML models and scripts
│   ├── unified\_advice.py       # Core advisory logic
│   ├── crop\_recommendation.py  # ML training pipeline
│   └── \*.pkl                   # Trained models
└── public/                     # Static frontend assets

````

---

## 🚀 Quick Start

### Prerequisites
- [Node.js](https://nodejs.org/) v16+
- [Python](https://www.python.org/downloads/) 3.8+
- [Git](https://git-scm.com/)

---

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/agrigrow.git
cd agrigrow
````

---

### 2. Install Dependencies

#### Frontend

```bash
npm install
```

#### Backend

```bash
cd backend
pip install -r requirements.txt
```

---

### 3. Set Up Environment Variables

Copy the example file and update with your API keys:

```bash
cp env.example .env
```

`.env` file example:

```properties
REACT_APP_API_URL=http://localhost:8000
OPENWEATHER_API_KEY=your_openweather_api_key
MANDI_PRICE_KEY=your_mandi_price_api_key
HUGGINGFACEHUB_API_KEY=your_huggingface_api_key
```

---

### 4. Run the Application

Open **three terminals** for the services:

#### A. Frontend (React)

```bash
npm start
```

Runs on [http://localhost:3000](http://localhost:3000)

#### B. Backend (FastAPI - main APIs)

```bash
cd backend
python main.py
```

Runs on [http://localhost:8000](http://localhost:8000)
API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

#### C. Chatbot API Service

```bash
cd backend
python main_fresh.py
```
**🚨NOTE: might the chatbot will not work is will display - user not found / 401 beacuse of the API is broke or lost because the Key has been also commited along with the code that will be reason else its working just need to change the key.**

Runs on [http://localhost:8001](http://localhost:8001)

---

## 📱 Application Pages

### 🏠 Dashboard

* Weather overview
* Quick advisory cards
* Real-time mandi prices
* AI chatbot interface

### 🌱 Crop Advisory

* Input soil parameters (N, P, K, pH, rainfall, etc.)
* ML-powered crop recommendations
* Weather validation
* Market price integration

### 🌤️ Weather

* Current conditions
* 5-day forecast
* Risk alerts (frost, heat stress)
* Spray suitability checks

### 💰 Market Prices

* Real-time mandi price feed
* Price trends & crop search

### 🐛 Pest Detection

* Upload pest images
* AI-based detection & treatment suggestions

---

## 🔧 API Endpoints

### Advisory

* `POST /api/advisory` → Get crop recommendations

### Weather

* `POST /api/weather` → Fetch weather data

### Market

* `POST /api/market-prices` → Get mandi price data

### Chat

* `POST /api/chat` → Chat with AI assistant

### Data

* `GET /api/crops` → List all crops
* `GET /api/districts` → List all districts
* `GET /api/district-crops/{state}/{district}` → Crops by district

---

## 🤖 ML Integration

Agrigrow uses multiple ML workflows:

1. **Crop Recommendation Model** – trained on soil & weather datasets
2. **Weather Validation** – cross-checks recommendations against live weather
3. **Location Suitability** – validates crops against district-level data
4. **Market Optimization** – ranks crops by price advantage

---

## 📊 Data Sources

- **Kaggle** – Crop recommendation datasets  
- **ICRISAT** – District-level agriculture data  
- **OpenWeatherMap** – Real-time weather API  
- **Agmarknet / Govt APIs** – Market price data  
- **OpenRouter (Google Gemini)** – LLM-powered chatbot responses  


---

## 🛠️ Development

Frontend:

```bash
npm start          # Dev server
npm run build      # Build for production
npm test           # Run tests
```

Backend:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

ML Model Training:

```bash
cd ml-model
python crop_recommendation.py
```

---

## 📱 Mobile-First Design

* Tailwind CSS responsive layout
* Touch-friendly UI
* Optimized for small screens
* PWA ready

---

## 🔐 Environment Variables

| Variable                 | Description          | Required |
| ------------------------ | -------------------- | -------- |
| `REACT_APP_API_URL`      | Backend API base URL | ✅        |
| `OPENWEATHER_API_KEY`    | Weather data API key | ✅        |
| `MANDI_PRICE_KEY`        | Market price API key | ✅        |
| `HUGGINGFACEHUB_API_KEY` | Hugging Face token   | Optional |

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

---

## 📄 License

MIT License © Agrigrow Team

