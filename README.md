# SGOV 6-Month Risk-Free Proxy

Professional course submission project for computing a 6-month risk-free return proxy from SGOV ETF prices.

## Stage-by-Stage Method

1. Stage 1 - Data download
- Pull SGOV daily prices from Yahoo Finance (`yfinance`).
- Use `Adj Close` when available (fallback: `Close`).

2. Stage 2 - Return calculation
- Daily log return: `ln(P_t / P_(t-1))`.
- Rolling 126-trading-day sum (approximately 6 months).
- Convert back to simple return: `exp(sum_log_returns) - 1`.
- Clip negative values at `0` to produce the final risk-free proxy.

3. Stage 3 - Output generation
- Save full results to CSV and Excel.
- Save latest value summary to TXT and CSV.
- Optionally save time-series chart as PNG.

4. Stage 4 - Reporting
- Print final summary in terminal.
- Generate a professional PDF submission report.

## Files Included

- `sgov_rf_6m.py` - main computation script with comments and stage logs
- `build_submission_report.py` - PDF report generator
- `README.md` - methodology and usage
- `requirements.txt` - dependencies
- `sample_output.txt` - captured terminal run output
- `out/` - generated data outputs
- `SGOV_Submission_Report.pdf` - final PDF report

## Setup

```bash
pip install -r requirements.txt
```

## Run Analysis

```bash
python sgov_rf_6m.py --start 2024-01-01 --end 2026-02-12 --window 126 --out out --plot
```

## Build PDF Report

```bash
python build_submission_report.py --project-dir . --author "Your Name"
```

Optional authorship line customization:

```bash
python build_submission_report.py --project-dir . --author "Your Name" --declaration "I confirm this code and analysis were prepared by me for course submission."
```

## Output Files

- `out/sgov_rf_6m.csv`
- `out/sgov_rf_6m.xlsx`
- `out/rf_latest.txt`
- `out/rf_latest.csv`
- `out/sgov_rf_6m.png`
- `SGOV_Submission_Report.pdf`
