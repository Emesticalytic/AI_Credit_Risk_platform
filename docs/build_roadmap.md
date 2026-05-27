# Build Roadmap

## Phase 0: Business Framing

1. Define the lending decision problem
2. Identify stakeholder groups and decision points
3. Translate business risk into measurable success metrics
4. Document constraints, assumptions, and explainability needs

## Phase 1: Foundation

1. Load application and relational tables into `data/raw/`
2. Validate schema and key columns
3. Produce data profile and EDA outputs
4. Document cleaning rules and unresolved data issues
5. Define train, validation, and test split strategy

## Phase 2: Cleaning and Preprocessing

1. Standardize column names and data types
2. Remove or flag duplicates
3. Handle impossible values and inconsistent categorical values
4. Define missing-value strategy by variable type and business meaning
5. Define outlier detection and treatment rules
6. Build reusable preprocessing pipeline fit on train only

## Phase 3: Modeling

1. Engineer relational aggregate features
3. Train baseline logistic regression
4. Train `RandomForest`, `XGBoost`, and `LightGBM`
5. Compare metrics and calibration

## Phase 4: Business Decisioning

1. Define approve, review, and reject thresholds
2. Estimate approval rate, bad rate, and expected loss
3. Create segment-level risk analysis
4. Build SHAP explanation views

## Phase 5: Production-Style Delivery

1. Expose `/health`, `/predict`, and `/model/summary`
2. Add Prometheus metrics
3. Simulate drift checks on a new scoring batch
4. Define feedback-loop and retraining workflow
