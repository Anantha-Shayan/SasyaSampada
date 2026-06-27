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
.
├── README.md
├── docker-compose.yml
├── docs/                          # Architecture & RAG design (start here)
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── routes.py          # Active API routes
│   │   │   └── v1/endpoints/      # Planned RAG route modules
│   │   ├── core/                  # Config, logging, DI (planned)
│   │   ├── domain/schemas/        # Target Pydantic home
│   │   ├── knowledge_base/        # Catalog & path conventions (Phase 2)
│   │   ├── ingestion/             # PDF → chunks → vectors
│   │   ├── embeddings/
│   │   ├── vector_db/
│   │   ├── retrieval/
│   │   ├── rag/
│   │   ├── llm/
│   │   ├── services/
│   │   ├── ml/
│   │   ├── models/
│   │   ├── config.py
│   │   └── utils.py
│   ├── model_assets/
│   └── tests/
│       ├── unit/
│       └── integration/
├── frontend/
├── scripts/
├── data/
│   ├── raw/                       # Source PDFs
│   ├── parsed/
│   ├── processed/
│   ├── metadata/
│   ├── embeddings/
│   ├── logs/
│   ├── manifests/                 # Document catalog (source of truth)
│   └── datasets/
└── training/
```

## 📚 RAG Documentation

Production RAG system design is documented in [`docs/`](docs/README.md). **Phase 1 (System Design)** is complete; implementation follows milestone-by-milestone.

| Document | Topic |
|----------|-------|
| [01_project_overview](docs/01_project_overview.md) | Goals and scope |
| [02_architecture](docs/02_architecture.md) | Components and folders |
| [03_request_flow](docs/03_request_flow.md) | HTTP lifecycle |
| [04_data_flow](docs/04_data_flow.md) | Write/read data paths |
| [05_rag_pipeline](docs/05_rag_pipeline.md) | Query-time RAG (planned) |
| [06_ingestion_pipeline](docs/06_ingestion_pipeline.md) | Ingestion stages (planned) |
| [Knowledge Base Organization](docs/knowledge_base_organization.md) | Disk layout, versioning, dedup |
| [16_scalability](docs/16_scalability.md) | Scale-out strategy |
| [23_engineering_decisions](docs/23_engineering_decisions.md) | ADR log |

## Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend entry point is `backend/app/main.py`. API routes live in `backend/app/api/`, business logic in `backend/app/services/`, inference code in `backend/app/ml/`, request models in `backend/app/models/`, and shared configuration in `backend/app/config.py`.

Model assets are loaded from `backend/model_assets/`:

```text
cr_model.pkl
cr_scaler.pkl
cr_encoder.pkl
district_crop_map.json
crop_district_map.json
```

## Frontend

```bash
cd frontend
npm install
npm start
```

The React app expects the backend at `http://localhost:8000` unless `REACT_APP_API_URL` is set.

## Training

Training code is isolated under `training/` and is not imported by the backend at runtime.

```bash
python training/train_model.py
python training/preprocess.py
```

Generated model files and mappings are written to `backend/model_assets/`. Agricultural PDFs live in `data/raw/` with catalog metadata in `data/manifests/documents.json`. See [`data/README.md`](data/README.md) for the full knowledge-base layout. Tabular ML data remains in `data/datasets/`.

## Docker

```bash
docker compose up --build
```

Backend: `http://localhost:8000`
Frontend: `http://localhost:3000`

## Tests

```bash
cd backend
pytest
```

---


## 📈 ML Training Results

- **22 crops** learned (rice, wheat, maize, cotton, coffee, etc.)
- **Random Forest** selected as best model
- Trained on 2200 samples (100 per crop)

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