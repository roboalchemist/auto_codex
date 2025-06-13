#!/usr/bin/env python3
"""
Real-Time Inspector Example - auto_codex

Demonstrates real-time agent inspection:
- Live agent status monitoring
- Event-driven notifications
- Interactive agent inspection
"""

import time
import sys
from datetime import datetime
from typing import List, Dict

# Add auto_codex to path for examples
sys.path.insert(0, 'auto_codex')

from auto_codex import CodexRun, CodexSession, get_health_monitor


class SimpleAgentInspector:
    """Simple real-time agent inspector"""
    
    def __init__(self):
        self.health_monitor = get_health_monitor()
        self.event_history: List[Dict] = []
        self.session = CodexSession(
            session_id="inspector-demo",
            enable_health_monitoring=True
        )
    
    def start_monitoring(self, runs: List[CodexRun], duration: int = 15):
        """Start monitoring a list of runs"""
        print(f"Monitoring {len(runs)} agents for {duration}s...")
        
        start_time = time.time()
        check_count = 0
        
        while time.time() - start_time < duration:
            time.sleep(2)
            check_count += 1
            
            print(f"\nCheck {check_count} [{self._format_time()}]:")
            
            for i, run in enumerate(runs, 1):
                health = run.get_health_status()
                
                status_icon = self._get_status_icon(health.status.value)
                health_icon = self._get_health_icon(health.health.value)
                
                print(f"  {i}. {run.run_id[:8]}: {status_icon} {health.status.value} | {health_icon} {health.health.value} | {health.runtime_seconds:.1f}s")
                
                self._log_event(run.run_id, health.status.value, health.health.value)
        
        print(f"\nMonitoring complete! Logged {len(self.event_history)} events")
    
    def inspect_agent(self, run: CodexRun) -> Dict:
        """Detailed inspection of a specific agent"""
        health = run.get_health_status()
        
        return {
            'agent_id': run.run_id,
            'prompt_preview': run.prompt[:50] + '...',
            'model': run.model,
            'provider': run.provider,
            'status': health.status.value,
            'health': health.health.value,
            'runtime_seconds': health.runtime_seconds,
            'is_running': health.is_running,
            'is_responsive': health.is_responsive
        }
    
    def generate_report(self, runs: List[CodexRun]):
        """Generate monitoring report"""
        print(f"\nMonitoring Report")
        print("=" * 30)
        
        total_runs = len(runs)
        healthy_count = 0
        running_count = 0
        total_runtime = 0
        
        for run in runs:
            health = run.get_health_status()
            if health.health.value == "healthy":
                healthy_count += 1
            if health.is_running:
                running_count += 1
            total_runtime += health.runtime_seconds
        
        print(f"Total Agents: {total_runs}")
        print(f"Healthy Rate: {(healthy_count/total_runs)*100:.1f}%")
        print(f"Currently Running: {running_count}")
        print(f"Average Runtime: {total_runtime/total_runs:.1f}s")
        print(f"Total Events: {len(self.event_history)}")
    
    def _get_status_icon(self, status: str) -> str:
        return {
            "running": " ", "completed": "✅", "failed": "❌",
            "initializing": " ", "cancelled": "", "timeout": ""
        }.get(status, "✅")
    
    def _get_health_icon(self, health: str) -> str:
        return {
            "healthy": "✅", "degraded": "✅", 
            "unhealthy": "❌", "unknown": "✅"
        }.get(health, "✅")
    
    def _format_time(self) -> str:
        return datetime.now().strftime("%H:%M:%S")
    
    def _log_event(self, agent_id: str, status: str, health: str):
        event = {
            'timestamp': datetime.now(),
            'agent_id': agent_id,
            'status': status,
            'health': health
        }
        self.event_history.append(event)


def basic_monitoring_example():
    """Basic real-time monitoring"""
    print("Basic Monitoring Example")
    print("=" * 30)
    
    inspector = SimpleAgentInspector()
    
    # Create runs to monitor
    tasks = [
        "Create Python web scraper",
        "Build data analysis tool",
        "Develop REST API"
    ]
    
    runs = []
    for task in tasks:
        run = inspector.session.add_run(
            prompt=task,
            model="gpt-4",
            provider="openai"
        )
        runs.append(run)
        print(f"Created: {task[:25]}... (ID: {run.run_id[:8]})")
    
    # Start monitoring
    inspector.start_monitoring(runs, duration=10)
    
    return inspector, runs


def detailed_inspection_example():
    """Detailed agent inspection"""
    print("\nDetailed Inspection Example")
    print("=" * 30)
    
    inspector = SimpleAgentInspector()
    
    # Create run for inspection
    run = inspector.session.add_run(
        prompt="Create machine learning model for text classification",
        model="gpt-4",
        provider="openai"
    )
    
    print(f"Inspecting agent: {run.run_id[:8]}...")
    
    # Perform inspection
    inspection = inspector.inspect_agent(run)
    
    print(f"\nInspection Results:")
    print(f"  Agent ID: {inspection['agent_id'][:16]}...")
    print(f"  Task: {inspection['prompt_preview']}")
    print(f"  Model: {inspection['model']} ({inspection['provider']})")
    print(f"  Status: {inspection['status']}")
    print(f"  Health: {inspection['health']}")
    print(f"  Runtime: {inspection['runtime_seconds']:.1f}s")
    print(f"  Running: {inspection['is_running']}")
    print(f"  Responsive: {inspection['is_responsive']}")
    
    return inspector, run


def monitoring_dashboard_example():
    """Real-time monitoring dashboard simulation"""
    print("\nMonitoring Dashboard Example")
    print("=" * 30)
    
    inspector = SimpleAgentInspector()
    
    # Create multiple runs for dashboard
    run_configs = [
        ("Data Processing", "Process large CSV dataset"),
        ("Web Scraping", "Scrape product information"),
        ("API Development", "Build REST API endpoints"),
        ("ML Training", "Train classification model")
    ]
    
    runs = []
    for name, prompt in run_configs:
        run = inspector.session.add_run(
            prompt=prompt,
            model="gpt-4",
            provider="openai"
        )
        runs.append(run)
        print(f"Dashboard: {name} started (ID: {run.run_id[:8]})")
    
    # Monitor and generate report
    inspector.start_monitoring(runs, duration=8)
    inspector.generate_report(runs)
    
    return inspector, runs


def main():
    """Run all real-time inspector examples"""
    print("Auto-Codex Real-Time Inspector Examples")
    print("=" * 45)
    
    inspector1, runs1 = basic_monitoring_example()
    inspector2, run2 = detailed_inspection_example()
    inspector3, runs3 = monitoring_dashboard_example()
    
    print(f"\nInspector examples completed!")


if __name__ == "__main__":
    main()
