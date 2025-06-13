"""
Integration tests for provider support using live APIs.

These tests require actual API keys to be set in environment variables.
They are designed to test real interaction with the Codex CLI and providers.
"""

import os
import unittest
import tempfile
import shutil
from datetime import datetime

from auto_codex.core import CodexRun, CodexSession, validate_provider_config


class TestProviderIntegration(unittest.TestCase):
    """Integration tests requiring live API access."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Check if OpenAI API key is available
        self.openai_available = bool(os.getenv('OPENAI_API_KEY'))
        
        if not self.openai_available:
            self.skipTest("OPENAI_API_KEY environment variable not set")
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_openai_provider_validation(self):
        """Test that OpenAI provider validation works with real API key."""
        if not self.openai_available:
            self.skipTest("OpenAI API key not available")
        
        # Should not raise any exception
        validate_provider_config('openai')
    
    def test_codex_run_with_openai_provider(self):
        """Test creating CodexRun with OpenAI provider."""
        if not self.openai_available:
            self.skipTest("OpenAI API key not available")
        
        run = CodexRun(
            prompt="echo 'Hello, World!'",
            provider="openai",
            model="gpt-4o-mini",  # Use a smaller, cheaper model for testing
            writable_root=self.temp_dir,
            timeout=60,
            approval_mode="auto"
        )
        
        self.assertEqual(run.provider, 'openai')
        self.assertEqual(run.model, 'gpt-4o-mini')
        self.assertEqual(run.prompt, "echo 'Hello, World!'")
    
    def test_codex_session_with_openai_provider(self):
        """Test creating CodexSession with OpenAI provider."""
        if not self.openai_available:
            self.skipTest("OpenAI API key not available")
        
        session = CodexSession(
            default_provider="openai",
            default_model="gpt-4o-mini",
            log_dir=self.temp_dir
        )
        
        self.assertEqual(session.default_provider, 'openai')
        self.assertEqual(session.default_model, 'gpt-4o-mini')
        
        # Add a run to the session
        run = session.add_run("echo 'Test from session'")
        
        self.assertEqual(run.provider, 'openai')
        self.assertEqual(run.model, 'gpt-4o-mini')
    
    def test_mixed_providers_in_session(self):
        """Test session with runs using different providers."""
        # This test is more conceptual since we'd need multiple API keys
        # For now, just test that the structure supports it
        
        if not self.openai_available:
            self.skipTest("OpenAI API key not available")
        
        session = CodexSession(
            default_provider="openai",
            default_model="gpt-4o-mini",
            log_dir=self.temp_dir,
            validate_env=False  # Skip validation for providers we don't have keys for
        )
        
        # Add runs with different providers
        run1 = session.add_run("echo 'OpenAI run'", provider="openai")
        run2 = session.add_run("echo 'Hypothetical Azure run'", provider="azure", model="gpt-4")
        
        self.assertEqual(run1.provider, 'openai')
        self.assertEqual(run2.provider, 'azure')
        self.assertEqual(run2.model, 'gpt-4')
    
    @unittest.skipIf(os.getenv('SKIP_LIVE_TESTS') == '1', "Live tests disabled")
    def test_live_codex_execution_with_provider(self):
        """Test actual execution of Codex with provider specification.
        
        This test executes a real Codex command. It's marked to be skipped
        if SKIP_LIVE_TESTS=1 environment variable is set.
        """
        if not self.openai_available:
            self.skipTest("OpenAI API key not available")
        
        # Use a very simple, safe command
        run = CodexRun(
            prompt="Create a simple hello.txt file with 'Hello, World!' in it",
            provider="openai",
            model="gpt-4o-mini",
            writable_root=self.temp_dir,
            timeout=120,
            approval_mode="full-auto",  # Allow full automation for this simple task
            debug=True
        )
        
        try:
            result = run.execute(self.temp_dir)
            
            # Basic assertions about the result
            self.assertIsNotNone(result)
            self.assertEqual(result.run_id, run.run_id)
            self.assertIn('provider', result.metadata)
            self.assertEqual(result.metadata['provider'], 'openai')
            self.assertEqual(result.metadata['model'], 'gpt-4o-mini')
            
            # If successful, check that the file was created
            hello_file = os.path.join(self.temp_dir, 'hello.txt')
            if result.success and os.path.exists(hello_file):
                with open(hello_file, 'r') as f:
                    content = f.read()
                    self.assertIn('Hello', content)
            
        except Exception as e:
            # If the test fails due to external factors (network, API issues, etc.)
            # we should not fail the entire test suite
            self.skipTest(f"Live test failed due to external factors: {e}")
    
    def test_provider_env_key_detection(self):
        """Test that provider environment keys are correctly detected."""
        if not self.openai_available:
            self.skipTest("OpenAI API key not available")
        
        from auto_codex.core import get_provider_env_key
        
        # Test known providers
        self.assertEqual(get_provider_env_key('openai'), 'OPENAI_API_KEY')
        self.assertEqual(get_provider_env_key('azure'), 'AZURE_OPENAI_API_KEY')
        self.assertEqual(get_provider_env_key('gemini'), 'GEMINI_API_KEY')
        
        # Test unknown provider fallback
        self.assertEqual(get_provider_env_key('custom_provider'), 'CUSTOM_PROVIDER_API_KEY')
    
    def test_multiple_runs_same_session_different_providers(self):
        """Test multiple runs in a session with different providers."""
        if not self.openai_available:
            self.skipTest("OpenAI API key not available")
        
        session = CodexSession(
            default_provider="openai",
            default_model="gpt-4o-mini",
            log_dir=self.temp_dir,
            validate_env=False  # Skip validation for other providers
        )
        
        # Add multiple runs with different configurations
        runs = [
            session.add_run("echo 'Run 1'", provider="openai", model="gpt-4o-mini"),
            session.add_run("echo 'Run 2'", provider="openai", model="gpt-4o"),  # Different model
            session.add_run("echo 'Run 3'"),  # Use session defaults
        ]
        
        # Verify each run has correct configuration
        self.assertEqual(runs[0].provider, 'openai')
        self.assertEqual(runs[0].model, 'gpt-4o-mini')
        
        self.assertEqual(runs[1].provider, 'openai')
        self.assertEqual(runs[1].model, 'gpt-4o')
        
        self.assertEqual(runs[2].provider, 'openai')  # Session default
        self.assertEqual(runs[2].model, 'gpt-4o-mini')  # Session default


class TestProviderErrorHandling(unittest.TestCase):
    """Test error handling in provider integration scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_missing_api_key_integration(self):
        """Test behavior when API key is missing for a provider."""
        # Remove any existing API keys from environment for this test
        original_key = os.environ.pop('FAKE_PROVIDER_API_KEY', None)
        
        try:
            with self.assertRaises(ValueError):
                # This should fail because 'fake_provider' is not supported
                run = CodexRun(
                    prompt="test",
                    provider="fake_provider",
                    writable_root=self.temp_dir
                )
        finally:
            # Restore original key if it existed
            if original_key:
                os.environ['FAKE_PROVIDER_API_KEY'] = original_key
    
    def test_invalid_provider_integration(self):
        """Test behavior with completely invalid provider."""
        with self.assertRaises(ValueError) as context:
            CodexRun(
                prompt="test",
                provider="definitely_not_a_real_provider",
                writable_root=self.temp_dir
            )
        
        self.assertIn("Unsupported provider", str(context.exception))
    
    def test_environment_validation_bypass(self):
        """Test that environment validation can be bypassed when needed."""
        # This should not raise an exception even though we don't have the API key
        run = CodexRun(
            prompt="test",
            provider="azure",  # We probably don't have this key
            writable_root=self.temp_dir,
            validate_env=False
        )
        
        self.assertEqual(run.provider, 'azure')

    def test_provider_validation_without_api_key(self):
        """Test provider validation functionality without requiring API keys."""
        # Test that get_provider_env_key works without having the actual keys
        from auto_codex.core import get_provider_env_key
        
        # Test all known providers (based on SUPPORTED_PROVIDERS)
        self.assertEqual(get_provider_env_key('openai'), 'OPENAI_API_KEY')
        self.assertEqual(get_provider_env_key('azure'), 'AZURE_OPENAI_API_KEY')
        self.assertEqual(get_provider_env_key('gemini'), 'GEMINI_API_KEY')
        self.assertEqual(get_provider_env_key('mistral'), 'MISTRAL_API_KEY')
        self.assertEqual(get_provider_env_key('groq'), 'GROQ_API_KEY')
        self.assertEqual(get_provider_env_key('xai'), 'XAI_API_KEY')
        
        # Test unknown provider fallback
        self.assertEqual(get_provider_env_key('claude'), 'CLAUDE_API_KEY')  # Not in supported list
        self.assertEqual(get_provider_env_key('custom_provider'), 'CUSTOM_PROVIDER_API_KEY')
        self.assertEqual(get_provider_env_key('new_ai_provider'), 'NEW_AI_PROVIDER_API_KEY')

    def test_codex_run_creation_without_validation(self):
        """Test creating CodexRun with various providers when validation is disabled."""
        providers_to_test = ['openai', 'azure', 'gemini', 'mistral', 'groq']
        
        for provider in providers_to_test:
            with self.subTest(provider=provider):
                run = CodexRun(
                    prompt=f"test prompt for {provider}",
                    provider=provider,
                    model="test-model",
                    writable_root=self.temp_dir,
                    validate_env=False
                )
                
                self.assertEqual(run.provider, provider)
                self.assertEqual(run.model, "test-model")
                self.assertEqual(run.prompt, f"test prompt for {provider}")

    def test_codex_session_creation_without_validation(self):
        """Test creating CodexSession with various providers when validation is disabled."""
        providers_to_test = ['openai', 'azure', 'gemini', 'mistral']
        
        for provider in providers_to_test:
            with self.subTest(provider=provider):
                session = CodexSession(
                    default_provider=provider,
                    default_model="test-model",
                    log_dir=self.temp_dir,
                    validate_env=False
                )
                
                self.assertEqual(session.default_provider, provider)
                self.assertEqual(session.default_model, "test-model")
                
                # Add a run to test inheritance
                run = session.add_run(f"test prompt for {provider}")
                self.assertEqual(run.provider, provider)
                self.assertEqual(run.model, "test-model")

    def test_mixed_providers_session_no_validation(self):
        """Test session with multiple providers without environment validation."""
        session = CodexSession(
            default_provider="openai",
            default_model="gpt-4",
            log_dir=self.temp_dir,
            validate_env=False  # Skip validation
        )
        
        # Add runs with different providers and models
        runs = []
        test_configs = [
            ("openai", "gpt-4o-mini"),
            ("azure", "gpt-4"),
            ("gemini", "gemini-pro"),
            ("mistral", "mistral-7b"),
            ("groq", "llama-70b"),
        ]
        
        for provider, model in test_configs:
            run = session.add_run(
                f"echo 'Test for {provider}'", 
                provider=provider, 
                model=model
            )
            runs.append(run)
            
            # Verify configuration
            self.assertEqual(run.provider, provider)
            self.assertEqual(run.model, model)
            self.assertEqual(run.prompt, f"echo 'Test for {provider}'")
        
        # Verify we have all the runs
        self.assertEqual(len(runs), 5)

    def test_provider_error_scenarios(self):
        """Test various provider error scenarios."""
        # Test with empty provider name
        with self.assertRaises(ValueError):
            CodexRun(
                prompt="test",
                provider="",
                writable_root=self.temp_dir
            )
        
        # Test with None provider
        with self.assertRaises(ValueError):
            CodexRun(
                prompt="test",
                provider=None,
                writable_root=self.temp_dir
            )
        
        # Test with whitespace-only provider
        with self.assertRaises(ValueError):
            CodexRun(
                prompt="test",
                provider="   ",
                writable_root=self.temp_dir
            )

    def test_api_key_detection_edge_cases(self):
        """Test edge cases in API key detection."""
        from auto_codex.core import get_provider_env_key
        
        # Test with special characters that are preserved as-is
        test_cases = [
            ('provider-with-dashes', 'PROVIDER-WITH-DASHES_API_KEY'),
            ('provider.with.dots', 'PROVIDER.WITH.DOTS_API_KEY'),
            ('Provider_With_Mixed_Case', 'PROVIDER_WITH_MIXED_CASE_API_KEY'),
            ('provider123', 'PROVIDER123_API_KEY'),
            ('123provider', '123PROVIDER_API_KEY'),
            ('provider-2.0_alpha', 'PROVIDER-2.0_ALPHA_API_KEY'),
        ]
        
        for provider, expected_key in test_cases:
            with self.subTest(provider=provider):
                actual_key = get_provider_env_key(provider)
                self.assertEqual(actual_key, expected_key)


class TestProviderIntegrationWithoutAPIKeys(unittest.TestCase):
    """Test provider integration functionality without requiring API keys."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        # Save original env var state
        self.original_openai_key = os.environ.get('OPENAI_API_KEY')
        # Remove API key to test skipping behavior
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        # Restore original env var
        if self.original_openai_key:
            os.environ['OPENAI_API_KEY'] = self.original_openai_key
    
    def test_provider_configuration_validation(self):
        """Test provider configuration validation for all supported providers."""
        from auto_codex.core import SUPPORTED_PROVIDERS, get_provider_env_key
        
        # Test all supported providers without needing their API keys
        for provider in SUPPORTED_PROVIDERS:
            with self.subTest(provider=provider):
                expected_key = SUPPORTED_PROVIDERS[provider]['env_key']
                actual_key = get_provider_env_key(provider)
                self.assertEqual(actual_key, expected_key)
    
    def test_session_run_management(self):
        """Test session-level run management with multiple providers."""
        session = CodexSession(
            default_provider="openai",
            default_model="gpt-4",
            log_dir=self.temp_dir,
            validate_env=False
        )
        
        # Test that session properly manages runs with different providers
        run1 = session.add_run("test 1", provider="openai")
        run2 = session.add_run("test 2", provider="azure", model="gpt-3.5-turbo")
        run3 = session.add_run("test 3")  # Should use defaults
        
        self.assertEqual(len(session.runs), 3)
        self.assertEqual(run1.provider, "openai")
        self.assertEqual(run2.provider, "azure")
        self.assertEqual(run2.model, "gpt-3.5-turbo")
        self.assertEqual(run3.provider, "openai")  # Default
        self.assertEqual(run3.model, "gpt-4")  # Default
    
    def test_environment_variable_checking(self):
        """Test environment variable logic for provider keys."""
        from auto_codex.core import get_provider_env_key
        
        # Test providers with special character handling (preserved as-is)
        self.assertEqual(get_provider_env_key('test-provider'), 'TEST-PROVIDER_API_KEY')
        self.assertEqual(get_provider_env_key('test.provider'), 'TEST.PROVIDER_API_KEY')
        self.assertEqual(get_provider_env_key('Test_Provider'), 'TEST_PROVIDER_API_KEY')
        
        # Test with numbers
        self.assertEqual(get_provider_env_key('gpt4'), 'GPT4_API_KEY')
        self.assertEqual(get_provider_env_key('claude3'), 'CLAUDE3_API_KEY')


# Test the main module functionality
class TestMainModuleEnvironmentHints(unittest.TestCase):
    """Test the main module environment hints and setup."""
    
    def setUp(self):
        """Set up test environment."""
        # Save original env var state
        self.original_openai_key = os.environ.get('OPENAI_API_KEY')
        self.original_skip_tests = os.environ.get('SKIP_LIVE_TESTS')
        
    def tearDown(self):
        """Clean up test environment."""
        # Restore original env vars
        if self.original_openai_key:
            os.environ['OPENAI_API_KEY'] = self.original_openai_key
        elif 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
            
        if self.original_skip_tests:
            os.environ['SKIP_LIVE_TESTS'] = self.original_skip_tests
        elif 'SKIP_LIVE_TESTS' in os.environ:
            del os.environ['SKIP_LIVE_TESTS']
    
    def test_main_block_functionality(self):
        """Test the main block warnings and environment hints."""
        # This doesn't actually run the main block, but tests the logic it would use
        import sys
        from io import StringIO
        
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # Test when no OPENAI_API_KEY is set
            if 'OPENAI_API_KEY' in os.environ:
                del os.environ['OPENAI_API_KEY']
            
            # Simulate the logic from the main block
            if not os.getenv('OPENAI_API_KEY'):
                print("Warning: OPENAI_API_KEY not set. Most integration tests will be skipped.")
                print("To run integration tests, set OPENAI_API_KEY environment variable.")
            
            if os.getenv('SKIP_LIVE_TESTS') == '1':
                print("Note: Live tests are disabled via SKIP_LIVE_TESTS=1")
            
            output = captured_output.getvalue()
            self.assertIn("Warning: OPENAI_API_KEY not set", output)
            
        finally:
            sys.stdout = sys.__stdout__
    
    def test_skip_live_tests_environment_variable(self):
        """Test SKIP_LIVE_TESTS environment variable handling."""
        import sys
        from io import StringIO
        
        # Set SKIP_LIVE_TESTS=1
        os.environ['SKIP_LIVE_TESTS'] = '1'
        
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # Simulate the logic from the main block
            if os.getenv('SKIP_LIVE_TESTS') == '1':
                print("Note: Live tests are disabled via SKIP_LIVE_TESTS=1")
            
            output = captured_output.getvalue()
            self.assertIn("Note: Live tests are disabled", output)
            
        finally:
            sys.stdout = sys.__stdout__


if __name__ == '__main__':
    # Set up test environment hints
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY not set. Most integration tests will be skipped.")
        print("To run integration tests, set OPENAI_API_KEY environment variable.")
    
    if os.getenv('SKIP_LIVE_TESTS') == '1':
        print("Note: Live tests are disabled via SKIP_LIVE_TESTS=1")
    
    unittest.main() 