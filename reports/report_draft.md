# Check-in 2 Report: Urban Energy Analytics — NYC vs LA 2022

**Authors:** Atharva Prasanna Mokashi, Maitreya Patankar, Vineet Malewar, Shefali Saini  
**Date:** [To be completed]

---

## 1. Introduction and Motivation

[Section outline per CHECK-IN 1]

The United States faces increasing challenges in meeting residential electricity demand while managing sustainability goals in major urban centers. This study focuses on New York City and Los Angeles, two structurally different metropolitan systems, to understand how socio-economic characteristics influence neighborhood-scale electricity consumption patterns.

**Key questions:**
- What patterns emerge when we cluster neighborhoods by their energy consumption profiles?
- How do income, housing age, and occupancy rates relate to electricity usage?
- Do NYC and LA exhibit structurally different energy consumption patterns?

---

## 2. Data Mining Objectives and Research Questions

This project applies unsupervised learning (PCA + agglomerative clustering) to identify latent energy consumption patterns across 2022 ZIP codes in NYC and LA.

**Research questions:**
1. Can we identify distinct clusters of neighborhoods with similar energy consumption profiles?
2. What socio-economic variables best explain variation in electricity consumption?
3. How do NYC and LA differ in their energy consumption patterns?

---

## 3. Related Work

[Review of:]
- Dimensionality reduction in urban analytics (PCA applications)
- Hierarchical clustering for neighborhood segmentation
- Prior studies linking socio-economic characteristics to energy consumption

---

## 4. Data Sources and Data Understanding

### 4.1 Datasets

| Dataset | Source | Records | Key Variables |
|---------|--------|---------|----------------|
| **EIA Form 861 (2022)** | https://www.eia.gov/electricity/data/eia861/ | ~40,000 ZIP codes | Residential MWh sales, customer count |
| **ACS 2022 5-Year Estimates** | https://data.census.gov | ~33,000 ZCTAs | Population, median income, housing age, tenure, household size |

### 4.2 Initial Data Understanding

- **EIA data:** ZIP-level residential electricity sales aggregated across utilities
- **ACS data:** ZCTA-level Census estimates (5-year rolling averages)
- **Merge:** Inner join on ZIP/ZCTA; ~15–25% loss expected (PO Box-only ZIPs, etc.)
- **Coverage:** NYC (5 boroughs, ~200 ZIPs) + LA County (~700 ZIPs)

---

## 5. Data Cleaning and Integration Pipeline

### 5.1 Cleaning Steps

1. **EIA:** Zero-pad ZIP codes, remove invalid rows, aggregate by ZIP (multiple utilities)
2. **ACS:** Replace Census null markers (-666666666) with NaN, drop incomplete records
3. **Merge:** Inner join on ZIP/ZCTA; document loss percentage
4. **Filter:** Retain only NYC and LA ZIP codes using curated range lists

### 5.2 Results

[To be filled with actual pipeline run:]
- X ZIPs after EIA cleaning
- Y ZCTAs after ACS cleaning
- Z merged records after join
- W final records after NYC/LA filtering

---

## 6. Feature Engineering and Normalization

### 6.1 Engineered Features

We derived 5 features for unsupervised learning:

| Feature | Definition | Unit |
|---------|-----------|------|
| `electricity_per_customer` | Annual MWh per residential account | MWh/account |
| `electricity_per_capita` | Annual MWh per person | MWh/person |
| `renter_occupancy_rate` | Fraction of occupied units that are rented | Proportion |
| `housing_age` | 2022 minus median year structure built | Years |
| `income_log` | log(median household income) | Log dollars |

### 6.2 Rationale

- **Normalization:** StandardScaler applied (zero mean, unit variance) before PCA to prevent high-variance features from dominating
- **Log income:** Corrects right skew in income distribution
- **Per capita/customer metrics:** Scale electricity usage to population/customer size for fair comparison

---

## 7. PCA for Dimensionality Reduction

### 7.1 Method

Applied PCA to the 5 standardized features; selected components explaining ≥85% cumulative variance.

### 7.2 Results

[To be filled with actual run:]
- Number of components selected: ?
- Explained variance per component: ?
- Cumulative variance threshold reached at: ?

### 7.3 Interpretation

The principal components capture correlated variation in socio-economic variables, enabling downstream clustering in a lower-dimensional space while retaining 85% of information.

---

## 8. Hierarchical Clustering Design

### 8.1 Method

- **Algorithm:** Agglomerative hierarchical clustering with Ward linkage
- **Distance metric:** Euclidean (in PCA space)
- **Cluster selection:** Silhouette score sweep for k ∈ [2, 7]

### 8.2 Why hierarchical clustering?

- Dendrograms provide interpretable hierarchical structure
- Ward linkage minimizes within-cluster variance
- No need to specify k a priori; silhouette score guides selection

---

## 9. Validation Metrics and Model Selection

### 9.1 Silhouette Score

For each k, we computed the silhouette score (range [-1, 1]):
- Higher scores indicate more cohesive, well-separated clusters
- Score near 0 suggests overlapping clusters

### 9.2 Model Selection

Selected k with the highest silhouette score. [To be filled with actual result.]

---

## 10. Comparative Findings: NYC vs LA

### 10.1 Cluster Distribution

[To be filled with cluster sizes and NYC/LA breakdown per cluster]

### 10.2 Energy Intensity Patterns

[Analysis of electricity_per_capita and electricity_per_customer by city and cluster]

### 10.3 Socio-Economic Profiles

[Analysis of income, housing age, renter rates by cluster]

### 10.4 Key Differences

- NYC: [patterns observed]
- LA: [patterns observed]

---

## 11. Business/Policy Interpretation

[Suggestions for:]
- Targeted energy efficiency programs by neighborhood cluster
- Equity-focused interventions in high-income vs. low-income clusters
- Urban planning implications (housing density, building age)

---

## 12. Conclusion and Future Work

### 12.1 Key Findings

[Summary of clusters, main patterns, NYC vs LA differences]

### 12.2 Effectiveness of Methods

PCA + agglomerative clustering successfully identified interpretable neighborhood energy consumption profiles based on socio-economic characteristics.

### 12.3 Future Work

1. Extend to multi-year data (2018–2022) to identify temporal trends
2. Finer geographic granularity (census tracts)
3. Incorporate weather data and building stock composition
4. Develop predictive models for energy demand

---

## 13. References

1. Principal Component Analysis (cite sklearn documentation / textbook)
2. Hierarchical Clustering (cite scipy documentation)
3. EIA Form 861: https://www.eia.gov/electricity/data/eia861/
4. American Community Survey: https://data.census.gov
5. [Additional academic references on energy consumption and urban analytics]

---

## Appendix: Code Availability

All code, data, and this report are available in the project repository:
- Repository structure: `Urban-Energy-Analytics/`
- Main analysis notebook: `notebooks/urban_energy_analysis.ipynb`
- Data pipeline modules: `src/`
- Raw datasets: `data/raw/`

Run `pip install -r requirements.txt` to install dependencies, then execute the notebook in Jupyter or Google Colab (see README).
