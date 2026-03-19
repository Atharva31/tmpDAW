"""Data loading module for EIA and ACS datasets."""

import pandas as pd
import os


def load_eia_data(filepath=None):
    """
    Load EIA Form 861 2022 ZIP-level residential electricity sales data.
    
    Parameters
    ----------
    filepath : str, optional
        Path to eia861_sales_2022.csv. If None, uses default data/raw/ path.
    
    Returns
    -------
    pd.DataFrame
        EIA data with columns: ZIP, state, residential_mwh_sales, num_customers, etc.
    """
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), '../data/raw/eia861_sales_2022.csv')
    
    df = pd.read_csv(filepath, dtype={'ZIP': str})
    print(f"[EIA] Loaded {len(df)} ZIP codes from {filepath}")
    print(f"[EIA] Columns: {df.columns.tolist()}")
    print(f"[EIA] Shape: {df.shape}")
    
    return df


def load_acs_data(filepath=None):
    """
    Load ACS 2022 5-year socio-economic estimates at ZCTA level.
    
    Parameters
    ----------
    filepath : str, optional
        Path to acs_zcta_2022.csv. If None, uses default data/raw/ path.
    
    Returns
    -------
    pd.DataFrame
        ACS data with columns: ZIP (ZCTA), population, median_income, etc.
    """
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), '../data/raw/acs_zcta_2022.csv')
    
    df = pd.read_csv(filepath, dtype={'ZIP': str})
    print(f"[ACS] Loaded {len(df)} ZCTAs from {filepath}")
    print(f"[ACS] Columns: {df.columns.tolist()}")
    print(f"[ACS] Shape: {df.shape}")
    
    return df


def load_all_data():
    """
    Load both EIA and ACS datasets.
    
    Returns
    -------
    tuple of pd.DataFrame
        (eia_df, acs_df)
    """
    eia_df = load_eia_data()
    acs_df = load_acs_data()
    
    return eia_df, acs_df
