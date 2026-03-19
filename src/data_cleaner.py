"""Data cleaning and integration module."""

import pandas as pd
import numpy as np


def clean_eia_data(df):
    """
    Clean EIA data: zero-pad ZIPs, drop invalid rows, aggregate by ZIP.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw EIA data.
    
    Returns
    -------
    pd.DataFrame
        Cleaned EIA data.
    """
    df = df.copy()
    
    # Zero-pad ZIP codes to 5 digits
    df['ZIP'] = df['ZIP'].astype(str).str.zfill(5)
    
    # Drop rows with missing critical fields
    df = df.dropna(subset=['ZIP', 'residential_mwh_sales', 'num_customers'])
    
    # Drop invalid rows (negative values, zeros in key fields)
    df = df[df['residential_mwh_sales'] >= 0]
    df = df[df['num_customers'] > 0]
    
    # Aggregate by ZIP (multiple utilities can serve same ZIP)
    df_agg = df.groupby('ZIP').agg({
        'residential_mwh_sales': 'sum',
        'num_customers': 'sum',
        'state': 'first'
    }).reset_index()
    
    print(f"[Clean EIA] After cleaning and aggregation: {len(df_agg)} unique ZIPs")
    
    return df_agg


def clean_acs_data(df):
    """
    Clean ACS data: replace Census nulls with NaN, drop empty ZCTAs.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw ACS data.
    
    Returns
    -------
    pd.DataFrame
        Cleaned ACS data.
    """
    df = df.copy()
    
    # Replace Census null values (-666666666) with NaN
    census_null = -666666666
    df = df.replace(census_null, np.nan)
    
    # Drop rows with critical missing values
    critical_cols = ['ZIP', 'population', 'median_income']
    df = df.dropna(subset=critical_cols)
    
    print(f"[Clean ACS] After cleaning: {len(df)} ZCTAs retained")
    
    return df


def merge_eia_acs(eia_df, acs_df):
    """
    Merge EIA and ACS on ZIP/ZCTA. Inner join.
    
    Parameters
    ----------
    eia_df : pd.DataFrame
        Cleaned EIA data.
    acs_df : pd.DataFrame
        Cleaned ACS data.
    
    Returns
    -------
    pd.DataFrame
        Merged dataset.
    """
    n_eia_before = len(eia_df)
    n_acs_before = len(acs_df)
    
    merged = pd.merge(eia_df, acs_df, on='ZIP', how='inner')
    
    n_merged = len(merged)
    loss_pct = 100 * (1 - n_merged / n_eia_before)
    
    print(f"[Merge] EIA ZIPs: {n_eia_before}, ACS ZCTAs: {n_acs_before}")
    print(f"[Merge] Inner join result: {n_merged} merged rows")
    print(f"[Merge] Loss: {loss_pct:.1f}% of EIA ZIPs (PO Box-only, etc.)")
    
    return merged


def filter_nyc_la(df):
    """
    Filter to NYC and LA ZIP codes.
    
    NYC ranges:
    - Manhattan: 10001-10282
    - Staten Island: 10301-10314
    - Bronx: 10451-10475
    - Brooklyn: 11201-11256
    - Queens: 11004-11436
    
    LA County: 90001-91899
    
    Parameters
    ----------
    df : pd.DataFrame
        Merged dataset with ZIP column.
    
    Returns
    -------
    pd.DataFrame
        Filtered to NYC and LA only.
    """
    df = df.copy()
    df['ZIP_int'] = df['ZIP'].astype(int)
    
    # Define NYC and LA ranges
    nyc_ranges = [
        (10001, 10282),  # Manhattan
        (10301, 10314),  # Staten Island
        (10451, 10475),  # Bronx
        (11201, 11256),  # Brooklyn
        (11004, 11436),  # Queens
    ]
    
    la_range = (90001, 91899)  # LA County
    
    # Create mask for NYC
    nyc_mask = pd.Series([False] * len(df), index=df.index)
    for start, end in nyc_ranges:
        nyc_mask |= (df['ZIP_int'] >= start) & (df['ZIP_int'] <= end)
    
    # Create mask for LA
    la_mask = (df['ZIP_int'] >= la_range[0]) & (df['ZIP_int'] <= la_range[1])
    
    # Filter
    df_filtered = df[nyc_mask | la_mask].copy()
    
    # Add city label
    df_filtered['city'] = 'LA'
    for start, end in nyc_ranges:
        df_filtered.loc[(df_filtered['ZIP_int'] >= start) & (df_filtered['ZIP_int'] <= end), 'city'] = 'NYC'
    
    print(f"[Filter] Extracted {len(df_filtered)} ZIP codes for NYC and LA")
    print(f"  NYC: {len(df_filtered[df_filtered['city'] == 'NYC'])}")
    print(f"  LA:  {len(df_filtered[df_filtered['city'] == 'LA'])}")
    
    return df_filtered.drop(columns='ZIP_int')


def clean_and_integrate(eia_df, acs_df):
    """
    Full pipeline: clean both datasets, merge, filter.
    
    Parameters
    ----------
    eia_df : pd.DataFrame
        Raw EIA data.
    acs_df : pd.DataFrame
        Raw ACS data.
    
    Returns
    -------
    pd.DataFrame
        Cleaned, merged, filtered dataset ready for feature engineering.
    """
    print("=" * 60)
    print("STEP 1: Clean EIA Data")
    print("=" * 60)
    eia_clean = clean_eia_data(eia_df)
    
    print("\n" + "=" * 60)
    print("STEP 2: Clean ACS Data")
    print("=" * 60)
    acs_clean = clean_acs_data(acs_df)
    
    print("\n" + "=" * 60)
    print("STEP 3: Merge EIA + ACS")
    print("=" * 60)
    merged = merge_eia_acs(eia_clean, acs_clean)
    
    print("\n" + "=" * 60)
    print("STEP 4: Filter to NYC + LA")
    print("=" * 60)
    result = filter_nyc_la(merged)
    
    print("\n" + "=" * 60)
    print("INTEGRATION COMPLETE")
    print("=" * 60)
    
    return result
