"""Input and output helpers for the credit risk platform."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def discover_csv_files(directory: Path) -> list[Path]:
    """Return CSV files in a directory sorted by name."""

    if not directory.exists():
        return []
    return sorted(directory.glob("*.csv"))


def load_csv(dataset_path: Path) -> pd.DataFrame:
    """Load a CSV dataset from disk."""

    return pd.read_csv(dataset_path)
