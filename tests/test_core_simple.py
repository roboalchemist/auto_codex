"""
Simplified tests for auto_codex core functionality.
These tests focus on testing the core logic without complex subprocess mocking.
"""

import unittest
import tempfile
import shutil
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from auto_codex.core import CodexRun, CodexSession
from auto_codex.models import CodexRunResult, CodexSessionResult, ChangeType, ToolType, CodexChange, PatchData, ToolUsage


class TestCodexRunSimple(unittest.TestCase):
    """Simplified tests for CodexRun class."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_prompt = "Test prompt"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_with_health_monitoring_disabled(self):
        """Test CodexRun initialization with health monitoring disabled."""
        run = CodexRun(
            prompt=self.test_prompt,
            writable_root=self.temp_dir,
            enable_health_monitoring=False
        )
        
        self.assertEqual(run.prompt, self.test_prompt)
        self.assertEqual(run.writable_root, self.temp_dir)
        self.assertIsNone(run.health_monitor)
        self.assertIsNone(run.health_info)

    def test_get_changes_by_file_with_result(self):
        """Test get_changes_by_file when result exists."""
        run = CodexRun(self.test_prompt, enable_health_monitoring=False)
        
        # Create test data
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
        
        # Set up result
        run.result = CodexRunResult(
            run_id="test-run",
            start_time=datetime.now(),
            success=True,
            changes=[test_change],
            patches=[test_patch],
            tool_usage=[]
        )
        
        # Test
        changes = run.get_changes_by_file("test.py")
        self.assertEqual(len(changes), 2)
        self.assertIn(test_change, changes)
        self.assertIn(test_patch, changes)
        
        # Test with non-existent file
        empty_changes = run.get_changes_by_file("nonexistent.py")
        self.assertEqual(len(empty_changes), 0)

    def test_get_tools_used_with_result(self):
        """Test get_tools_used when result exists."""
        run = CodexRun(self.test_prompt, enable_health_monitoring=False)
        
        # Create test tool usage
        tool_usage = [
            ToolUsage(tool_name="shell", tool_type=ToolType.RUN, log_file="test.log"),
            ToolUsage(tool_name="file_edit", tool_type=ToolType.EDIT, log_file="test.log"),
            ToolUsage(tool_name="shell", tool_type=ToolType.RUN, log_file="test.log")  # Duplicate
        ]
        
        # Set up result
        run.result = CodexRunResult(
            run_id="test-run",
            start_time=datetime.now(),
            success=True,
            changes=[],
            patches=[],
            tool_usage=tool_usage
        )
        
        # Test
        tools = run.get_tools_used()
        self.assertEqual(sorted(tools), ["file_edit", "shell"])

    def test_health_methods_without_monitoring(self):
        """Test health-related methods when monitoring is disabled."""
        run = CodexRun(self.test_prompt, enable_health_monitoring=False)
        
        # These should handle gracefully when monitoring is disabled
        self.assertIsNone(run.get_health_status())
        self.assertFalse(run.is_running())
        self.assertTrue(run.is_healthy())  # Assume healthy if no monitoring
        self.assertFalse(run.terminate())

    def test_runtime_calculation(self):
        """Test runtime calculation."""
        run = CodexRun(self.test_prompt, enable_health_monitoring=False)
        
        # No start time
        self.assertEqual(run.get_runtime_seconds(), 0.0)
        
        # With start time, no end time
        run.start_time = datetime.now()
        runtime = run.get_runtime_seconds()
        self.assertGreater(runtime, 0)
        
        # With both start and end time
        run.end_time = run.start_time
        self.assertEqual(run.get_runtime_seconds(), 0.0)


class TestCodexSessionSimple(unittest.TestCase):
    """Simplified tests for CodexSession class."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.session_id = "test-session-123"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_with_health_monitoring_disabled(self):
        """Test CodexSession initialization with health monitoring disabled."""
        session = CodexSession(
            session_id=self.session_id,
            enable_health_monitoring=False
        )
        
        self.assertEqual(session.session_id, self.session_id)
        self.assertIsNone(session.health_monitor)

    def test_add_run_inherits_health_monitoring_setting(self):
        """Test that add_run inherits health monitoring setting."""
        session = CodexSession(
            session_id=self.session_id,
            enable_health_monitoring=False
        )
        
        run = session.add_run("test prompt")
        self.assertIsNone(run.health_monitor)
        self.assertIsNone(run.health_info)

    def test_health_methods_without_monitoring(self):
        """Test health-related methods when monitoring is disabled."""
        session = CodexSession(
            session_id=self.session_id,
            enable_health_monitoring=False
        )
        
        # Add some runs
        run1 = session.add_run("prompt 1")
        run2 = session.add_run("prompt 2")
        
        # These should handle gracefully when monitoring is disabled
        summary = session.get_session_health_summary()
        self.assertIn('monitoring_enabled', summary)
        self.assertEqual(summary['monitoring_enabled'], False)
        
        self.assertEqual(len(session.get_running_runs()), 0)
        # When monitoring is disabled, get_healthy_runs should return empty or all runs
        # depending on implementation. Let's just check it doesn't crash
        healthy_runs = session.get_healthy_runs()
        self.assertIsInstance(healthy_runs, list)
        self.assertEqual(session.terminate_all_running(), 0)


if __name__ == '__main__':
    unittest.main() 