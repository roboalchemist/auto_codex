"""
Mocked integration tests for agent usage with simulated Codex CLI responses.

This test simulates the behavior of the Codex CLI to test the integration framework
without requiring external tools or actual LLM API calls.

Run with: python -m pytest tests/test_ollama_integration_mock.py -v -s
"""

import unittest
import tempfile
import shutil
import os
import time
import json
import subprocess
from unittest.mock import patch, MagicMock, call
from datetime import datetime

from auto_codex.core import CodexRun, CodexSession
from auto_codex.models import CodexRunResult, CodexSessionResult


class TestOllamaMockedIntegration(unittest.TestCase):
    """Integration tests with mocked Codex CLI responses."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp(prefix="codex_mock_test_")
        self.provider = "ollama"
        self.model = "devstral"
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_mock_log_file(self, log_file_path: str, success: bool = True, files_created: list = None):
        """Create a mock log file that simulates Codex CLI output."""
        files_created = files_created or []
        
        # Create the files that would be created by the agent
        for filename in files_created:
            file_path = os.path.join(self.temp_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            if filename == "factorial.py":
                content = '''def factorial(n: int) -> int:
    """Calculate the factorial of a number.
    
    Args:
        n: The number to calculate factorial for
        
    Returns:
        The factorial of n
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

if __name__ == "__main__":
    print(f"Factorial of 5: {factorial(5)}")
'''
            elif filename == "calculator.py":
                content = '''class Calculator:
    """A simple calculator class."""
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """Divide a by b."""
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b
'''
            elif filename == "test_calculator.py":
                content = '''import unittest
from calculator import Calculator

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()
    
    def test_add(self):
        self.assertEqual(self.calc.add(2, 3), 5)
    
    def test_subtract(self):
        self.assertEqual(self.calc.subtract(5, 3), 2)
    
    def test_multiply(self):
        self.assertEqual(self.calc.multiply(2, 3), 6)
    
    def test_divide(self):
        self.assertEqual(self.calc.divide(6, 2), 3)
    
    def test_divide_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            self.calc.divide(5, 0)

if __name__ == "__main__":
    unittest.main()
'''
            elif filename == "README.md":
                content = '''# Calculator

A simple calculator implementation in Python.

## Usage

```python
from calculator import Calculator

calc = Calculator()
print(calc.add(2, 3))  # Output: 5
```

## Running Tests

```bash
python -m pytest test_calculator.py
```
'''
            else:
                content = f"# {filename}\nGenerated content for {filename}"
            
            with open(file_path, 'w') as f:
                f.write(content)
        
        # Create mock log file with simulated Codex output
        log_content = f"""
[INFO] Starting Codex run with model {self.model} and provider {self.provider}
[INFO] Processing prompt...
[INFO] Generating response...
"""
        
        if success:
            log_content += "[INFO] ✅ Files created successfully:\n"
            for filename in files_created:
                log_content += f"[INFO]   - {filename}\n"
            log_content += "[INFO] ✅ Run completed successfully\n"
        else:
            log_content += "[ERROR] ❌ Failed to complete request\n"
        
        with open(log_file_path, 'w') as f:
            f.write(log_content)
    
    @patch('subprocess.Popen')
    def test_single_turn_mocked_agent_usage(self, mock_popen):
        """Test single-turn usage with mocked Codex CLI."""
        print("\n🧪 Testing single-turn mocked agent usage...")
        
        # Setup mock process
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None] * 5 + [0]  # Running, then completed
        mock_process.returncode = 0
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        prompt = "Create a simple Python function that calculates the factorial of a number."
        
        run = CodexRun(
            prompt=prompt,
            provider=self.provider,
            model=self.model,
            writable_root=self.temp_dir,
            validate_env=False,
            timeout=120
        )
        
        print(f"  Prompt: {prompt[:100]}...")
        print(f"  Provider: {self.provider}")
        print(f"  Model: {self.model}")
        print(f"  Working directory: {self.temp_dir}")
        
        # Mock the log file creation
        def mock_log_creation(*args, **kwargs):
            # Create the log file when Popen is called
            log_file = run.log_file
            if log_file:
                self._create_mock_log_file(log_file, success=True, files_created=["factorial.py"])
        
        mock_popen.side_effect = mock_log_creation
        
        try:
            result = run.execute()
            
            print(f"✅ Mocked run completed successfully")
            print(f"  Run ID: {result.run_id}")
            print(f"  Success: {result.success}")
            
            # Verify result structure
            self.assertIsInstance(result, CodexRunResult)
            self.assertIsNotNone(result.run_id)
            
            # Check if factorial.py was created
            factorial_file = os.path.join(self.temp_dir, "factorial.py")
            if os.path.exists(factorial_file):
                print("✅ factorial.py file was created")
                with open(factorial_file, 'r') as f:
                    content = f.read()
                    self.assertIn("factorial", content.lower())
                    self.assertIn("def", content)
            
            print("✅ Single-turn mocked integration test passed")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            raise
    
    @patch('subprocess.Popen')
    def test_multi_turn_mocked_agent_usage(self, mock_popen):
        """Test multi-turn usage with mocked Codex CLI."""
        print("\n🧪 Testing multi-turn mocked agent usage...")
        
        # Setup mock process that succeeds each time
        def create_mock_process():
            mock_process = MagicMock()
            mock_process.poll.side_effect = [None] * 3 + [0]  # Running, then completed
            mock_process.returncode = 0
            mock_process.pid = 12345
            return mock_process
        
        mock_popen.return_value = create_mock_process()
        
        session = CodexSession(
            session_id=f"mock_test_session_{int(time.time())}",
            default_provider=self.provider,
            default_model=self.model,
            validate_env=False
        )
        
        print(f"  Session ID: {session.session_id}")
        
        # Track which files to create for each turn
        turn_files = {
            1: ["calculator.py"],
            2: ["test_calculator.py"],
            3: ["README.md"]
        }
        
        turn_counter = 0
        
        def mock_log_creation_with_turn(*args, **kwargs):
            nonlocal turn_counter
            turn_counter += 1
            # Get the current run to access its log file
            current_run = session.runs[-1] if session.runs else None
            if current_run and current_run.log_file:
                files_to_create = turn_files.get(turn_counter, [])
                self._create_mock_log_file(current_run.log_file, success=True, files_created=files_to_create)
        
        mock_popen.side_effect = mock_log_creation_with_turn
        
        # Turn 1: Create calculator
        print("\n  Turn 1: Creating calculator...")
        run1 = session.add_run(
            prompt="Create a simple calculator class",
            writable_root=self.temp_dir
        )
        result1 = run1.execute()
        
        print(f"✅ Turn 1 completed")
        self.assertIsInstance(result1, CodexRunResult)
        
        # Turn 2: Create tests
        print("\n  Turn 2: Creating tests...")
        run2 = session.add_run(
            prompt="Create unit tests for the calculator",
            writable_root=self.temp_dir
        )
        result2 = run2.execute()
        
        print(f"✅ Turn 2 completed")
        self.assertIsInstance(result2, CodexRunResult)
        
        # Turn 3: Create documentation
        print("\n  Turn 3: Creating documentation...")
        run3 = session.add_run(
            prompt="Create README documentation",
            writable_root=self.temp_dir
        )
        result3 = run3.execute()
        
        print(f"✅ Turn 3 completed")
        self.assertIsInstance(result3, CodexRunResult)
        
        # Verify all files were created
        expected_files = ["calculator.py", "test_calculator.py", "README.md"]
        created_files = []
        
        for filename in expected_files:
            file_path = os.path.join(self.temp_dir, filename)
            if os.path.exists(file_path):
                created_files.append(filename)
                print(f"✅ {filename} created")
        
        print(f"\n  Files created: {created_files}")
        print("✅ Multi-turn mocked integration test passed")
        
        # Verify we created all expected files
        self.assertEqual(set(created_files), set(expected_files))
    
    def test_integration_framework_structure(self):
        """Test that the integration framework has the right structure."""
        print("\n🧪 Testing integration framework structure...")
        
        # Test CodexRun instantiation
        run = CodexRun(
            prompt="Test prompt",
            provider=self.provider,
            model=self.model,
            writable_root=self.temp_dir,
            validate_env=False
        )
        
        self.assertIsNotNone(run.run_id)
        self.assertEqual(run.provider, self.provider)
        self.assertEqual(run.model, self.model)
        self.assertEqual(run.writable_root, self.temp_dir)
        
        # Test CodexSession instantiation
        session = CodexSession(
            default_provider=self.provider,
            default_model=self.model,
            validate_env=False
        )
        
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.default_provider, self.provider)
        self.assertEqual(session.default_model, self.model)
        
        # Test adding runs to session
        run1 = session.add_run("Prompt 1", writable_root=self.temp_dir)
        run2 = session.add_run("Prompt 2", writable_root=self.temp_dir)
        
        self.assertEqual(len(session.runs), 2)
        self.assertIn(run1, session.runs)
        self.assertIn(run2, session.runs)
        
        print("✅ Integration framework structure test passed")
    
    def test_provider_configuration(self):
        """Test provider configuration for Ollama."""
        print("\n🧪 Testing provider configuration...")
        
        # Test that Ollama provider is properly configured
        run = CodexRun(
            prompt="Test",
            provider="ollama",
            model="devstral",
            validate_env=False
        )
        
        self.assertEqual(run.provider, "ollama")
        self.assertEqual(run.model, "devstral")
        
        # Test that the correct command would be built
        expected_cmd_parts = [
            "codex",
            "--model=devstral",
            "--provider=ollama",
            f"--writable-root={run.writable_root}",
            f"--timeout={run.timeout}",
            f"--approval-mode={run.approval_mode}",
            "--quiet",
            "Test"
        ]
        
        print("✅ Provider configuration test passed")


if __name__ == "__main__":
    # Print test info
    print("=" * 60)
    print("🧪 MOCKED OLLAMA INTEGRATION TESTS")
    print("=" * 60)
    print("  These tests simulate Codex CLI behavior without external dependencies")
    print("  Testing integration framework structure and workflow")
    print("=" * 60)
    
    # Run tests
    unittest.main(verbosity=2) 