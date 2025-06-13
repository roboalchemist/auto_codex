"""
Comprehensive tests for auto_codex health monitoring functionality.
These tests focus on increasing coverage for health.py module.
"""

import unittest
import tempfile
import shutil
import time
import threading
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from auto_codex.health import (
    AgentStatus, HealthStatus, AgentMetrics, AgentHealthInfo, 
    AgentHealthMonitor, get_global_health_monitor
)


class TestAgentMetrics(unittest.TestCase):
    """Test AgentMetrics dataclass."""

    def test_init_with_defaults(self):
        """Test AgentMetrics initialization with default values."""
        metrics = AgentMetrics()
        
        self.assertIsNone(metrics.cpu_usage)
        self.assertIsNone(metrics.memory_usage)
        self.assertIsNone(metrics.disk_usage)
        self.assertIsNone(metrics.network_io)
        self.assertIsNone(metrics.runtime_seconds)
        self.assertIsNone(metrics.tokens_used)
        self.assertIsNone(metrics.api_calls)
        self.assertEqual(metrics.error_count, 0)
        self.assertIsNone(metrics.last_activity)

    def test_init_with_custom_values(self):
        """Test AgentMetrics initialization with custom values."""
        now = datetime.now()
        metrics = AgentMetrics(
            cpu_usage=85.5,
            memory_usage=1024.0,
            disk_usage=512.0,
            network_io={"bytes_sent": 1000, "bytes_received": 2000},
            runtime_seconds=120.5,
            tokens_used=500,
            api_calls=10,
            error_count=2,
            last_activity=now
        )
        
        self.assertEqual(metrics.cpu_usage, 85.5)
        self.assertEqual(metrics.memory_usage, 1024.0)
        self.assertEqual(metrics.disk_usage, 512.0)
        self.assertEqual(metrics.network_io, {"bytes_sent": 1000, "bytes_received": 2000})
        self.assertEqual(metrics.runtime_seconds, 120.5)
        self.assertEqual(metrics.tokens_used, 500)
        self.assertEqual(metrics.api_calls, 10)
        self.assertEqual(metrics.error_count, 2)
        self.assertEqual(metrics.last_activity, now)


class TestAgentHealthInfo(unittest.TestCase):
    """Test AgentHealthInfo dataclass."""

    def test_init_with_minimal_data(self):
        """Test AgentHealthInfo initialization with minimal data."""
        now = datetime.now()
        info = AgentHealthInfo(
            agent_id="test-agent",
            status=AgentStatus.RUNNING,
            health=HealthStatus.HEALTHY,
            start_time=now
        )
        
        self.assertEqual(info.agent_id, "test-agent")
        self.assertEqual(info.status, AgentStatus.RUNNING)
        self.assertEqual(info.health, HealthStatus.HEALTHY)
        self.assertEqual(info.start_time, now)
        self.assertIsNone(info.last_heartbeat)
        self.assertIsNone(info.last_update)
        self.assertIsNone(info.process_id)
        self.assertIsNone(info.log_file)
        self.assertIsNone(info.error_message)
        self.assertIsInstance(info.metrics, AgentMetrics)
        self.assertEqual(info.metadata, {})

    def test_runtime_property_with_start_time(self):
        """Test runtime property with start_time set."""
        start_time = datetime.now() - timedelta(seconds=60)
        info = AgentHealthInfo(
            agent_id="test-agent",
            status=AgentStatus.RUNNING,
            health=HealthStatus.HEALTHY,
            start_time=start_time
        )
        
        runtime = info.runtime_seconds
        self.assertGreater(runtime, 50)  # Should be around 60 seconds
        self.assertLess(runtime, 70)

    def test_is_running_property(self):
        """Test is_running property for different statuses."""
        start_time = datetime.now()
        
        # Test running statuses
        for status in [AgentStatus.INITIALIZING, AgentStatus.RUNNING, AgentStatus.WAITING_APPROVAL]:
            info = AgentHealthInfo(
                agent_id="test-agent",
                status=status,
                health=HealthStatus.HEALTHY,
                start_time=start_time
            )
            self.assertTrue(info.is_running, f"Status {status} should be running")
        
        # Test non-running statuses
        for status in [AgentStatus.COMPLETED, AgentStatus.FAILED, AgentStatus.CANCELLED]:
            info = AgentHealthInfo(
                agent_id="test-agent",
                status=status,
                health=HealthStatus.HEALTHY,
                start_time=start_time
            )
            self.assertFalse(info.is_running, f"Status {status} should not be running")

    def test_is_responsive_property(self):
        """Test is_responsive property."""
        start_time = datetime.now()
        
        # No heartbeat - not responsive
        info = AgentHealthInfo(
            agent_id="test-agent",
            status=AgentStatus.RUNNING,
            health=HealthStatus.HEALTHY,
            start_time=start_time
        )
        self.assertFalse(info.is_responsive)
        
        # Recent heartbeat - responsive
        info.last_heartbeat = datetime.now()
        self.assertTrue(info.is_responsive)
        
        # Old heartbeat - not responsive
        info.last_heartbeat = datetime.now() - timedelta(seconds=60)
        self.assertFalse(info.is_responsive)


class TestAgentHealthMonitor(unittest.TestCase):
    """Test AgentHealthMonitor class."""

    def setUp(self):
        self.monitor = AgentHealthMonitor()

    def tearDown(self):
        self.monitor.stop_monitoring()

    def test_init(self):
        """Test AgentHealthMonitor initialization."""
        self.assertIsInstance(self.monitor.heartbeat_interval, float)
        self.assertIsInstance(self.monitor.health_check_interval, float)
        self.assertIsInstance(self.monitor.timeout_threshold, float)
        self.assertIsInstance(self.monitor.max_error_count, int)
        self.assertEqual(len(self.monitor._agents), 0)

    def test_register_agent(self):
        """Test agent registration."""
        agent_id = "test-agent"
        
        info = self.monitor.register_agent(agent_id, process_id=12345)
        
        self.assertIn(agent_id, self.monitor._agents)
        self.assertEqual(info.agent_id, agent_id)
        self.assertEqual(info.process_id, 12345)
        self.assertEqual(info.status, AgentStatus.INITIALIZING)

    def test_register_agent_duplicate(self):
        """Test registering the same agent twice."""
        agent_id = "test-agent"
        
        self.monitor.register_agent(agent_id)
        original_start_time = self.monitor._agents[agent_id].start_time
        
        # Register again
        time.sleep(0.1)  # Small delay to ensure different timestamp
        self.monitor.register_agent(agent_id)
        
        # Should update the existing entry
        self.assertIn(agent_id, self.monitor._agents)
        # Start time should be different
        self.assertNotEqual(self.monitor._agents[agent_id].start_time, original_start_time)

    def test_update_agent_status(self):
        """Test updating agent status."""
        agent_id = "test-agent"
        self.monitor.register_agent(agent_id)
        
        self.monitor.update_agent_status(agent_id, AgentStatus.RUNNING)
        
        agent_info = self.monitor._agents[agent_id]
        self.assertEqual(agent_info.status, AgentStatus.RUNNING)
        self.assertIsNotNone(agent_info.last_update)

    def test_update_agent_status_unregistered(self):
        """Test updating status for unregistered agent."""
        # Should not raise an error, just log warning
        self.monitor.update_agent_status("unknown-agent", AgentStatus.RUNNING)
        self.assertNotIn("unknown-agent", self.monitor._agents)

    def test_heartbeat(self):
        """Test heartbeat functionality."""
        agent_id = "test-agent"
        self.monitor.register_agent(agent_id)
        
        # Send heartbeat
        metrics = AgentMetrics(cpu_usage=50.0)
        self.monitor.heartbeat(agent_id, metrics)
        
        agent_info = self.monitor._agents[agent_id]
        self.assertIsNotNone(agent_info.last_heartbeat)
        self.assertEqual(agent_info.metrics.cpu_usage, 50.0)

    def test_heartbeat_unregistered(self):
        """Test heartbeat for unregistered agent."""
        # Should not raise an error, just log warning
        self.monitor.heartbeat("unknown-agent")
        self.assertNotIn("unknown-agent", self.monitor._agents)

    def test_get_agent_health(self):
        """Test getting agent health info."""
        agent_id = "test-agent"
        self.monitor.register_agent(agent_id)
        
        info = self.monitor.get_agent_health(agent_id)
        self.assertIsNotNone(info)
        self.assertEqual(info.agent_id, agent_id)

    def test_get_agent_health_unregistered(self):
        """Test getting health for unregistered agent."""
        info = self.monitor.get_agent_health("unknown-agent")
        self.assertIsNone(info)

    def test_get_all_agents(self):
        """Test getting all agents."""
        # Register some agents
        self.monitor.register_agent("agent-1")
        self.monitor.register_agent("agent-2")
        
        agents = self.monitor.get_all_agents()
        
        self.assertEqual(len(agents), 2)
        agent_ids = list(agents.keys())
        self.assertIn("agent-1", agent_ids)
        self.assertIn("agent-2", agent_ids)

    def test_get_agents_by_status(self):
        """Test filtering agents by status."""
        self.monitor.register_agent("agent-1")
        self.monitor.register_agent("agent-2")
        
        # Update statuses
        self.monitor.update_agent_status("agent-1", AgentStatus.RUNNING)
        self.monitor.update_agent_status("agent-2", AgentStatus.COMPLETED)
        
        running_agents = self.monitor.get_agents_by_status(AgentStatus.RUNNING)
        completed_agents = self.monitor.get_agents_by_status(AgentStatus.COMPLETED)
        
        self.assertEqual(len(running_agents), 1)
        self.assertEqual(running_agents[0].agent_id, "agent-1")
        self.assertEqual(len(completed_agents), 1)
        self.assertEqual(completed_agents[0].agent_id, "agent-2")

    def test_get_healthy_agents(self):
        """Test filtering agents by health status."""
        self.monitor.register_agent("agent-1")
        self.monitor.register_agent("agent-2")
        
        # Update health statuses
        self.monitor._agents["agent-1"].health = HealthStatus.HEALTHY
        self.monitor._agents["agent-2"].health = HealthStatus.UNHEALTHY
        
        healthy_agents = self.monitor.get_healthy_agents()
        
        self.assertEqual(len(healthy_agents), 1)
        self.assertEqual(healthy_agents[0].agent_id, "agent-1")

    def test_get_running_agents(self):
        """Test getting running agents."""
        self.monitor.register_agent("agent-1")
        self.monitor.register_agent("agent-2")
        
        # Update statuses
        self.monitor.update_agent_status("agent-1", AgentStatus.RUNNING)
        self.monitor.update_agent_status("agent-2", AgentStatus.COMPLETED)
        
        running_agents = self.monitor.get_running_agents()
        
        self.assertEqual(len(running_agents), 1)
        self.assertEqual(running_agents[0].agent_id, "agent-1")

    def test_terminate_agent_no_process(self):
        """Test terminating agent without process ID."""
        agent_id = "test-agent"
        self.monitor.register_agent(agent_id)  # No process_id
        
        result = self.monitor.terminate_agent(agent_id)
        
        # Should return True even if no process (according to implementation)
        self.assertTrue(result)

    @patch('os.kill')
    def test_terminate_agent_with_process(self, mock_kill):
        """Test terminating agent with process ID."""
        agent_id = "test-agent"
        self.monitor.register_agent(agent_id, process_id=12345)
        
        result = self.monitor.terminate_agent(agent_id)
        
        self.assertTrue(result)
        mock_kill.assert_called_once()

    def test_terminate_agent_unregistered(self):
        """Test terminating unregistered agent."""
        result = self.monitor.terminate_agent("unknown-agent")
        self.assertFalse(result)

    def test_add_status_callback(self):
        """Test adding status change callback."""
        callback_called = []
        
        def test_callback(agent_id, status):
            callback_called.append((agent_id, status))
        
        self.monitor.add_status_callback(test_callback)
        
        # Register agent and change status
        agent_id = "test-agent"
        self.monitor.register_agent(agent_id)
        self.monitor.update_agent_status(agent_id, AgentStatus.RUNNING)
        
        # Callback should be called
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0], (agent_id, AgentStatus.RUNNING))

    def test_add_health_callback(self):
        """Test adding health change callback."""
        self.monitor.add_health_callback(lambda agent_id, health: None)
        # Just test that the method exists and doesn't raise
        self.assertEqual(len(self.monitor._health_callbacks), 1)

    def test_add_error_callback(self):
        """Test adding error callback."""
        self.monitor.add_error_callback(lambda agent_id, error: None)
        # Just test that the method exists and doesn't raise
        self.assertEqual(len(self.monitor._error_callbacks), 1)

    def test_get_summary_stats(self):
        """Test getting summary statistics."""
        # Register some agents with different states
        self.monitor.register_agent("agent-1")
        self.monitor.register_agent("agent-2")
        
        self.monitor.update_agent_status("agent-1", AgentStatus.RUNNING)
        self.monitor.update_agent_status("agent-2", AgentStatus.COMPLETED)
        
        stats = self.monitor.get_summary_stats()
        
        # Check the actual attributes returned by get_summary_stats
        self.assertIn('total', stats)
        self.assertIn('status_counts', stats)
        self.assertIn('health_counts', stats)
        self.assertEqual(stats['total'], 2)


class TestGlobalHealthMonitor(unittest.TestCase):
    """Test global health monitor functionality."""

    def test_get_global_health_monitor_singleton(self):
        """Test that global health monitor is a singleton."""
        monitor1 = get_global_health_monitor()
        monitor2 = get_global_health_monitor()
        
        self.assertIs(monitor1, monitor2)

    def test_global_monitor_functionality(self):
        """Test basic functionality of global monitor."""
        monitor = get_global_health_monitor()
        
        # Test basic registration
        agent_info = monitor.register_agent("global-test-agent")
        self.assertEqual(agent_info.agent_id, "global-test-agent")
        
        # Clean up
        monitor.unregister_agent("global-test-agent")


if __name__ == '__main__':
    unittest.main() 