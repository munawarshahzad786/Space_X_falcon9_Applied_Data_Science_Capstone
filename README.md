I am Muhammad Munawar Shahzad & have completed this Falcon 9 Data Science Capstone Project and here is the  Overview of the this falcon9 Project. 

This project analyzes SpaceX Falcon 9 launch data from multiple sources, including API and web scraping. It covers the complete data science workflow: data collection, cleaning, exploratory analysis, visualization, dashboard creation, and final presentation.

Usage Workflow of the project

-Collect data → API + Scraping
-Wrangle data → Clean & preprocess
-EDA with SQL & Visuals → Launch trends, payloads, orbits, outcomes
-Maps & Dashboards → Folium + Plotly Dash
-Predictive ML → Classification for launch success
-Presentation → Automated visual + report generation

Automated presentation outputs

Project Structure
falcon9_project/
│
├── README.md        # 📄 Project overview, usage, and installation instructions
├── requirements.txt # 📦 Python dependencies with versions
├── LICENSE          # ⚖️ MIT License
│
├── data/                                  # 📊 Datasets
│   ├── raw/                               # 📥 Original datasets (API / Web scraping)
│   │   └── falcon9_launches.csv
│   │   └── falcon9_web_scraped.csv
│   └── processed/                           # 🧹 Cleaned datasets for EDA/ML
│       └── falcon_web_scraped_cleaned.csv
│       └── falcon9_cleaned_for_eda.csv
│
├── notebooks/                             # 📓 Jupyter Notebooks (step-by-step workflow)
│   ├── 1_data_collection_api.ipynb        # 📡 Collect launch data using SpaceX API
│   ├── 2_web_scraping.ipynb               # 🌐 Scrape additional launch details
│   ├── 3_data_wrangling.ipynb             # 🧽 Clean + preprocess data
│   ├── 4_exploratory_analysis_with_SQL.ipynb # 📊 EDA & SQL-based analysis
│   ├── 5_dash_dashboard.ipynb              # 📈 Interactive dashboard & Folium map
│   ├── 6_predictive_analysis_classification.ipynb # 🤖 ML model (classification of launch success/failure)
│   └── 7_presentation.ipynb                # 🎤 Final presentation + visuals
│
├── scripts/                                # 🛠 Automation-ready Python scripts
│   ├── 1_data_collection_api.py
│   ├── 2_web_scraping.py
│   ├── 3_data_wrangling.py
│   ├── 4_dashboard_app.py              # Plotly Dash App
│   ├── 5_folium_map.py                 # Folium map (launch sites + proximities)
│   ├── 6_presentation.py
│   └── 7_run_all.py                    # 🔁 Automate running the full pipeline
│
├── outputs/                            # 📤 Results & generated outputs
│   ├── figures/                        # 📷 Graphs, charts, screenshots
│   └── reports/                        # 📑 Summary CSVs, reports, insights
│
└── docs/                               # 📚 Documentation
│    ├── api_reference.md
│    ├── project_steps.md
│    └── changelog.md
├──  working_launch_map.html

Installation Instructions
Python Version: Python 3.10.18 is required for compatibility with all packages.

Clone the Repository:

git clone <repository_url>
cd falcon9_project

Install Dependencies:

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

Ensure you have Python 3.10 set as default interpreter before installing.

Run the interactive dashboard locally:
Open http://127.0.0.1:8050/ in your browser.


Outputs

Figures: Generated charts and plots stored in outputs/figure
Reports: Summary CSVs and data insights stored in outputs/reports/

Notes

Make sure to have all required libraries installed.
For deployment, test locally first before uploading to Streamlit or other hosting services.

All paths and filenames are consistent with the project structure for reproducibility.
