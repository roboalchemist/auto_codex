#!/usr/bin/env python3
"""
Interactive Controller Example - auto_codex

Demonstrates interactive agent control:
- Starting and stopping agents
- Callback-driven workflows
- Dynamic agent management
"""

import sys
import time
from typing import Dict, Any

# Add auto_codex to path for examples
sys.path.insert(0, 'auto_codex')

from auto_codex import CodexRun, CodexSession


class SimpleAgentController:
    """Simple agent controller for demonstrations"""
    
    def __init__(self):
        self.session = CodexSession(session_id="controller-demo")
        self.active_runs: Dict[str, CodexRun] = {}
        self.callbacks = []
    
    def start_agent(self, task: str, agent_id: str = None) -> CodexRun:
        """Start a new agent with given task"""
        run = self.session.add_run(
            prompt=task,
            model="gpt-4",
            provider="openai"
        )
        
        agent_id = agent_id or run.run_id[:8]
        self.active_runs[agent_id] = run
        
        print(f"Started agent {agent_id}: {task[:40]}...")
        return run
    
    def stop_agent(self, agent_id: str) -> bool:
        """Stop an active agent"""
        if agent_id in self.active_runs:
            run = self.active_runs[agent_id]
            # In real implementation, would call run.stop()
            del self.active_runs[agent_id]
            print(f"Stopped agent {agent_id}")
            return True
        return False
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status of specific agent"""
        if agent_id not in self.active_runs:
            return {"error": "Agent not found"}
        
        run = self.active_runs[agent_id]
        return {
            "id": agent_id,
            "status": run.status,
            "model": run.model,
            "prompt": run.prompt[:50] + "...",
            "results_count": len(run.results) if run.results else 0
        }
    
    def list_agents(self) -> Dict[str, Dict]:
        """List all active agents"""
        return {aid: self.get_agent_status(aid) for aid in self.active_runs}
    
    def add_callback(self, callback_func):
        """Add callback for agent events"""
        self.callbacks.append(callback_func)
    
    def trigger_callbacks(self, event_type: str, agent_id: str, data: Dict):
        """Trigger registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(event_type, agent_id, data)
            except Exception as e:
                print(f"Callback error: {e}")


def agent_event_callback(event_type: str, agent_id: str, data: Dict):
    """Example callback function"""
    print(f"Event: {event_type} | Agent: {agent_id} | Data: {data}")


def basic_control_example():
    """Basic agent control operations"""
    print("Basic Control Example")
    print("=" * 30)
    
    controller = SimpleAgentController()
    
    # Start multiple agents
    tasks = [
        "Create a web scraper",
        "Build a calculator",
        "Design a database schema"
    ]
    
    agent_ids = []
    for i, task in enumerate(tasks, 1):
        agent_id = f"agent_{i}"
        run = controller.start_agent(task, agent_id)
        agent_ids.append(agent_id)
    
    # Check status
    print(f"\nActive agents: {len(controller.active_runs)}")
    for aid in agent_ids:
        status = controller.get_agent_status(aid)
        print(f"  {aid}: {status['status']} - {status['prompt']}")
    
    # Stop one agent
    controller.stop_agent(agent_ids[1])
    print(f"Active agents after stop: {len(controller.active_runs)}")
    
    return controller


def callback_workflow_example():
    """Callback-driven workflow example"""
    print("\nCallback Workflow Example")
    print("=" * 30)
    
    controller = SimpleAgentController()
    
    # Add callback
    controller.add_callback(agent_event_callback)
    
    # Start agent and trigger events
    run = controller.start_agent("Analyze data patterns", "analyzer")
    
    # Simulate events
    controller.trigger_callbacks("started", "analyzer", {"timestamp": time.time()})
    time.sleep(1)
    controller.trigger_callbacks("progress", "analyzer", {"completion": 0.5})
    time.sleep(1)
    controller.trigger_callbacks("completed", "analyzer", {"results": "analysis complete"})
    
    return controller


def dynamic_management_example():
    """Dynamic agent management example"""
    print("\nDynamic Management Example")
    print("=" * 30)
    
    controller = SimpleAgentController()
    
    # Start initial agents
    initial_tasks = [
        "Process user data",
        "Generate reports"
    ]
    
    for i, task in enumerate(initial_tasks, 1):
        controller.start_agent(task, f"worker_{i}")
    
    print(f"Initial agents: {len(controller.active_runs)}")
    
    # Simulate dynamic scaling
    time.sleep(1)
    
    # Add more agents based on load
    if len(controller.active_runs) < 5:
        controller.start_agent("Handle overflow tasks", "overflow_1")
        controller.start_agent("Backup processing", "backup_1")
    
    print(f"Scaled agents: {len(controller.active_runs)}")
    
    # List all agents
    agents = controller.list_agents()
    for aid, info in agents.items():
        print(f"  {aid}: {info['status']} ({info['results_count']} results)")
    
    return controller


def main():
    """Run all interactive controller examples"""
    print("Auto-Codex Interactive Controller Examples")
    print("=" * 45)
    
    controller1 = basic_control_example()
    controller2 = callback_workflow_example()
    controller3 = dynamic_management_example()
    
    print(f"\nController examples completed!")


if __name__ == "__main__":
    main()
