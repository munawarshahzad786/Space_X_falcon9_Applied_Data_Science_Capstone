"""
Falcon 9 Project - Data Cleaning & Wrangling (Fixed)
Author: Muhammad Munawar Shahzad
Date: 2025-08-15
Description:
This script loads the raw web-scraped Falcon 9 launch data,
cleans it, fixes numeric columns, and saves the processed version ready for analysis and dashboard.
"""

# ===============================
# Step 1: Import Required Libraries
# ===============================
import pandas as pd
from pathlib import Path
import logging
import sys
import re

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
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_RAW / "falcon9_web_scraped.csv"
OUTPUT_FILE = DATA_PROCESSED / "falcon_web_scraped_cleaned.csv"
DASHBOARD_FILE = BASE_DIR / "data" / "falcon9_launches.csv"
EDA_FILE = DATA_PROCESSED / "falcon9_cleaned_for_eda.csv"

# ===============================
# Step 4: Load Raw Data
# ===============================
try:
    df = pd.read_csv(INPUT_FILE)
    logging.info(f"📁 Raw data loaded successfully from: {INPUT_FILE}")
    logging.info(f"📊 Raw data shape: {df.shape}")
    logging.info(f"📋 Raw data columns: {list(df.columns)}")
except FileNotFoundError:
    logging.error(f"❌ File not found: {INPUT_FILE}")
    sys.exit(1)
except Exception as e:
    logging.error(f"❌ Error loading CSV: {e}")
    sys.exit(1)

# ===============================
# Step 5: Data Cleaning
# ===============================
logging.info("🔄 Cleaning data...")

# Drop duplicates
initial_rows = len(df)
df = df.drop_duplicates()
logging.info(f"🗑️ Removed {initial_rows - len(df)} duplicate rows")

# Strip column names and string values
df.columns = df.columns.str.strip()
str_cols = df.select_dtypes(include="object").columns
for col in str_cols:
    df[col] = df[col].astype(str).str.strip()

# ===============================
# Step 5a: Clean Payload Mass (Improved)
# ===============================
def extract_payload_mass(value):
    """Extract payload mass from text like '~16,800 kg (37,000 lb)' to float in kg"""
    if pd.isna(value) or value == "Unknown" or value == "nan":
        return 0.0
    
    try:
        if isinstance(value, str):
            # Look for pattern like "~16,800 kg" or "1,800 kg"
            match = re.search(r'([\d,]+)\s*kg', value)
            if match:
                # Remove commas and convert to float
                mass_str = match.group(1).replace(',', '')
                return float(mass_str)
            else:
                # Try to extract any number
                numbers = re.findall(r'[\d,]+', str(value))
                if numbers:
                    return float(numbers[0].replace(',', ''))
        return 0.0
    except:
        return 0.0

# Apply improved payload mass cleaning
if 'Payload mass' in df.columns:
    df['payload_mass_kg'] = df['Payload mass'].apply(extract_payload_mass)
    logging.info(f"⚖️ Payload mass cleaned. Range: {df['payload_mass_kg'].min():.0f} - {df['payload_mass_kg'].max():.0f} kg")
else:
    logging.warning("⚠️ No 'Payload mass' column found")

# ===============================
# Step 5b: Clean and Rename Columns
# ===============================
# Create a clean column mapping
column_mapping = {}
if 'Launch site' in df.columns:
    column_mapping['Launch site'] = 'launch_site'
if 'Launch outcome' in df.columns:
    column_mapping['Launch outcome'] = 'launch_outcome'
if 'Version, booster[i]' in df.columns:
    column_mapping['Version, booster[i]'] = 'booster_version'
if 'Date and time (UTC)' in df.columns:
    column_mapping['Date and time (UTC)'] = 'date'
if 'Flight No.' in df.columns:
    column_mapping['Flight No.'] = 'flight_number'
if 'Payload[j]' in df.columns:
    column_mapping['Payload[j]'] = 'payload'
if 'Orbit' in df.columns:
    column_mapping['Orbit'] = 'orbit'
if 'Customer' in df.columns:
    column_mapping['Customer'] = 'customer'
if 'Booster landing' in df.columns:
    column_mapping['Booster landing'] = 'booster_landing'

# Rename columns
df.rename(columns=column_mapping, inplace=True)

# ===============================
# Step 5c: Data Type Conversions
# ===============================
# Convert date column with better parsing
if 'date' in df.columns:
    def parse_date(date_str):
        """Parse date strings like 'January 3, 2024 03:44[24]' to datetime"""
        if pd.isna(date_str) or date_str == '':
            return pd.NaT
        
        try:
            # Remove citation markers like [24], [25], etc.
            clean_date = str(date_str).split('[')[0].strip()
            
            # Try different date formats
            for fmt in ['%B %d, %Y %H:%M', '%B %d, %Y', '%Y-%m-%d', '%m/%d/%Y']:
                try:
                    return pd.to_datetime(clean_date, format=fmt)
                except:
                    continue
            
            # Fallback to pandas parser
            return pd.to_datetime(clean_date, errors='coerce')
        except:
            return pd.NaT
    
    df['date'] = df['date'].apply(parse_date)
    
    # Extract year from successful dates
    df['launch_year'] = df['date'].dt.year
    
    logging.info(f"📅 Date column converted to datetime. Valid dates: {df['date'].notna().sum()}")
else:
    logging.warning("⚠️ No 'date' column found")
    df['launch_year'] = None

# Convert flight number to numeric
if 'flight_number' in df.columns:
    df['flight_number'] = pd.to_numeric(df['flight_number'], errors='coerce')
    logging.info(f"🔢 Flight number converted to numeric")

# ===============================
# Step 5d: Create Additional Features
# ===============================
# Extract launch site code (first letter of each word)
if 'launch_site' in df.columns:
    df['launch_site_code'] = df['launch_site'].apply(
        lambda x: ''.join([word[0] for word in str(x).split() if word]) if pd.notna(x) else ''
    )

# Create success flag
if 'launch_outcome' in df.columns:
    df['success_flag'] = (df['launch_outcome'] == 'Success').astype(int)

logging.info("✅ Data cleaning complete.")

# ===============================
# Step 6: Save Cleaned Data
# ===============================
# Save the main cleaned file
try:
    df.to_csv(OUTPUT_FILE, index=False)
    logging.info(f"📁 Cleaned data saved successfully to: {OUTPUT_FILE}")
except Exception as e:
    logging.error(f"❌ Failed to save cleaned CSV: {e}")
    sys.exit(1)

# Save dashboard-ready version
try:
    df.to_csv(DASHBOARD_FILE, index=False)
    logging.info(f"📁 Dashboard-ready data saved successfully to: {DASHBOARD_FILE}")
except Exception as e:
    logging.error(f"❌ Failed to save dashboard CSV: {e}")
    sys.exit(1)

# Save EDA-ready version (select only essential columns)
eda_columns = ['flight_number', 'date', 'booster_version', 'launch_site', 'payload', 
               'payload_mass_kg', 'orbit', 'customer', 'launch_outcome', 'booster_landing', 
               'launch_year', 'launch_site_code', 'success_flag']
eda_df = df[eda_columns].copy()

try:
    eda_df.to_csv(EDA_FILE, index=False)
    logging.info(f"📁 EDA-ready data saved successfully to: {EDA_FILE}")
except Exception as e:
    logging.error(f"❌ Failed to save EDA CSV: {e}")
    sys.exit(1)

# ===============================
# Step 7: Data Quality Report
# ===============================
logging.info("📊 Data Quality Report:")
logging.info(f"📈 Total rows: {len(df)}")
logging.info(f"📋 Total columns: {len(df.columns)}")
logging.info(f"🔍 Missing values per column:")
for col in df.columns:
    missing = df[col].isna().sum()
    if missing > 0:
        logging.info(f"   {col}: {missing} ({missing/len(df)*100:.1f}%)")

logging.info(f"✅ Success rate: {(df['success_flag'].sum() / len(df) * 100):.1f}%" if 'success_flag' in df.columns else "⚠️ Success rate not calculated")

# ===============================
# Step 8: Preview First 5 Rows
# ===============================
logging.info("📊 Preview of cleaned data:")
print("\n" + "="*80)
print("CLEANED DATA PREVIEW")
print("="*80)
print(df.head())
print("\n" + "="*80)
print("COLUMN SUMMARY")
print("="*80)
print(df.info())
print("\n" + "="*80)
