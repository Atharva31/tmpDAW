"""Data loading module for EIA and ACS datasets."""

import os
import pandas as pd


def _resolve_path(relative_path: str) -> str:
    """Resolve path relative to the repo root, regardless of CWD.

    Works both when running from:
      - repo root:      python3 scripts/...
      - notebooks dir:  jupyter notebook  (CWD = notebooks/)
    """
    # Try relative to this file's directory (src/)
    src_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(src_dir, ".."))
    return os.path.join(repo_root, relative_path)


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
        EIA data with columns: ZIP, state, residential_mwh_sales, num_customers.
    """
    if filepath is None:
        filepath = _resolve_path("data/raw/eia861_sales_2022.csv")

    df = pd.read_csv(filepath, dtype={"ZIP": str})
    # Ensure ZIP is zero-padded to 5 digits
    df["ZIP"] = df["ZIP"].str.zfill(5)

    print(f"[EIA] Loaded {len(df):,} ZIP codes from {os.path.basename(filepath)}")
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
        ACS data with columns: ZIP (ZCTA), population, median_income,
        median_year_structure_built, renter_occupied_units, total_occupied_units.
    """
    if filepath is None:
        filepath = _resolve_path("data/raw/acs_zcta_2022.csv")

    df = pd.read_csv(filepath, dtype={"ZIP": str})
    # Ensure ZIP is zero-padded to 5 digits
    df["ZIP"] = df["ZIP"].str.zfill(5)

    print(f"[ACS] Loaded {len(df):,} ZCTAs from {os.path.basename(filepath)}")
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
