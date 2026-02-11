import argparse
from pathlib import Path
from datetime import date
import sys

import numpy as np
import pandas as pd


def fetch_sgov(start: str, end: str) -> pd.DataFrame:
    try:
        import yfinance as yf
    except Exception:
        raise SystemExit("Missing dependency yfinance. Run: pip install -r requirements.txt")

    df = yf.download("SGOV", start=start, end=end, auto_adjust=False, progress=False)
    if df is None or df.empty:
        raise SystemExit("No data returned for SGOV. Check dates/internet connection.")

    # Flatten columns if MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()
    return df


def compute_rf_6m(df: pd.DataFrame, window: int) -> pd.DataFrame:
    price_col = "Adj Close" if "Adj Close" in df.columns else "Close"
    if price_col not in df.columns:
        raise SystemExit("Could not find 'Adj Close' or 'Close' in downloaded data.")

    df = df[["Date", price_col]].copy()
    df = df.sort_values("Date").reset_index(drop=True)

    px = df[price_col].astype(float)
    df["daily_log_return"] = np.log(px / px.shift(1))

    df["rf_6m_log_raw"] = df["daily_log_return"].rolling(window=window, min_periods=window).sum()
    df["rf_6m_simple_raw"] = np.exp(df["rf_6m_log_raw"]) - 1.0
    df["rf_6m_simple_clipped"] = df["rf_6m_simple_raw"].clip(lower=0.0)

    df = df.dropna(subset=["rf_6m_simple_raw"]).reset_index(drop=True)
    return df


def save_outputs(df: pd.DataFrame, out_dir: Path, make_plot: bool) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "sgov_rf_6m.csv"
    xlsx_path = out_dir / "sgov_rf_6m.xlsx"
    latest_txt = out_dir / "rf_latest.txt"
    latest_csv = out_dir / "rf_latest.csv"

    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)

    last = df.iloc[-1]
    latest_df = pd.DataFrame([{
        "Date": last["Date"],
        "rf_6m_simple_clipped": float(last["rf_6m_simple_clipped"]),
    }])
    latest_df.to_csv(latest_csv, index=False)

    latest_txt.write_text(
        f"Date: {last['Date']}\nrf_6m_simple_clipped: {float(last['rf_6m_simple_clipped']):.6f}\n",
        encoding="utf-8"
    )

    if make_plot:
        import matplotlib.pyplot as plt

        plt.figure()
        plt.plot(df["Date"], df["rf_6m_simple_clipped"])
        plt.title("SGOV 6M Risk-Free Proxy (Simple Return, Clipped)")
        plt.xlabel("Date")
        plt.ylabel("6M simple return")
        plt.tight_layout()
        plt.savefig(out_dir / "sgov_rf_6m.png", dpi=200)
        plt.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True, help="YYYY-MM-DD")
    p.add_argument("--end", default=str(date.today()), help="YYYY-MM-DD (default=today)")
    p.add_argument("--window", type=int, default=126, help="trading days (~6 months)")
    p.add_argument("--out", default="out", help="output folder")
    p.add_argument("--plot", action="store_true", help="save plot PNG")
    p.add_argument("--debug", action="store_true", help="print sample rows")
    args = p.parse_args()

    df_raw = fetch_sgov(args.start, args.end)
    df_rf = compute_rf_6m(df_raw, args.window)

    if args.debug:
        print(df_rf.head(3))
        print(df_rf.tail(3))

    save_outputs(df_rf, Path(args.out), args.plot)

    last = df_rf.iloc[-1]
    print("DONE")
    print(f"Latest date: {last['Date']}")
    print(f"Latest rf_6m_simple_clipped: {float(last['rf_6m_simple_clipped']):.6f}")
    print(f"Outputs saved in: {Path(args.out).resolve()}")


if __name__ == "__main__":
    main()
