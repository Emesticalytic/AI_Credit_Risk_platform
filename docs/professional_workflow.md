# Professional Workflow

This document sets the intended project order for a clean, industry-style credit risk workflow.

## Recommended Sequence

1. Business problem
   Define the lending pain point, stakeholder decisions, and business constraints.

2. Objective and target definition
   Define the prediction target, success metrics, and decision thresholds at a conceptual level.

3. Raw data ingestion
   Load all source tables without altering the originals in `data/raw/`.

4. Data profiling and EDA
   Review:

   - schema and table relationships
   - target balance
   - missingness
   - duplicates
   - impossible values
   - segment-level default patterns
   - early leakage risks

5. Data cleaning plan
   Create explicit cleaning rules before changing data:

   - column type fixes
   - duplicate treatment
   - invalid value handling
   - category standardization
   - business rule checks

6. Split strategy
   Decide the split before fitting learned preprocessing steps.

   Preferred order:

   - use time-based split if a reliable application timeline exists
   - otherwise use stratified train, validation, and test split

7. Outlier detection and treatment design
   Detect outliers on the training split and define reproducible handling.

   Suitable approaches:

   - percentile clipping
   - winsorization
   - log transform for skewed financial variables
   - business-rule flags for suspicious values

   Do not let validation or test data influence learned thresholds.

8. Preprocessing pipeline
   Fit transformations on train only:

   - missing-value imputation
   - rare category grouping
   - encoding
   - scaling where required
   - outlier clipping transformer

9. Feature engineering
   Build borrower-level relational aggregates and behavior features.

10. Modeling
    Start with baseline interpretable models, then move to stronger ensemble methods.

11. Evaluation
    Review:

    - ROC-AUC
    - PR-AUC
    - calibration
    - confusion matrix
    - threshold tradeoffs
    - expected loss
    - approval and rejection mix

12. Explainability
    Add global and local SHAP views and business-facing explanation summaries.

13. Deployment
    Expose scoring and health endpoints and connect a lightweight dashboard.

14. Monitoring and feedback loop
    Track service health, score drift, feature drift, approval drift, and delayed repayment outcomes for retraining decisions.

## Working Rule

EDA can inspect the full raw dataset.

Any step that learns values from data must be fit on the training data only. This includes:

- imputation values
- scaling parameters
- encoding mappings
- outlier thresholds
- feature selection logic

## Recommended `src/` Modules

As implementation grows, keep reusable logic outside notebooks.

- `data/`: ingestion, schema checks, joins
- `analysis/`: profiling and EDA helpers
- `cleaning/`: data correction and validation rules
- `preprocessing/`: imputers, encoders, split logic, outlier transformers
- `features/`: relational aggregates and feature builders
- `models/`: training and registry logic
- `evaluation/`: metrics, calibration, threshold analysis
- `explainability/`: SHAP and explanation formatting
- `monitoring/`: drift checks and service metrics
- `api/`: scoring service
