"""
Health management and monitoring system for Codex agents.

This module provides real-time health monitoring, status tracking, and
management capabilities for running Codex agents.
"""

import asyncio
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Callable, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import logging
import json
import os
import signal
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Status of a Codex agent."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class HealthStatus(Enum):
    """Health status of an agent."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class AgentMetrics:
    """Metrics for an agent."""
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    network_io: Optional[Dict[str, int]] = None
    runtime_seconds: Optional[float] = None
    tokens_used: Optional[int] = None
    api_calls: Optional[int] = None
    error_count: int = 0
    last_activity: Optional[datetime] = None


@dataclass
class AgentHealthInfo:
    """Comprehensive health information for an agent."""
    agent_id: str
    status: AgentStatus
    health: HealthStatus
    start_time: datetime
    last_heartbeat: Optional[datetime] = None
    last_update: Optional[datetime] = None
    process_id: Optional[int] = None
    log_file: Optional[str] = None
    error_message: Optional[str] = None
    metrics: AgentMetrics = field(default_factory=AgentMetrics)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def runtime_seconds(self) -> float:
        """Calculate runtime in seconds."""
        return (datetime.now() - self.start_time).total_seconds()
    
    @property
    def is_running(self) -> bool:
        """Check if agent is currently running."""
        return self.status in {AgentStatus.INITIALIZING, AgentStatus.RUNNING, AgentStatus.WAITING_APPROVAL}
    
    @property
    def is_responsive(self) -> bool:
        """Check if agent is responsive based on recent heartbeat."""
        if not self.last_heartbeat:
            return False
        return datetime.now() - self.last_heartbeat < timedelta(seconds=30)


class AgentHealthMonitor:
    """
    Monitors health and status of running Codex agents.
    
    Provides real-time monitoring, status tracking, and health management
    for multiple concurrent agent executions.
    """
    
    def __init__(self, 
                 heartbeat_interval: float = 10.0,
                 health_check_interval: float = 5.0,
                 timeout_threshold: float = 300.0,
                 max_error_count: int = 5):
        """
        Initialize the health monitor.
        
        Args:
            heartbeat_interval: Seconds between heartbeat checks
            health_check_interval: Seconds between health evaluations
            timeout_threshold: Seconds before considering an agent timed out
            max_error_count: Maximum errors before marking agent unhealthy
        """
        self.heartbeat_interval = heartbeat_interval
        self.health_check_interval = health_check_interval
        self.timeout_threshold = timeout_threshold
        self.max_error_count = max_error_count
        
        # Agent tracking
        self._agents: Dict[str, AgentHealthInfo] = {}
        self._lock = threading.RLock()
        
        # Monitoring thread
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Event callbacks
        self._status_callbacks: List[Callable[[str, AgentStatus], None]] = []
        self._health_callbacks: List[Callable[[str, HealthStatus], None]] = []
        self._error_callbacks: List[Callable[[str, str], None]] = []
        
        # Start monitoring
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start the health monitoring thread."""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Agent health monitoring started")
    
    def stop_monitoring(self):
        """Stop the health monitoring thread."""
        self._monitoring = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
        logger.info("Agent health monitoring stopped")
    
    def register_agent(self, 
                      agent_id: str, 
                      process_id: Optional[int] = None,
                      log_file: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> AgentHealthInfo:
        """
        Register a new agent for monitoring.
        
        Args:
            agent_id: Unique identifier for the agent
            process_id: OS process ID if available
            log_file: Path to agent's log file
            metadata: Additional metadata about the agent
            
        Returns:
            AgentHealthInfo object for the registered agent
        """
        with self._lock:
            if agent_id in self._agents:
                logger.warning(f"Agent {agent_id} already registered, updating")
            
            agent_info = AgentHealthInfo(
                agent_id=agent_id,
                status=AgentStatus.INITIALIZING,
                health=HealthStatus.UNKNOWN,
                start_time=datetime.now(),
                process_id=process_id,
                log_file=log_file,
                metadata=metadata or {}
            )
            
            self._agents[agent_id] = agent_info
            logger.info(f"Registered agent {agent_id} for monitoring")
            
            return agent_info
    
    def unregister_agent(self, agent_id: str):
        """
        Unregister an agent from monitoring.
        
        Args:
            agent_id: ID of the agent to unregister
        """
        with self._lock:
            if agent_id in self._agents:
                del self._agents[agent_id]
                logger.info(f"Unregistered agent {agent_id}")
    
    def update_agent_status(self, agent_id: str, status: AgentStatus, error_message: Optional[str] = None):
        """
        Update an agent's status.
        
        Args:
            agent_id: ID of the agent
            status: New status
            error_message: Optional error message
        """
        with self._lock:
            if agent_id not in self._agents:
                logger.warning(f"Agent {agent_id} not registered")
                return
            
            old_status = self._agents[agent_id].status
            self._agents[agent_id].status = status
            self._agents[agent_id].last_update = datetime.now()
            
            if error_message:
                self._agents[agent_id].error_message = error_message
                self._agents[agent_id].metrics.error_count += 1
            
            # Trigger status change callbacks
            if old_status != status:
                for callback in self._status_callbacks:
                    try:
                        callback(agent_id, status)
                    except Exception as e:
                        logger.error(f"Error in status callback: {e}")
    
    def heartbeat(self, agent_id: str, metrics: Optional[AgentMetrics] = None):
        """
        Record a heartbeat from an agent.
        
        Args:
            agent_id: ID of the agent
            metrics: Optional updated metrics
        """
        with self._lock:
            if agent_id not in self._agents:
                logger.warning(f"Heartbeat from unregistered agent {agent_id}")
                return
            
            self._agents[agent_id].last_heartbeat = datetime.now()
            self._agents[agent_id].last_update = datetime.now()
            
            if metrics:
                self._agents[agent_id].metrics = metrics
                self._agents[agent_id].metrics.last_activity = datetime.now()
    
    def get_agent_health(self, agent_id: str) -> Optional[AgentHealthInfo]:
        """
        Get health information for a specific agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            AgentHealthInfo or None if agent not found
        """
        with self._lock:
            return self._agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, AgentHealthInfo]:
        """
        Get health information for all monitored agents.
        
        Returns:
            Dictionary mapping agent IDs to their health info
        """
        with self._lock:
            return self._agents.copy()
    
    def get_agents_by_status(self, status: AgentStatus) -> List[AgentHealthInfo]:
        """
        Get all agents with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of AgentHealthInfo objects
        """
        with self._lock:
            return [info for info in self._agents.values() if info.status == status]
    
    def get_healthy_agents(self) -> List[AgentHealthInfo]:
        """
        Get all healthy agents.
        
        Returns:
            List of healthy AgentHealthInfo objects
        """
        with self._lock:
            return [info for info in self._agents.values() if info.health == HealthStatus.HEALTHY]
    
    def get_running_agents(self) -> List[AgentHealthInfo]:
        """
        Get all currently running agents.
        
        Returns:
            List of running AgentHealthInfo objects
        """
        with self._lock:
            return [info for info in self._agents.values() if info.is_running]
    
    def terminate_agent(self, agent_id: str, force: bool = False) -> bool:
        """
        Terminate a running agent.
        
        Args:
            agent_id: ID of the agent to terminate
            force: Whether to force termination
            
        Returns:
            True if termination was attempted, False if agent not found
        """
        with self._lock:
            if agent_id not in self._agents:
                return False
            
            agent_info = self._agents[agent_id]
            
            if agent_info.process_id:
                try:
                    if force:
                        os.kill(agent_info.process_id, signal.SIGKILL)
                    else:
                        os.kill(agent_info.process_id, signal.SIGTERM)
                    
                    self.update_agent_status(agent_id, AgentStatus.CANCELLED)
                    logger.info(f"Terminated agent {agent_id} (PID {agent_info.process_id})")
                    return True
                    
                except ProcessLookupError:
                    logger.warning(f"Process {agent_info.process_id} for agent {agent_id} not found")
                    self.update_agent_status(agent_id, AgentStatus.FAILED, "Process not found")
                except PermissionError:
                    logger.error(f"Permission denied terminating agent {agent_id}")
                    return False
            
            return True
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics for all agents.
        
        Returns:
            Dictionary with summary statistics
        """
        with self._lock:
            total = len(self._agents)
            if total == 0:
                return {"total": 0}
            
            status_counts = {}
            health_counts = {}
            total_runtime = 0
            total_errors = 0
            
            for agent in self._agents.values():
                # Count by status
                status_counts[agent.status.value] = status_counts.get(agent.status.value, 0) + 1
                
                # Count by health
                health_counts[agent.health.value] = health_counts.get(agent.health.value, 0) + 1
                
                # Accumulate metrics
                total_runtime += agent.runtime_seconds
                total_errors += agent.metrics.error_count
            
            return {
                "total": total,
                "status_counts": status_counts,
                "health_counts": health_counts,
                "average_runtime": total_runtime / total if total > 0 else 0,
                "total_errors": total_errors,
                "healthy_percentage": (health_counts.get("healthy", 0) / total * 100) if total > 0 else 0
            }
    
    def add_status_callback(self, callback: Callable[[str, AgentStatus], None]):
        """Add a callback for status changes."""
        self._status_callbacks.append(callback)
    
    def add_health_callback(self, callback: Callable[[str, HealthStatus], None]):
        """Add a callback for health changes."""
        self._health_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable[[str, str], None]):
        """Add a callback for errors."""
        self._error_callbacks.append(callback)
    
    def _monitor_loop(self):
        """Main monitoring loop running in background thread."""
        while self._monitoring:
            try:
                self._check_agent_health()
                time.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1.0)
    
    def _check_agent_health(self):
        """Check health of all registered agents."""
        with self._lock:
            current_time = datetime.now()
            
            for agent_id, agent_info in self._agents.items():
                old_health = agent_info.health
                new_health = self._evaluate_agent_health(agent_info, current_time)
                
                if old_health != new_health:
                    agent_info.health = new_health
                    logger.info(f"Agent {agent_id} health changed: {old_health.value} -> {new_health.value}")
                    
                    # Trigger health change callbacks
                    for callback in self._health_callbacks:
                        try:
                            callback(agent_id, new_health)
                        except Exception as e:
                            logger.error(f"Error in health callback: {e}")
                
                # Check for timeouts
                if agent_info.is_running and agent_info.runtime_seconds > self.timeout_threshold:
                    self.update_agent_status(agent_id, AgentStatus.TIMEOUT, "Agent timed out")
    
    def _evaluate_agent_health(self, agent_info: AgentHealthInfo, current_time: datetime) -> HealthStatus:
        """
        Evaluate the health status of an agent.
        
        Args:
            agent_info: Agent information
            current_time: Current timestamp
            
        Returns:
            Evaluated health status
        """
        # Check if agent has failed or been cancelled
        if agent_info.status in {AgentStatus.FAILED, AgentStatus.CANCELLED, AgentStatus.TIMEOUT}:
            return HealthStatus.UNHEALTHY
        
        # Check if agent is completed
        if agent_info.status == AgentStatus.COMPLETED:
            return HealthStatus.HEALTHY
        
        # Check error count
        if agent_info.metrics.error_count >= self.max_error_count:
            return HealthStatus.UNHEALTHY
        
        # Check responsiveness for running agents
        if agent_info.is_running:
            if not agent_info.is_responsive:
                return HealthStatus.DEGRADED
            
            # Check if process is still alive
            if agent_info.process_id:
                try:
                    os.kill(agent_info.process_id, 0)  # Check if process exists
                except ProcessLookupError:
                    return HealthStatus.UNHEALTHY
                except PermissionError:
                    pass  # Process exists but we can't signal it
        
        # Default to healthy if no issues detected
        return HealthStatus.HEALTHY


# Global health monitor instance
_global_monitor: Optional[AgentHealthMonitor] = None


def get_health_monitor() -> AgentHealthMonitor:
    """Get the global health monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = AgentHealthMonitor()
    return _global_monitor


def get_global_health_monitor() -> AgentHealthMonitor:
    """Get the global health monitor instance. Alias for get_health_monitor()."""
    return get_health_monitor()


def stop_global_monitor():
    """Stop the global health monitor."""
    global _global_monitor
    if _global_monitor:
        _global_monitor.stop_monitoring()
        _global_monitor = None 