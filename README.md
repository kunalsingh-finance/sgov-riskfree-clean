# SGOV 6-Month Risk-Free Proxy

This project computes a 6-month risk-free return proxy from SGOV ETF prices.

## What The Code Does (Stage by Stage)

1. Stage 1 - Download data
- Pulls daily SGOV prices from Yahoo Finance using `yfinance`.
- Uses `Adj Close` when available (fallback: `Close`).

2. Stage 2 - Calculate the 6M proxy
- Computes daily log return: `ln(P_t / P_(t-1))`.
- Sums log returns over a rolling 126-trading-day window (about 6 months).
- Converts back to simple return: `exp(sum_log_returns) - 1`.
- Clips negative values to 0 for the final risk-free proxy field.

3. Stage 3 - Export outputs
- Writes full data to CSV and Excel.
- Writes latest value to both TXT and CSV.
- Optionally saves a PNG chart.

4. Stage 4 - Print final summary
- Prints latest date, latest proxy value, and output path.

## Why This Produces The Result

The method uses additive log returns over a fixed horizon (126 trading days),
which is a standard way to aggregate multi-period returns. The final conversion
back to simple return gives an interpretable 6M return percentage proxy.

## Files To Submit

- `sgov_rf_6m.py` (main script with comments and stage logs)
- `README.md` (method + usage + explanation)
- `requirements.txt` (dependencies)
- `sample_output.txt` (example terminal output)
- `out/` generated files after running locally

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python sgov_rf_6m.py --start 2024-01-01 --end 2026-02-12 --window 126 --out out --plot
```

## Output Files

- `out/sgov_rf_6m.csv`
- `out/sgov_rf_6m.xlsx`
- `out/rf_latest.txt`
- `out/rf_latest.csv`
- `out/sgov_rf_6m.png` (if `--plot` used)
