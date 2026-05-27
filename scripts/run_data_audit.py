"""Run a lightweight data audit and save artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from credit_risk_platform.analysis.profiling import (
    build_dataframe_profile,
    save_missingness_table,
    save_profile,
)
from credit_risk_platform.utils.io import load_csv
from credit_risk_platform.visualization.plots import (
    save_missingness_chart,
    save_target_distribution_chart,
)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description="Run a starter data audit for a credit dataset.")
    parser.add_argument("--input", required=True, help="Path to the input CSV file.")
    parser.add_argument("--dataset-name", default="credit_dataset", help="Dataset label.")
    parser.add_argument("--target-col", default="TARGET", help="Target column for plots if present.")
    parser.add_argument(
        "--artifacts-dir",
        default="artifacts",
        help="Base directory for generated artifacts.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the audit workflow and write profile outputs."""

    args = parse_args()
    input_path = Path(args.input)
    artifacts_dir = Path(args.artifacts_dir)

    df = load_csv(input_path)

    profile = build_dataframe_profile(df=df, dataset_name=args.dataset_name)
    save_profile(profile, artifacts_dir / "profiles" / f"{args.dataset_name}_profile.json")
    save_missingness_table(df, artifacts_dir / "profiles" / f"{args.dataset_name}_missingness.csv")
    save_missingness_chart(df, artifacts_dir / "eda" / f"{args.dataset_name}_missingness.png")

    if args.target_col in df.columns:
        save_target_distribution_chart(
            df=df,
            target_column=args.target_col,
            output_path=artifacts_dir / "eda" / f"{args.dataset_name}_target_distribution.png",
        )

    print(f"Saved profile outputs to: {artifacts_dir}")


if __name__ == "__main__":
    main()
