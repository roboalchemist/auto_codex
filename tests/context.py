"""
Test context file for easy package imports.

This module allows tests to import the auto_codex package without
needing to install it first.
"""

import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import auto_codex  # noqa: E402 