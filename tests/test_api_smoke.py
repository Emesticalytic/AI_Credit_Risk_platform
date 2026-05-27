"""Smoke tests for the credit-risk scoring API."""

import numpy as np
import pytest
from fastapi.testclient import TestClient

from credit_risk_platform.api import main


client = TestClient(main.app)


class FakeModel:
    """Small test double that avoids loading the real model artifact."""

    def predict_proba(self, features):  # noqa: ANN001
        return np.array([[0.333, 0.667] for _ in range(len(features))])


@pytest.fixture(autouse=True)
def fake_model(monkeypatch: pytest.MonkeyPatch) -> None:
    original_load_model = main.load_model
    original_load_model.cache_clear()
    monkeypatch.setattr(main, "load_model", lambda: FakeModel())
    monkeypatch.setattr(main, "log_predictions", lambda features, predictions: None)
    yield
    monkeypatch.setattr(main, "load_model", original_load_model)
    original_load_model.cache_clear()


def sample_applicant_payload() -> dict[str, object]:
    """Return one valid applicant payload for API scoring tests."""
    return {
        "checking_account_status": "A11",
        "duration_months": 24,
        "credit_history": "A32",
        "purpose": "A43",
        "credit_amount": 2500,
        "savings_account": "A61",
        "employment_duration": "A73",
        "installment_rate_pct_income": 3,
        "personal_status_sex": "A93",
        "other_debtors_guarantors": "A101",
        "present_residence_years": 2,
        "property_type": "A121",
        "age_years": 35,
        "other_installment_plans": "A143",
        "housing": "A152",
        "existing_credits_count": 1,
        "job_type": "A173",
        "liable_people_count": 1,
        "telephone": "A191",
        "foreign_worker": "A201",
    }


def test_root_endpoint() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "AI Credit Risk Assessment API"


def test_health_endpoint() -> None:
    response = client.get("/health")
    body = response.json()

    assert response.status_code == 200
    assert body["status"] == "ok"
    assert body["model_available"] is True


def test_model_summary_endpoint() -> None:
    response = client.get("/model/summary")
    body = response.json()

    assert response.status_code == 200
    assert body["champion_model"] == "random_forest"
    assert body["feature_count"] == 20
    assert "decision_policy" in body


def test_decision_policy_endpoint() -> None:
    response = client.get("/decision_policy")
    body = response.json()

    assert response.status_code == 200
    assert body["target"] == "high_risk_probability"
    assert set(body["thresholds"]) == {"approve", "manual_review", "reject"}


def test_predict_endpoint_returns_business_response() -> None:
    response = client.post("/predict", json=sample_applicant_payload())
    body = response.json()

    assert response.status_code == 200
    assert 0 <= body["high_risk_probability"] <= 1
    assert body["predicted_label"] in {"low_risk", "high_risk"}
    assert body["risk_band"] in {"low", "medium", "high"}
    assert body["decision"] in {"approve", "manual_review", "reject"}
    assert body["reason"]
    assert body["recommended_action"]


def test_batch_predict_endpoint_returns_one_prediction_per_applicant() -> None:
    payload = {"applicants": [sample_applicant_payload(), sample_applicant_payload()]}
    response = client.post("/batch_predict", json=payload)
    body = response.json()

    assert response.status_code == 200
    assert len(body["predictions"]) == 2
    assert all("high_risk_probability" in prediction for prediction in body["predictions"])


def test_predict_rejects_invalid_payload() -> None:
    payload = sample_applicant_payload()
    payload["credit_amount"] = -100

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_metrics_endpoint() -> None:
    client.post("/predict", json=sample_applicant_payload())
    response = client.get("/metrics")
    body = response.json()

    assert response.status_code == 200
    assert body["request_count"] >= 1
    assert body["prediction_count"] >= 1
    assert "decision_counts" in body
    assert "prediction_log_path" in body


def test_prometheus_metrics_endpoint() -> None:
    client.post("/predict", json=sample_applicant_payload())
    response = client.get("/prometheus")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "credit_risk_predictions_total" in response.text
    assert "credit_risk_decisions_total" in response.text
