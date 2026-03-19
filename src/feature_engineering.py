"""Feature engineering module."""

import pandas as pd
import numpy as np


def engineer_features(df):
    """
    Derive the 5 modeling features from merged EIA + ACS data.

    Features:
    1. electricity_per_customer: annual MWh per residential account
    2. electricity_per_capita: MWh per person
    3. renter_occupancy_rate: fraction of occupied units that are rented
    4. housing_age: 2022 minus median year structure built
    5. income_log: log-transformed median household income

    Parameters
    ----------
    df : pd.DataFrame
        Merged and filtered dataset.

    Returns
    -------
    pd.DataFrame
        Dataset with engineered features (rows with invalid/missing features dropped).
    """
    df = df.copy()

    # 1. Electricity per customer (MWh/account/year)
    df["electricity_per_customer"] = (
        df["residential_mwh_sales"] / df["num_customers"]
    )

    # 2. Electricity per capita (MWh/person/year)
    df["electricity_per_capita"] = (
        df["residential_mwh_sales"] / df["population"]
    )

    # 3. Renter occupancy rate
    if "renter_occupied_units" in df.columns and "total_occupied_units" in df.columns:
        df["renter_occupancy_rate"] = df["renter_occupied_units"] / df["total_occupied_units"]
    else:
        df["renter_occupancy_rate"] = np.nan

    # 4. Housing age (2022 - median_year_structure_built)
    if "median_year_structure_built" in df.columns:
        df["housing_age"] = 2022 - df["median_year_structure_built"]
    else:
        df["housing_age"] = np.nan

    # 5. Income log (log-transform to handle right skew)
    df["income_log"] = np.log(df["median_income"] + 1)  # +1 to avoid log(0)

    feature_cols = [
        "electricity_per_customer",
        "electricity_per_capita",
        "renter_occupancy_rate",
        "housing_age",
        "income_log",
    ]

    # Drop rows with any NaN or Inf in engineered features (bad source data)
    before = len(df)
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=feature_cols)
    dropped = before - len(df)
    if dropped > 0:
        print(f"[Features] Dropped {dropped} rows with invalid/missing features")

    print(f"[Features] Engineered 5 features for {len(df):,} ZIPs:")
    for col in feature_cols:
        print(f"  - {col}")

    print("\nFeature Summary Statistics:")
    print(df[feature_cols].describe())

    return df


def get_feature_matrix(df):
    """
    Extract the 5 modeling features as a matrix.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset with engineered features.

    Returns
    -------
    pd.DataFrame
        Feature matrix (5 columns, n_zips rows).
    """
    feature_cols = [
        "electricity_per_customer",
        "electricity_per_capita",
        "renter_occupancy_rate",
        "housing_age",
        "income_log",
    ]

    # Validate all columns exist
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}. Run engineer_features() first.")

    return df[feature_cols].copy()
