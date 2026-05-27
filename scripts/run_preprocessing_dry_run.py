"""Run a dry-run preprocessing review for a credit dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from credit_risk_platform.preprocessing.outliers import numeric_outlier_summary
from credit_risk_platform.preprocessing.split import split_frame
from credit_risk_platform.utils.io import load_csv


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description="Run split and outlier dry-run checks.")
    parser.add_argument("--input", required=True, help="Path to the input CSV file.")
    parser.add_argument("--target-col", default="TARGET", help="Target column used for splitting.")
    parser.add_argument(
        "--artifacts-dir",
        default="artifacts",
        help="Base directory for generated artifacts.",
    )
    return parser.parse_args()


def main() -> None:
    """Run split and outlier review outputs."""

    args = parse_args()
    df = load_csv(Path(args.input))
    split_result = split_frame(df=df, target_column=args.target_col)
    outlier_table = numeric_outlier_summary(split_result.train)

    artifacts_dir = Path(args.artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    split_summary = {
        "train_rows": int(split_result.train.shape[0]),
        "validation_rows": int(split_result.validation.shape[0]),
        "test_rows": int(split_result.test.shape[0]),
        "target_column": args.target_col,
    }
    (artifacts_dir / "profiles").mkdir(parents=True, exist_ok=True)
    (artifacts_dir / "monitoring").mkdir(parents=True, exist_ok=True)

    (artifacts_dir / "profiles" / "split_summary.json").write_text(json.dumps(split_summary, indent=2))
    outlier_table.to_csv(artifacts_dir / "monitoring" / "train_outlier_summary.csv", index=False)

    print(f"Saved split summary and outlier review to: {artifacts_dir}")


if __name__ == "__main__":
    main()
