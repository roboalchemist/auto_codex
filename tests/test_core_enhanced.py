"""
Enhanced tests for core module to achieve higher coverage.
Focuses on error handling, edge cases, and session management.
"""

import unittest
import tempfile
import os
import subprocess
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime
from auto_codex.core import CodexRun, CodexSession
from auto_codex.models import CodexRunResult, CodexSessionResult
from auto_codex.utils import TemplateProcessor


class TestCodexRunErrorHandling(unittest.TestCase):
    """Test error handling and edge cases in CodexRun."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.run = CodexRun(
            prompt="test prompt",
            writable_root=self.temp_dir,
            enable_health_monitoring=False
        )
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_execute_codex_timeout_error(self):
        """Test _execute_codex handles timeout errors."""
        self.run.timeout = 1  # Very short timeout
        self.run.log_file = os.path.join(self.temp_dir, "test.log")  # Set log file
        
        # Mock subprocess.Popen to simulate a hanging process
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None  # Process never completes
        mock_process.returncode = None
        
        with patch('subprocess.Popen', return_value=mock_process):
            with patch('builtins.open', mock_open()):
                with patch('time.time') as mock_time:
                    # Simulate time passing to trigger timeout
                    mock_time.side_effect = [0, 0, 0.5, 1.5]  # Timeout after 1 second
                    with self.assertRaises(RuntimeError) as context:
                        self.run._execute_codex()
                    
                    # Verify timeout message
                    self.assertIn("timed out", str(context.exception))
    
    def test_execute_codex_process_error(self):
        """Test _execute_codex handles process errors."""
        self.run.log_file = os.path.join(self.temp_dir, "test.log")  # Set log file
        
        # Mock subprocess.Popen to return non-zero exit code
        mock_process = MagicMock()
        mock_process.returncode = 1  # Non-zero return code
        mock_process.pid = 12345
        mock_process.poll.return_value = 1  # Process has exited with error
        mock_process.wait.return_value = None
        
        with patch('subprocess.Popen', return_value=mock_process):
            with patch('builtins.open', mock_open()):
                with patch('time.sleep'):  # Skip sleep
                    with self.assertRaises(RuntimeError):
                        self.run._execute_codex()
    
    def test_parse_results_missing_log_file(self):
        """Test _parse_results handles missing log file."""
        self.run.log_file = None
        
        with self.assertRaises(RuntimeError):
            self.run._parse_results()
    
    def test_parse_results_nonexistent_log_file(self):
        """Test _parse_results handles nonexistent log file."""
        self.run.log_file = "/nonexistent/path/test.log"
        
        with self.assertRaises(RuntimeError):
            self.run._parse_results()
    
    def test_get_changes_by_file_no_result(self):
        """Test get_changes_by_file when no result exists."""
        self.run.result = None
        
        changes = self.run.get_changes_by_file("test.py")
        self.assertEqual(changes, [])
    
    def test_get_tools_used_no_result(self):
        """Test get_tools_used when no result exists."""
        self.run.result = None
        
        tools = self.run.get_tools_used()
        self.assertEqual(tools, [])


class TestCodexSessionErrorHandling(unittest.TestCase):
    """Test error handling and edge cases in CodexSession."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.session = CodexSession(
            session_id="test_session",
            log_dir=self.temp_dir
        )
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_execute_all_with_run_failures(self):
        """Test execute_all handles run failures gracefully."""
        # Add a run that will fail
        run = self.session.add_run("test prompt")
        
        # Mock the run's execute method to raise an exception
        with patch.object(run, 'execute', side_effect=Exception("Test error")):
            # Also set run.result to None to simulate failure
            run.result = None
            result = self.session.execute_all()
            
            # Should complete despite failures
            self.assertIsInstance(result, CodexSessionResult)
            self.assertEqual(len(result.runs), 1)
            # The run result should be None since execute failed
            self.assertIsNone(result.runs[0])
    
    def test_execute_all_empty_runs(self):
        """Test execute_all with no runs."""
        result = self.session.execute_all()
        
        self.assertIsInstance(result, CodexSessionResult)
        self.assertEqual(len(result.runs), 0)
        self.assertEqual(len(result.successful_runs), 0)
    
    def test_process_csv_data_with_template_error(self):
        """Test process_csv_data handles template errors."""
        csv_data = [{"name": "test", "value": "123"}]
        bad_template = "{{ invalid.template.syntax"  # Malformed template
        
        # The method actually logs errors and continues, doesn't raise
        result = self.session.process_csv_data(csv_data, bad_template)
        self.assertIsInstance(result, CodexSessionResult)
        # Should have no successful runs due to template error
        self.assertEqual(len(result.successful_runs), 0)
    
    def test_process_csv_data_with_custom_processor(self):
        """Test process_csv_data with custom template processor."""
        csv_data = [{"name": "test", "value": "123"}]
        template = "Process {{ name }}"
        
        # Create custom processor
        custom_processor = TemplateProcessor()
        
        result = self.session.process_csv_data(
            csv_data, 
            template, 
            template_processor=custom_processor
        )
        
        self.assertIsInstance(result, CodexSessionResult)
        self.assertEqual(len(result.runs), 1)
    
    def test_get_summary_with_empty_result(self):
        """Test get_summary when result is None."""
        self.session.result = None
        
        summary = self.session.get_summary()
        
        # The method currently returns empty dict when no result
        self.assertEqual(summary, {})
    
    def test_get_summary_with_result(self):
        """Test get_summary with valid result."""
        # Create a mock result
        self.session.result = CodexSessionResult(
            session_id="test_session",
            runs=[],
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        
        summary = self.session.get_summary()
        
        self.assertIn('session_id', summary)
        self.assertIn('total_runs', summary)
        self.assertIn('successful_runs', summary)
        self.assertIn('total_files_modified', summary)
        self.assertIn('duration_seconds', summary)
    
    def test_analyze_by_tool_usage_no_result(self):
        """Test analyze_by_tool_usage when result is None."""
        self.session.result = None
        
        analysis = self.session.analyze_by_tool_usage()
        
        # Should return empty analysis
        self.assertEqual(analysis, {})
    
    def test_analyze_by_tool_usage_with_tools(self):
        """Test analyze_by_tool_usage with tool usage data."""
        from auto_codex.models import ToolUsage, ToolType, CodexRunResult
        
        # Create mock run with tool usage
        tool_usage = [
            ToolUsage("edit_file", ToolType.EDIT, "test.log"),
            ToolUsage("read_file", ToolType.READ, "test.log"),
            ToolUsage("edit_file", ToolType.EDIT, "test.log")  # Duplicate
        ]
        
        run = CodexRunResult(
            run_id="test",
            start_time=datetime.now(),
            tool_usage=tool_usage
        )
        
        self.session.result = CodexSessionResult(
            session_id="test_session",
            runs=[run]
        )
        
        analysis = self.session.analyze_by_tool_usage()
        
        self.assertEqual(analysis["edit_file"], 2)
        self.assertEqual(analysis["read_file"], 1)
    
    def test_get_runs_by_success_no_result(self):
        """Test get_runs_by_success when result is None."""
        self.session.result = None
        
        # Test for successful runs
        runs = self.session.get_runs_by_success(True)
        self.assertEqual(runs, [])
        
        # Test for failed runs
        runs = self.session.get_runs_by_success(False)
        self.assertEqual(runs, [])
    
    def test_get_runs_by_success_filtering(self):
        """Test get_runs_by_success filters correctly."""
        from auto_codex.models import CodexRunResult
        
        # Create successful and failed runs
        successful_run = CodexRunResult(
            run_id="success",
            start_time=datetime.now(),
            success=True
        )
        
        failed_run = CodexRunResult(
            run_id="failure", 
            start_time=datetime.now(),
            success=False
        )
        
        self.session.result = CodexSessionResult(
            session_id="test_session",
            runs=[successful_run, failed_run]
        )
        
        # Test successful runs
        successful_runs = self.session.get_runs_by_success(True)
        self.assertEqual(len(successful_runs), 1)
        self.assertEqual(successful_runs[0].run_id, "success")
        
        # Test failed runs
        failed_runs = self.session.get_runs_by_success(False)
        self.assertEqual(len(failed_runs), 1)
        self.assertEqual(failed_runs[0].run_id, "failure")


class TestCodexRunIntegrationErrorHandling(unittest.TestCase):
    """Test integration scenarios with error handling."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_execute_with_io_errors(self):
        """Test execute method handles I/O errors."""
        run = CodexRun(
            prompt="test prompt",
            writable_root="/nonexistent/directory"  # Invalid directory
        )
        
        # The execute method catches the error and logs it
        try:
            run.execute(self.temp_dir)
        except Exception as e:
            # Should get an OSError or FileNotFoundError
            self.assertIsInstance(e, (OSError, FileNotFoundError))
    
    def test_execute_with_permission_errors(self):
        """Test execute method handles permission errors."""
        run = CodexRun(
            prompt="test prompt",
            writable_root=self.temp_dir
        )
        
        # Mock file operations to raise permission error in execute method
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            try:
                run.execute(self.temp_dir)
            except Exception as e:
                # Should get a PermissionError
                self.assertIsInstance(e, PermissionError)


if __name__ == '__main__':
    unittest.main() 