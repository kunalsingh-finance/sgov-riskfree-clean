# SGOV 6-Month Risk-Free Proxy

This project calculates a 6-month risk-free return proxy using SGOV ETF prices. It is a compact fixed-income analytics project showing how short-duration Treasury ETF data can be transformed into a reproducible rolling risk-free rate estimate.

The project is educational and does not represent investment advice, a live rate recommendation, or production market data infrastructure.

## What This Project Does

- Downloads SGOV daily price data with `yfinance`
- Uses adjusted close prices when available, with close-price fallback
- Calculates daily log returns
- Computes a rolling 126-trading-day return, roughly six months
- Converts rolling log returns back into simple returns
- Clips negative values at zero for the final risk-free proxy
- Exports CSV, Excel, text summary, chart, and PDF report outputs

## Methodology

1. Download SGOV daily price data.
2. Select adjusted close prices where available.
3. Calculate daily log returns:

```text
ln(P_t / P_(t-1))
```

4. Sum log returns over a 126-trading-day window.
5. Convert the result back to a simple return:

```text
exp(sum_log_returns) - 1
```

6. Clip negative values at zero to produce the final proxy.

## Why SGOV

SGOV is used as a short-duration Treasury bill ETF proxy. It is not identical to a Treasury bill curve, SOFR, or a directly observed risk-free rate, but it is a practical public-market proxy for a small educational analytics workflow.

## Files Included

- `sgov_rf_6m.py`: main computation script
- `build_submission_report.py`: PDF report generator
- `requirements.txt`: Python dependencies
- `sample_output.txt`: captured terminal output
- `out/`: generated data outputs
- `SGOV_Submission_Report.pdf`: generated report artifact

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the analysis:

```bash
python sgov_rf_6m.py --start 2024-01-01 --end 2026-02-12 --window 126 --out out --plot
```

Build the PDF report:

```bash
python build_submission_report.py --project-dir . --author "Your Name"
```

## Outputs

- `out/sgov_rf_6m.csv`
- `out/sgov_rf_6m.xlsx`
- `out/rf_latest.txt`
- `out/rf_latest.csv`
- `out/sgov_rf_6m.png`
- `SGOV_Submission_Report.pdf`

## Skills Demonstrated

- Fixed-income proxy construction
- Rolling return calculations
- Financial data cleaning
- Python reporting automation
- CSV, Excel, chart, and PDF output generation

## Limitations

- SGOV is an ETF proxy, not a direct Treasury bill curve or SOFR series.
- ETF prices can include market microstructure effects and fund-specific behavior.
- The 126-trading-day window is an approximation for six months.
- This is an educational project, not production rate infrastructure.
