import unittest
import tempfile
import os
import shutil
from unittest.mock import patch, Mock, MagicMock, call
from datetime import datetime
from auto_codex.core import CodexRun, CodexSession
from auto_codex.models import CodexRunResult, CodexSessionResult, CodexChange, PatchData, ToolUsage, ChangeType, ToolType


class TestCodexRun(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_prompt = "Test prompt"
        self.test_model = "gpt-4.1-nano"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_default_values(self):
        """Test CodexRun initialization with default values."""
        run = CodexRun(self.test_prompt, validate_env=False)
        
        self.assertEqual(run.prompt, self.test_prompt)
        self.assertEqual(run.model, "gpt-4.1-nano")
        self.assertEqual(run.timeout, 300)
        self.assertEqual(run.approval_mode, "full-auto")
        self.assertFalse(run.debug)
        self.assertIsNotNone(run.run_id)
        self.assertIsNone(run.start_time)
        self.assertIsNone(run.end_time)
        self.assertFalse(run.success)
        
    def test_init_custom_values(self):
        """Test CodexRun initialization with custom values."""
        custom_run_id = "test-run-123"
        custom_timeout = 600
        
        run = CodexRun(
            prompt=self.test_prompt,
            model="gpt-3.5-turbo",
            writable_root=self.temp_dir,
            timeout=custom_timeout,
            run_id=custom_run_id,
            approval_mode="full-auto",
            debug=True,
            validate_env=False
        )
        
        self.assertEqual(run.run_id, custom_run_id)
        self.assertEqual(run.model, "gpt-3.5-turbo")
        self.assertEqual(run.writable_root, self.temp_dir)
        self.assertEqual(run.timeout, custom_timeout)
        self.assertEqual(run.approval_mode, "full-auto")
        self.assertTrue(run.debug)

    @patch('auto_codex.core.CodexLogParser')
    @patch('subprocess.Popen')
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_execute_success(self, mock_exists, mock_open, mock_subprocess, mock_parser_class):
        """Test successful execution of CodexRun."""
        # Setup mocks
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.pid = 12345
        mock_process.poll.return_value = 0
        mock_process.wait.return_value = None
        # Simulate readline behavior
        mock_process.stdout.readline.side_effect = ["Test output\n", ""]
        mock_subprocess.return_value = mock_process
        
        # Mock file operations
        mock_exists.return_value = True
        mock_file = Mock()
        mock_file.read.return_value = "Test output"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock parser
        mock_parser = Mock()
        mock_result = CodexRunResult(
            run_id="test-run",
            start_time=datetime.now(),
            success=True,
            changes=[],
            patches=[],
            tool_usage=[]
        )
        mock_parser.parse_run.return_value = mock_result
        mock_parser_class.return_value = mock_parser
        
        # Execute
        run = CodexRun(self.test_prompt, writable_root=self.temp_dir, enable_health_monitoring=False, validate_env=False)
        result = run.execute(self.temp_dir)
        
        # Assertions
        self.assertTrue(run.success)
        self.assertIsNotNone(run.start_time)
        self.assertIsNotNone(run.end_time)
        self.assertIsNotNone(run.log_file)
        self.assertEqual(result, mock_result)
        
        # Verify subprocess was called with correct arguments
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]  # First positional arg
        self.assertIn("auto-codex", call_args)
        self.assertIn(f"--model={self.test_model}", call_args)
        self.assertIn(f"--writable-root={self.temp_dir}", call_args)
        self.assertIn("--full-auto", call_args)
        self.assertIn("--quiet", call_args)
        self.assertIn(self.test_prompt, call_args)

    @patch('subprocess.Popen')
    def test_execute_subprocess_failure(self, mock_subprocess):
        """Test execution with subprocess failure."""
        # Setup subprocess to fail
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.pid = 12345
        mock_process.poll.return_value = 1
        mock_process.wait.return_value = None
        mock_process.stdout.readline.side_effect = ["Error output\n", ""]
        mock_subprocess.return_value = mock_process
        
        run = CodexRun(self.test_prompt, writable_root=self.temp_dir, enable_health_monitoring=False, validate_env=False)
        result = run.execute(self.temp_dir)
        
        # Should handle failure gracefully
        self.assertFalse(run.success)
        self.assertIsNotNone(run.error)
        self.assertIsNotNone(result)
        self.assertFalse(result.success)

    @patch('auto_codex.core.CodexLogParser')
    @patch('subprocess.Popen')
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_get_changes_by_file(self, mock_exists, mock_open, mock_subprocess, mock_parser_class):
        """Test getting changes for a specific file."""
        # Setup successful execution
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.pid = 12345
        mock_process.poll.return_value = 0
        mock_process.wait.return_value = None
        mock_process.stdout.readline.side_effect = ["Test output\n", ""]
        mock_subprocess.return_value = mock_process
        
        mock_exists.return_value = True
        mock_file = Mock()
        mock_file.read.return_value = "Test output"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Create test changes and patches
        test_change = CodexChange(
            type=ChangeType.PATCH,
            log_file="test.log",
            file_path="test.py",
            content="test content"
        )
        test_patch = PatchData(
            file_path="test.py",
            diff_content="test patch",
            log_file="test.log",
            lines_added=1,
            lines_removed=0
        )
        
        mock_result = CodexRunResult(
            run_id="test-run",
            start_time=datetime.now(),
            success=True,
            changes=[test_change],
            patches=[test_patch],
            tool_usage=[]
        )
        
        mock_parser = Mock()
        mock_parser.parse_run.return_value = mock_result
        mock_parser_class.return_value = mock_parser
        
        # Execute and test
        run = CodexRun(self.test_prompt, writable_root=self.temp_dir, enable_health_monitoring=False, validate_env=False)
        run.execute(self.temp_dir)
        
        changes = run.get_changes_by_file("test.py")
        self.assertEqual(len(changes), 2)
        self.assertIn(test_change, changes)
        self.assertIn(test_patch, changes)
        
        # Test with non-existent file
        empty_changes = run.get_changes_by_file("nonexistent.py")
        self.assertEqual(len(empty_changes), 0)

    @patch('auto_codex.core.CodexLogParser')
    @patch('subprocess.Popen')
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_get_tools_used(self, mock_exists, mock_open, mock_subprocess, mock_parser_class):
        """Test getting list of tools used."""
        # Setup successful execution
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.pid = 12345
        mock_process.poll.return_value = 0
        mock_process.wait.return_value = None
        mock_process.stdout.readline.side_effect = ["Test output\n", ""]
        mock_subprocess.return_value = mock_process
        
        mock_exists.return_value = True
        mock_file = Mock()
        mock_file.read.return_value = "Test output"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Create test tool usage
        tool_usage = [
            ToolUsage(tool_name="shell", tool_type=ToolType.RUN, log_file="test.log"),
            ToolUsage(tool_name="file_edit", tool_type=ToolType.EDIT, log_file="test.log"),
            ToolUsage(tool_name="shell", tool_type=ToolType.RUN, log_file="test.log")  # Duplicate
        ]
        
        mock_result = CodexRunResult(
            run_id="test-run",
            start_time=datetime.now(),
            success=True,
            changes=[],
            patches=[],
            tool_usage=tool_usage
        )
        
        mock_parser = Mock()
        mock_parser.parse_run.return_value = mock_result
        mock_parser_class.return_value = mock_parser
        
        # Execute and test
        run = CodexRun(self.test_prompt, writable_root=self.temp_dir, enable_health_monitoring=False, validate_env=False)
        run.execute(self.temp_dir)
        
        tools = run.get_tools_used()
        self.assertEqual(sorted(tools), ["file_edit", "shell"])


class TestCodexSession(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.session_id = "test-session-123"
        self.test_prompt = "Test prompt"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_default_values(self):
        """Test CodexSession initialization with default values."""
        session = CodexSession(validate_env=False)
        
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.default_model, "gpt-4.1-nano")
        self.assertEqual(session.default_timeout, 300)
        self.assertEqual(session.log_dir, ".")
        self.assertFalse(session.debug)
        self.assertEqual(len(session.runs), 0)

    def test_init_custom_values(self):
        """Test CodexSession initialization with custom values."""
        session = CodexSession(
            session_id=self.session_id,
            default_model="gpt-3.5-turbo",
            default_timeout=600,
            log_dir=self.temp_dir,
            debug=True,
            validate_env=False
        )
        
        self.assertEqual(session.session_id, self.session_id)
        self.assertEqual(session.default_model, "gpt-3.5-turbo")
        self.assertEqual(session.default_timeout, 600)
        self.assertEqual(session.log_dir, self.temp_dir)
        self.assertTrue(session.debug)

    def test_add_run_default_values(self):
        """Test adding a run with default values."""
        session = CodexSession(session_id=self.session_id, validate_env=False)
        run = session.add_run(self.test_prompt)
        
        self.assertEqual(run.prompt, self.test_prompt)
        self.assertEqual(run.model, "gpt-4.1-nano")
        self.assertEqual(run.approval_mode, "full-auto")
        self.assertIs(run.debug, False)

    def test_add_run_custom_values(self):
        """Test adding a run with custom values."""
        session = CodexSession(session_id=self.session_id, validate_env=False)
        run = session.add_run(
            prompt=self.test_prompt,
            model="gpt-3.5-turbo",
            timeout=600,
            approval_mode="manual",
            dangerously_auto_approve_everything=True
        )
        
        self.assertEqual(run.model, "gpt-3.5-turbo")
        self.assertEqual(run.timeout, 600)
        self.assertEqual(run.approval_mode, "manual")
        self.assertTrue(run.dangerously_auto_approve_everything)

    @patch('auto_codex.core.CodexRun.execute')
    def test_execute_all_success(self, mock_execute):
        """Test executing all runs successfully."""
        session = CodexSession(session_id=self.session_id, log_dir=self.temp_dir, validate_env=False)
        
        # Add multiple runs
        run1 = session.add_run("Prompt 1")
        run2 = session.add_run("Prompt 2")
        
        # Mock successful execution
        mock_result1 = CodexRunResult(
            run_id=run1.run_id,
            start_time=datetime.now(),
            success=True,
            changes=[],
            patches=[],
            tool_usage=[]
        )
        mock_result2 = CodexRunResult(
            run_id=run2.run_id,
            start_time=datetime.now(),
            success=True,
            changes=[],
            patches=[],
            tool_usage=[]
        )
        
        mock_execute.side_effect = [mock_result1, mock_result2]
        
        # Execute all
        result = session.execute_all()
        
        # Assertions
        self.assertIsInstance(result, CodexSessionResult)
        self.assertEqual(result.session_id, self.session_id)
        self.assertEqual(len(result.runs), 2)
        self.assertIsNotNone(session.start_time)
        self.assertIsNotNone(session.end_time)
        
        # Verify execute was called for each run
        self.assertEqual(mock_execute.call_count, 2)
        mock_execute.assert_has_calls([
            call(self.temp_dir),
            call(self.temp_dir)
        ])

    @patch('auto_codex.core.TemplateProcessor')
    def test_process_csv_data(self, mock_template_processor_class):
        """Test processing CSV data with template."""
        session = CodexSession(session_id=self.session_id, validate_env=False)
        
        # Mock template processor
        mock_processor = Mock()
        mock_processor.render_template.side_effect = [
            "Rendered prompt 1",
            "Rendered prompt 2"
        ]
        mock_template_processor_class.return_value = mock_processor
        
        # Test data
        csv_data = [
            {"name": "John", "age": "30"},
            {"name": "Jane", "age": "25"}
        ]
        template = "Process user {{name}} aged {{age}}"
        
        # Mock execute_all
        with patch.object(session, 'execute_all') as mock_execute_all:
            mock_result = CodexSessionResult(
                session_id=self.session_id,
                runs=[],
                start_time=datetime.now(),
                end_time=datetime.now()
            )
            mock_execute_all.return_value = mock_result
            
            result = session.process_csv_data(csv_data, template)
            
            # Verify runs were created
            self.assertEqual(len(session.runs), 2)
            self.assertEqual(session.runs[0].prompt, "Rendered prompt 1")
            self.assertEqual(session.runs[1].prompt, "Rendered prompt 2")
            
            # Verify CSV metadata was added
            self.assertEqual(session.runs[0].csv_row_index, 0)
            self.assertEqual(session.runs[0].csv_row_data, csv_data[0])
            
            # Verify execute_all was called
            mock_execute_all.assert_called_once()

    def test_get_summary_no_result(self):
        """Test getting summary when no result is available."""
        session = CodexSession(session_id=self.session_id, validate_env=False)
        summary = session.get_summary()
        self.assertEqual(summary, {})

    def test_analyze_by_tool_usage_no_result(self):
        """Test tool usage analysis when no result is available."""
        session = CodexSession(session_id=self.session_id, validate_env=False)
        analysis = session.analyze_by_tool_usage()
        self.assertEqual(analysis, {})

    def test_get_runs_by_success_no_result(self):
        """Test filtering runs by success when no result is available."""
        session = CodexSession(session_id=self.session_id, validate_env=False)
        successful_runs = session.get_runs_by_success(True)
        failed_runs = session.get_runs_by_success(False)
        self.assertEqual(successful_runs, [])
        self.assertEqual(failed_runs, [])


if __name__ == '__main__':
    unittest.main() 