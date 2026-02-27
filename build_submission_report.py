"""
Build a PDF submission report from SGOV 6M outputs.

The report includes:
- Project summary and stage-by-stage methodology
- Latest computed 6M proxy value
- Full time-series chart
- Captured terminal run output
"""

from __future__ import annotations

import argparse
import textwrap
from datetime import date
from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate SGOV submission PDF report.")
    parser.add_argument(
        "--project-dir",
        default=".",
        help="Project root containing out/ and sample_output.txt",
    )
    parser.add_argument(
        "--author",
        default="Your Name",
        help="Author name shown in the report",
    )
    parser.add_argument(
        "--declaration",
        default=(
            "I confirm this code and analysis were prepared by me for course submission."
        ),
        help="Authorship declaration text to print in the report",
    )
    parser.add_argument(
        "--output",
        default="SGOV_Submission_Report.pdf",
        help="PDF output filename",
    )
    return parser.parse_args()


def require_file(path: Path) -> Path:
    # Fail fast with a clear message when expected pipeline outputs are missing.
    if not path.exists():
        raise SystemExit(f"Required file not found: {path}")
    return path


def _wrapped(lines: list[str], width: int = 100) -> str:
    chunks: list[str] = []
    for line in lines:
        wrapped = textwrap.fill(line, width=width)
        chunks.append(wrapped)
    return "\n".join(chunks)


def page_overview(pdf: PdfPages, author: str, declaration: str, latest_date: str, latest_value: float) -> None:
    fig = plt.figure(figsize=(11, 8.5))
    fig.suptitle("SGOV 6-Month Risk-Free Proxy: Submission Report", fontsize=18, fontweight="bold", y=0.97)

    body_lines = [
        f"Author: {author}",
        f"Generated on: {date.today().isoformat()}",
        "",
        "Project objective:",
        "Compute a 6-month risk-free return proxy from SGOV daily prices.",
        "",
        "Methodology (stage by stage):",
        "1) Stage 1 - Download SGOV daily price data from Yahoo Finance.",
        "2) Stage 2 - Compute daily log returns and sum over a rolling 126-day window.",
        "3) Stage 3 - Convert to simple return and clip negatives at 0 for the final proxy.",
        "4) Stage 4 - Export CSV/XLSX/TXT and print terminal summary.",
        "",
        "Latest computed result:",
        f"Date: {latest_date}",
        f"rf_6m_simple_clipped: {latest_value:.6f}",
        "",
        "Authorship declaration:",
        declaration,
    ]

    fig.text(0.06, 0.88, _wrapped(body_lines), fontsize=11, va="top", family="monospace")
    fig.text(0.06, 0.04, "Supporting files: sgov_rf_6m.py, README.md, out/, sample_output.txt", fontsize=9)
    pdf.savefig(fig)
    plt.close(fig)


def page_chart(pdf: PdfPages, df: pd.DataFrame) -> None:
    plot_df = df.copy()
    plot_df["Date"] = pd.to_datetime(plot_df["Date"])

    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.plot(plot_df["Date"], plot_df["rf_6m_simple_clipped"], linewidth=1.8)
    ax.set_title("SGOV 6M Risk-Free Proxy (Simple Return, Clipped at 0)", fontsize=15)
    ax.set_xlabel("Date")
    ax.set_ylabel("6M simple return")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def page_terminal_output(pdf: PdfPages, output_text: str) -> None:
    fig = plt.figure(figsize=(11, 8.5))
    fig.suptitle("Terminal Run Output", fontsize=16, fontweight="bold", y=0.97)

    display_text = output_text.strip() or "No terminal output captured."
    fig.text(
        0.06,
        0.9,
        display_text,
        fontsize=10,
        va="top",
        family="monospace",
    )
    pdf.savefig(fig)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    project_dir = Path(args.project_dir).resolve()
    out_dir = project_dir / "out"

    latest_csv = require_file(out_dir / "rf_latest.csv")
    full_csv = require_file(out_dir / "sgov_rf_6m.csv")
    sample_output_path = require_file(project_dir / "sample_output.txt")

    # Latest snapshot is used on the overview page.
    latest_df = pd.read_csv(latest_csv)
    if latest_df.empty:
        raise SystemExit(f"No rows found in {latest_csv}")

    latest_row = latest_df.iloc[-1]
    latest_date = str(latest_row["Date"])
    latest_value = float(latest_row["rf_6m_simple_clipped"])

    # Full history is used for the time-series chart page.
    full_df = pd.read_csv(full_csv)
    if full_df.empty:
        raise SystemExit(f"No rows found in {full_csv}")

    terminal_output = sample_output_path.read_text(encoding="utf-8")

    output_pdf = project_dir / args.output
    with PdfPages(output_pdf) as pdf:
        page_overview(
            pdf=pdf,
            author=args.author,
            declaration=args.declaration,
            latest_date=latest_date,
            latest_value=latest_value,
        )
        page_chart(pdf=pdf, df=full_df)
        page_terminal_output(pdf=pdf, output_text=terminal_output)

    print(f"PDF report generated: {output_pdf}")


if __name__ == "__main__":
    main()
