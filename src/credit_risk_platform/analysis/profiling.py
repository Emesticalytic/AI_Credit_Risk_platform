"""Data profiling helpers for the credit risk platform."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def build_dataframe_profile(df: pd.DataFrame, dataset_name: str) -> dict[str, Any]:
    """Build a lightweight profile for a dataframe.

    The profile is intentionally simple so it can be used before a full
    profiling tool is introduced.
    """

    missingness = (
        df.isna()
        .mean()
        .sort_values(ascending=False)
        .rename("missing_share")
        .reset_index()
        .rename(columns={"index": "column"})
    )

    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    categorical_columns = [column for column in df.columns if column not in numeric_columns]

    return {
        "dataset_name": dataset_name,
        "row_count": int(df.shape[0]),
        "column_count": int(df.shape[1]),
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "top_missing_columns": missingness.head(20).to_dict(orient="records"),
    }


def save_profile(profile: dict[str, Any], output_path: Path) -> None:
    """Save a dataframe profile as JSON."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(profile, indent=2))


def save_missingness_table(df: pd.DataFrame, output_path: Path) -> None:
    """Save a missingness summary for later review."""

    table = (
        df.isna()
        .mean()
        .sort_values(ascending=False)
        .rename("missing_share")
        .reset_index()
        .rename(columns={"index": "column"})
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output_path, index=False)
