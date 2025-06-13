#!/usr/bin/env python3
"""
Health Monitoring Example - auto_codex

Demonstrates health monitoring capabilities:
- Basic health status checking
- Real-time monitoring
- Health analytics and reporting
"""

import sys
import os
import time
from datetime import datetime

# Add auto_codex to path for examples
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auto_codex import CodexRun, CodexSession, get_health_monitor


def basic_health_check():
    """Basic health status checking"""
    print("Basic Health Check")
    print("=" * 30)
    
    run = CodexRun(
        prompt="Create a data processing script",
        model="gpt-4",
        provider="openai",
        enable_health_monitoring=True
    )
    
    health = run.get_health_status()
    if health:
        print(f"Status: {health.status.value}")
        print(f"Health: {health.health.value}")
        print(f"Runtime: {health.runtime_seconds:.1f}s")
        print(f"Responsive: {health.is_responsive}")
    
    return run


def real_time_monitoring():
    """Real-time health monitoring with alerts"""
    print("\nReal-Time Monitoring")
    print("=" * 30)
    
    run = CodexRun(
        prompt="Analyze large dataset",
        model="gpt-4",
        provider="openai",
        enable_health_monitoring=True
    )
    
    print(f"Monitoring: {run.run_id[:8]}...")
    
    # Monitor for 10 seconds
    for i in range(5):
        time.sleep(2)
        health = run.get_health_status()
        
        if health:
            status_icon = "✅" if health.status.value == "completed" else "❌" if health.status.value == "failed" else " "
            health_icon = "✅" if health.health.value == "healthy" else "❌" if health.health.value == "unhealthy" else "✅"
            
            print(f"  Check {i+1}: {status_icon} {health.status.value} | {health_icon} {health.health.value} | {health.runtime_seconds:.1f}s")
            
            # Alert on issues
            if health.health.value == "unhealthy":
                print(f"    ALERT: Agent unhealthy!")
            elif health.runtime_seconds > 8:
                print(f"    WARNING: Long runtime ({health.runtime_seconds:.1f}s)")
    
    return run


def session_health_monitoring():
    """Monitor multiple agents in a session"""
    print("\nSession Health Monitoring")
    print("=" * 30)
    
    session = CodexSession(
        session_id="health-demo",
        enable_health_monitoring=True
    )
    
    # Create multiple runs
    tasks = [
        "Build web scraper",
        "Create ML model", 
        "Design API"
    ]
    
    runs = []
    for task in tasks:
        run = session.add_run(
            prompt=task,
            model="gpt-4",
            provider="openai"
        )
        runs.append(run)
    
    # Check session health
    healthy_count = 0
    running_count = 0
    
    for run in runs:
        health = run.get_health_status()
        if health:
            if health.health.value == "healthy":
                healthy_count += 1
            if health.is_running:
                running_count += 1
    
    print(f"Session: {session.session_id}")
    print(f"Total runs: {len(runs)}")
    print(f"Healthy: {healthy_count}")
    print(f"Running: {running_count}")
    
    return session


def health_analytics():
    """Health analytics and reporting"""
    print("\nHealth Analytics")
    print("=" * 30)
    
    session = CodexSession(
        session_id="analytics-demo",
        enable_health_monitoring=True
    )
    
    # Create runs for analytics
    run_types = [
        ("Quick", "Write function"),
        ("Medium", "Create script"),
        ("Complex", "Build app")
    ]
    
    runs = []
    for run_type, prompt in run_types:
        run = session.add_run(
            prompt=prompt,
            model="gpt-4",
            provider="openai"
        )
        runs.append((run_type, run))
        time.sleep(0.3)
    
    # Generate analytics
    total_runs = len(runs)
    healthy_count = 0
    total_runtime = 0
    
    print("\nAnalytics Report:")
    for run_type, run in runs:
        health = run.get_health_status()
        
        if health.health.value == "healthy":
            healthy_count += 1
        total_runtime += health.runtime_seconds
        
        print(f"  {run_type:8} | {health.status.value:12} | {health.health.value:10} | {health.runtime_seconds:5.1f}s")
    
    print(f"\nSummary:")
    print(f"  Total: {total_runs}")
    print(f"  Healthy Rate: {(healthy_count/total_runs)*100:.1f}%")
    print(f"  Avg Runtime: {total_runtime/total_runs:.1f}s")
    
    return session


def main():
    """Run all health monitoring examples"""
    print("Auto-Codex Health Monitoring Examples")
    print("=" * 40)
    
    run1 = basic_health_check()
    run2 = real_time_monitoring()
    session1 = session_health_monitoring()
    session2 = health_analytics()
    
    print(f"\nHealth monitoring examples completed!")


if __name__ == "__main__":
    main() 