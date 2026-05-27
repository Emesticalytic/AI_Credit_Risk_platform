"""Basic data quality helpers for early-stage analysis."""

from __future__ import annotations

import pandas as pd


def summarize_duplicate_rows(df: pd.DataFrame) -> dict[str, int]:
    """Return duplicate row counts for quick data quality review."""

    duplicate_rows = int(df.duplicated().sum())
    unique_rows = int(df.drop_duplicates().shape[0])
    return {
        "duplicate_rows": duplicate_rows,
        "unique_rows_after_deduplication": unique_rows,
    }
