# Makefile for auto_codex package

# Variables
PYTHON := python3
PIP := pip3
PACKAGE_NAME := auto_codex
TEST_DIR := tests
DOCS_DIR := docs

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  install       Install the package in development mode"
	@echo "  install-dev   Install with development dependencies"
	@echo "  test          Run tests with coverage"
	@echo "  test-quick    Run tests without coverage"
	@echo "  lint          Run linting checks"
	@echo "  format        Format code with black and isort"
	@echo "  type-check    Run type checking with mypy"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build distribution packages"
	@echo "  upload        Upload to PyPI (requires credentials)"
	@echo "  docs          Build documentation"
	@echo "  all           Run all quality checks"

# Installation targets
.PHONY: install
install:
	$(PIP) install -e .

.PHONY: install-dev
install-dev:
	$(PIP) install -e ".[dev,docs]"

# Testing targets
.PHONY: test
test:
	$(PYTHON) -m pytest $(TEST_DIR) --cov=$(PACKAGE_NAME) --cov-report=term-missing --cov-report=html

.PHONY: test-quick
test-quick:
	$(PYTHON) -m pytest $(TEST_DIR) -v

# Code quality targets
.PHONY: lint
lint:
	$(PYTHON) -m flake8 $(PACKAGE_NAME) $(TEST_DIR)

.PHONY: format
format:
	$(PYTHON) -m black $(PACKAGE_NAME) $(TEST_DIR)
	$(PYTHON) -m isort $(PACKAGE_NAME) $(TEST_DIR)

.PHONY: type-check
type-check:
	$(PYTHON) -m mypy $(PACKAGE_NAME)

# Build targets
.PHONY: clean
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: build
build: clean
	$(PYTHON) -m build

.PHONY: upload
upload: build
	$(PYTHON) -m twine upload dist/*

# Documentation targets
.PHONY: docs
docs:
	cd $(DOCS_DIR) && make html

.PHONY: docs-clean
docs-clean:
	cd $(DOCS_DIR) && make clean

# Combined targets
.PHONY: all
all: format lint type-check test

# Development workflow
.PHONY: dev-setup
dev-setup: install-dev
	@echo "Development environment setup complete"
	@echo "You can now run 'make test' to verify everything works"

# Package verification
.PHONY: verify
verify: all build
	@echo "Package verification complete" 