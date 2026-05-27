PYTHON ?= python3

.PHONY: install lint test coverage api

install:
	$(PYTHON) -m pip install -e ".[dev]"

lint:
	$(PYTHON) -m ruff check src tests

test:
	$(PYTHON) -m pytest -q

coverage:
	$(PYTHON) -m coverage run -m pytest -q
	$(PYTHON) -m coverage report -m

api:
	PYTHONPATH=src uvicorn credit_risk_platform.api.main:app --host 0.0.0.0 --port 8000 --reload
