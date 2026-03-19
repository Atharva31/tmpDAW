# Check-in 2 Plan — Urban Energy Analytics

## What Changed from Check-in 1
- **Data strategy updated:** Instead of fetching ACS data via Census API (which requires a key), we download both datasets once and commit them directly to the repo. Anyone can clone and run immediately — no setup required beyond `pip install -r requirements.txt`.

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
│   │   ├── eia861_sales_2022.csv     ← EIA Form 861 residential sales (committed)
│   │   └── acs_zcta_2022.csv         ← ACS 2022 5-year ZCTA estimates (committed)
│   └── processed/
│       └── nyc_la_merged.csv         ← Output of pipeline (generated + committed)
├── notebooks/
│   └── urban_energy_analysis.ipynb   ← Main analysis notebook
├── src/
│   ├── __init__.py
│   ├── data_loader.py                ← Load EIA + ACS from local files
│   ├── data_cleaner.py               ← Clean, merge, filter to NYC + LA
│   ├── feature_engineering.py        ← Derive modeling features
│   └── modeling.py                   ← PCA, clustering, evaluation
└── reports/
    └── report_draft.md               ← Written Check-in 2 report
```

---

## Commit Plan (10 commits)

| # | Commit Message | What Goes In |
|---|---------------|-------------|
| 1 | `Initial project setup: repo structure, gitignore, requirements` | `.gitignore`, `requirements.txt`, `README.md`, placeholder `.gitkeep` files, `src/__init__.py` |
| 2 | `Add raw datasets: EIA Form 861 2022 and ACS 2022 ZCTA` | `data/raw/eia861_sales_2022.csv`, `data/raw/acs_zcta_2022.csv` |
| 3 | `Add data loader module to read local EIA and ACS files` | `src/data_loader.py` |
| 4 | `Add data cleaning and NYC/LA ZIP filtering pipeline` | `src/data_cleaner.py` |
| 5 | `Add feature engineering module` | `src/feature_engineering.py` |
| 6 | `Add modeling utilities: PCA, clustering, evaluation` | `src/modeling.py` |
| 7 | `Add notebook: setup, data loading, and EDA sections` | Notebook sections 0–3 |
| 8 | `Add notebook: feature engineering and PCA sections` | Notebook sections 4–5 |
| 9 | `Add notebook: clustering and NYC vs LA comparison` | Notebook sections 6–7 |
| 10 | `Add Check-in 2 report draft and finalize README` | `reports/report_draft.md`, final `README.md` |

---

## Data Sources

| Dataset | Source | What We Use |
|---------|--------|------------|
| EIA Form 861 (2022) | https://www.eia.gov/electricity/data/eia861/ | ZIP-level residential MWh sales + customer counts |
| ACS 2022 5-Year Estimates | https://data.census.gov | Population, median income, household size, housing age, tenure (owner vs renter) by ZCTA |

Both are downloaded once, cleaned, and committed as CSVs to `data/raw/`.

---

## Pipeline (What the Code Does)

**Step 1 — Load:** Read both CSVs from `data/raw/` into DataFrames

**Step 2 — Clean:**
- EIA: zero-pad ZIPs to 5 digits, drop invalid rows, aggregate by ZIP (multiple utilities can serve the same ZIP)
- ACS: replace Census null values (-666666666) with NaN, drop empty ZCTAs

**Step 3 — Merge:** Inner join on ZIP/ZCTA. Note: ~15–25% of EIA ZIPs won't match an ACS ZCTA (PO Box-only ZIPs). This is expected and documented.

**Step 4 — Filter:** Keep only NYC and LA ZIP codes using curated range lists:
- NYC: Manhattan (10001–10282), Staten Island (10301–10314), Bronx (10451–10475), Brooklyn (11201–11256), Queens (11004–11436)
- LA County: 90001–91899 in California

**Step 5 — Feature Engineering:** Derive the 5 modeling features:
- `electricity_per_customer` — annual MWh per residential account
- `electricity_per_capita` — MWh per person
- `renter_occupancy_rate` — fraction of occupied units that are rented
- `housing_age` — 2022 minus median year structure built
- `income_log` — log-transformed median household income (corrects right skew)

**Step 6 — PCA:** StandardScaler → PCA, select components explaining ≥85% variance (expected: 2–3 components)

**Step 7 — Clustering:** AgglomerativeClustering with Ward linkage, k selected via silhouette score sweep (k = 2–7)

**Step 8 — Evaluate:** Silhouette scores, dendrogram (on 200-ZIP subsample), cluster profile table, NYC vs LA comparison chart

---

## Notebook Sections

| Section | Content |
|---------|---------|
| 0 — Setup | Imports, paths, plot styling |
| 1 — Data Loading | Load EIA + ACS, display shape and head |
| 2 — Cleaning & Integration | Clean, merge, filter; show merge loss %, ZIP counts per city |
| 3 — EDA | Histograms, box plots (income by city), scatter (electricity vs income), correlation heatmap |
| 4 — Feature Engineering | Compute all features, distribution plots |
| 5 — PCA | Scree plot, cumulative variance, loadings table |
| 6 — Clustering | Silhouette sweep, dendrogram, final cluster scatter, cluster profile table |
| 7 — NYC vs LA | Cluster distribution by city, written observations |
| 8 — Summary | Key findings, next steps |

---

## Report Draft Sections (`reports/report_draft.md`)

1. **Abstract** (~150 words)
2. **Report Outline** — Full 13-section outline (matching Check-in 1 structure)
3. **Literature Survey** — 6 sources:
   - Kontokosta & Tull (2017) — ZIP-level building energy in NYC
   - Reames (2016) — Spatial and income-based energy disparities
   - Golbazi & Aktas (2020) — Occupant behavior and energy consumption
   - Jolliffe (2002) — PCA methodology
   - Jain et al. (1999) — Clustering algorithms review
   - EIA Form 861 + ACS official documentation
4. **Approach** — Two approaches explored:
   - Approach A *(rejected)*: ZIP-level regression — unsuitable for pattern discovery, no ground-truth labels
   - Approach B *(adopted)*: PCA + Agglomerative Hierarchical Clustering
5. **Algorithms** — StandardScaler, PCA, Ward linkage clustering, Silhouette Score

---

## Division of Work for Check-in 2

| Member | Task |
|--------|------|
| Shefali Saini | Download + clean EIA and ACS datasets, commit `data/raw/` CSVs, write `src/data_loader.py` and `src/data_cleaner.py` |
| Atharva Prasanna Mokashi | Write `src/feature_engineering.py`, notebook sections 4–5 (feature engineering + PCA), literature survey (PCA papers) |
| Vineet Malewar | Write `src/modeling.py`, notebook sections 6–7 (clustering + NYC vs LA), literature survey (clustering papers) |
| Maitreya Umesh Patankar | Write `reports/report_draft.md` (abstract, outline, approach, algorithms), coordinate commits, finalize README |

---

## Requirements

```
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
scipy>=1.11
matplotlib>=3.7
seaborn>=0.12
requests>=2.31
openpyxl>=3.1
jupyter>=1.0
```
