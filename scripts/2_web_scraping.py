"""
Falcon 9 Project - Web Scraping (Fixed)
Author: Muhammad Munawar Shahzad
Date: 2025-08-15
Description:
This script scrapes Falcon 9 launch data from Wikipedia,
saves it as a raw CSV file, and provides a log of the process.
"""

# ===============================
# Step 1: Import Required Libraries
# ===============================
import requests
from bs4 import BeautifulSoup
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
# Step 3: Define Paths
# ===============================
BASE_DIR = Path(__file__).parent.parent  # Project root
DATA_RAW = BASE_DIR / "data" / "raw"    # Raw data folder
DATA_RAW.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = DATA_RAW / "falcon9_web_scraped.csv"

# ===============================
# Step 4: Scrape SpaceX Launches Table
# ===============================
URL = "https://en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches"

logging.info(f"🔄 Fetching data from {URL}...")
try:
    res = requests.get(URL)
    res.raise_for_status()
except requests.exceptions.RequestException as e:
    logging.error(f"❌ Failed to fetch the webpage: {e}")
    sys.exit(1)

logging.info("✅ Webpage fetched successfully. Parsing HTML...")

soup = BeautifulSoup(res.text, "lxml")
tables = soup.find_all("table", {"class": "wikitable"})

if not tables:
    logging.error("❌ No tables found on the webpage.")
    sys.exit(1)

try:
    # Find the main launches table (usually the first one)
    main_table = None
    for table in tables:
        # Look for table with flight numbers
        if table.find("th", string=lambda x: x and "Flight No." in x):
            main_table = table
            break
    
    if not main_table:
        main_table = tables[0]  # Fallback to first table
    
    # Extract table data
    df = pd.read_html(str(main_table))[0]
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Remove any completely empty rows
    df = df.dropna(how='all')
    
    # Remove any rows where all values are the same (corrupted data)
    df = df[~(df.apply(lambda x: x == x.iloc[0], axis=1).all(axis=1))]
    
    logging.info(f"✅ Table parsed successfully. Shape: {df.shape}")
    
except ValueError as e:
    logging.error(f"❌ Failed to parse HTML table: {e}")
    sys.exit(1)

# ===============================
# Step 5: Save Scraped Data
# ===============================
try:
    df.to_csv(OUTPUT_FILE, index=False)
    logging.info(f"📁 Web-scraped data saved successfully to: {OUTPUT_FILE}")
except Exception as e:
    logging.error(f"❌ Failed to save CSV: {e}")
    sys.exit(1)

# ===============================
# Step 6: Preview First 5 Rows
# ===============================
logging.info("📊 Preview of scraped data:")
print(df.head())
print(f"\nData shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
