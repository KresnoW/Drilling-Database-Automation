# Drilling Database Automation

A Python pipeline that automates coal drilling data processing and generates professional daily PDF reports.

## What It Does

1. **Ingests** raw drilling data (CSV/Excel)
2. **Cleans** duplicates and converts data types
3. **Analyzes** coal seam thickness, quality (CVAR, TM, TS, ASH), and lithology distribution
4. **Ranks** rigs by performance (depth drilled, intervals completed)
5. **Generates** a 7-page PDF report with tables and charts

## Tech Stack

- Python 3.11+
- pandas (data processing)
- matplotlib (charts)
- reportlab (PDF generation)
- openpyxl (Excel I/O)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run full pipeline
python run_all.py

| Script            | Purpose                             |
| ----------------- | ----------------------------------- |
| `main.py`         | Build master database from raw data |
| `coal_summary.py` | Calculate seam thicknesses          |
| `coal_rank.py`    | Rank seams by quality (CVAR)        |
| `lith_summary.py` | Analyze lithology distribution      |
| `rig_drilled.py`  | Summarize rig performance           |
| `daily_report.py` | Generate PDF report                 |

Drilling-Database-Automation/
|-- data/                    # Raw drilling data
|-- output/                  # Generated reports & Excel files
|-- main.py                  # Data ingestion
|-- coal_summary.py          # Seam thickness
|-- coal_rank.py             # Quality ranking
|-- lith_summary.py          # Lithology analysis
|-- rig_drilled.py           # Rig metrics
|-- daily_report.py          # PDF generator
|-- run_all.py               # Pipeline orchestrator
|-- requirements.txt         # Dependencies
|-- README.md                # This file