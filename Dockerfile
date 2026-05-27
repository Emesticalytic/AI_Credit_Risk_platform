FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    "fastapi>=0.110,<1.0" \
    "uvicorn[standard]>=0.30,<1.0" \
    "pandas>=2.2,<3.0" \
    "numpy>=1.26,<3.0" \
    "scikit-learn==1.7.2" \
    "joblib>=1.4,<2.0" \
    "prometheus-client>=0.20,<1.0" \
    "pydantic>=2.7,<3.0"

COPY src ./src
COPY models ./models

RUN find /app/src -type d -name "__pycache__" -prune -exec rm -rf {} +
RUN mkdir -p artifacts/logs

EXPOSE 8000

CMD ["uvicorn", "credit_risk_platform.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
