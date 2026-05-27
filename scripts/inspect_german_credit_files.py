"""Inspect standardized German Credit files in the project."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from credit_risk_platform.data.german_credit import interim_german_credit_dir
from credit_risk_platform.utils.io import load_csv


def main() -> None:
    """Print quick summaries for standardized German Credit CSV files."""

    interim_dir = interim_german_credit_dir(PROJECT_ROOT)
    csv_files = sorted(interim_dir.glob("*.csv"))
    if not csv_files:
        print(f"No standardized CSV files found in {interim_dir}")
        return

    for csv_path in csv_files:
        frame = load_csv(csv_path).head(5)
        print(f"\n=== {csv_path.name} ===")
        print(f"rows previewed: {len(frame)}")
        print(f"columns: {len(frame.columns)}")
        print("sample columns:", ", ".join(frame.columns[:10]))
        print(frame.head(2).to_string(index=False))


if __name__ == "__main__":
    main()
