#!/bin/bash

# Test script for auto_codex package
# This script runs the test suite with coverage reporting

set -e  # Exit on any error

echo "======================================"
echo "Running auto_codex test suite"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Check if auto_codex package exists
if [ ! -d "auto_codex" ]; then
    echo "Error: auto_codex directory not found."
    exit 1
fi

# Check if tests directory exists
if [ ! -d "tests" ]; then
    echo "Error: tests directory not found."
    exit 1
fi

echo "Project structure verified ✓"
echo ""

# Install the package in development mode if not already installed
echo "Installing package in development mode..."
pip install -e . 2>/dev/null || echo "Package installation skipped (may already be installed)"
echo ""

# Run tests with coverage
echo "Running tests with coverage..."
python -m pytest tests/ \
    --cov=auto_codex \
    --cov-report=term-missing \
    --cov-report=html \
    --tb=short \
    -v

echo ""
echo "======================================"
echo "Test execution complete!"
echo "======================================"
echo ""
echo "Coverage report saved to htmlcov/index.html"
echo "Open htmlcov/index.html in your browser to view detailed coverage" 