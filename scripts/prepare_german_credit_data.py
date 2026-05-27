"""Prepare standardized CSV files from raw Statlog German Credit files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from credit_risk_platform.data.german_credit import prepare_standardized_german_credit


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description="Prepare standardized German Credit CSV files.")
    parser.add_argument(
        "--output",
        default="artifacts/profiles/german_credit_prepare_summary.json",
        help="Optional JSON summary output path.",
    )
    return parser.parse_args()


def main() -> None:
    """Prepare standardized data and write a summary artifact."""

    args = parse_args()
    summary = prepare_standardized_german_credit(PROJECT_ROOT)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2))

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
