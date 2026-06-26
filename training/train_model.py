#!/usr/bin/env python3
"""
Train the crop recommendation model and save .pkl files.
Run this once to generate cr_model.pkl, cr_scaler.pkl, and cr_encoder.pkl
"""

import sys
from pathlib import Path
import os

# Add parent directory to path to access .env
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAINING_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TRAINING_DIR))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / '.env')

print("🌱 Starting Crop Recommendation Model Training...")
print(f"📁 Project root: {PROJECT_ROOT}")
print(f"🔑 Kaggle token found: {bool(os.getenv('KAGGLE_API_TOKEN'))}")
print()

# Now run the training
try:
    import crop_recommendation
    print("\n✅ Model training completed!")
    print("📦 Generated files:")
    print("   - backend/model_assets/cr_model.pkl (trained model)")
    print("   - backend/model_assets/cr_scaler.pkl (feature scaler)")
    print("   - backend/model_assets/cr_encoder.pkl (label encoder)")
except Exception as e:
    print(f"❌ Training failed: {e}")
    sys.exit(1)
