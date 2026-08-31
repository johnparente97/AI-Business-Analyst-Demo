# ==============================================================================
# InsightBridge AI — Automation & Operations Makefile
# ==============================================================================

SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
STREAMLIT := $(VENV)/bin/streamlit
PYTEST := $(VENV)/bin/pytest

.PHONY: help install test test-react lint-react run-streamlit run-react build-react check clean

help:
	@echo "InsightBridge AI — Available Commands:"
	@echo "  make install        Install Python dependencies and React node_modules"
	@echo "  make test           Execute pytest test suite with coverage report"
	@echo "  make test-react     Execute React utility tests"
	@echo "  make lint-react     Lint the React application"
	@echo "  make run-streamlit  Launch Python/Streamlit analytical dashboard (Port 8501)"
	@echo "  make run-react      Launch React/Vite frontend (Port 5173)"
	@echo "  make build-react    Typecheck and build production React bundle"
	@echo "  make check          Run complete syntax validation and test suite"
	@echo "  make clean          Remove Python cache, coverage, and build artifacts"

$(VENV):
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: $(VENV)
	$(PIP) install -r requirements.txt
	@if [ -d "gravity-app" ]; then cd gravity-app && npm install; fi

test: $(VENV)
	$(PYTHON) -m pytest -v --cov=utils tests/

test-react:
	cd gravity-app && npm test

lint-react:
	cd gravity-app && npm run lint

run-streamlit: $(VENV)
	$(STREAMLIT) run app.py --server.port=8501 --server.headless=false

run-react:
	cd gravity-app && npm run dev

build-react:
	cd gravity-app && npm run build

check: test test-react lint-react build-react
	$(PYTHON) -m py_compile app.py utils/*.py tests/*.py
	@echo "✅ All checks, builds, and unit tests passed successfully."

clean:
	rm -rf .pytest_cache .coverage htmlcov __pycache__ utils/__pycache__ tests/__pycache__
	rm -rf gravity-app/dist gravity-app/node_modules/.vite
