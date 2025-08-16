# 6_python_run_all.py (Updated)
# Purpose: Run all Falcon 9 project scripts sequentially with error handling
# Compatible with latest dashboard (app.run)
# Author: Muhammad Munawar Shahzad
# Date: 2025-08-15

import subprocess
import logging
from pathlib import Path

# -------------------------------
# Setup logging
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------------------------
# Define all steps and their script paths
# -------------------------------
steps = {
    "data_collection": "scripts/1_data_collection_api.py",
    "web_scraping": "scripts/2_web_scraping.py",
    "data_wrangling": "scripts/3_data_wrangling.py",
    "dashboard": "scripts/4_dashboard_app.py",
    "presentation": "scripts/5_presentation.py"
}

# -------------------------------
# Run each step
# -------------------------------
for step_name, script_path in steps.items():
    path = Path(script_path)
    if not path.exists():
        logging.error(f"❌ Script for step '{step_name}' not found: {path}")
        continue

    logging.info(f"🔹 Running step: {step_name} → {path}")
    try:
        # Run scripts in a separate process
        result = subprocess.run(
            ["python", str(path)],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"  # ensures no UnicodeDecodeError
        )
        logging.info(result.stdout)
        logging.info(f"✅ Step '{step_name}' completed successfully.")

    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Step '{step_name}' failed with CalledProcessError:")
        logging.error(e.stderr)
    except Exception as e:
        logging.error(f"❌ Unexpected error in step '{step_name}': {e}")
