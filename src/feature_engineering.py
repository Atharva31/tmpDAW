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
        Dataset with engineered features.
    """
    df = df.copy()
    
    # 1. Electricity per customer (MWh/account/year)
    df['electricity_per_customer'] = df['residential_mwh_sales'] / df['num_customers']
    
    # 2. Electricity per capita (MWh/person/year)
    df['electricity_per_capita'] = df['residential_mwh_sales'] / df['population']
    
    # 3. Renter occupancy rate
    # Assuming: renter_occupied_units and total_occupied_units available from ACS
    df['renter_occupancy_rate'] = df.get('renter_occupied_units', 0) / df.get('total_occupied_units', 1)
    
    # 4. Housing age (2022 - median_year_structure_built)
    df['housing_age'] = 2022 - df.get('median_year_structure_built', 2000)
    
    # 5. Income log (log-transform to handle right skew)
    df['income_log'] = np.log(df['median_income'] + 1)  # +1 to avoid log(0)
    
    print(f"[Features] Engineered 5 features for {len(df)} ZIPs:")
    print(f"  - electricity_per_customer")
    print(f"  - electricity_per_capita")
    print(f"  - renter_occupancy_rate")
    print(f"  - housing_age")
    print(f"  - income_log")
    
    # Show summary statistics
    feature_cols = [
        'electricity_per_customer',
        'electricity_per_capita',
        'renter_occupancy_rate',
        'housing_age',
        'income_log'
    ]
    
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
        'electricity_per_customer',
        'electricity_per_capita',
        'renter_occupancy_rate',
        'housing_age',
        'income_log'
    ]
    
    return df[feature_cols].copy()
