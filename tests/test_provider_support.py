"""
Test cases for provider support in auto_codex.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
from datetime import datetime

from auto_codex.core import (
    CodexRun, 
    CodexSession, 
    SUPPORTED_PROVIDERS, 
    validate_provider_config, 
    get_provider_env_key
)


class TestProviderConfiguration(unittest.TestCase):
    """Test provider configuration utilities."""
    
    def test_supported_providers_structure(self):
        """Test that SUPPORTED_PROVIDERS has the expected structure."""
        required_keys = ['name', 'env_key', 'base_url']
        
        self.assertIsInstance(SUPPORTED_PROVIDERS, dict)
        self.assertGreater(len(SUPPORTED_PROVIDERS), 0)
        
        for provider_name, config in SUPPORTED_PROVIDERS.items():
            self.assertIsInstance(provider_name, str)
            self.assertIsInstance(config, dict)
            
            for key in ['name', 'env_key']:  # base_url can be None for some providers
                self.assertIn(key, config)
                self.assertIsInstance(config[key], str)
    
    def test_get_provider_env_key_known_providers(self):
        """Test getting environment keys for known providers."""
        self.assertEqual(get_provider_env_key('openai'), 'OPENAI_API_KEY')
        self.assertEqual(get_provider_env_key('azure'), 'AZURE_OPENAI_API_KEY')
        self.assertEqual(get_provider_env_key('gemini'), 'GEMINI_API_KEY')
    
    def test_get_provider_env_key_unknown_provider(self):
        """Test getting environment key for unknown provider."""
        result = get_provider_env_key('unknown_provider')
        self.assertEqual(result, 'UNKNOWN_PROVIDER_API_KEY')
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_validate_provider_config_success(self):
        """Test successful provider validation."""
        # Should not raise any exception
        validate_provider_config('openai')
    
    @patch.dict(os.environ, {}, clear=True)
    def test_validate_provider_config_missing_env_var(self):
        """Test provider validation with missing environment variable."""
        with self.assertRaises(RuntimeError) as context:
            validate_provider_config('openai')
        
        self.assertIn('Missing environment variable OPENAI_API_KEY', str(context.exception))
    
    def test_validate_provider_config_invalid_provider(self):
        """Test provider validation with invalid provider."""
        with self.assertRaises(ValueError) as context:
            validate_provider_config('invalid_provider')
        
        self.assertIn('Unsupported provider: invalid_provider', str(context.exception))


class TestCodexRunProviderSupport(unittest.TestCase):
    """Test provider support in CodexRun class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_codex_run_default_provider(self):
        """Test CodexRun with default provider."""
        run = CodexRun(
            prompt="test prompt",
            writable_root=self.temp_dir
        )
        
        self.assertEqual(run.provider, 'openai')
        self.assertEqual(run.model, 'gpt-4.1-nano')
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_codex_run_custom_provider(self):
        """Test CodexRun with custom provider."""
        run = CodexRun(
            prompt="test prompt",
            provider="gemini",
            model="gemini-pro",
            writable_root=self.temp_dir
        )
        
        self.assertEqual(run.provider, 'gemini')
        self.assertEqual(run.model, 'gemini-pro')
    
    @patch.dict(os.environ, {}, clear=True)
    def test_codex_run_missing_env_var(self):
        """Test CodexRun with missing environment variable."""
        with self.assertRaises(RuntimeError) as context:
            CodexRun(
                prompt="test prompt",
                provider="openai",
                writable_root=self.temp_dir
            )
        
        self.assertIn('Missing environment variable OPENAI_API_KEY', str(context.exception))
    
    @patch.dict(os.environ, {}, clear=True)
    def test_codex_run_skip_validation(self):
        """Test CodexRun with validation disabled."""
        # Should not raise exception even without env var
        run = CodexRun(
            prompt="test prompt",
            provider="openai",
            writable_root=self.temp_dir,
            validate_env=False
        )
        
        self.assertEqual(run.provider, 'openai')
    
    def test_codex_run_invalid_provider(self):
        """Test CodexRun with invalid provider."""
        with self.assertRaises(ValueError) as context:
            CodexRun(
                prompt="test prompt",
                provider="invalid_provider",
                writable_root=self.temp_dir
            )
        
        self.assertIn('Unsupported provider: invalid_provider', str(context.exception))
    
    @patch('auto_codex.core.subprocess.Popen')
    @patch('builtins.open')
    @patch('auto_codex.core.CodexLogParser')
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_execute_includes_provider_flag(self, mock_parser, mock_open, mock_subprocess):
        """Test that execute includes the --provider flag in the command."""
        # Setup mocks
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.pid = 12345
        mock_process.poll.return_value = 0  # Process completed successfully
        mock_process.wait.return_value = None
        mock_subprocess.return_value = mock_process
        
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_result = MagicMock()
        mock_result.metadata = {}
        mock_parser_instance.parse_run.return_value = mock_result
        
        # Create and execute run
        run = CodexRun(
            prompt="test prompt",
            provider="gemini",
            model="gemini-pro",
            writable_root=self.temp_dir,
            enable_health_monitoring=False
        )
        
        run.execute(self.temp_dir)
        
        # Check that subprocess was called with provider flag
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]  # First positional argument (cmd_parts)
        
        self.assertIn('--provider=gemini', call_args)
        self.assertIn('--model=gemini-pro', call_args)
    
    @patch('auto_codex.core.subprocess.Popen')
    @patch('builtins.open')
    @patch('auto_codex.core.CodexLogParser')
    @patch('os.path.exists')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_execute_metadata_includes_provider(self, mock_exists, mock_parser, mock_open, mock_subprocess):
        """Test that execution metadata includes provider information."""
        # Setup mocks
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.pid = 12345
        mock_process.poll.return_value = 0  # Process completed successfully
        mock_process.wait.return_value = None
        mock_subprocess.return_value = mock_process
        
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock that log file exists
        mock_exists.return_value = True
        
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_result = MagicMock()
        mock_result.metadata = {}
        mock_parser_instance.parse_run.return_value = mock_result
        
        # Create and execute run
        run = CodexRun(
            prompt="test prompt",
            provider="openai",
            writable_root=self.temp_dir,
            enable_health_monitoring=False
        )
        
        result = run.execute(self.temp_dir)
        
        # Check metadata includes provider
        self.assertIn('provider', result.metadata)
        self.assertEqual(result.metadata['provider'], 'openai')


class TestCodexSessionProviderSupport(unittest.TestCase):
    """Test provider support in CodexSession class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_codex_session_default_provider(self):
        """Test CodexSession with default provider."""
        session = CodexSession(
            log_dir=self.temp_dir
        )
        
        self.assertEqual(session.default_provider, 'openai')
        self.assertEqual(session.default_model, 'gpt-4.1-nano')
    
    @patch.dict(os.environ, {'AZURE_OPENAI_API_KEY': 'test-key'})
    def test_codex_session_custom_provider(self):
        """Test CodexSession with custom provider."""
        session = CodexSession(
            default_provider="azure",
            default_model="gpt-4",
            log_dir=self.temp_dir
        )
        
        self.assertEqual(session.default_provider, 'azure')
        self.assertEqual(session.default_model, 'gpt-4')
    
    @patch.dict(os.environ, {}, clear=True)
    def test_codex_session_missing_env_var(self):
        """Test CodexSession with missing environment variable."""
        with self.assertRaises(RuntimeError) as context:
            CodexSession(
                default_provider="openai",
                log_dir=self.temp_dir
            )
        
        self.assertIn('Missing environment variable OPENAI_API_KEY', str(context.exception))
    
    @patch.dict(os.environ, {}, clear=True)
    def test_codex_session_skip_validation(self):
        """Test CodexSession with validation disabled."""
        # Should not raise exception even without env var
        session = CodexSession(
            default_provider="openai",
            log_dir=self.temp_dir,
            validate_env=False
        )
        
        self.assertEqual(session.default_provider, 'openai')
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_add_run_inherits_provider(self):
        """Test that add_run inherits session's default provider."""
        session = CodexSession(
            default_provider="openai",
            default_model="gpt-4",
            log_dir=self.temp_dir
        )
        
        run = session.add_run("test prompt")
        
        self.assertEqual(run.provider, 'openai')
        self.assertEqual(run.model, 'gpt-4')
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key', 'GEMINI_API_KEY': 'test-key'})
    def test_add_run_override_provider(self):
        """Test that add_run can override session's default provider."""
        session = CodexSession(
            default_provider="openai",
            default_model="gpt-4",
            log_dir=self.temp_dir,
            validate_env=False  # Skip validation to avoid needing all env vars
        )
        
        run = session.add_run(
            "test prompt",
            provider="gemini",
            model="gemini-pro"
        )
        
        self.assertEqual(run.provider, 'gemini')
        self.assertEqual(run.model, 'gemini-pro')


class TestProviderEnvironmentHandling(unittest.TestCase):
    """Test environment variable handling for different providers."""
    
    def test_all_providers_have_env_keys(self):
        """Test that all supported providers have environment keys defined."""
        for provider_name, config in SUPPORTED_PROVIDERS.items():
            env_key = config['env_key']
            self.assertIsInstance(env_key, str)
            self.assertTrue(env_key.endswith('_API_KEY'))
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'openai-key',
        'AZURE_OPENAI_API_KEY': 'azure-key',
        'GEMINI_API_KEY': 'gemini-key',
        'GROQ_API_KEY': 'groq-key'
    })
    def test_multiple_providers_validation(self):
        """Test validation with multiple provider environment variables set."""
        # All of these should succeed
        validate_provider_config('openai')
        validate_provider_config('azure')
        validate_provider_config('gemini')
        validate_provider_config('groq')
    
    @patch.dict(os.environ, {}, clear=True)
    def test_no_env_vars_set(self):
        """Test behavior when no environment variables are set."""
        providers_to_test = ['openai', 'azure', 'gemini', 'groq']
        
        for provider in providers_to_test:
            with self.assertRaises(RuntimeError):
                validate_provider_config(provider)


if __name__ == '__main__':
    unittest.main() 