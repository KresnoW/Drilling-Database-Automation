# Drilling Database Automation

Automated mining drilling database and PDF reporting pipeline built with Python.

## Overview

This project automates geological drilling data processing and generates operational drilling reports in PDF format.

The workflow includes:
- raw drilling database cleaning
- coal seam thickness calculations
- coal quality ranking
- lithology distribution analysis
- rig productivity summaries
- automated chart generation
- PDF operational reporting

---

## Features

- Automated drilling data processing
- Coal seam thickness analytics
- CVAR quality ranking
- Lithology percentage summaries
- Rig drilling performance tracking
- Automated visualization generation
- PDF report automation

---

## Workflow

```text
Raw CSV Files
      ↓
main.py
      ↓
coal_summary.py
      ↓
coal_rank.py
      ↓
lith_summary.py
      ↓
rig_drilled.py
      ↓
daily_report.py
      ↓
Final PDF Report
```

---

## Tech Stack

- Python
- Pandas
- NumPy
- Matplotlib
- ReportLab
- OpenPyXL

---

## Sample Outputs

### Rig Performance Dashboard
[INSERT IMAGE]

### Lithology Distribution
[INSERT IMAGE]

### Automated PDF Report
[INSERT IMAGE]

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Run Full Automation

```bash
python run_all.py
```

---

## Author

Nur Kresno Wicaksono

Mining Data Analyst | Geologist | Reporting Automation