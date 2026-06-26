# Dockerfile for SasyaSampada backend
FROM python:3.14-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend files and requirements
COPY backend/requirements.txt ./requirements.txt
COPY backend/requirements-simple.txt ./requirements-simple.txt
COPY backend/ .
COPY ../ml-model/ ./ml-model/

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose backend port
EXPOSE 8000

ENV BACKEND_PORT=8000
ENV OPENWEATHER_API_KEY=
ENV MANDI_PRICE_KEY=
ENV OPENROUTER_API_KEY=
ENV KAGGLE_API_TOKEN=

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
