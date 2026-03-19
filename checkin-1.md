# **Project Check-in 1**

Urban Sustainability and Energy Behavior: A 2022 Comparative Study of NYC and LA

Team Information:

● Atharva Prasanna Mokashi \- SJSU ID: 019117046  
● Maitreya Patankar \- SJSU ID: 019146166  
● Vineet Malewar \- SJSU ID: 018399589  
● Shefali Saini \- SJSU ID: 018281848

## **Abstract**

The objective of this project is to analyze the relationship between socio-economic characteristics and residential electricity consumption across ZIP codes in New York City and Los Angeles using the data from the year 2022\. The data about the electricity consumption is obtained from the U.S. Energy Information Administration (EIA) Form 861 ZIP-level electricity sales dataset, while demographic and housing variables are sourced from the 2022 American Community Survey (ACS) 5-year estimates.

After combining the datasets by ZIP code, features like electricity consumption per customer, median household income, household size, housing age, and renter occupancy rate are engineered and standardized. Principal Component Analysis (PCA) is then used to reduce correlated socio-economic variables, followed by agglomerative hierarchical clustering to identify unique neighborhood energy consumption profiles. The Clustering quality is evaluated using silhouette scores.

The comparative analysis highlights structural differences between dense urban ZIP codes in NYC and more dispersed ZIP codes in LA, providing insights into how income, density, and housing characteristics influence electricity usage patterns.

# **Report Outline**

1. ## **Introduction and Motivation:** Brief background on urban electricity consumption and sustainability challenges in large metropolitan cities. Rationale for comparing New York City and Los Angeles as two structurally different urban systems. Motivation for applying data mining techniques to uncover latent patterns in energy behavior.

2. ## **Data Mining Objectives and Research Questions:** Clear statement of the project’s objective: to identify distinct energy consumption patterns across ZIP codes using unsupervised learning. Research questions will focus on how socio-economic factors relate to electricity usage, whether meaningful clusters of neighborhoods emerge, and whether structural differences exist between NYC and LA.

3. ## **Related Work:** Short review of literature on dimensionality reduction (PCA), clustering in urban analytics, and prior studies linking socio-economic characteristics to energy consumption patterns.

4. ## **Data Sources and Data Understanding:** Description of the 2022 EIA Form 861 ZIP-level residential electricity data and the 2022 ACS 5-year socio-economic data. Explanation of key variables used, dataset size, and initial exploratory analysis including summary statistics and distribution observations.

5. ## **Data Cleaning and Integration Pipeline:** Overview of filtering ZIP codes for NYC and LA, merging datasets, handling missing values, converting energy units, and validating data consistency. Brief explanation of preprocessing steps taken before modeling.

6. ## **Feature Engineering and Normalization:** Description of derived variables such as electricity per capita and electricity per customer. Explanation of why normalization is necessary prior to PCA and clustering, and summary of scaling approach applied.

7. ## **PCA for Dimensionality Reduction:** Rationale for applying PCA to reduce multicollinearity among socio-economic variables. Summary of explained variance, interpretation of principal components, and how reduced dimensions support clustering.

8. ## **Hierarchical Clustering Design:** Justification for using agglomerative hierarchical clustering. Explanation of linkage method, cluster selection approach, and how clusters represent neighborhood energy profiles.

9. ## **Validation Metrics and Model Selection:** Discussion of silhouette score and cluster interpretability. Explanation of how the optimal number of clusters was determined and evaluated.

10. ## **Comparative Findings: NYC vs LA:** Analysis of cluster distribution across both cities. Identification of key differences in income levels, housing characteristics, and energy intensity patterns between NYC and LA.

11. ## **Business/Policy Interpretation:** Discussion of how findings could inform urban sustainability policies, targeted energy efficiency programs, and equity-focused interventions.

12. ## **Conclusion and Future Work:** Summary of major insights and effectiveness of the applied data mining techniques. Suggestions for extending the study to multi-year data or finer geographic granularity.

13. ## **References:** Academic and data source references used in the project.

# **Identified Data Sources**

For this project, we identified two primary datasets for the year 2022 to ensure consistency across cities and variables, data set and findings are mentioned below.

The first dataset is the **U.S. Energy Information Administration (EIA) Form 861 ZIP Code Data (2022)**. This dataset provides ZIP-level residential electricity sales (in MWh), number of customers, and state-level identifiers. We reviewed the dataset structure and confirmed that it contains the necessary variables to compute normalized energy metrics such as electricity consumption per customer. The dataset includes ZIP codes across the United States, and we verified that ZIP codes corresponding to New York City and Los Angeles County are available.

The second dataset is the **American Community Survey (ACS) 2022 5-Year Estimates** at the ZIP Code Tabulation Area (ZCTA) level. We identified relevant socio-economic variables including total population, median household income, household size, housing characteristics, tenure (owner vs renter), and education levels. We confirmed that these variables are available at the ZIP-level geography and can be downloaded in CSV format for integration.

We also verified that ZIP codes from the EIA dataset can be aligned with ZCTAs from the ACS dataset, enabling straightforward merging using ZIP code identifiers. Initial inspection of the datasets indicates that they are manageable in size and suitable for dimensionality reduction and clustering techniques as proposed.
