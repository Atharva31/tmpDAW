# Urban Energy Analytics: NYC vs LA 2022

**Project Goal:** Identify distinct energy consumption patterns across ZIP codes in New York City and Los Angeles using data mining techniques (PCA + hierarchical clustering).

**Data:** 2022 EIA Form 861 (residential electricity sales) + 2022 ACS 5-year estimates (socio-economic data)  
**Methods:** PCA for dimensionality reduction, agglomerative clustering with silhouette evaluation  
**Output:** Neighborhood energy profiles, comparative insights on NYC vs LA

---

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# 1. Clone repository
git clone <repo>
cd Urban-Energy-Analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the notebook
jupyter notebook notebooks/urban_energy_analysis.ipynb
```

### Google Colab

You can also run this project in Google Colab:

1. Upload the notebook to Google Drive or clone the repo
2. Open the notebook in Colab
3. In the first cell, mount Google Drive and install dependencies:
   ```python
   # Mount Drive (if needed)
   from google.colab import drive
   drive.mount('/content/drive')
   
   # Install dependencies
   !pip install -r requirements.txt
   ```
4. Run the cells in order

---

## Repository Structure

```
Urban-Energy-Analytics/
├── .gitignore
├── README.md
├── PLAN.md
├── requirements.txt
├── data/
│   ├── raw/
│   │   ├── eia861_sales_2022.csv
│   │   └── acs_zcta_2022.csv
│   └── processed/
│       └── nyc_la_merged.csv
├── notebooks/
│   └── urban_energy_analysis.ipynb
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── data_cleaner.py
│   ├── feature_engineering.py
│   └── modeling.py
└── reports/
    └── report_draft.md
```

---

## Data Pipeline

1. **Load:** Read EIA and ACS CSVs from `data/raw/`
2. **Clean:** Standardize ZIP codes, handle missing values
3. **Merge:** Inner join on ZIP/ZCTA
4. **Filter:** Keep only NYC and LA ZIP codes
5. **Feature Engineering:** Derive 5 modeling features
6. **PCA:** Reduce to 2–3 components (85% variance)
7. **Clustering:** Agglomerative hierarchical clustering
8. **Evaluate:** Silhouette scores, dendrograms, profiles

---

## Key Features

- **No API keys required:** Datasets committed to repo
- **Reproducible:** Fixed data, deterministic pipeline
- **Modular:** Separate modules for each pipeline step
- **Jupyter-based:** Analysis with code + markdown + visualizations
- **Colab-compatible:** Works in both local and cloud environments

---

## Team

- Atharva Prasanna Mokashi (SJSU ID: 019117046)
- Maitreya Patankar (SJSU ID: 019146166)
- Vineet Malewar (SJSU ID: 018399589)
- Shefali Saini (SJSU ID: 018281848)

---

## References

- **EIA Form 861:** https://www.eia.gov/electricity/data/eia861/
- **ACS 2022 5-Year Estimates:** https://data.census.gov
