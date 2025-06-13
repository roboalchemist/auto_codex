#!/usr/bin/env python3
"""
Interactive Usage Example - auto_codex

Demonstrates interactive auto_codex usage:
- Interactive session management
- Dynamic prompt handling
- Real-time result processing
"""

import sys
import time
from typing import List, Dict

# Add auto_codex to path for examples
sys.path.insert(0, 'auto_codex')

from auto_codex import CodexRun, CodexSession, get_health_monitor


class InteractiveCodexDemo:
    """Interactive auto_codex demonstration"""
    
    def __init__(self):
        self.session = CodexSession(
            session_id="interactive-demo",
            enable_health_monitoring=True
        )
        self.runs: List[CodexRun] = []
    
    def add_task(self, prompt: str, model: str = "gpt-4") -> CodexRun:
        """Add a new task to the session"""
        run = self.session.add_run(
            prompt=prompt,
            model=model,
            provider="openai"
        )
        self.runs.append(run)
        print(f"Added task: {prompt[:40]}... (ID: {run.run_id[:8]})")
        return run
    
    def check_status(self) -> Dict:
        """Check status of all runs"""
        status_summary = {
            "total": len(self.runs),
            "completed": 0,
            "running": 0,
            "failed": 0
        }
        
        for run in self.runs:
            health = run.get_health_status()
            if health:
                if health.status.value == "completed":
                    status_summary["completed"] += 1
                elif health.status.value == "running":
                    status_summary["running"] += 1
                elif health.status.value == "failed":
                    status_summary["failed"] += 1
        
        return status_summary
    
    def get_results(self, run_id: str = None) -> List[Dict]:
        """Get results from specific run or all runs"""
        results = []
        
        target_runs = [r for r in self.runs if r.run_id.startswith(run_id)] if run_id else self.runs
        
        for run in target_runs:
            if run.results:
                for result in run.results:
                    results.append({
                        "run_id": run.run_id[:8],
                        "type": result.type,
                        "content_preview": result.content[:100] + "...",
                        "full_content": result.content
                    })
        
        return results
    
    def monitor_progress(self, duration: int = 10):
        """Monitor progress of all runs"""
        print(f"Monitoring progress for {duration} seconds...")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            status = self.check_status()
            print(f"Status: {status['completed']} completed, {status['running']} running, {status['failed']} failed")
            
            # Show individual run status
            for run in self.runs[-3:]:  # Show last 3 runs
                health = run.get_health_status()
                if health:
                    status_icon = "✅" if health.status.value == "completed" else "❌" if health.status.value == "failed" else "✅"
                    print(f"  {run.run_id[:8]}: {status_icon} {health.status.value} ({health.runtime_seconds:.1f}s)")
            
            time.sleep(2)
            print()


def basic_interactive_example():
    """Basic interactive usage"""
    print("Basic Interactive Example")
    print("=" * 30)
    
    demo = InteractiveCodexDemo()
    
    # Add some tasks
    tasks = [
        "Write a Python function to parse JSON",
        "Create a simple web server",
        "Build a data validation script"
    ]
    
    for task in tasks:
        demo.add_task(task)
    
    # Check initial status
    status = demo.check_status()
    print(f"\nInitial status: {status}")
    
    return demo


def dynamic_task_management():
    """Dynamic task addition and monitoring"""
    print("\nDynamic Task Management")
    print("=" * 30)
    
    demo = InteractiveCodexDemo()
    
    # Start with initial tasks
    demo.add_task("Create a calculator class")
    demo.add_task("Write unit tests")
    
    # Monitor progress
    demo.monitor_progress(duration=6)
    
    # Add more tasks dynamically
    demo.add_task("Generate documentation")
    demo.add_task("Create deployment script")
    
    print(f"Total tasks: {len(demo.runs)}")
    
    return demo


def result_processing_example():
    """Result processing and extraction"""
    print("\nResult Processing Example")
    print("=" * 30)
    
    demo = InteractiveCodexDemo()
    
    # Add tasks that generate code
    demo.add_task("Create a Python class for file operations")
    demo.add_task("Write a function to connect to database")
    
    # Wait a moment for processing
    time.sleep(2)
    
    # Get and process results
    results = demo.get_results()
    
    print(f"Retrieved {len(results)} results:")
    for result in results:
        print(f"  Run {result['run_id']}: {result['type']} - {result['content_preview']}")
        
        # Check for code content
        if "```python" in result['full_content']:
            print(f"    ✅ Contains Python code")
        if "class " in result['full_content']:
            print(f"    ✅ Contains class definition")
        if "def " in result['full_content']:
            print(f"    ✅ Contains function definition")
    
    return demo


def session_management_example():
    """Session management and coordination"""
    print("\nSession Management Example")
    print("=" * 30)
    
    demo = InteractiveCodexDemo()
    
    # Create a coordinated set of tasks
    project_tasks = [
        "Design database schema for user management",
        "Create user authentication API",
        "Build user registration form",
        "Write integration tests"
    ]
    
    print("Creating coordinated project tasks:")
    for task in project_tasks:
        demo.add_task(task)
    
    # Monitor the session
    print(f"\nSession ID: {demo.session.session_id}")
    print(f"Total runs in session: {len(demo.session.runs)}")
    
    # Check final status
    final_status = demo.check_status()
    print(f"Final status: {final_status}")
    
    return demo


def main():
    """Run all interactive usage examples"""
    print("Auto-Codex Interactive Usage Examples")
    print("=" * 42)
    
    demo1 = basic_interactive_example()
    demo2 = dynamic_task_management()
    demo3 = result_processing_example()
    demo4 = session_management_example()
    
    print(f"\nInteractive examples completed!")
    total_runs = sum(len(demo.runs) for demo in [demo1, demo2, demo3, demo4])
    print(f"Total runs created: {total_runs}")


if __name__ == "__main__":
    main()
