"""FastAPI scoring service for the credit risk platform."""

import csv
from functools import lru_cache
from pathlib import Path
from time import perf_counter
from datetime import datetime, timezone
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, ConfigDict, Field

from credit_risk_platform.config import PROJECT_ROOT


MODEL_PATH = PROJECT_ROOT / "models" / "random_forest_champion_pipeline.joblib"
PREDICTION_LOG_PATH = PROJECT_ROOT / "artifacts" / "logs" / "prediction_log.csv"
APPROVE_THRESHOLD = 0.40
REJECT_THRESHOLD = 0.65

FEATURE_COLUMNS = [
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
]

REQUEST_COUNT = 0
PREDICTION_COUNT = 0
LAST_LATENCY_MS = 0.0
DECISION_COUNTS = {"approve": 0, "manual_review": 0, "reject": 0}
RISK_SCORE_TOTAL = 0.0

API_REQUESTS = Counter(
    "credit_risk_api_requests_total",
    "Total number of API requests by endpoint.",
    ["endpoint"],
)
API_PREDICTIONS = Counter(
    "credit_risk_predictions_total",
    "Total number of applicants scored by the credit risk model.",
)
API_DECISIONS = Counter(
    "credit_risk_decisions_total",
    "Total number of model decisions by decision band.",
    ["decision"],
)
API_LATENCY = Histogram(
    "credit_risk_prediction_latency_seconds",
    "Prediction endpoint latency in seconds.",
    ["endpoint"],
)
API_AVERAGE_RISK_SCORE = Gauge(
    "credit_risk_average_high_risk_probability",
    "Average high-risk probability across scored applicants since API start.",
)


class ApplicantFeatures(BaseModel):
    """Applicant fields expected by the champion model pipeline."""

    model_config = ConfigDict(extra="forbid")

    checking_account_status: str = Field(..., examples=["A11"])
    duration_months: int = Field(..., ge=1, examples=[24])
    credit_history: str = Field(..., examples=["A32"])
    purpose: str = Field(..., examples=["A43"])
    credit_amount: float = Field(..., gt=0, examples=[2500])
    savings_account: str = Field(..., examples=["A61"])
    employment_duration: str = Field(..., examples=["A73"])
    installment_rate_pct_income: int = Field(..., ge=1, examples=[3])
    personal_status_sex: str = Field(..., examples=["A93"])
    other_debtors_guarantors: str = Field(..., examples=["A101"])
    present_residence_years: int = Field(..., ge=1, examples=[2])
    property_type: str = Field(..., examples=["A121"])
    age_years: int = Field(..., ge=18, examples=[35])
    other_installment_plans: str = Field(..., examples=["A143"])
    housing: str = Field(..., examples=["A152"])
    existing_credits_count: int = Field(..., ge=1, examples=[1])
    job_type: str = Field(..., examples=["A173"])
    liable_people_count: int = Field(..., ge=1, examples=[1])
    telephone: str = Field(..., examples=["A191"])
    foreign_worker: str = Field(..., examples=["A201"])


class PredictionResponse(BaseModel):
    """Credit-risk scoring response."""

    high_risk_probability: float
    predicted_label: Literal["low_risk", "high_risk"]
    risk_band: Literal["low", "medium", "high"]
    decision: Literal["approve", "manual_review", "reject"]
    reason: str
    recommended_action: str


class BatchPredictionRequest(BaseModel):
    """Batch scoring request."""

    applicants: list[ApplicantFeatures]


class BatchPredictionResponse(BaseModel):
    """Batch scoring response."""

    predictions: list[PredictionResponse]


app = FastAPI(title="AI Credit Risk Assessment API", version="0.1.0")


@lru_cache(maxsize=1)
def load_model():
    """Load the champion model pipeline once per API process."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Champion model not found at {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def applicant_to_frame(applicant: ApplicantFeatures) -> pd.DataFrame:
    """Convert one applicant payload into the model's expected feature table."""
    record = applicant.model_dump()
    return pd.DataFrame([record], columns=FEATURE_COLUMNS)


def assign_decision(high_risk_probability: float) -> str:
    """Convert a model score into a business decision band."""
    if high_risk_probability < APPROVE_THRESHOLD:
        return "approve"
    if high_risk_probability < REJECT_THRESHOLD:
        return "manual_review"
    return "reject"


def assign_risk_band(high_risk_probability: float) -> str:
    """Convert a model score into a human-readable risk band."""
    if high_risk_probability < APPROVE_THRESHOLD:
        return "low"
    if high_risk_probability < REJECT_THRESHOLD:
        return "medium"
    return "high"


def decision_reason(decision: str) -> tuple[str, str]:
    """Return a plain-language decision reason and recommended action."""
    if decision == "approve":
        return (
            "Applicant falls below the manual-review threshold.",
            "Proceed with approval subject to standard policy checks.",
        )
    if decision == "manual_review":
        return (
            "Applicant falls between the approval and rejection thresholds.",
            "Send to a credit analyst for manual review before final decision.",
        )
    return (
        "Applicant meets or exceeds the rejection threshold.",
        "Reject or send for strict senior credit review depending on policy.",
    )


def log_predictions(features: pd.DataFrame, predictions: list[PredictionResponse]) -> None:
    """Append prediction events to a lightweight CSV audit log."""
    try:
        PREDICTION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        file_exists = PREDICTION_LOG_PATH.exists()
        fieldnames = [
            "timestamp_utc",
            "high_risk_probability",
            "predicted_label",
            "risk_band",
            "decision",
            *FEATURE_COLUMNS,
        ]

        with PREDICTION_LOG_PATH.open("a", newline="") as log_file:
            writer = csv.DictWriter(log_file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()

            for (_, row), prediction in zip(features.iterrows(), predictions):
                writer.writerow(
                    {
                        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        "high_risk_probability": prediction.high_risk_probability,
                        "predicted_label": prediction.predicted_label,
                        "risk_band": prediction.risk_band,
                        "decision": prediction.decision,
                        **row.to_dict(),
                    }
                )
    except OSError:
        # A temporary logging failure should not block a real-time credit decision.
        return


def score_frame(features: pd.DataFrame) -> list[PredictionResponse]:
    """Score one or more applicants with the champion pipeline."""
    global PREDICTION_COUNT, RISK_SCORE_TOTAL

    model = load_model()
    probabilities = model.predict_proba(features)[:, 1]
    predictions = []

    for probability in probabilities:
        probability_float = round(float(probability), 4)
        decision = assign_decision(probability_float)
        risk_band = assign_risk_band(probability_float)
        reason, recommended_action = decision_reason(decision)
        predictions.append(
            PredictionResponse(
                high_risk_probability=probability_float,
                predicted_label="high_risk" if probability_float >= 0.50 else "low_risk",
                risk_band=risk_band,
                decision=decision,
                reason=reason,
                recommended_action=recommended_action,
            )
        )
        DECISION_COUNTS[decision] += 1
        API_DECISIONS.labels(decision=decision).inc()
        RISK_SCORE_TOTAL += probability_float

    PREDICTION_COUNT += len(predictions)
    API_PREDICTIONS.inc(len(predictions))
    API_AVERAGE_RISK_SCORE.set(RISK_SCORE_TOTAL / PREDICTION_COUNT)
    log_predictions(features, predictions)
    return predictions


@app.get("/")
def root() -> dict[str, str]:
    """Return a simple service description."""
    API_REQUESTS.labels(endpoint="/").inc()
    return {"message": "AI Credit Risk Assessment API"}


@app.get("/health")
def health() -> dict[str, object]:
    """Return service and model availability."""
    API_REQUESTS.labels(endpoint="/health").inc()
    return {
        "status": "ok",
        "model_available": MODEL_PATH.exists(),
        "model_path": str(MODEL_PATH.relative_to(PROJECT_ROOT)),
    }


@app.get("/model/summary")
def model_summary() -> dict[str, object]:
    """Return champion model and decision-policy metadata."""
    API_REQUESTS.labels(endpoint="/model/summary").inc()
    return {
        "champion_model": "random_forest",
        "model_path": str(MODEL_PATH.relative_to(PROJECT_ROOT)),
        "feature_count": len(FEATURE_COLUMNS),
        "decision_policy": {
            "approve": f"score < {APPROVE_THRESHOLD}",
            "manual_review": f"{APPROVE_THRESHOLD} <= score < {REJECT_THRESHOLD}",
            "reject": f"score >= {REJECT_THRESHOLD}",
        },
    }


@app.get("/decision_policy")
def decision_policy() -> dict[str, object]:
    """Return the decision bands used to convert scores into actions."""
    API_REQUESTS.labels(endpoint="/decision_policy").inc()
    return {
        "target": "high_risk_probability",
        "thresholds": {
            "approve": {"rule": f"score < {APPROVE_THRESHOLD}", "risk_band": "low"},
            "manual_review": {
                "rule": f"{APPROVE_THRESHOLD} <= score < {REJECT_THRESHOLD}",
                "risk_band": "medium",
            },
            "reject": {"rule": f"score >= {REJECT_THRESHOLD}", "risk_band": "high"},
        },
        "note": "Thresholds are business-policy choices and can be tuned to risk appetite.",
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(applicant: ApplicantFeatures) -> PredictionResponse:
    """Score one applicant and return a credit-risk decision."""
    global REQUEST_COUNT, LAST_LATENCY_MS

    start = perf_counter()
    REQUEST_COUNT += 1
    API_REQUESTS.labels(endpoint="/predict").inc()

    try:
        with API_LATENCY.labels(endpoint="/predict").time():
            features = applicant_to_frame(applicant)
            prediction = score_frame(features)[0]
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    LAST_LATENCY_MS = round((perf_counter() - start) * 1000, 4)
    return prediction


@app.post("/batch_predict", response_model=BatchPredictionResponse)
def batch_predict(request: BatchPredictionRequest) -> BatchPredictionResponse:
    """Score multiple applicants in one request."""
    global REQUEST_COUNT, LAST_LATENCY_MS

    start = perf_counter()
    REQUEST_COUNT += 1
    API_REQUESTS.labels(endpoint="/batch_predict").inc()

    if not request.applicants:
        raise HTTPException(status_code=400, detail="At least one applicant is required.")

    try:
        with API_LATENCY.labels(endpoint="/batch_predict").time():
            features = pd.DataFrame(
                [applicant.model_dump() for applicant in request.applicants],
                columns=FEATURE_COLUMNS,
            )
            predictions = score_frame(features)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    LAST_LATENCY_MS = round((perf_counter() - start) * 1000, 4)
    return BatchPredictionResponse(predictions=predictions)


@app.get("/metrics")
def metrics() -> dict[str, object]:
    """Return lightweight API metrics for local monitoring."""
    API_REQUESTS.labels(endpoint="/metrics").inc()
    average_risk_score = RISK_SCORE_TOTAL / PREDICTION_COUNT if PREDICTION_COUNT else 0.0
    return {
        "request_count": REQUEST_COUNT,
        "prediction_count": PREDICTION_COUNT,
        "last_latency_ms": LAST_LATENCY_MS,
        "average_high_risk_probability": round(average_risk_score, 4),
        "decision_counts": DECISION_COUNTS,
        "prediction_log_path": str(PREDICTION_LOG_PATH.relative_to(PROJECT_ROOT)),
    }


@app.get("/prometheus")
def prometheus_metrics() -> Response:
    """Expose Prometheus-compatible metrics for Grafana dashboards."""
    API_REQUESTS.labels(endpoint="/prometheus").inc()
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
