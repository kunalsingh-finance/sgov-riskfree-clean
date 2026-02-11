# SGOV Risk-Free (6M proxy)

Computes a 6-month risk-free proxy using SGOV prices and exports CSV/XLSX + a plot.

## Setup
pip install -r requirements.txt

## Run
python sgov_rf_6m.py --start 2024-01-01 --end 2026-02-10 --window 126 --out out --plot
