"""
Falcon 9 Project - Data Collection via API
Author: Muhammad Munawar Shahzad
Date: 2025-08-13
Description:
This script fetches Falcon 9 launch data from the SpaceX API,
saves it as a raw CSV file, and provides a preview of the data.
"""

# ===============================
# Step 1: Import Required Libraries
# ===============================
import requests
import pandas as pd
from pathlib import Path
import logging
import sys

# ===============================
# Step 2: Setup Logging
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ===============================
# Step 3: Define Paths and API URL
# ===============================
BASE_DIR = Path(__file__).parent.parent  # Project root
DATA_DIR = BASE_DIR / "data"             # Data folder path
RAW_FILE = DATA_DIR / "falcon9_launches_raw.csv"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

API_URL = "https://api.spacexdata.com/v4/launches"
PARAMS = {}  # Optional API parameters

# ===============================
# Step 4: Send GET Request to API
# ===============================
logging.info("🔄 Fetching data from SpaceX API...")
try:
    response = requests.get(API_URL, params=PARAMS)
    response.raise_for_status()
    logging.info("✅ API request successful!")
except requests.exceptions.RequestException as e:
    logging.error(f"❌ API request failed: {e}")
    sys.exit(1)

# ===============================
# Step 5: Convert JSON Data to DataFrame
# ===============================
try:
    data = response.json()
    df = pd.DataFrame(data)
except ValueError as e:
    logging.error(f"❌ Failed to parse JSON data: {e}")
    sys.exit(1)

# ===============================
# Step 6: Save Raw Data to CSV
# ===============================
try:
    df.to_csv(RAW_FILE, index=False, encoding="utf-8")
    logging.info(f"📁 Raw data saved successfully to: {RAW_FILE}")
except Exception as e:
    logging.error(f"❌ Failed to save CSV: {e}")
    sys.exit(1)

# ===============================
# Step 7: Preview First 5 Rows
# ===============================
logging.info("📊 Preview of fetched data:")
print(df.head())
