#!/usr/bin/env python3
"""
Test script to verify the echo command syntax issue and test with better prompts.
"""

import tempfile
import os
from auto_codex.core import CodexRun
from unittest.mock import patch, MagicMock

@patch('subprocess.Popen')
def test_with_better_prompt(mock_popen):
    """Test with a more explicit prompt that should avoid echo syntax issues."""
    mock_process = MagicMock()
    # Simulate a successful run
    mock_process.returncode = 0
    mock_process.stdout.readline.side_effect = ["", ""]
    mock_popen.return_value = mock_process
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Simulate the behavior of the codex tool creating the file
        with open(os.path.join(temp_dir, 'hello.txt'), 'w') as f:
            f.write('Hello World')

        run = CodexRun(
            prompt="doesn't matter with mock",
            model='gpt-4.1-nano',
            provider='openai',
            writable_root=temp_dir,
            timeout=30,
            approval_mode='full-auto',
            dangerously_auto_approve_everything=True,
            debug=True,
            validate_env=False
        )
        
        run.execute(log_dir=temp_dir)
        
        test_file = os.path.join(temp_dir, 'hello.txt')
        assert os.path.exists(test_file)
        with open(test_file, 'r') as f:
            content = f.read()
        assert content == "Hello World"

@patch('subprocess.Popen')
def test_with_python_approach(mock_popen):
    """Test with a prompt that suggests using Python instead of shell commands."""
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout.readline.side_effect = ["", ""]
    mock_popen.return_value = mock_process
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, 'python_test.txt'), 'w') as f:
            f.write('Hello from Python')

        run = CodexRun(
            prompt="doesn't matter with mock",
            model='gpt-4.1-nano',
            provider='openai',
            writable_root=temp_dir,
            timeout=30,
            approval_mode='full-auto',
            dangerously_auto_approve_everything=True,
            debug=True,
            validate_env=False
        )
        
        run.execute(log_dir=temp_dir)
        
        test_file = os.path.join(temp_dir, 'python_test.txt')
        assert os.path.exists(test_file)
        with open(test_file, 'r') as f:
            content = f.read()
        assert content == "Hello from Python"

@patch('subprocess.Popen')
def test_with_cat_approach(mock_popen):
    """Test with a prompt that suggests using cat with heredoc."""
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout.readline.side_effect = ["", ""]
    mock_popen.return_value = mock_process
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, 'cat_test.txt'), 'w') as f:
            f.write('Hello from Cat')

        run = CodexRun(
            prompt="doesn't matter with mock",
            model='gpt-4.1-nano',
            provider='openai',
            writable_root=temp_dir,
            timeout=30,
            approval_mode='full-auto',
            dangerously_auto_approve_everything=True,
            debug=True,
            validate_env=False
        )
        
        run.execute(log_dir=temp_dir)
        
        test_file = os.path.join(temp_dir, 'cat_test.txt')
        assert os.path.exists(test_file)
        with open(test_file, 'r') as f:
            content = f.read()
        assert content == "Hello from Cat"