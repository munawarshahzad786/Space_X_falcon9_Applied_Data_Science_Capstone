"""
Falcon 9 Project - Presentation Automation
Author: Muhammad Munawar Shahzad
Date: 2025-08-14
Description:
Automatically generates summary reports and visualizations from processed Falcon 9 launch data.
"""

# ===============================
# Step 1: Import Required Libraries
# ===============================
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging

# ===============================
# Step 2: Configure logging & plotting style
# ===============================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
sns.set(style="whitegrid")

# ===============================
# Step 3: Define project paths
# ===============================
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ===============================
# Step 4: Load processed CSV
# ===============================
processed_file = DATA_DIR / "falcon_web_scraped_cleaned.csv"

if not processed_file.exists():
    logging.error(f"❌ Processed data file not found: {processed_file}")
    logging.info("💡 Make sure data collection and wrangling steps are completed first.")
    # Instead of sys.exit, we just stop running the rest
    raise FileNotFoundError(f"Processed data file not found: {processed_file}")

df = pd.read_csv(processed_file)
logging.info(f"✅ Data loaded from: {processed_file}")
logging.info(f"📊 Dataset shape: {df.shape}")

# ===============================
# Step 5: Check and prepare essential columns
# ===============================
essential_cols = ['Date', 'Outcome', 'Version']
for col in essential_cols:
    if col not in df.columns:
        logging.warning(f"⚠️ Column '{col}' missing. Some plots may be skipped.")
        df[col] = None  # Fill missing columns to avoid crashes

# Convert Date column to datetime and add Year
if df['Date'].notnull().any():
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df['Date'].dt.year
else:
    logging.warning("⚠️ 'Date' column is empty or invalid. Skipping year-based plots.")
    df['Year'] = None

# ===============================
# Step 6: Save summary statistics
# ===============================
summary_file = REPORTS_DIR / "data_summary.csv"
summary = df.describe(include='all')
summary.to_csv(summary_file)
logging.info(f"📄 Summary report saved at: {summary_file}")

# ===============================
# Step 7: Plot launches per year
# ===============================
if df['Year'].notnull().any():
    launches_per_year = df.groupby('Year').size().reset_index(name='Launches')
    plt.figure(figsize=(10, 6))
    sns.barplot(data=launches_per_year, x='Year', y='Launches', palette='viridis')
    plt.title("Falcon 9 Launches Per Year")
    plt.xticks(rotation=45)
    plt.tight_layout()
    launches_per_year_file = FIGURES_DIR / "launches_per_year.png"
    plt.savefig(launches_per_year_file)
    plt.close()
    logging.info(f"📈 Saved: {launches_per_year_file}")
else:
    logging.warning("⚠️ Skipping launches per year plot due to missing 'Year' data.")

# ===============================
# Step 8: Plot launch outcomes
# ===============================
if df['Outcome'].notnull().any():
    outcome_counts = df['Outcome'].value_counts()
    plt.figure(figsize=(8, 6))
    sns.barplot(x=outcome_counts.index, y=outcome_counts.values, palette='pastel')
    plt.title("Launch Outcomes")
    plt.ylabel("Number of Launches")
    plt.xticks(rotation=45)
    plt.tight_layout()
    outcomes_file = FIGURES_DIR / "launch_outcomes.png"
    plt.savefig(outcomes_file)
    plt.close()
    logging.info(f"📊 Saved: {outcomes_file}")
else:
    logging.warning("⚠️ Skipping launch outcomes plot due to missing 'Outcome' data.")

# ===============================
# Step 9: Plot booster version usage
# ===============================
if df['Version'].notnull().any():
    booster_counts = df['Version'].value_counts()
    plt.figure(figsize=(10, 6))
    sns.barplot(x=booster_counts.index, y=booster_counts.values, palette='magma')
    plt.title("Booster Version Usage Frequency")
    plt.ylabel("Number of Launches")
    plt.xticks(rotation=45)
    plt.tight_layout()
    booster_usage_file = FIGURES_DIR / "booster_usage.png"
    plt.savefig(booster_usage_file)
    plt.close()
    logging.info(f"🚀 Saved: {booster_usage_file}")

    booster_report_file = REPORTS_DIR / "booster_report.csv"
    booster_report = df.groupby('Version').size().reset_index(name='Launch Count')
    booster_report.to_csv(booster_report_file, index=False)
    logging.info(f"📄 Booster report saved at: {booster_report_file}")
else:
    logging.warning("⚠️ Skipping booster usage plot due to missing 'Version' data.")

logging.info("✅ All visuals and reports generated successfully!")
