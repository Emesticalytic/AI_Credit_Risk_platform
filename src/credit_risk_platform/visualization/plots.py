"""Plotting helpers for saved artifacts."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MPL_CACHE_DIR = PROJECT_ROOT / ".mpl-cache"
MPL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))

import matplotlib
import pandas as pd


matplotlib.use("Agg")
import matplotlib.pyplot as plt


def save_missingness_chart(df: pd.DataFrame, output_path: Path, top_n: int = 20) -> None:
    """Save a missingness bar chart for the most incomplete columns."""

    missingness = df.isna().mean().sort_values(ascending=False).head(top_n)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 6))
    missingness.sort_values().plot(kind="barh")
    plt.title("Top Missingness Columns")
    plt.xlabel("Missing Share")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def save_target_distribution_chart(
    df: pd.DataFrame,
    target_column: str,
    output_path: Path,
) -> None:
    """Save a target distribution chart if the target column exists."""

    if target_column not in df.columns:
        raise KeyError(f"Target column '{target_column}' not found in dataframe.")

    counts = df[target_column].value_counts(dropna=False).sort_index()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))
    counts.plot(kind="bar")
    plt.title(f"Target Distribution: {target_column}")
    plt.xlabel(target_column)
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
