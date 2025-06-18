#!/bin/bash
set -e
 
# Run tests with coverage, excluding ollama integration tests
pytest -v --cov=auto_codex --cov-report=term-missing tests/ --ignore=tests/test_ollama_integration.py 