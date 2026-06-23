"""
Day 1: Data Ingestion & Quality Assessment
==========================================
Loads all 10 CSVs from data/raw/, inspects each dataset,
flags anomalies, and explores the fund master file.

Bluestock Fintech - Mutual Fund Analytics Capstone
"""

import os
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

# ----------------------------- CONFIG -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# The 10 original CSVs (in order)
CSV_FILES = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]

# Columns that should be parsed as dates
DATE_COLUMNS = {
    "01_fund_master.csv": ["launch_date"],
    "02_nav_history.csv": ["date"],
    "03_aum_by_fund_house.csv": ["date"],
    "04_monthly_sip_inflows.csv": [],            # 'month' is YYYY-MM, not a full date
    "05_category_inflows.csv": [],               # 'month' is YYYY-MM
    "06_industry_folio_count.csv": [],            # 'month' is YYYY-MM
    "07_scheme_performance.csv": [],
    "08_investor_transactions.csv": ["transaction_date"],
    "09_portfolio_holdings.csv": ["portfolio_date"],
    "10_benchmark_indices.csv": ["date"],
}

# Columns expected to be numeric
NUMERIC_COLUMNS = {
    "01_fund_master.csv": ["expense_ratio_pct", "exit_load_pct", "min_sip_amount", "min_lumpsum_amount"],
    "02_nav_history.csv": ["nav"],
    "03_aum_by_fund_house.csv": ["aum_lakh_crore", "aum_crore", "num_schemes"],
    "04_monthly_sip_inflows.csv": ["sip_inflow_crore", "active_sip_accounts_crore",
                                    "new_sip_accounts_lakh", "sip_aum_lakh_crore", "yoy_growth_pct"],
    "05_category_inflows.csv": ["net_inflow_crore"],
    "06_industry_folio_count.csv": ["total_folios_crore", "equity_folios_crore",
                                     "debt_folios_crore", "hybrid_folios_crore", "others_folios_crore"],
    "07_scheme_performance.csv": ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
                                   "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio",
                                   "sortino_ratio", "std_dev_ann_pct", "max_drawdown_pct",
                                   "aum_crore", "expense_ratio_pct", "morningstar_rating"],
    "08_investor_transactions.csv": ["amount_inr", "annual_income_lakh"],
    "09_portfolio_holdings.csv": ["weight_pct", "market_value_cr", "current_price_inr"],
    "10_benchmark_indices.csv": ["close_value"],
}


def separator(title: str) -> str:
    return f"\n{'=' * 70}\n  {title}\n{'=' * 70}"


def load_all_csvs() -> dict[str, pd.DataFrame]:
    """Load all 10 CSVs into a dict keyed by filename."""
    frames = {}
    for fname in CSV_FILES:
        path = RAW_DIR / fname
        if not path.exists():
            print(f"  [!] MISSING: {fname}")
            continue
        df = pd.read_csv(path)
        frames[fname] = df
    return frames


def inspect_dataframe(fname: str, df: pd.DataFrame) -> list[str]:
    """Print shape/dtypes/head for one DataFrame; return list of anomaly strings."""
    anomalies: list[str] = []
    print(separator(fname))

    # -- Shape --
    print(f"\n  Shape: {df.shape[0]} rows x {df.shape[1]} columns")

    # -- Dtypes --
    print("\n  Dtypes:")
    for col, dtype in df.dtypes.items():
        print(f"    {col:40s}  {dtype}")

    # -- Head --
    print("\n  Head (first 5 rows):")
    print(df.head().to_string(index=False))

    # -- Null check --
    null_counts = df.isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0]
    if len(cols_with_nulls):
        msg = f"[{fname}] Null values found: " + ", ".join(
            f"{c}={n}" for c, n in cols_with_nulls.items()
        )
        anomalies.append(msg)
        print(f"\n  [!] {msg}")

    # -- Duplicate rows --
    n_dupes = df.duplicated().sum()
    if n_dupes > 0:
        msg = f"[{fname}] {n_dupes} duplicate row(s) detected"
        anomalies.append(msg)
        print(f"  [!] {msg}")

    # -- Date-format checks --
    for col in DATE_COLUMNS.get(fname, []):
        if col not in df.columns:
            continue
        try:
            parsed = pd.to_datetime(df[col], format="%Y-%m-%d", errors="coerce")
            n_bad = parsed.isna().sum() - df[col].isna().sum()
            if n_bad > 0:
                msg = f"[{fname}] {n_bad} values in '{col}' do not match YYYY-MM-DD format"
                anomalies.append(msg)
                print(f"  [!] {msg}")
        except Exception as e:
            anomalies.append(f"[{fname}] Error parsing date column '{col}': {e}")

    # -- Numeric-stored-as-string check --
    for col in NUMERIC_COLUMNS.get(fname, []):
        if col not in df.columns:
            continue
        if df[col].dtype == object:
            msg = f"[{fname}] Column '{col}' expected numeric but stored as string/object"
            anomalies.append(msg)
            print(f"  [!] {msg}")

    return anomalies


def explore_fund_master(df: pd.DataFrame) -> None:
    """Print exploration of the fund master file (Step 6)."""
    print(separator("FUND MASTER EXPLORATION"))

    # Unique fund houses
    fund_houses = df["fund_house"].unique()
    print(f"\n  Unique Fund Houses ({len(fund_houses)}):")
    for fh in sorted(fund_houses):
        print(f"    - {fh}")

    # Unique categories
    categories = df["category"].unique()
    print(f"\n  Unique Categories ({len(categories)}):")
    for c in sorted(categories):
        print(f"    - {c}")

    # Unique sub-categories
    sub_cats = df["sub_category"].unique()
    print(f"\n  Unique Sub-Categories ({len(sub_cats)}):")
    for sc in sorted(sub_cats):
        print(f"    - {sc}")

    # Unique risk grades
    risk_col = "risk_category" if "risk_category" in df.columns else "risk_grade"
    if risk_col in df.columns:
        risks = df[risk_col].unique()
        print(f"\n  Unique Risk Grades ({len(risks)}):")
        for r in sorted(risks):
            print(f"    - {r}")
    else:
        print("\n  [!] No risk_category/risk_grade column found")

    # AMFI scheme code structure explanation
    print("""
  --- AMFI Scheme Code Structure ---
  AMFI (Association of Mutual Funds in India) assigns a unique numeric code
  to every mutual fund scheme-plan-option combination. Key points:

  * Each code is a 6-digit integer (e.g. 125497 = HDFC Top 100 Fund - Direct Plan - Growth)
  * The same underlying fund has DIFFERENT codes for:
      - Direct vs. Regular plan
      - Growth vs. IDCW (Dividend) option
  * Codes are NOT sequential by fund house; they are allocated chronologically
    as new schemes/options are registered with SEBI/AMFI.
  * The code serves as the primary key to look up daily NAV on mfapi.in:
      https://api.mfapi.in/mf/{amfi_code}
  * In this dataset the 'sebi_category_code' column (e.g. EC01, DC01) maps to
    SEBI's standardised fund categories (EC = Equity Category, DC = Debt Category).
""")


def validate_amfi_codes(
    fund_master: pd.DataFrame,
    nav_history: pd.DataFrame,
    live_nav_dir: Path,
) -> str:
    """
    Step 7: Cross-check that every AMFI code in fund_master
    exists in nav_history + freshly-fetched live NAV data.
    Returns a markdown-formatted summary string.
    """
    master_codes = set(fund_master["amfi_code"].astype(str).unique())

    # Codes in the 02_nav_history.csv
    hist_codes = set(nav_history["amfi_code"].astype(str).unique())

    # Codes in any live-fetched CSVs
    live_codes: set[str] = set()
    for f in live_nav_dir.glob("*_nav.csv"):
        try:
            live_df = pd.read_csv(f)
            if "amfi_code" in live_df.columns:
                live_codes.update(live_df["amfi_code"].astype(str).unique())
        except Exception:
            pass

    all_nav_codes = hist_codes | live_codes
    missing_from_nav = master_codes - all_nav_codes
    orphaned_in_nav = all_nav_codes - master_codes

    # Build markdown report
    lines = [
        "# AMFI Code Validation Report",
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
        "## Summary",
        f"- Fund master codes: **{len(master_codes)}**",
        f"- NAV history codes (02_nav_history): **{len(hist_codes)}**",
        f"- Live-fetched NAV codes: **{len(live_codes)}**",
        f"- Combined NAV codes: **{len(all_nav_codes)}**\n",
        "## Validation Results",
    ]

    if missing_from_nav:
        lines.append(f"\n### [!] Missing from NAV data ({len(missing_from_nav)} codes)")
        lines.append("These AMFI codes are in the fund master but have **no NAV history**:\n")
        for code in sorted(missing_from_nav):
            name = fund_master.loc[
                fund_master["amfi_code"].astype(str) == code, "scheme_name"
            ]
            name_str = name.iloc[0] if len(name) else "Unknown"
            lines.append(f"- `{code}` -- {name_str}")
    else:
        lines.append("\n[OK] All fund master codes have NAV data.")

    if orphaned_in_nav:
        lines.append(f"\n### [i] Orphaned NAV codes ({len(orphaned_in_nav)} codes)")
        lines.append("These codes appear in NAV data but **not** in the fund master:\n")
        for code in sorted(orphaned_in_nav):
            lines.append(f"- `{code}`")
    else:
        lines.append("\n[OK] No orphaned NAV codes.")

    lines.append("\n## Data Quality Verdict")
    if not missing_from_nav and not orphaned_in_nav:
        lines.append("All AMFI codes are fully aligned between fund master and NAV datasets. [OK]")
    else:
        total_issues = len(missing_from_nav) + len(orphaned_in_nav)
        lines.append(
            f"**{total_issues}** code mismatches found. Review and resolve before Day 2 (SQL schema design)."
        )

    return "\n".join(lines)


# ------------------------------ MAIN --------------------------------
def main() -> None:
    print(separator("DAY 1: DATA INGESTION - Bluestock MF Capstone"))
    print(f"  Timestamp : {datetime.now()}")
    print(f"  Raw dir   : {RAW_DIR}")
    print(f"  Reports   : {REPORTS_DIR}\n")

    # -- Step 3: Load & inspect --
    frames = load_all_csvs()
    all_anomalies: list[str] = []

    for fname, df in frames.items():
        anomalies = inspect_dataframe(fname, df)
        all_anomalies.extend(anomalies)

    # -- Save anomaly log --
    log_path = REPORTS_DIR / "data_quality_log.txt"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("DATA QUALITY ANOMALY LOG\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write("=" * 60 + "\n\n")
        if all_anomalies:
            for a in all_anomalies:
                f.write(f"* {a}\n")
        else:
            f.write("No anomalies detected.\n")
        f.write(f"\nTotal anomalies flagged: {len(all_anomalies)}\n")

    print(separator("ANOMALY LOG SAVED"))
    print(f"  -> {log_path}")
    print(f"  Total anomalies: {len(all_anomalies)}")
    for a in all_anomalies:
        print(f"    * {a}")

    # -- Step 6: Explore fund master --
    if "01_fund_master.csv" in frames:
        explore_fund_master(frames["01_fund_master.csv"])

    # -- Step 7: Validate AMFI codes --
    if "01_fund_master.csv" in frames and "02_nav_history.csv" in frames:
        summary_md = validate_amfi_codes(
            frames["01_fund_master.csv"],
            frames["02_nav_history.csv"],
            RAW_DIR,
        )
        summary_path = REPORTS_DIR / "amfi_code_validation.md"
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_md)
        print(separator("AMFI CODE VALIDATION"))
        print(summary_md)
        print(f"\n  Saved to: {summary_path}")

    print(separator("DATA INGESTION COMPLETE"))


if __name__ == "__main__":
    main()
