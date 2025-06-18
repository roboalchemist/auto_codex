#!/usr/bin/env python3
"""
Real integration tests for agent usage with Ollama backend.

This test uses the actual auto_codex library to wrap the real OpenAI Codex CLI
and test integration with Ollama and the Devstral model.
"""

import unittest
import tempfile
import os
import shutil
import requests
import sys
import time
from pathlib import Path

# Add the parent directory to Python path to import auto_codex
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from auto_codex.core import CodexRun, CodexSession


class TestOllamaIntegration(unittest.TestCase):
    """Real integration tests with Ollama backend."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        print("\n  Setting up Ollama integration tests...")
        
        # codex is now available in system PATH, no need to modify PATH
        
        # Check if Ollama is running
        cls.ollama_available = cls._check_ollama_availability()
        if not cls.ollama_available:
            print("   Ollama not available - tests will be skipped")
            return
        
        # Check if Devstral model is available
        cls.devstral_available = cls._check_devstral_model()
        if not cls.devstral_available:
            print("   Devstral model not available - tests will be skipped")
        
        print(f"✅ Environment ready - Ollama: {cls.ollama_available}, Devstral: {cls.devstral_available}")
    
    @classmethod 
    def tearDownClass(cls):
        """Restore original environment."""
        # No longer needed since we don't modify PATH
        pass
    
    @classmethod
    def _check_ollama_availability(cls) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    @classmethod
    def _check_devstral_model(cls) -> bool:
        """Check if Devstral model is available in Ollama."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any('devstral' in model.get('name', '').lower() for model in models)
            return False
        except Exception:
            return False
    
    def setUp(self):
        """Setup for individual tests."""
        # Create temporary directory for file operations
        self.test_dir = tempfile.mkdtemp(prefix="codex_integration_test_")
        self.addCleanup(shutil.rmtree, self.test_dir)
    
    @unittest.skipUnless(lambda: hasattr(TestOllamaIntegration, 'ollama_available') and 
                                 TestOllamaIntegration.ollama_available, 
                        "Ollama not available")
    def test_environment_detection(self):
        """Test that we can detect the Ollama environment properly."""
        print("\n🧪 Testing environment detection...")
        
        # Test Ollama availability
        self.assertTrue(self.ollama_available, "Ollama should be available")
        
        # Check models available
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        self.assertEqual(response.status_code, 200)
        
        models = response.json().get('models', [])
        print(f"  Found {len(models)} models in Ollama")
        
        model_names = [model.get('name', '') for model in models]
        print(f"  Available models: {model_names}")
        
        if self.devstral_available:
            print("✅ Devstral model is available")
        else:
            print("   Devstral model not found - using alternative")
    
    @unittest.skipUnless(lambda: hasattr(TestOllamaIntegration, 'ollama_available') and 
                                 TestOllamaIntegration.ollama_available, 
                        "Ollama not available")
    def test_single_turn_agent_usage(self):
        """Test single-turn agent usage with real auto_codex library."""
        print("\n🧪 Testing single-turn agent usage...")
        
        # Use Ollama model
        model = "devstral" if self.devstral_available else "gemma:2b"
        provider = "ollama"
        
        # Create CodexRun instance
        run = CodexRun(
            prompt="Create a simple Python function that calculates the factorial of a number and save it to factorial.py",
            model=model,
            provider=provider, 
            writable_root=self.test_dir,
            timeout=120,
            approval_mode="auto",
            debug=True,
            validate_env=False,  # Skip env validation for testing
            dangerously_auto_approve_everything=True  # Skip confirmations for testing
        )
        
        print(f"  Starting CodexRun with model: {model} ({provider})")
        
        # Execute the run
        try:
            result = run.execute(log_dir=self.test_dir)
            
            # Verify execution completed
            self.assertIsNotNone(result, "CodexRunResult should not be None")
            print(f"✅ Run completed successfully in {run.get_runtime_seconds():.2f}s")
            
            # Check if files were created
            expected_file = os.path.join(self.test_dir, "factorial.py")
            if os.path.exists(expected_file):
                print(f"✅ factorial.py was created")
                
                # Verify content
                with open(expected_file, 'r') as f:
                    content = f.read()
                self.assertIn("factorial", content.lower(), "File should contain factorial function")
                print(f"✅ factorial.py contains factorial implementation")
            else:
                print("   factorial.py was not created - checking for other files")
                created_files = os.listdir(self.test_dir)
                print(f"  Files in test directory: {created_files}")
            
            # Check if there were any changes
            if result.changes:
                print(f"  {len(result.changes)} changes detected")
                for change in result.changes:
                    print(f"   - {change.change_type}: {change.file_path}")
            
            # Check tool usage
            if result.tool_usage:
                print(f"  {len(result.tool_usage)} tool usages detected")
                for tool in result.tool_usage:
                    operation = tool.operation or "unknown operation"
                    print(f"   - {tool.tool_name}: {operation} ({tool.tool_type.value})")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            # Print debug information
            if hasattr(run, 'output') and run.output:
                print(f"  Codex output: {run.output[:500]}...")
            raise
    
    @unittest.skipUnless(lambda: hasattr(TestOllamaIntegration, 'ollama_available') and 
                                 TestOllamaIntegration.ollama_available, 
                        "Ollama not available")
    def test_multi_turn_agent_session(self):
        """Test multi-turn agent session using CodexSession."""
        print("\n🧪 Testing multi-turn agent session...")
        
        # Choose model based on availability
        model = "devstral" if self.devstral_available else "gemma:2b"
        
        # Create CodexSession
        session = CodexSession(
            default_model=model,
            default_provider="ollama",
            default_timeout=120,
            log_dir=self.test_dir,
            debug=True,
            validate_env=False
        )
        
        print(f"  Starting CodexSession with model: {model}")
        
        # Add multiple runs to simulate conversation
        run1 = session.add_run(
            prompt="Create a simple calculator class in Python and save it to calculator.py",
            writable_root=self.test_dir,
            approval_mode="auto",
            dangerously_auto_approve_everything=True
        )
        
        run2 = session.add_run(
            prompt="Now create comprehensive unit tests for the calculator class and save to test_calculator.py", 
            writable_root=self.test_dir,
            approval_mode="auto",
            dangerously_auto_approve_everything=True
        )
        
        run3 = session.add_run(
            prompt="Create a README.md file documenting how to use the calculator",
            writable_root=self.test_dir,
            approval_mode="auto",
            dangerously_auto_approve_everything=True
        )
        
        try:
            # Execute all runs
            session_result = session.execute_all()
            
            print(f"✅ Session completed with {len(session_result.runs)} runs")
            
            # Check session summary
            summary = session.get_summary()
            print(f"  Session summary:")
            print(f"   - Total runs: {summary.get('total_runs', 0)}")
            print(f"   - Successful runs: {summary.get('successful_runs', 0)}")
            print(f"   - Total changes: {summary.get('total_changes', 0)}")
            print(f"   - Total runtime: {summary.get('total_runtime', 0):.2f}s")
            
            # Check for created files
            expected_files = ["calculator.py", "test_calculator.py", "README.md"]
            created_files = []
            
            for filename in expected_files:
                filepath = os.path.join(self.test_dir, filename)
                if os.path.exists(filepath):
                    created_files.append(filename)
                    print(f"✅ {filename} was created")
                    
                    # Basic content verification
                    with open(filepath, 'r') as f:
                        content = f.read()
                    
                    if filename == "calculator.py":
                        self.assertIn("class", content.lower(), "Calculator.py should contain a class")
                    elif filename == "test_calculator.py":
                        self.assertIn("test", content.lower(), "test_calculator.py should contain tests")
                    elif filename == "README.md":
                        self.assertIn("calculator", content.lower(), "README.md should mention calculator")
                else:
                    print(f"   {filename} was not created")
            
            if not created_files:
                print("   No expected files were created - checking what was created")
                all_files = os.listdir(self.test_dir)
                print(f"  Files in test directory: {all_files}")
            
            # Verify we have at least some successful execution
            self.assertGreater(summary.get('successful_runs', 0), 0, 
                             "At least one run should be successful")
            
        except Exception as e:
            print(f"❌ Multi-turn test failed: {e}")
            
            # Print debug info for each run
            for i, run in enumerate([run1, run2, run3], 1):
                if hasattr(run, 'output') and run.output:
                    print(f"  Run {i} output: {run.output[:200]}...")
            raise
    
    @unittest.skipUnless(lambda: hasattr(TestOllamaIntegration, 'ollama_available') and 
                                 TestOllamaIntegration.ollama_available, 
                        "Ollama not available")
    def test_error_handling_and_recovery(self):
        """Test error handling with invalid prompts."""
        print("\n🧪 Testing error handling and recovery...")
        
        model = "devstral" if self.devstral_available else "gemma:2b"
        
        # Test with a timeout scenario
        run = CodexRun(
            prompt="Create a complex application with 50 files",
            model=model,
            provider="ollama",
            writable_root=self.test_dir,
            timeout=5,  # Very short timeout to trigger timeout handling
            approval_mode="auto",
            debug=True,
            validate_env=False
        )
        
        print(f"  Testing timeout handling with model: {model}")
        
        try:
            result = run.execute(log_dir=self.test_dir)
            print("   Expected timeout but run completed normally")
        except Exception as e:
            print(f"✅ Timeout was correctly triggered: {e}")
            self.assertIn("timed out", str(e).lower())
    
    def test_integration_framework_structure(self):
        """Test the basic structure of CodexRun and CodexSession."""
        print("\n🧪 Testing integration framework structure...")
        
        # Test CodexRun instantiation
        run = CodexRun(
            prompt="Test prompt",
            provider="ollama",
            model="devstral",
            writable_root=self.test_dir,
            validate_env=False
        )
        self.assertIsNotNone(run.run_id)
        
        # Test CodexSession instantiation
        session = CodexSession(
            default_provider="ollama",
            default_model="devstral",
            validate_env=False
        )
        self.assertIsNotNone(session.session_id)
        
        # Test adding a run
        session.add_run("Test prompt 2", writable_root=self.test_dir)
        self.assertEqual(len(session.runs), 1)


if __name__ == '__main__':
    unittest.main() 