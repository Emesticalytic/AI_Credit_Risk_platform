"""Sync local Statlog German Credit files into the project raw-data directory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from credit_risk_platform.data.german_credit import default_source_dir, sync_statlog_files


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description="Sync Statlog German Credit source files.")
    parser.add_argument(
        "--source-dir",
        default=str(default_source_dir()),
        help="Local directory containing german.data, german.data-numeric, german.doc, and Index.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files in data/raw/statlog_german_credit.",
    )
    parser.add_argument(
        "--output",
        default="artifacts/profiles/german_credit_sync_summary.json",
        help="Optional JSON summary output path.",
    )
    return parser.parse_args()


def main() -> None:
    """Sync local Statlog files and write a summary artifact."""

    args = parse_args()
    source_dir = Path(args.source_dir).expanduser().resolve()
    summary = sync_statlog_files(PROJECT_ROOT, source_dir=source_dir, overwrite=args.overwrite)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2))

    print(json.dumps(summary, indent=2))

    if not summary["verification"]["is_complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
