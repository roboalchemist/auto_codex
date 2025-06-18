"""
Advanced edge case tests for auto_codex to improve test coverage.
Focuses on uncovered lines in core.py and health.py.
"""

import unittest
import tempfile
import os
import signal
import time
import subprocess
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime, timedelta

from auto_codex.core import CodexSession, CodexRun
from auto_codex.health import (
    AgentHealthMonitor, AgentMetrics, AgentHealthInfo, 
    AgentStatus, HealthStatus, get_health_monitor, stop_global_monitor
)
from auto_codex.utils import TemplateProcessor
from auto_codex.models import CodexRunResult


class TestCodexSessionAdvancedEdgeCases(unittest.TestCase):
    """Test advanced edge cases in CodexSession."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.session = CodexSession(
            log_dir=self.temp_dir,
            enable_health_monitoring=True,
            validate_env=False
        )
    
    def tearDown(self):
        # Clean up
        if hasattr(self.session, 'health_monitor') and self.session.health_monitor:
            self.session.health_monitor.stop_monitoring()
    
    def test_get_session_health_summary_no_monitoring(self):
        """Test session health summary when monitoring is disabled."""
        session = CodexSession(enable_health_monitoring=False, validate_env=False)
        summary = session.get_session_health_summary()
        self.assertFalse(summary["monitoring_enabled"])
    
    def test_get_session_health_summary_no_agents(self):
        """Test session health summary when no agents are registered."""
        summary = self.session.get_session_health_summary()
        self.assertTrue(summary["monitoring_enabled"])
        self.assertEqual(summary["agents"], 0)
    
    def test_get_session_health_summary_with_agents(self):
        """Test session health summary with various agent states."""
        # Add some runs to the session
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.stdout.readline.side_effect = ["", ""]
            mock_popen.return_value = mock_process
            run1 = self.session.add_run("test prompt 1")
            run2 = self.session.add_run("test prompt 2")
        
        # Register agents with different statuses
        if self.session.health_monitor:
            self.session.health_monitor.register_agent(run1.run_id)
            self.session.health_monitor.register_agent(run2.run_id)
            
            # Set different statuses
            self.session.health_monitor.update_agent_status(run1.run_id, AgentStatus.COMPLETED)
            self.session.health_monitor.update_agent_status(run2.run_id, AgentStatus.FAILED, "Test error")
        
        summary = self.session.get_session_health_summary()
        
        self.assertTrue(summary["monitoring_enabled"])
        self.assertEqual(summary["total_agents"], 2)
        self.assertEqual(summary["completed"], 1)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["completion_percentage"], 50.0)
    
    def test_get_runs_by_status(self):
        """Test filtering runs by agent status."""
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.stdout.readline.side_effect = ["", ""]
            mock_popen.return_value = mock_process
            run1 = self.session.add_run("test prompt 1")
            run2 = self.session.add_run("test prompt 2")
        
        if self.session.health_monitor:
            self.session.health_monitor.register_agent(run1.run_id)
            self.session.health_monitor.register_agent(run2.run_id)
            
            self.session.health_monitor.update_agent_status(run1.run_id, AgentStatus.COMPLETED)
            self.session.health_monitor.update_agent_status(run2.run_id, AgentStatus.FAILED)
        
        completed_runs = self.session.get_runs_by_status(AgentStatus.COMPLETED)
        failed_runs = self.session.get_runs_by_status(AgentStatus.FAILED)
        
        self.assertEqual(len(completed_runs), 1)
        self.assertEqual(len(failed_runs), 1)
        self.assertEqual(completed_runs[0].run_id, run1.run_id)
        self.assertEqual(failed_runs[0].run_id, run2.run_id)
    
    def test_get_runs_by_status_no_monitoring(self):
        """Test get_runs_by_status when monitoring is disabled."""
        session = CodexSession(enable_health_monitoring=False, validate_env=False)
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.stdout.readline.side_effect = ["", ""]
            mock_popen.return_value = mock_process
            session.add_run("test prompt")
        
        runs = session.get_runs_by_status(AgentStatus.COMPLETED)
        self.assertEqual(len(runs), 0)
    
    def test_terminate_all_running_no_monitoring(self):
        """Test terminate_all_running when monitoring is disabled."""
        session = CodexSession(enable_health_monitoring=False, validate_env=False)
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.stdout.readline.side_effect = ["", ""]
            mock_popen.return_value = mock_process
            session.add_run("test prompt")
        
        count = session.terminate_all_running()
        self.assertEqual(count, 0)
    
    @patch('auto_codex.core.CodexRun.terminate')
    def test_terminate_all_running_with_agents(self, mock_terminate):
        """Test terminating all running agents."""
        mock_terminate.return_value = True
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.stdout.readline.side_effect = ["", ""]
            mock_popen.return_value = mock_process
            run1 = self.session.add_run("test prompt 1")
            run2 = self.session.add_run("test prompt 2")
        
        if self.session.health_monitor:
            self.session.health_monitor.register_agent(run1.run_id)
            self.session.health_monitor.register_agent(run2.run_id)
            
            # Set both as running
            self.session.health_monitor.update_agent_status(run1.run_id, AgentStatus.RUNNING)
            self.session.health_monitor.update_agent_status(run2.run_id, AgentStatus.RUNNING)
        
        count = self.session.terminate_all_running()
        self.assertEqual(count, 2)
        self.assertEqual(mock_terminate.call_count, 2)
    
    def test_process_csv_data_template_error(self):
        """Test CSV processing with template rendering errors."""
        csv_data = [{"name": "test", "value": "123"}]
        template_processor = Mock()
        template_processor.render_template.side_effect = Exception("Template rendering error: unexpected end of template, expected 'end of print statement'.")
        
        # This should handle the error gracefully
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.stdout.readline.side_effect = ["", ""]
            mock_popen.return_value = mock_process
            result = self.session.process_csv_data(csv_data, "{{invalid template", template_processor)
        
        # Should still execute (even with 0 runs if template failed)
        self.assertIsInstance(result.runs, list)


class TestAgentHealthMonitorAdvancedCoverage(unittest.TestCase):
    """Test advanced edge cases in AgentHealthMonitor to improve coverage."""
    
    def setUp(self):
        self.monitor = AgentHealthMonitor()
    
    def tearDown(self):
        self.monitor.stop_monitoring()
        stop_global_monitor()
    
    def test_terminate_agent_process_lookup_error(self):
        """Test terminating agent when process doesn't exist."""
        agent_id = "test-agent"
        fake_pid = 99999999  # Very unlikely to exist
        
        self.monitor.register_agent(agent_id, process_id=fake_pid)
        
        with patch('os.kill', side_effect=ProcessLookupError("Process not found")):
            result = self.monitor.terminate_agent(agent_id)
            self.assertTrue(result)
            
            # Check that agent status was updated
            agent_info = self.monitor.get_agent_health(agent_id)
            self.assertEqual(agent_info.status, AgentStatus.FAILED)
            self.assertEqual(agent_info.error_message, "Process not found")
    
    def test_terminate_agent_permission_error(self):
        """Test terminating agent with permission denied."""
        agent_id = "test-agent"
        fake_pid = 1  # Usually init process
        
        self.monitor.register_agent(agent_id, process_id=fake_pid)
        
        with patch('os.kill', side_effect=PermissionError("Permission denied")):
            result = self.monitor.terminate_agent(agent_id)
            self.assertFalse(result)
    
    def test_terminate_agent_force_sigkill(self):
        """Test force termination using SIGKILL."""
        agent_id = "test-agent"
        fake_pid = 12345
        
        self.monitor.register_agent(agent_id, process_id=fake_pid)
        
        with patch('os.kill') as mock_kill:
            result = self.monitor.terminate_agent(agent_id, force=True)
            self.assertTrue(result)
            mock_kill.assert_called_once_with(fake_pid, signal.SIGKILL)
    
    def test_terminate_agent_no_process_id(self):
        """Test terminating agent without process ID."""
        agent_id = "test-agent"
        self.monitor.register_agent(agent_id)  # No process_id
        
        result = self.monitor.terminate_agent(agent_id)
        self.assertTrue(result)
    
    def test_health_callback_error_handling(self):
        """Test that health callback errors don't break monitoring."""
        agent_id = "test-agent"
        
        # Add a callback that will raise an exception
        def failing_callback(agent_id, health_status):
            raise Exception("Callback error")
        
        self.monitor.add_health_callback(failing_callback)
        self.monitor.register_agent(agent_id)
        
        # Change status to trigger health evaluation and callback
        original_health = self.monitor.get_agent_health(agent_id).health
        
        # Force a health change by setting status to failed
        self.monitor.update_agent_status(agent_id, AgentStatus.FAILED)
        
        # Run health check manually to trigger callback
        self.monitor._check_agent_health()
        
        # Monitor should still be functional despite callback error
        agent_info = self.monitor.get_agent_health(agent_id)
        self.assertIsNotNone(agent_info)
    
    def test_evaluate_agent_health_process_check(self):
        """Test health evaluation with process existence checking."""
        agent_id = "test-agent"
        fake_pid = 99999999  # Very unlikely to exist
        
        self.monitor.register_agent(agent_id, process_id=fake_pid)
        self.monitor.update_agent_status(agent_id, AgentStatus.RUNNING)
        
        # Set last heartbeat to make agent responsive
        agent_info = self.monitor.get_agent_health(agent_id)
        agent_info.last_heartbeat = datetime.now()
        
        # Mock os.kill to raise ProcessLookupError
        with patch('os.kill', side_effect=ProcessLookupError("Process not found")):
            health = self.monitor._evaluate_agent_health(agent_info, datetime.now())
            self.assertEqual(health, HealthStatus.UNHEALTHY)
    
    def test_evaluate_agent_health_permission_error(self):
        """Test health evaluation when we can't signal process (permission error)."""
        agent_id = "test-agent"
        fake_pid = 1  # init process
        
        self.monitor.register_agent(agent_id, process_id=fake_pid)
        self.monitor.update_agent_status(agent_id, AgentStatus.RUNNING)
        
        agent_info = self.monitor.get_agent_health(agent_id)
        agent_info.last_heartbeat = datetime.now()
        
        # Mock os.kill to raise PermissionError (process exists but we can't signal)
        with patch('os.kill', side_effect=PermissionError("Permission denied")):
            health = self.monitor._evaluate_agent_health(agent_info, datetime.now())
            # Should pass this check and continue to default healthy
            self.assertEqual(health, HealthStatus.HEALTHY)
    
    def test_evaluate_agent_health_max_errors(self):
        """Test health evaluation with max error count exceeded."""
        agent_id = "test-agent"
        self.monitor.register_agent(agent_id)
        
        agent_info = self.monitor.get_agent_health(agent_id)
        # Set error count above threshold
        agent_info.metrics.error_count = self.monitor.max_error_count + 1
        
        health = self.monitor._evaluate_agent_health(agent_info, datetime.now())
        self.assertEqual(health, HealthStatus.UNHEALTHY)
    
    def test_evaluate_agent_health_unresponsive(self):
        """Test health evaluation for unresponsive running agent."""
        agent_id = "test-agent"
        self.monitor.register_agent(agent_id)
        self.monitor.update_agent_status(agent_id, AgentStatus.RUNNING)
        
        agent_info = self.monitor.get_agent_health(agent_id)
        # Set old heartbeat to make agent unresponsive
        agent_info.last_heartbeat = datetime.now() - timedelta(minutes=5)
        
        health = self.monitor._evaluate_agent_health(agent_info, datetime.now())
        self.assertEqual(health, HealthStatus.DEGRADED)
    
    def test_monitor_loop_exception_handling(self):
        """Test that monitor loop handles exceptions gracefully."""
        # Start monitoring
        self.monitor.start_monitoring()
        
        # Mock _check_agent_health to raise an exception
        original_check = self.monitor._check_agent_health
        
        def failing_check():
            if not hasattr(failing_check, 'called'):
                failing_check.called = True
                raise Exception("Health check error")
            else:
                # Call original after first exception
                original_check()
        
        self.monitor._check_agent_health = failing_check
        
        # Wait a bit for the monitor loop to run
        time.sleep(0.2)
        
        # Monitor should still be running despite the exception
        self.assertTrue(self.monitor._monitoring)
    
    def test_check_agent_health_timeout_detection(self):
        """Test timeout detection in health checking."""
        agent_id = "test-agent"
        
        # Set a very low timeout threshold for testing
        self.monitor.timeout_threshold = 0.001  # 1ms
        
        self.monitor.register_agent(agent_id)
        self.monitor.update_agent_status(agent_id, AgentStatus.RUNNING)
        
        # Wait a bit to exceed timeout
        time.sleep(0.002)
        
        # Run health check manually
        self.monitor._check_agent_health()
        
        # Agent should be marked as timed out
        agent_info = self.monitor.get_agent_health(agent_id)
        self.assertEqual(agent_info.status, AgentStatus.TIMEOUT)


class TestCodexRunAdvancedCoverage(unittest.TestCase):
    """Test advanced edge cases in CodexRun to improve coverage."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def test_execute_timeout_with_kill(self):
        """Test execute timeout with process kill."""
        run = CodexRun(
            "test prompt",
            timeout=1,
            enable_health_monitoring=False,
            validate_env=False
        )
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.poll.return_value = None
            mock_process.wait.side_effect = subprocess.TimeoutExpired("cmd", 1)
            mock_process.stdout.readline.side_effect = ["", ""]
            mock_popen.return_value = mock_process
            
            with patch('builtins.open', mock_open(read_data="log data")):
                result = run.execute(self.temp_dir)
                self.assertFalse(result.success)
                self.assertIn("timed out", result.metadata['error'])
                # Process gets terminated twice: once in TimeoutExpired block and once in finally block
                self.assertEqual(mock_process.terminate.call_count, 2)
                mock_process.kill.assert_called_once()


if __name__ == '__main__':
    unittest.main() 