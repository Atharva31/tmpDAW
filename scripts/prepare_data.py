#!/usr/bin/env python3
"""
prepare_data.py

Downloads and processes real data from EIA Form 861 and Census ACS.
Produces the two CSVs that the notebook reads from data/raw/.

Usage:
    python3 scripts/prepare_data.py

Requirements:
    - Download f8612022.zip from https://www.eia.gov/electricity/data/eia861/
      and place it in the repo root before running.
    - The ACS data is fetched automatically from the Census Bureau API
      (no API key required for this endpoint).

Outputs:
    data/raw/eia861_sales_2022.csv  — ZIP, state, residential_mwh_sales, num_customers
    data/raw/acs_zcta_2022.csv      — ZIP, population, median_income,
                                       median_year_structure_built,
                                       renter_occupied_units, total_occupied_units
"""

import os
import sys
import zipfile
import io
import requests
import pandas as pd
import numpy as np

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_RAW = os.path.join(REPO_ROOT, "data", "raw")
EIA_ZIP_PATH = os.path.join(REPO_ROOT, "f8612022.zip")

os.makedirs(DATA_RAW, exist_ok=True)

# ZIP-to-utility mapping from OpenEI (covers both investor-owned and non-IOU utilities)
IOU_CSV_URL = "https://data.openei.org/files/5993/iou_zipcodes_2022.csv"
NON_IOU_CSV_URL = "https://data.openei.org/files/5993/non_iou_zipcodes_2022.csv"

# Census ACS 2022 5-year estimates at ZCTA level (no API key needed)
ACS_BASE = "https://api.census.gov/data/2022/acs/acs5"
ACS_FOR = "zip+code+tabulation+area:*"

ACS_VARIABLES = {
    "B01003_001E": "population",
    "B19013_001E": "median_income",
    "B25035_001E": "median_year_structure_built",
    "B25003_001E": "total_occupied_units",
    "B25003_003E": "renter_occupied_units",
}

CENSUS_NULL = -666666666


def load_eia_sales(eia_zip_path):
    """Extract utility-level residential MWh sales from EIA 861 Excel file."""
    print("\nExtracting Sales_Ult_Cust_2022.xlsx from EIA 861 ZIP...")
    with zipfile.ZipFile(eia_zip_path, "r") as zf:
        with zf.open("Sales_Ult_Cust_2022.xlsx") as f:
            raw_bytes = f.read()

    xl = pd.ExcelFile(io.BytesIO(raw_bytes), engine="openpyxl")
    df = xl.parse("States", header=2)

    df.columns = [str(c).strip() for c in df.columns]

    # Select: utility ID (col 1), state (col 6), residential MWh (col 10), customers (col 11)
    df_sel = df.iloc[:, [1, 6, 10, 11]].copy()
    df_sel.columns = ["eiaid", "state", "residential_mwh", "num_customers"]

    for col in ["eiaid", "residential_mwh", "num_customers"]:
        df_sel[col] = pd.to_numeric(df_sel[col], errors="coerce")

    df_sel = df_sel.dropna(subset=["eiaid", "residential_mwh", "num_customers"])
    df_sel = df_sel[(df_sel["residential_mwh"] > 0) & (df_sel["num_customers"] > 0)]
    df_sel["eiaid"] = df_sel["eiaid"].astype(int)

    print(f"Loaded {len(df_sel)} utilities with residential sales")
    return df_sel


def load_utility_zip_mapping():
    """Download IOU and Non-IOU ZIP-to-utility mapping from OpenEI."""
    print("\nDownloading utility-ZIP mapping from OpenEI...")
    iou = pd.read_csv(IOU_CSV_URL, dtype={"zip": str})
    non_iou = pd.read_csv(NON_IOU_CSV_URL, dtype={"zip": str})

    mapping = pd.concat([iou, non_iou], ignore_index=True)
    mapping = mapping[["zip", "eiaid", "state"]].drop_duplicates()
    mapping.columns = ["ZIP", "eiaid", "state_zip"]
    mapping["ZIP"] = mapping["ZIP"].astype(str).str.zfill(5)

    print(f"Total utility-ZIP pairs: {len(mapping)}")
    return mapping


def build_zip_level_eia(sales, mapping):
    """
    Join utility sales with ZIP mapping and distribute MWh/customers across ZIPs.
    Each utility's sales are split evenly across all ZIPs it serves (uniform distribution).
    """
    print("\nJoining EIA sales with ZIP mapping...")
    merged = mapping.merge(sales, on="eiaid", how="inner")
    print(f"Joined rows: {len(merged)}")

    # Even distribution across ZIPs per utility
    zip_count = merged.groupby("eiaid")["ZIP"].transform("count")
    merged["residential_mwh_sales"] = merged["residential_mwh"] / zip_count
    merged["num_customers"] = merged["num_customers"] / zip_count
    merged["state"] = merged["state_zip"].combine_first(merged["state"])

    df_zip = (
        merged.groupby("ZIP")
        .agg(
            residential_mwh_sales=("residential_mwh_sales", "sum"),
            num_customers=("num_customers", "sum"),
            state=("state", "first"),
        )
        .reset_index()
    )

    df_zip = df_zip[(df_zip["residential_mwh_sales"] > 0) & (df_zip["num_customers"] > 0)]
    df_zip["num_customers"] = df_zip["num_customers"].round().astype(int)
    df_zip["residential_mwh_sales"] = df_zip["residential_mwh_sales"].round(2)

    print(f"ZIP-level rows: {len(df_zip)} | NY: {len(df_zip[df_zip['state']=='NY'])} | CA: {len(df_zip[df_zip['state']=='CA'])}")
    return df_zip[["ZIP", "state", "residential_mwh_sales", "num_customers"]]


def fetch_acs_data():
    """Download 2022 ACS 5-year ZCTA data from the Census Bureau API."""
    vars_param = ",".join(ACS_VARIABLES.keys())
    url = f"{ACS_BASE}?get={vars_param}&for={ACS_FOR}"

    print("\nFetching ACS 2022 ZCTA data from Census API...")
    try:
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching ACS data: {e}")
        sys.exit(1)

    data = resp.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    print(f"Received {len(df)} ZCTAs")

    df = df.rename(columns={"zip code tabulation area": "ZIP"})
    df = df.rename(columns=ACS_VARIABLES)
    df = df[["ZIP"] + list(ACS_VARIABLES.values())].copy()

    for col in ACS_VARIABLES.values():
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.replace(CENSUS_NULL, np.nan)
    df = df.dropna(subset=["population", "median_income"])
    df = df[(df["population"] > 100) & (df["median_income"] > 0)]
    df["ZIP"] = df["ZIP"].astype(str).str.zfill(5)

    print(f"Retained {len(df)} ZCTAs after cleaning")
    return df


def main():
    print("Urban Energy Analysis — Data Preparation")
    print("=" * 50)

    if not os.path.exists(EIA_ZIP_PATH):
        print(f"\nEIA ZIP not found: {EIA_ZIP_PATH}")
        print("Download f8612022.zip from https://www.eia.gov/electricity/data/eia861/")
        sys.exit(1)

    eia_sales = load_eia_sales(EIA_ZIP_PATH)
    zip_mapping = load_utility_zip_mapping()
    eia_zip = build_zip_level_eia(eia_sales, zip_mapping)

    eia_out = os.path.join(DATA_RAW, "eia861_sales_2022.csv")
    eia_zip.to_csv(eia_out, index=False)
    print(f"\nSaved EIA data -> {eia_out} ({len(eia_zip)} rows)")

    acs_df = fetch_acs_data()
    acs_out = os.path.join(DATA_RAW, "acs_zcta_2022.csv")
    acs_df.to_csv(acs_out, index=False)
    print(f"Saved ACS data -> {acs_out} ({len(acs_df)} rows)")

    # Quick validation
    print("\nValidation")
    print("-" * 40)
    eia_check = pd.read_csv(eia_out, dtype={"ZIP": str})
    acs_check = pd.read_csv(acs_out, dtype={"ZIP": str})

    required_eia = {"ZIP", "state", "residential_mwh_sales", "num_customers"}
    required_acs = {"ZIP", "population", "median_income", "median_year_structure_built",
                    "renter_occupied_units", "total_occupied_units"}

    assert required_eia.issubset(eia_check.columns), f"Missing EIA cols: {required_eia - set(eia_check.columns)}"
    assert required_acs.issubset(acs_check.columns), f"Missing ACS cols: {required_acs - set(acs_check.columns)}"

    ny = len(eia_check[eia_check["state"] == "NY"])
    ca = len(eia_check[eia_check["state"] == "CA"])
    print(f"EIA: {len(eia_check)} rows | NY: {ny} | CA: {ca}")
    print(f"ACS: {len(acs_check)} rows")

    assert ny > 100, f"Too few NY ZIPs ({ny})"
    assert ca > 100, f"Too few CA ZIPs ({ca})"
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
