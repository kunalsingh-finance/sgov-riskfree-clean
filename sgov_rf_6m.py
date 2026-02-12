"""
SGOV 6-Month Risk-Free Proxy

This script builds a 6-month risk-free return proxy from SGOV price data.
Method summary:
1) Download SGOV daily prices.
2) Compute daily log returns.
3) Sum log returns over a 126-trading-day rolling window (~6 months).
4) Convert back to simple return and clip negative values to 0.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    """Parse command line options for the SGOV 6M workflow."""
    parser = argparse.ArgumentParser(
        description="Compute SGOV-based 6-month risk-free proxy and export results."
    )
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument(
        "--end",
        default=str(date.today()),
        help="End date (YYYY-MM-DD). Default: today's date.",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=126,
        help="Rolling window in trading days. 126 ~= 6 months.",
    )
    parser.add_argument("--out", default="out", help="Output folder")
    parser.add_argument("--plot", action="store_true", help="Save PNG chart")
    parser.add_argument("--debug", action="store_true", help="Print sample rows")
    return parser.parse_args()


def fetch_sgov(start: str, end: str) -> pd.DataFrame:
    """
    Stage 1: Download SGOV daily OHLCV data.

    Returns a dataframe with a standard (single-level) column layout.
    """
    try:
        import yfinance as yf
    except Exception as exc:
        raise SystemExit(
            "Missing dependency yfinance. Run: pip install -r requirements.txt"
        ) from exc

    print("[Stage 1/4] Downloading SGOV prices...")
    df = yf.download("SGOV", start=start, end=end, auto_adjust=False, progress=False)
    if df is None or df.empty:
        raise SystemExit("No data returned for SGOV. Check date range or internet connection.")

    # yfinance can return MultiIndex columns; flatten to single-level names.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df


def compute_rf_6m(df: pd.DataFrame, window: int) -> pd.DataFrame:
    """
    Stage 2: Compute 6M proxy using rolling log-return math.

    Formula:
      daily_log_return_t = ln(P_t / P_(t-1))
      rf_6m_log_t        = sum(daily_log_return over rolling window)
      rf_6m_simple_t     = exp(rf_6m_log_t) - 1
      rf_6m_clipped_t    = max(rf_6m_simple_t, 0)
    """
    if window <= 0:
        raise SystemExit("--window must be a positive integer.")

    price_col = "Adj Close" if "Adj Close" in df.columns else "Close"
    if price_col not in df.columns:
        raise SystemExit("Could not find 'Adj Close' or 'Close' in downloaded data.")

    print("[Stage 2/4] Computing rolling 6M risk-free proxy...")
    working = df[["Date", price_col]].copy()
    working = working.sort_values("Date").reset_index(drop=True)

    px = working[price_col].astype(float)
    working["daily_log_return"] = np.log(px / px.shift(1))
    working["rf_6m_log_raw"] = working["daily_log_return"].rolling(
        window=window, min_periods=window
    ).sum()
    working["rf_6m_simple_raw"] = np.exp(working["rf_6m_log_raw"]) - 1.0

    # Clipping prevents negative risk-free proxy outputs for presentation purposes.
    working["rf_6m_simple_clipped"] = working["rf_6m_simple_raw"].clip(lower=0.0)

    # Rows before the first complete rolling window do not have 6M values.
    working = working.dropna(subset=["rf_6m_simple_raw"]).reset_index(drop=True)
    return working


def save_outputs(df: pd.DataFrame, out_dir: Path, make_plot: bool) -> None:
    """Stage 3: Save tabular outputs, latest-value summary, and optional chart."""
    print("[Stage 3/4] Writing output files...")
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "sgov_rf_6m.csv"
    xlsx_path = out_dir / "sgov_rf_6m.xlsx"
    latest_txt = out_dir / "rf_latest.txt"
    latest_csv = out_dir / "rf_latest.csv"

    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)

    last = df.iloc[-1]
    latest_df = pd.DataFrame(
        [
            {
                "Date": last["Date"],
                "rf_6m_simple_clipped": float(last["rf_6m_simple_clipped"]),
            }
        ]
    )
    latest_df.to_csv(latest_csv, index=False)

    latest_txt.write_text(
        "Date: {date}\nrf_6m_simple_clipped: {value:.6f}\n".format(
            date=last["Date"], value=float(last["rf_6m_simple_clipped"])
        ),
        encoding="utf-8",
    )

    if make_plot:
        import matplotlib.pyplot as plt

        plt.figure(figsize=(9, 4.5))
        plt.plot(df["Date"], df["rf_6m_simple_clipped"], linewidth=1.6)
        plt.title("SGOV 6M Risk-Free Proxy (Simple Return, Clipped at 0)")
        plt.xlabel("Date")
        plt.ylabel("6M simple return")
        plt.tight_layout()
        plt.savefig(out_dir / "sgov_rf_6m.png", dpi=200)
        plt.close()


def print_summary(df: pd.DataFrame, out_dir: Path) -> None:
    """Stage 4: Print final summary to terminal for quick reporting."""
    last = df.iloc[-1]
    print("[Stage 4/4] Completed successfully")
    print(f"Latest date: {last['Date']}")
    print(f"Latest rf_6m_simple_clipped: {float(last['rf_6m_simple_clipped']):.6f}")
    print(f"Outputs saved in: {out_dir.resolve()}")


def main() -> None:
    args = parse_args()
    df_raw = fetch_sgov(args.start, args.end)
    df_rf = compute_rf_6m(df_raw, args.window)

    if args.debug:
        print("[Debug] First 3 rows:")
        print(df_rf.head(3))
        print("[Debug] Last 3 rows:")
        print(df_rf.tail(3))

    out_dir = Path(args.out)
    save_outputs(df_rf, out_dir=out_dir, make_plot=args.plot)
    print_summary(df_rf, out_dir=out_dir)


if __name__ == "__main__":
    main()
