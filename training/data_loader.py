import os
import zipfile
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi

# Load environment variables from project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(PROJECT_ROOT / ".env")

def load_kaggle_csv(dataset_slug, *filename):
    """
    Download a Kaggle dataset and return a pandas DataFrame.
    The downloaded zip is deleted after extraction.
    """
    # Set Kaggle token from environment if available
    kaggle_token = os.getenv("KAGGLE_API_TOKEN")
    if kaggle_token:
        os.environ["KAGGLE_API_TOKEN"] = kaggle_token
        print(f"✅ Using Kaggle token from .env file")
    
    api = KaggleApi()
    api.authenticate()    
    api.dataset_download_files(dataset_slug, path=RAW_DATA_DIR, quiet=True)
    
    zip_name = RAW_DATA_DIR / f"{dataset_slug.split('/')[-1]}.zip"
    
    with zipfile.ZipFile(zip_name) as z:
        # List available files in the zip
        available_files = z.namelist()
        print(f"📦 Files in archive: {available_files}")
        
        # Try to find the target file
        target_file = None
        for file in available_files:
            if file.endswith(filename[0]) or filename[0] in file:
                target_file = file
                break
        
        if not target_file and available_files:
            # Use the first CSV file if exact match not found
            csv_files = [f for f in available_files if f.endswith('.csv')]
            if csv_files:
                target_file = csv_files[0]
                print(f"ℹ️ Using file: {target_file}")
        
        if not target_file:
            raise FileNotFoundError(f"No CSV file found in archive. Available: {available_files}")
        
        with z.open(target_file) as f:
            df = pd.read_csv(f)

    zip_name.unlink()

    return df
