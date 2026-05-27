"""Split helpers for train, validation, and test workflows."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.model_selection import train_test_split


@dataclass
class SplitResult:
    """Container for train, validation, and test partitions."""

    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def split_frame(
    df: pd.DataFrame,
    target_column: str,
    test_size: float = 0.2,
    validation_size: float = 0.2,
    random_state: int = 42,
    stratify: bool = True,
) -> SplitResult:
    """Split a dataframe into train, validation, and test partitions."""

    if target_column not in df.columns:
        raise KeyError(f"Target column '{target_column}' not found in dataframe.")

    stratify_values = df[target_column] if stratify else None
    train_validation, test = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_values,
    )

    validation_share_of_train_validation = validation_size / (1 - test_size)
    validation_stratify = train_validation[target_column] if stratify else None
    train, validation = train_test_split(
        train_validation,
        test_size=validation_share_of_train_validation,
        random_state=random_state,
        stratify=validation_stratify,
    )

    return SplitResult(
        train=train.reset_index(drop=True),
        validation=validation.reset_index(drop=True),
        test=test.reset_index(drop=True),
    )
