# Notebook Plan

The first six starter notebooks now exist. Continue in this order:

1. `01_business_problem_and_stakeholders.ipynb`
2. `02_business_understanding_and_target_definition.ipynb`
3. `03_data_audit_and_eda.ipynb`
4. `04_data_cleaning_plan.ipynb`
5. `05_split_strategy_and_leakage_control.ipynb`
6. `06_outlier_detection_and_preprocessing.ipynb`
7. `07_feature_engineering.ipynb`
8. `08_baseline_models.ipynb`
9. `09_boosting_models.ipynb`
10. `10_model_evaluation_and_thresholds.ipynb`
11. `11_explainability.ipynb`
12. `12_monitoring_and_drift.ipynb`

Keep the notebooks presentation-oriented and move reusable logic into `src/`.

Each notebook now starts by adding the local `src/` directory to `sys.path`, so the notebook can import project code before the package is installed.
