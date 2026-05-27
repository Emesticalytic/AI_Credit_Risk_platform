# Scripts

This folder is for repeatable command-line runs that do not require opening Jupyter.

## Intended roles

- `notebooks/`: interactive exploration and narrative analysis
- `scripts/`: headless repeatable runs
- `src/`: reusable project code
- `src/credit_risk_platform/api/main.py`: API deployment entry point

The scripts now self-bootstrap the local `src/` path, so you can run them directly with `python3 scripts/...py` without installing the package first.

## Starter scripts

- `sync_german_credit_data.py`: copy the Statlog source files into `data/raw/statlog_german_credit/`
- `prepare_german_credit_data.py`: create standardized CSV files from the raw Statlog files
- `inspect_german_credit_files.py`: inspect the standardized CSV files and print schema previews
- `run_data_audit.py`: create profile and EDA artifacts from a source CSV
- `run_preprocessing_dry_run.py`: simulate split, outlier summary, and preprocessing checks
- `run_project_bootstrap.py`: verify data, run the first audit, and generate starter artifacts
