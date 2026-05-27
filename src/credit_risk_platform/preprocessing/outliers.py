"""Outlier review helpers for the credit risk platform."""

from __future__ import annotations

import pandas as pd


def numeric_outlier_summary(
    df: pd.DataFrame,
    quantile_low: float = 0.01,
    quantile_high: float = 0.99,
) -> pd.DataFrame:
    """Summarize numeric clipping thresholds for candidate outlier handling."""

    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        return pd.DataFrame(columns=["column", "q_low", "q_high"])

    summary = pd.DataFrame(
        {
            "column": numeric_df.columns,
            "q_low": numeric_df.quantile(quantile_low).values,
            "q_high": numeric_df.quantile(quantile_high).values,
        }
    )
    return summary.sort_values("column").reset_index(drop=True)
