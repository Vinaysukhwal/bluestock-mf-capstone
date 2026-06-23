"""
Live NAV Fetcher - mfapi.in
============================
Fetches historical NAV data from the MFAPI public API for selected
mutual fund schemes and saves each as a CSV in data/raw/.

Covers:
  Step 4 - Single scheme: HDFC Top 100 Direct (125497)
  Step 5 - 5 additional key large-cap schemes

Bluestock Fintech - Mutual Fund Analytics Capstone
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests

# ----------------------------- CONFIG -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

API_BASE = "https://api.mfapi.in/mf"
TIMEOUT_SECONDS = 30
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5          # seconds between retries

# Schemes to fetch  {amfi_code: (slug_for_filename, display_name)}
SCHEMES = {
    "125497": ("hdfc_top100_nav",       "HDFC Top 100 Fund - Direct Plan"),
    "119551": ("sbi_bluechip_nav",      "SBI Bluechip Fund - Direct Plan"),
    "120503": ("icici_bluechip_nav",    "ICICI Pru Bluechip Fund - Direct Plan"),
    "118632": ("nippon_largecap_nav",   "Nippon India Large Cap Fund - Direct Plan"),
    "119092": ("axis_bluechip_nav",     "Axis Bluechip Fund - Direct Plan"),
    "120841": ("kotak_bluechip_nav",    "Kotak Bluechip Fund - Direct Plan"),
}


def fetch_nav(amfi_code: str, name: str) -> pd.DataFrame | None:
    """
    GET historical NAV JSON from mfapi.in for a single scheme.
    Returns a DataFrame with columns [date, nav, amfi_code] or None on failure.
    """
    url = f"{API_BASE}/{amfi_code}"
    print(f"\n  Fetching {name} ({amfi_code})...")
    print(f"  URL: {url}")

    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            resp = requests.get(url, timeout=TIMEOUT_SECONDS)

            # -- Non-200 response --
            if resp.status_code != 200:
                print(f"    [!] Attempt {attempt}: HTTP {resp.status_code}")
                if attempt < RETRY_ATTEMPTS:
                    time.sleep(RETRY_DELAY)
                    continue
                print(f"    [X] Failed after {RETRY_ATTEMPTS} attempts (HTTP {resp.status_code})")
                return None

            payload = resp.json()

            # -- Empty payload check --
            if "data" not in payload or not payload["data"]:
                print(f"    [!] Attempt {attempt}: Empty or missing 'data' array")
                if attempt < RETRY_ATTEMPTS:
                    time.sleep(RETRY_DELAY)
                    continue
                print(f"    [X] No data received after {RETRY_ATTEMPTS} attempts")
                return None

            # -- Parse data --
            records = payload["data"]
            df = pd.DataFrame(records)           # columns: date, nav
            df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

            # mfapi returns dates as dd-mm-yyyy; convert to YYYY-MM-DD
            df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
            df = df.dropna(subset=["date", "nav"])
            df["date"] = df["date"].dt.strftime("%Y-%m-%d")
            df["amfi_code"] = amfi_code
            df = df.sort_values("date").reset_index(drop=True)

            print(f"    [OK] {len(df)} NAV records fetched "
                  f"({df['date'].iloc[0]} -> {df['date'].iloc[-1]})")
            return df[["amfi_code", "date", "nav"]]

        except requests.exceptions.Timeout:
            print(f"    [!] Attempt {attempt}: Request timed out")
        except requests.exceptions.ConnectionError:
            print(f"    [!] Attempt {attempt}: Connection error")
        except requests.exceptions.RequestException as e:
            print(f"    [!] Attempt {attempt}: {e}")
        except (ValueError, KeyError) as e:
            print(f"    [!] Attempt {attempt}: JSON parse error - {e}")

        if attempt < RETRY_ATTEMPTS:
            time.sleep(RETRY_DELAY)

    print(f"    [X] All {RETRY_ATTEMPTS} attempts failed for {amfi_code}")
    return None


def main() -> None:
    print("=" * 60)
    print("  LIVE NAV FETCH - mfapi.in")
    print(f"  Timestamp: {datetime.now()}")
    print(f"  Output dir: {RAW_DIR}")
    print("=" * 60)

    success = 0
    failed = 0

    for code, (slug, name) in SCHEMES.items():
        df = fetch_nav(code, name)
        if df is not None and len(df) > 0:
            out_path = RAW_DIR / f"{slug}.csv"
            df.to_csv(out_path, index=False)
            print(f"    Saved -> {out_path}")
            success += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"  DONE - {success} succeeded, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
