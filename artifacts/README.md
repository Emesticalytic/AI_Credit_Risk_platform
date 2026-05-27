# Artifact Layout

This folder stores generated outputs from scripts and notebooks.

- `eda/`: saved charts such as target distribution, missingness, and segment visuals
- `profiles/`: JSON or CSV profiling outputs
- `models/`: lightweight metadata or local model summaries
- `monitoring/`: drift and monitoring summaries

Typical first-run outputs:

- `profiles/german_credit_sync_summary.json`
- `profiles/german_credit_prepare_summary.json`
- `profiles/german_credit_standardized_profile.json`
- `profiles/german_credit_standardized_missingness.csv`
- `eda/german_credit_standardized_missingness.png`
- `eda/german_credit_standardized_target_distribution.png`
- `monitoring/train_outlier_summary.csv`

Use `artifacts/` for machine-generated working outputs.

Use `reports/` for polished stakeholder-facing deliverables.
