# Testing & Verification Guide

Before committing anything to the main repository, run through every step below and confirm each checkpoint passes. We recommend **Google Colab Pro** for this — it's already available, handles all dependencies, and gives you a clean environment that mirrors what a grader would see.

---

## Recommended Environment: Google Colab Pro

Colab is the best option here because:
- Clean environment — no "works on my machine" issues
- GPU/TPU not needed (our workload is CPU-only), but Colab Pro gives longer runtimes and more RAM
- Easy to share a run with teammates for review
- Graders may run it the same way

**To get started in Colab:**

1. Go to [colab.research.google.com](https://colab.research.google.com)
2. Open a new notebook
3. Mount Google Drive or clone the repo directly:

```python
# Option A: Clone from GitHub (once repo is public)
!git clone https://github.com/SJSUF25/Urban-Energy-Analytics.git
%cd Urban-Energy-Analytics

# Option B: Upload the project folder to Google Drive, then mount
from google.colab import drive
drive.mount('/content/drive')
%cd /content/drive/MyDrive/Urban-Energy-Analytics
```

4. Install dependencies:
```python
!pip install -r requirements.txt -q
```

---

## Step 0 — Confirm Data Files Exist

Before running anything, verify that the real data files are in place.

```python
import os

files = [
    'data/raw/eia861_sales_2022.csv',
    'data/raw/acs_zcta_2022.csv',
]

for f in files:
    exists = os.path.exists(f)
    size = os.path.getsize(f) if exists else 0
    print(f"{'✅' if exists and size > 1000 else '❌'} {f} — {size:,} bytes")
```

**Expected:** Both files exist and are well above 1,000 bytes (real data, not sample placeholders).

> **If files are small (< 5 KB):** The sample/placeholder CSVs are still in place. Replace them with real data first — see the [Real Data section](#getting-real-data) below.

---

## Step 1 — Load Raw Data

```python
import sys
sys.path.insert(0, '.')

from src.data_loader import load_eia_data, load_acs_data

eia_df = load_eia_data()
acs_df = load_acs_data()

print(f"\nEIA shape: {eia_df.shape}")
print(f"ACS shape: {acs_df.shape}")
print(f"\nEIA columns: {eia_df.columns.tolist()}")
print(f"ACS columns: {acs_df.columns.tolist()}")
print(f"\nEIA sample:\n{eia_df.head(3)}")
print(f"\nACS sample:\n{acs_df.head(3)}")
```

**Checkpoints:**
- [ ] EIA shape: roughly **(40,000+ rows, 4 columns)** — `ZIP, state, residential_mwh_sales, num_customers`
- [ ] ACS shape: roughly **(33,000+ rows, 6 columns)** — `ZIP, population, median_income, median_year_structure_built, renter_occupied_units, total_occupied_units`
- [ ] No import errors
- [ ] ZIP column loads as string (not integer — leading zeros matter for NYC ZIPs like `10001`)

---

## Step 2 — Clean and Integrate Data

```python
from src.data_cleaner import clean_and_integrate, clean_eia_data, clean_acs_data, merge_eia_acs, filter_nyc_la

# Run full pipeline
df = clean_and_integrate(eia_df, acs_df)

print(f"\nFinal dataset shape: {df.shape}")
print(f"Cities: {df['city'].value_counts().to_dict()}")
print(f"\nSample:\n{df.head(3)}")
```

**Checkpoints:**
- [ ] No errors or crashes
- [ ] Merge loss printed (expect ~15–25% — if it's 0% or 100% something is wrong)
- [ ] Final dataset has both `NYC` and `LA` in the `city` column
- [ ] **NYC ZIP count:** should be roughly 150–250 rows
- [ ] **LA ZIP count:** should be roughly 300–700 rows
- [ ] No completely empty columns (run `df.isnull().sum()` to check)

```python
# Extra check: null counts
print(df.isnull().sum())
```

---

## Step 3 — Feature Engineering

```python
from src.feature_engineering import engineer_features, get_feature_matrix

df = engineer_features(df)
feature_matrix = get_feature_matrix(df)

print(f"\nFeature matrix shape: {feature_matrix.shape}")
print(f"\nFeature ranges:")
print(feature_matrix.describe())
```

**Checkpoints:**
- [ ] Feature matrix has **5 columns** and same number of rows as filtered dataset
- [ ] `electricity_per_customer`: should be between ~1 and ~50 MWh (realistic residential range)
- [ ] `renter_occupancy_rate`: should be between 0 and 1 (it's a proportion)
- [ ] `housing_age`: should be between ~0 and ~120 (years old)
- [ ] `income_log`: should be between ~10 and ~13 (log of dollar amounts ~$20k–$300k)
- [ ] No columns that are all zeros or all NaN

```python
# Check for silent defaults (the known fragile spot in feature_engineering.py)
print("\nrenter_occupancy_rate unique values (sample):", df['renter_occupancy_rate'].describe())
print("housing_age unique values (sample):", df['housing_age'].describe())

# If renter_occupancy_rate is all 0.0, the ACS column names don't match
# If housing_age is all 22 (2022 - 2000), the ACS column names don't match
assert df['renter_occupancy_rate'].std() > 0, "❌ renter_occupancy_rate has no variation — column name mismatch in ACS data"
assert df['housing_age'].std() > 0, "❌ housing_age has no variation — column name mismatch in ACS data"
print("✅ Feature variation looks healthy")
```

---

## Step 4 — PCA

```python
from src.modeling import standardize_features, apply_pca

scaler, std_features = standardize_features(feature_matrix.values)
pca_result = apply_pca(std_features, variance_threshold=0.85)

print(f"\nComponents selected: {pca_result['n_components']}")
print(f"Explained variance per component: {pca_result['explained_variance_ratio']}")
print(f"Cumulative variance: {pca_result['cumulative_variance']}")
print(f"Transformed shape: {pca_result['transformed'].shape}")
```

**Checkpoints:**
- [ ] **2 or 3 components selected** (5 features → expect 2–3 PCs for 85% variance)
- [ ] Cumulative variance of selected components is **≥ 0.85**
- [ ] Transformed shape is `(n_zips, n_components)` — no data lost
- [ ] No NaN warnings from sklearn

```python
import matplotlib.pyplot as plt
import numpy as np

# Scree plot — run this visually
pca_full = __import__('sklearn.decomposition', fromlist=['PCA']).PCA()
pca_full.fit(std_features)
cumvar = np.cumsum(pca_full.explained_variance_ratio_)

plt.figure(figsize=(7, 4))
plt.plot(range(1, len(cumvar)+1), cumvar, marker='o')
plt.axhline(0.85, color='red', linestyle='--', label='85% threshold')
plt.xlabel('Number of Components')
plt.ylabel('Cumulative Variance Explained')
plt.title('PCA Scree Plot')
plt.legend()
plt.tight_layout()
plt.show()
```

**Checkpoint:** The scree plot should show a clear elbow and reach the red 85% line by component 2 or 3.

---

## Step 5 — Clustering

```python
from src.modeling import apply_clustering

clustering_result = apply_clustering(pca_result, k_min=2, k_max=7)

print(f"\nOptimal k: {clustering_result['optimal_k']}")
print(f"Best silhouette score: {clustering_result['best_silhouette']:.4f}")
print(f"\nAll silhouette scores:")
for k, score in clustering_result['silhouette_scores'].items():
    print(f"  k={k}: {score:.4f}")
```

**Checkpoints:**
- [ ] Optimal k is between **2 and 5** (more than 5 clusters for ~300–900 ZIPs is likely overfitting)
- [ ] Best silhouette score is **> 0.10** (anything above 0.10 is reasonable; > 0.25 is good)
- [ ] All 6 k values (2–7) are tested and printed without errors

```python
# Silhouette score plot
plt.figure(figsize=(7, 4))
ks = list(clustering_result['silhouette_scores'].keys())
scores = list(clustering_result['silhouette_scores'].values())
plt.plot(ks, scores, marker='o', color='steelblue')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Score vs. Number of Clusters')
plt.xticks(ks)
plt.tight_layout()
plt.show()
```

---

## Step 6 — Full Evaluation

```python
from src.modeling import evaluate_clustering

eval_result = evaluate_clustering(df, pca_result, clustering_result)

print("\nCluster profiles (mean feature values):")
print(eval_result['profiles'])

print("\nCluster distribution by city:")
print(eval_result['city_distribution'])
```

**Checkpoints:**
- [ ] Cluster profiles table shows **meaningful differences** between clusters (not all rows the same)
- [ ] Both `NYC` and `LA` appear in the city distribution table
- [ ] No cluster has fewer than **5 ZIP codes** (too small = unstable cluster)

```python
# Scatter: PC1 vs PC2 colored by cluster
import seaborn as sns

transformed = pca_result['transformed']
labels = clustering_result['labels']

plt.figure(figsize=(8, 6))
scatter = plt.scatter(
    transformed[:, 0], transformed[:, 1],
    c=labels, cmap='tab10', alpha=0.7,
    marker='o', s=50
)
plt.colorbar(scatter, label='Cluster')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.title('ZIP Codes in PCA Space — Colored by Cluster')
plt.tight_layout()
plt.show()
```

**Checkpoint:** The scatter plot should show **visually distinct groupings** — if all points are the same color or fully mixed, something is off.

---

## Step 7 — NYC vs LA Comparison

```python
df_clustered = eval_result['df_clustered']

city_cluster = df_clustered.groupby(['city', 'cluster']).size().unstack(fill_value=0)
city_cluster_pct = city_cluster.div(city_cluster.sum(axis=1), axis=0) * 100

print("Cluster distribution by city (%):")
print(city_cluster_pct.round(1))

city_cluster_pct.T.plot(kind='bar', figsize=(8, 5), colormap='Set2')
plt.title('Cluster Distribution: NYC vs LA')
plt.xlabel('Cluster')
plt.ylabel('% of ZIP Codes')
plt.xticks(rotation=0)
plt.legend(title='City')
plt.tight_layout()
plt.show()
```

**Checkpoint:** NYC and LA should have **noticeably different cluster distributions** — this is the core finding of the project.

---

## Full End-to-End Sanity Check

Run this block after completing all steps. It should print all green checkmarks:

```python
print("=" * 50)
print("FINAL SANITY CHECK")
print("=" * 50)

checks = {
    "EIA rows > 1000": len(eia_df) > 1000,
    "ACS rows > 1000": len(acs_df) > 1000,
    "NYC ZIPs present": (df['city'] == 'NYC').sum() > 50,
    "LA ZIPs present": (df['city'] == 'LA').sum() > 50,
    "5 features engineered": feature_matrix.shape[1] == 5,
    "No NaN in features": feature_matrix.isnull().sum().sum() == 0,
    "PCA components 2-4": 2 <= pca_result['n_components'] <= 4,
    "PCA variance >= 85%": pca_result['cumulative_variance'][-1] >= 0.85,
    "Optimal k in 2-5": 2 <= clustering_result['optimal_k'] <= 5,
    "Silhouette > 0.10": clustering_result['best_silhouette'] > 0.10,
    "Both cities in results": set(eval_result['city_distribution'].columns) >= {'NYC', 'LA'},
}

all_pass = True
for check, result in checks.items():
    status = "✅" if result else "❌"
    print(f"  {status} {check}")
    if not result:
        all_pass = False

print()
if all_pass:
    print("✅ ALL CHECKS PASSED — safe to commit to main repository")
else:
    print("❌ SOME CHECKS FAILED — fix issues before committing")
```

---

## Getting Real Data

The current `data/raw/` files are **placeholder samples with only 10 rows**. Replace them with real data before testing.

### EIA Form 861 2022

1. Go to: https://www.eia.gov/electricity/data/eia861/
2. Download `f8612022.zip`
3. Extract it — find the file `Sales_Ult_Cust_2022.xlsx`
4. Open it in Excel or run this Python snippet to extract the residential columns:

```python
import pandas as pd

# The EIA Excel file has 2-3 merged header rows — skip them
df_raw = pd.read_excel('Sales_Ult_Cust_2022.xlsx', header=2, dtype=str)
print(df_raw.columns.tolist())   # inspect actual column names first

# Then select: state column, ZIP column, residential MWh, residential customers
# Column names vary slightly by year — inspect and rename accordingly
```

5. Save as `data/raw/eia861_sales_2022.csv` with columns: `ZIP, state, residential_mwh_sales, num_customers`

### ACS 2022 5-Year ZCTA Data

1. Go to: https://data.census.gov
2. Search for **"B01003"** → Select table → Geography: **Zip Code Tabulation Area (All ZCTAs)**  → Year: **2022**  → Download CSV
3. Repeat for tables: **B19013** (income), **B25010** (household size), **B25035** (year built), **B25003** (tenure/renter)
4. Merge all tables on ZCTA and save as `data/raw/acs_zcta_2022.csv` with columns:
   `ZIP, population, median_income, median_year_structure_built, renter_occupied_units, total_occupied_units`

> **Note:** The downloaded files from `data.census.gov` use `GEO_ID` (like `"8600000US10001"`) as the ZCTA identifier. Extract the 5-digit ZIP from the last 5 characters: `geo_id.str[-5:]`

---

## What "Ready to Commit" Looks Like

Before pushing to the main repo, confirm:

- [ ] Full sanity check above prints all ✅
- [ ] Notebook runs top-to-bottom without errors in a **fresh Colab environment**
- [ ] All plots render (scree plot, silhouette plot, cluster scatter, NYC vs LA bar chart)
- [ ] `data/raw/` has real data files (not 10-row placeholders)
- [ ] No `.env` files, no `*.zip`, no `*.xlsx` in the repo
- [ ] `git log --oneline` shows ~8–10 meaningful commits (not a single `"code"` commit)
