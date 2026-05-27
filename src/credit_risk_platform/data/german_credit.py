"""Helpers for locating, syncing, and preparing the Statlog German Credit data."""

from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd


def raw_german_credit_dir(project_root: Path) -> Path:
    """Return the expected raw Statlog German Credit directory."""

    return project_root / "data" / "raw" / "statlog_german_credit"


def interim_german_credit_dir(project_root: Path) -> Path:
    """Return the expected interim directory for standardized German Credit files."""

    return project_root / "data" / "interim" / "statlog_german_credit"


def default_source_dir() -> Path:
    """Return the default local download location if it exists."""

    return Path.home() / "Downloads" / "statlog+german+credit+data"


def expected_statlog_files() -> list[str]:
    """Return the expected Statlog German Credit file names."""

    return [
        "german.data",
        "german.data-numeric",
        "german.doc",
        "Index",
    ]


def original_column_names() -> list[str]:
    """Return professional column names for the original German Credit file."""

    return [
        "checking_account_status",
        "duration_months",
        "credit_history",
        "purpose",
        "credit_amount",
        "savings_account",
        "employment_duration",
        "installment_rate_pct_income",
        "personal_status_sex",
        "other_debtors_guarantors",
        "present_residence_years",
        "property_type",
        "age_years",
        "other_installment_plans",
        "housing",
        "existing_credits_count",
        "job_type",
        "liable_people_count",
        "telephone",
        "foreign_worker",
        "risk_class",
    ]


def numeric_column_names() -> list[str]:
    """Return placeholder column names for the numeric Statlog variant."""

    return [f"numeric_feature_{index:02d}" for index in range(1, 25)] + ["risk_class"]


def existing_statlog_files(project_root: Path) -> list[Path]:
    """Return raw Statlog files currently present on disk."""

    return sorted(raw_german_credit_dir(project_root).glob("*"))


def missing_statlog_files(project_root: Path) -> list[str]:
    """Return expected Statlog files that are not present."""

    raw_dir = raw_german_credit_dir(project_root)
    return [filename for filename in expected_statlog_files() if not (raw_dir / filename).exists()]


def verify_statlog_extract(project_root: Path) -> dict[str, object]:
    """Return a structured summary of the raw Statlog data directory."""

    raw_dir = raw_german_credit_dir(project_root)
    existing_files = existing_statlog_files(project_root)
    missing_files = missing_statlog_files(project_root)
    return {
        "raw_dir": str(raw_dir),
        "exists": raw_dir.exists(),
        "existing_files": [path.name for path in existing_files],
        "missing_files": missing_files,
        "is_complete": len(missing_files) == 0,
    }


def sync_statlog_files(project_root: Path, source_dir: Path, overwrite: bool = False) -> dict[str, object]:
    """Copy Statlog source files into the project raw-data directory."""

    raw_dir = raw_german_credit_dir(project_root)
    raw_dir.mkdir(parents=True, exist_ok=True)

    copied_files: list[str] = []
    for filename in expected_statlog_files():
        source_path = source_dir / filename
        destination_path = raw_dir / filename
        if not source_path.exists():
            continue
        if destination_path.exists() and not overwrite:
            continue
        shutil.copy2(source_path, destination_path)
        copied_files.append(filename)

    verification = verify_statlog_extract(project_root)
    return {
        "source_dir": str(source_dir),
        "raw_dir": str(raw_dir),
        "copied_files": copied_files,
        "verification": verification,
    }


def load_original_german_credit(raw_file_path: Path) -> pd.DataFrame:
    """Load the original categorical German Credit dataset."""

    df = pd.read_csv(
        raw_file_path,
        sep=r"\s+",
        header=None,
        names=original_column_names(),
    )
    df["risk_label"] = df["risk_class"].map({1: "good", 2: "bad"})
    df["TARGET"] = (df["risk_class"] == 2).astype(int)
    df.insert(0, "applicant_id", range(1, len(df) + 1))
    return df


def load_numeric_german_credit(raw_file_path: Path) -> pd.DataFrame:
    """Load the numeric Statlog German Credit dataset."""

    df = pd.read_csv(
        raw_file_path,
        sep=r"\s+",
        header=None,
        names=numeric_column_names(),
    )
    df["risk_label"] = df["risk_class"].map({1: "good", 2: "bad"})
    df["TARGET"] = (df["risk_class"] == 2).astype(int)
    df.insert(0, "applicant_id", range(1, len(df) + 1))
    return df


def prepare_standardized_german_credit(project_root: Path) -> dict[str, object]:
    """Create standardized CSV files from the raw Statlog source files."""

    raw_dir = raw_german_credit_dir(project_root)
    interim_dir = interim_german_credit_dir(project_root)
    interim_dir.mkdir(parents=True, exist_ok=True)

    categorical_df = load_original_german_credit(raw_dir / "german.data")
    numeric_df = load_numeric_german_credit(raw_dir / "german.data-numeric")

    categorical_output = interim_dir / "german_credit_standardized.csv"
    numeric_output = interim_dir / "german_credit_numeric_standardized.csv"

    categorical_df.to_csv(categorical_output, index=False)
    numeric_df.to_csv(numeric_output, index=False)

    return {
        "categorical_output": str(categorical_output),
        "numeric_output": str(numeric_output),
        "categorical_rows": int(categorical_df.shape[0]),
        "numeric_rows": int(numeric_df.shape[0]),
        "categorical_columns": int(categorical_df.shape[1]),
        "numeric_columns": int(numeric_df.shape[1]),
    }
