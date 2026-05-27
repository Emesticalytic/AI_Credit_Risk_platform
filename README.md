# AI Credit Risk and Financial Intelligence Platform

This project is a production-style credit risk platform built around the open Statlog German Credit dataset. The objective is to move beyond model training and build a deployable decision-support system with clear business value.

## Business Problem

Lenders do not only need a model score. They need a reliable way to reduce default risk, protect portfolio quality, and make consistent approval decisions across large applicant volumes. Without a structured risk workflow, teams can approve too many risky loans, reject too many good borrowers, or make decisions that are hard to explain to stakeholders.

## Stakeholder Decision

The core decision is:

- should this applicant be approved, reviewed manually, or rejected?

Secondary stakeholder questions include:

- which customer segments are driving portfolio risk?
- what factors explain elevated default probability?
- how do approval thresholds change expected loss and approval rate?

## Business Objective

Predict the probability of default for loan applicants and translate model outputs into business actions such as:

- approve
- manual review
- reject

The project should also support:

- expected loss analysis
- portfolio risk segmentation
- model explainability
- deployment and monitoring
- retraining and feedback-loop design

## Core Workflow

1. Business problem framing and stakeholder mapping
2. Business understanding and target definition
3. Data ingestion and schema validation
4. EDA and data profiling
5. Data cleaning and quality remediation
6. Split strategy and leakage control
7. Outlier detection and preprocessing design
8. Feature engineering from relational credit tables
9. Baseline and advanced model development
10. Evaluation and threshold strategy
11. Explainability with SHAP
12. API and dashboard deployment
13. Monitoring, drift checks, and feedback-loop design

## Dataset

- Primary target dataset: Statlog German Credit
- Supporting alternatives: South German Credit, Credit Approval, Default of Credit Card Clients

## Data Access

The preferred setup is to sync the open Statlog files into the project and then prepare standardized CSVs for analysis.

Expected flow:

1. place the Statlog files in a local directory
2. run the sync script
3. prepare standardized CSV files
4. run the project bootstrap

Starter data helpers:

- [scripts/sync_german_credit_data.py](/Users/ememakpan/Documents/New project/applied_ai_economics_portfolio/project_01_ai_credit_risk_platform/scripts/sync_german_credit_data.py)
- [scripts/prepare_german_credit_data.py](/Users/ememakpan/Documents/New project/applied_ai_economics_portfolio/project_01_ai_credit_risk_platform/scripts/prepare_german_credit_data.py)
- [scripts/inspect_german_credit_files.py](/Users/ememakpan/Documents/New project/applied_ai_economics_portfolio/project_01_ai_credit_risk_platform/scripts/inspect_german_credit_files.py)
- [scripts/run_project_bootstrap.py](/Users/ememakpan/Documents/New project/applied_ai_economics_portfolio/project_01_ai_credit_risk_platform/scripts/run_project_bootstrap.py)

## Repo Structure

```text
project_01_ai_credit_risk_platform/
├── artifacts/
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── docs/
├── notebooks/
├── scripts/
├── src/credit_risk_platform/
├── tests/
├── reports/
│   ├── figures/
│   ├── tables/
│   └── executive_summary/
├── Makefile
├── pyproject.toml
└── README.md
```

## Working Layout

- `notebooks/`: interactive Jupyter analysis, EDA, cleaning review, split strategy, and modeling walkthroughs
- `src/credit_risk_platform/`: reusable project code called by notebooks and scripts
- `scripts/`: runnable Python entry points for repeatable, non-notebook tasks
- `src/credit_risk_platform/api/main.py`: deployable API layer
- `artifacts/`: machine-generated outputs such as profiles, plots, model metadata, and monitoring summaries
- `reports/`: curated stakeholder-facing outputs

## First Direct-Load Run

After the Statlog files are available locally:

```bash
cd "/Users/ememakpan/Documents/New project/applied_ai_economics_portfolio/project_01_ai_credit_risk_platform"
python3 scripts/sync_german_credit_data.py --source-dir "/Users/ememakpan/Downloads/statlog+german+credit+data"
python3 scripts/prepare_german_credit_data.py
python3 scripts/run_project_bootstrap.py
```

This should generate starter outputs in:

- `artifacts/profiles/`
- `artifacts/eda/`
- `artifacts/monitoring/`

## First Build Milestones

- Set up data contracts and ingestion workflow
- Create profiling and EDA artifacts
- Build cleaning, outlier, preprocessing, and feature pipelines
- Train baseline and boosted models
- Add SHAP explanations and threshold analysis
- Expose a `FastAPI` scoring service
- Add `Prometheus` metrics and drift checks

See [docs/build_roadmap.md](/Users/ememakpan/Documents/New project/applied_ai_economics_portfolio/project_01_ai_credit_risk_platform/docs/build_roadmap.md) for the detailed sequence.
See [docs/professional_workflow.md](/Users/ememakpan/Documents/New project/applied_ai_economics_portfolio/project_01_ai_credit_risk_platform/docs/professional_workflow.md) for the recommended professional structure.

## API and Docker Deployment

The trained champion model is served through a `FastAPI` scoring service. The API loads the saved random forest pipeline from:

```text
models/random_forest_champion_pipeline.joblib
```

Run the API locally with Docker:

```bash
cd "/Users/ememakpan/Documents/New project/applied_ai_economics_portfolio/project_01_ai_credit_risk_platform"
docker compose build credit-risk-api
docker compose up credit-risk-api
```

Open the interactive API documentation:

```text
http://127.0.0.1:8002/docs
```

Useful API endpoints:

- `GET /`: confirms the credit risk API is running
- `GET /health`: confirms the service is healthy and the model file is available
- `GET /model/summary`: returns champion model and feature metadata
- `GET /decision_policy`: shows the approve, manual review, and reject thresholds
- `POST /predict`: scores one applicant
- `POST /batch_predict`: scores multiple applicants
- `GET /metrics`: returns lightweight request, prediction, latency, and decision counts
- `GET /prometheus`: exposes Prometheus-compatible monitoring metrics

The API returns a model score plus a business decision:

```json
{
  "high_risk_probability": 0.667,
  "predicted_label": "high_risk",
  "risk_band": "high",
  "decision": "reject",
  "reason": "Applicant meets or exceeds the rejection threshold.",
  "recommended_action": "Reject or send for strict senior credit review depending on policy."
}
```

Prediction events are logged to:

```text
artifacts/logs/prediction_log.csv
```

This log supports the monitoring and feedback-loop stage of the project by recording incoming applicant features, model scores, risk bands, and business decisions.

## Prometheus and Grafana Monitoring

The Docker Compose stack also includes a small MLOps monitoring layer:

- `Prometheus` scrapes model-serving metrics from the API
- `Grafana` visualizes request activity, prediction volume, decision mix, risk score, and latency
- the API exposes machine-readable monitoring data at `GET /prometheus`

Start the full local monitoring stack:

```bash
docker compose up -d credit-risk-api prometheus grafana
```

Open the services:

```text
FastAPI Swagger: http://127.0.0.1:8002/docs
Prometheus:      http://127.0.0.1:9090
Grafana:         http://127.0.0.1:3000
```

Grafana login:

```text
username: admin
password: admin
```

The dashboard is provisioned automatically from:

```text
monitoring/grafana/dashboards/credit-risk-api-dashboard.json
```

To generate visible dashboard activity, submit a few requests to `POST /predict` or `POST /batch_predict`, then refresh Grafana.
