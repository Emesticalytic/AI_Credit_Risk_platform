"""Tests for Statlog German Credit data helpers."""

from pathlib import Path

from credit_risk_platform.data.german_credit import (
    expected_statlog_files,
    interim_german_credit_dir,
    missing_statlog_files,
    original_column_names,
    raw_german_credit_dir,
    verify_statlog_extract,
)


def test_expected_statlog_files_contains_german_data() -> None:
    assert "german.data" in expected_statlog_files()


def test_original_column_names_include_target() -> None:
    assert original_column_names()[-1] == "risk_class"


def test_missing_statlog_files_detects_missing_files(tmp_path: Path) -> None:
    raw_dir = raw_german_credit_dir(tmp_path)
    raw_dir.mkdir(parents=True)
    missing = missing_statlog_files(tmp_path)
    assert "german.data" in missing


def test_verify_statlog_extract_reports_incomplete_when_empty(tmp_path: Path) -> None:
    raw_german_credit_dir(tmp_path).mkdir(parents=True)
    summary = verify_statlog_extract(tmp_path)
    assert summary["exists"] is True
    assert summary["is_complete"] is False


def test_interim_dir_helper_returns_expected_path(tmp_path: Path) -> None:
    assert interim_german_credit_dir(tmp_path).name == "statlog_german_credit"
