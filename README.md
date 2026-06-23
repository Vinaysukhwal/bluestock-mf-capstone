# Bluestock Fintech — Mutual Fund Analytics Capstone

A full-stack **Mutual Fund Analytics Platform** built as a capstone project for Bluestock Fintech. The platform ingests publicly available data from AMFI India, transforms it through a robust ETL pipeline, stores it in a relational database, and presents insights via an interactive dashboard.

---

## Business Context

The Indian mutual fund industry manages over **Rs. 81 lakh crore** in AUM across 1,908 schemes and 26.12 crore investor folios (as of Dec 2025). This project builds a data platform that:

- Tracks NAV movements of **40+ key mutual fund schemes** from top AMCs
- Monitors AUM growth trends for the **10 largest fund houses** over 4+ years
- Analyses investor behaviour patterns across geographies and demographics
- Computes risk-adjusted return metrics (Sharpe, Sortino, Alpha, Beta)
- Benchmarks fund performance against Nifty 50, Nifty 100, BSE SmallCap indices
- Provides an executive-level **interactive dashboard** for fund selection

---

## Project Structure

```
bluestock-mf-capstone/
├── data/
│   ├── raw/                  # Original CSVs + live-fetched NAV data
│   └── processed/            # Cleaned, merged datasets (Day 2+)
├── notebooks/                # Jupyter notebooks for EDA & analytics
├── sql/                      # SQL schema & analytical queries
├── dashboard/                # Power BI / Tableau dashboard files
├── reports/                  # Data quality logs, validation reports
│   ├── data_quality_log.txt
│   └── amfi_code_validation.md
├── data_ingestion.py         # ETL script: load, inspect, validate
├── live_nav_fetch.py         # Fetch live NAV from mfapi.in
├── requirements.txt          # Python dependencies
├── .gitignore
└── README.md
```

---

## Datasets

| # | File | Rows | Description |
|---|------|------|-------------|
| 01 | `fund_master.csv` | 40 | Master list of 40 real MF schemes (AMFI codes, fund house, category, risk grade) |
| 02 | `nav_history.csv` | ~46,000 | Daily NAV for all 40 schemes (Jan 2022 – May 2026) |
| 03 | `aum_by_fund_house.csv` | ~90 | Quarterly AUM for 10 fund houses (2022–2025) |
| 04 | `monthly_sip_inflows.csv` | 48 | Monthly SIP inflows, active accounts, new registrations |
| 05 | `category_inflows.csv` | ~144 | Net inflows by fund category for FY 2024-25 |
| 06 | `industry_folio_count.csv` | 21 | Total MF folios by type (Equity, Debt, Hybrid) |
| 07 | `scheme_performance.csv` | 40 | 1yr/3yr/5yr returns, Sharpe, Sortino, Alpha, Beta, Max Drawdown |
| 08 | `investor_transactions.csv` | ~32,000 | SIP/Lumpsum/Redemption transactions for 5,000 investors |
| 09 | `portfolio_holdings.csv` | ~320 | Top equity holdings (stock, weight %, sector) |
| 10 | `benchmark_indices.csv` | ~8,000 | Daily closing values for Nifty 50, Nifty 100, Midcap 150, etc. |

**Live-fetched NAV** (via [mfapi.in](https://api.mfapi.in)):
| Scheme | AMFI Code | Records |
|--------|-----------|---------|
| HDFC Top 100 Direct | 125497 | ~3,100 |
| SBI Bluechip Direct | 119551 | ~3,250 |
| ICICI Pru Bluechip Direct | 120503 | ~3,320 |
| Nippon Large Cap Direct | 118632 | ~3,310 |
| Axis Bluechip Direct | 119092 | ~3,580 |
| Kotak Bluechip Direct | 120841 | ~3,316 |

---

## 7-Day Roadmap

| Day | Focus | Status |
|-----|-------|--------|
| **1** | Project Setup + Data Ingestion (ETL) | ✅ Complete |
| **2** | Data Cleaning + SQL Database Design | ⬜ Pending |
| **3** | Exploratory Data Analysis (EDA) | ⬜ Pending |
| **4** | Fund Performance Analytics | ⬜ Pending |
| **5** | Dashboard Development (Power BI / Tableau) | ⬜ Pending |
| **6** | Advanced Analytics + Risk Metrics | ⬜ Pending |
| **7** | Final Report + Presentation + Deployment | ⬜ Pending |

---

## Day 1 Summary

### What was done
- **Folder structure** created (`data/raw/`, `data/processed/`, `notebooks/`, `sql/`, `dashboard/`, `reports/`)
- **10 CSVs** loaded and inspected (shape, dtypes, head for each)
- **Anomaly detection**: nulls, duplicates, date format issues, wrong dtypes flagged
- **Live NAV fetched** for 6 schemes from mfapi.in with retry logic and error handling
- **Fund master explored**: 10 fund houses, 2 categories, 12 sub-categories, 5 risk grades
- **AMFI code validation**: all 40 codes cross-checked — zero mismatches
- **Reports generated**: `data_quality_log.txt` + `amfi_code_validation.md`

### Data Quality Findings
| Finding | Details |
|---------|---------|
| Anomalies found | 1 — `yoy_growth_pct` has 12 nulls in `04_monthly_sip_inflows.csv` (expected: first year lacks YoY data) |
| AMFI code alignment | All 40 fund master codes present in NAV history ✅ |
| Duplicate rows | None across all 10 datasets ✅ |
| Date format issues | None detected ✅ |

---

## Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | All data processing, ETL, analytics |
| Pandas | 3.x | DataFrames, cleaning, aggregation |
| NumPy | 2.x | Risk metrics, statistical functions |
| Matplotlib | 3.x | Static charts for reports |
| Seaborn | 0.13+ | Heatmaps, distributions |
| Plotly | 6.x | Interactive charts in Jupyter |
| SQLAlchemy | 2.x | Python-to-SQLite interface |
| SciPy | 1.x | OLS regression for Beta/Alpha |
| Jupyter | 4.x | EDA and analytics notebooks |
| Git + GitHub | Latest | Version control |

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Vinaysukhwal/bluestock-mf-capstone.git
cd bluestock-mf-capstone

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Fetch live NAV data
python live_nav_fetch.py

# Run data ingestion & quality checks
python data_ingestion.py
```

---

## Data Sources

| Source | URL | Data Type |
|--------|-----|-----------|
| AMFI India | [amfiindia.com](https://www.amfiindia.com) | NAV, AUM, Folio, SIP |
| mfapi.in | [api.mfapi.in](https://api.mfapi.in) | Historical NAV (JSON API) |
| NSE India | [nseindia.com](https://www.nseindia.com) | Benchmark Index Prices |
| BSE India | [bseindia.com](https://www.bseindia.com) | BSE SmallCap Index |

---

## License

This project is for **educational purposes only** and does not constitute financial advice. All data is sourced from publicly available information published by AMFI India, NSE, BSE, and open APIs.

> *Mutual Fund investments are subject to market risks. Read all scheme-related documents carefully.*
