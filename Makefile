.PHONY: help install install-dev format lint test coverage theory docs docs-serve build toy check clean

PYTHON ?= python

help:
	@printf "%s\n" \
	  "install      Install runtime package" \
	  "install-dev  Install development and documentation tools" \
	  "format       Format Python files with Ruff" \
	  "lint         Run Ruff lint and format checks" \
	  "test         Run the test suite" \
	  "coverage     Run tests with coverage reports" \
	  "theory       Validate theory sources and Markdown" \
	  "docs         Build documentation in strict mode" \
	  "docs-serve   Serve documentation locally" \
	  "build        Build and validate wheel/sdist" \
	  "toy          Run C01-C09 experiments" \
	  "check        Run all local quality gates" \
	  "clean        Remove generated artifacts"

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e ".[dev,docs]"

format:
	ruff check --fix .
	ruff format .

lint:
	ruff check .
	ruff format --check .

test:
	$(PYTHON) -m pytest

coverage:
	$(PYTHON) -m pytest --cov=llm_theory_lab --cov-report=term-missing --cov-report=xml

theory:
	$(PYTHON) scripts/normalize_markdown_math.py --check
	$(PYTHON) scripts/validate_catalog.py
	$(PYTHON) scripts/validate_source_digest.py
	$(PYTHON) scripts/check_repository.py
	$(PYTHON) scripts/check_markdown_links.py

docs:
	mkdocs build --strict

docs-serve:
	mkdocs serve

build:
	rm -rf build dist
	$(PYTHON) -m build
	$(PYTHON) -m twine check dist/*

toy:
	llm-theory-lab run-toy

check: lint theory test docs build toy

clean:
	rm -rf build dist site reports .coverage coverage.xml htmlcov .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
