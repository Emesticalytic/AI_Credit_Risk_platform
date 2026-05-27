"""Run a first-pass bootstrap workflow for Project 1."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from credit_risk_platform.data.german_credit import (
    default_source_dir,
    interim_german_credit_dir,
    prepare_standardized_german_credit,
    sync_statlog_files,
    verify_statlog_extract,
)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the bootstrap workflow."""

    parser = argparse.ArgumentParser(
        description="Sync, prepare, and profile the Statlog German Credit data."
    )
    parser.add_argument(
        "--dataset-name",
        default="german_credit_standardized",
        help="Dataset label used for generated artifacts.",
    )
    parser.add_argument(
        "--target-col",
        default="TARGET",
        help="Target column used for target distribution output.",
    )
    parser.add_argument(
        "--skip-preprocessing-dry-run",
        action="store_true",
        help="Skip the split and outlier dry-run stage.",
    )
    parser.add_argument(
        "--sync-if-missing",
        action="store_true",
        help="Attempt local sync from the source directory automatically when raw data is missing.",
    )
    parser.add_argument(
        "--source-dir",
        default=str(default_source_dir()),
        help="Local directory containing the Statlog German Credit source files.",
    )
    return parser.parse_args()


def run_python_script(script_path: Path, *args: str) -> None:
    """Run one of the local project scripts with the correct Python path."""

    command = [sys.executable, str(script_path), *args]
    subprocess.run(
        command,
        check=True,
        cwd=PROJECT_ROOT,
        env={**os.environ, "PYTHONPATH": "src"},
    )


def main() -> None:
    """Run verification plus first-pass audit and preprocessing dry-run."""

    args = parse_args()
    source_dir = Path(args.source_dir).expanduser().resolve()
    summary = verify_statlog_extract(PROJECT_ROOT)
    if not summary["is_complete"]:
        if args.sync_if_missing:
            sync_statlog_files(PROJECT_ROOT, source_dir=source_dir, overwrite=False)
            summary = verify_statlog_extract(PROJECT_ROOT)
        if not summary["is_complete"]:
            print("Statlog German Credit extract is incomplete. Missing files:")
            for filename in summary["missing_files"]:
                print(f"- {filename}")
            print("Run scripts/sync_german_credit_data.py first.")
            raise SystemExit(1)

    prepare_standardized_german_credit(PROJECT_ROOT)
    standardized_path = (
        interim_german_credit_dir(PROJECT_ROOT) / "german_credit_standardized.csv"
    )

    run_python_script(
        PROJECT_ROOT / "scripts" / "run_data_audit.py",
        "--input",
        str(standardized_path),
        "--dataset-name",
        args.dataset_name,
        "--target-col",
        args.target_col,
        "--artifacts-dir",
        "artifacts",
    )

    if not args.skip_preprocessing_dry_run:
        run_python_script(
            PROJECT_ROOT / "scripts" / "run_preprocessing_dry_run.py",
            "--input",
            str(standardized_path),
            "--target-col",
            args.target_col,
            "--artifacts-dir",
            "artifacts",
        )

    print("Bootstrap completed successfully.")


if __name__ == "__main__":
    main()
