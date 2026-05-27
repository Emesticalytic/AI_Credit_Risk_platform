"""Tests for split utilities."""

import pandas as pd

from credit_risk_platform.preprocessing.split import split_frame


def test_split_frame_returns_all_partitions() -> None:
    df = pd.DataFrame(
        {
            "feature_a": range(50),
            "TARGET": [0, 1] * 25,
        }
    )

    result = split_frame(df=df, target_column="TARGET", random_state=7)

    assert len(result.train) + len(result.validation) + len(result.test) == len(df)
    assert not result.train.empty
    assert not result.validation.empty
    assert not result.test.empty
