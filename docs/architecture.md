# Architecture

```mermaid
flowchart LR
    A["Statlog German Credit raw files"] --> B["Ingestion and schema validation"]
    B --> C["EDA and data profiling"]
    C --> D["Preprocessing and leakage control"]
    D --> E["Feature engineering"]
    E --> F["Train, validation, test workflow"]
    F --> G["Baseline and boosted models"]
    G --> H["Threshold strategy and expected loss logic"]
    G --> I["SHAP explainability"]
    G --> J["MLflow tracking"]
    H --> K["FastAPI scoring service"]
    K --> L["Prometheus metrics"]
    L --> M["Dashboard and monitoring layer"]
    K --> N["Feedback-loop storage design"]
```

## System Intent

This project is designed as a business-grade analytical product rather than a notebook-only exercise.

## Key Design Principles

- separate EDA from preprocessing and modeling
- avoid target leakage across joined credit tables
- keep reproducible training and scoring contracts
- support both analysts and non-technical stakeholders
- design for observability from the beginning
