# 🌿 SasyaSampada - Farmer's Friend

![Python](https://img.shields.io/badge/Python-blue)
![LangChain](https://img.shields.io/badge/LangChain-blue)
![Hugging Face](https://img.shields.io/badge/Hugging%20Face-yellow)
![Machine Learning](https://img.shields.io/badge/Scikit%20Learn-orange)
![React](https://img.shields.io/badge/React-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-green)


SasyaSampada aims to provide a comprehensive AI-driven agricultural advisory system for farmers. It leverages Machine Learning, Natural Language Processing, and Computer Vision to assist farmers in crop recommendation, financial literacy, pest detection, and real-time decision support through a conversational AI chatbot

---

## ✨ Features

- **🌱 Crop Recommendation** - AI-powered crop recommendation system based on soil type, weather, and regional patterns.
- **🤖 AI Chatbot** - Conversational chatbot in local language with retrieval-augmented generation using FAISS and HuggingFace LLMs.
- **📸 Pest Detection** (Yet to be added) - Planned integration of pest detection using Convolutional Neural Networks (CNNs).  
- **💻 Full-Stack Application** – React frontend + FastAPI backend + ML model integration  
- **📱 Mobile-First Design** – Responsive interface optimized for smartphones  
- **🚨 Note** – Some features like live AI assistance may require API keys or local ML models to function fully.

---

## 🏗️ Project Structure

```text
sasyasampada/
├── src/                        # React frontend
│   ├── components/             # Reusable UI components
│   ├── pages/                  # Page-level components
│   ├── context/                # Global state management
│   ├── services/               # API service layer
│   └── App.js                  # Root app
├── backend/                    # FastAPI backend
│   ├── main.py                 # Backend API entrypoint
│   ├── plant_api.py            # Plant-related endpoints
│   ├── chat_api.py             # AI chatbot endpoints
│   ├── ml_integration.py       # ML model inference utilities
│   └── requirements.txt        # Python dependencies
├── ml-model/                   # Machine learning models and scripts
│   ├── crop_recommendation.py  # ML model for crop recommendations
│   ├── unified_advice.py       # Core advisory logic
│   ├── langchain_integration.py # AI chat integration
│   └── *.pkl                   # Trained ML models
├── public/                     # Static frontend assets
└── data/                       # Sample datasets / images
````

## 📚 ml-model Directory Breakdown

1. **`crop_recommendation.py`**  
   This script is responsible for training and evaluating the machine learning model that provides crop recommendations based on soil parameters and climatic conditions. It utilizes datasets containing information about various crops and their suitability to different regions.

2. **`unified_advice.py`**  
   This module integrates the outputs of the crop recommendation model with additional data sources, such as weather forecasts and market prices, to generate comprehensive advisory reports for farmers. It aims to provide actionable insights that consider multiple factors influencing crop selection.

3. **`langchain_integration.py`**  
   This script facilitates the integration of the LangChain framework with Retrieval Augmented Generation (RAG) that retrieves information from external government websites and relevent youtube transcripts
   with the backend FastAPI application that is used to build the AI-powered chatbot that assists users by answering agricultural queries and providing personalized advice based on the trained models.

5. **`*.pkl` (Trained Model Files)**  
   These are serialized machine learning models saved in the pickle format. They include:
   - The crop recommendation model trained on historical agricultural data.
   - StandardScaler and OneHotEncoder

---

## 🚀 Quick Start

### Prerequisites
- [Node.js](https://nodejs.org/) v16+
- [Python](https://www.python.org/downloads/) 3.8+
- [Git](https://git-scm.com/)

---

### 1. Clone the Repository
```bash
git clone "https://github.com/Anantha-Shayan/SasyaSampada.git"
cd SasyaSampada
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
cp .env.example .env
```

Example values in `.env`:

```properties
REACT_APP_API_URL=http://localhost:8000
BACKEND_PORT=8000
OPENWEATHER_API_KEY=your_openweather_api_key_here
MANDI_PRICE_KEY=your_mandi_price_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
KAGGLE_API_TOKEN=your_kaggle_api_token_here
```

---

### 4. Run the Application

Open two terminals for the services:

#### A. Backend (FastAPI)

```bash
cd backend
python main.py
```

#### B. Frontend (React)

```bash
cd frontend
PATH="/home/anantha/Projects/SasyaSampada/frontend/.venv/bin:$PATH" npm start
```

If you want the optional chatbot service too, run:

```bash
cd backend
python main_fresh.py
```

---

## 📱 Application Pages

### 🏠 Dashboard

* Weather overview
* Quick advisory cards
* Real-time mandi prices
* AI chatbot interface

### 🌱 Crop Advisory

* Input soil parameters (N, P, K, pH, rainfall, etc.) manually or by uploading Soil Card
* ML-powered crop recommendations
* Weather validation
* Market price integration

### 🌤️ Weather

* Current conditions
* 5-day forecast
* Risk alerts (frost, heat stress)

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
- **OpenRouter (Google Gemini) OR Hugging Face models** – LLM-powered chatbot responses  
                        

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
