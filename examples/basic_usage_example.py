#!/usr/bin/env python3
"""
Basic Usage Example - auto_codex

Demonstrates core auto_codex functionality:
- Creating and running CodexRun instances
- Session management with CodexSession
- Basic result extraction
"""

import sys
import os

# Add auto_codex to path for examples
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auto_codex import CodexRun, CodexSession


def single_run_example():
    """Basic single run example"""
    print("Single Run Example")
    print("=" * 30)
    
    # Create and execute a single run
    run = CodexRun(
        prompt="Write a Python function to calculate fibonacci numbers",
        model="gpt-4",
        provider="openai"
    )
    
    print(f"Run ID: {run.run_id[:8]}...")
    print(f"Status: {run.status}")
    print(f"Model: {run.model}")
    
    # Extract results
    if run.results:
        print(f"Results: {len(run.results)} items")
        for i, result in enumerate(run.results[:2], 1):
            print(f"  {i}. {result.content[:50]}...")
    
    return run


def session_example():
    """Session with multiple runs example"""
    print("\nSession Example")
    print("=" * 30)
    
    # Create session
    session = CodexSession(session_id="demo-session")
    
    # Add multiple runs
    tasks = [
        "Create a simple web scraper",
        "Write unit tests for a calculator",
        "Build a REST API endpoint"
    ]
    
    runs = []
    for task in tasks:
        run = session.add_run(
            prompt=task,
            model="gpt-4",
            provider="openai"
        )
        runs.append(run)
        print(f"Added: {task[:30]}... (ID: {run.run_id[:8]})")
    
    print(f"\nSession: {session.session_id}")
    print(f"Total runs: {len(session.runs)}")
    
    return session


def result_extraction_example():
    """Result extraction and processing example"""
    print("\nResult Extraction Example")
    print("=" * 30)
    
    run = CodexRun(
        prompt="Create a Python class for managing a todo list with add, remove, and list methods",
        model="gpt-4",
        provider="openai"
    )
    
    # Process results
    if run.results:
        for result in run.results:
            print(f"Type: {result.type}")
            print(f"Content length: {len(result.content)} chars")
            
            # Extract code blocks if present
            if "```python" in result.content:
                print("✅ Contains Python code")
            if "class" in result.content.lower():
                print("✅ Contains class definition")
    
    return run


def main():
    """Run all basic usage examples"""
    print("Auto-Codex Basic Usage Examples")
    print("=" * 40)
    
    # Run examples
    run1 = single_run_example()
    session = session_example()
    run2 = result_extraction_example()
    
    print(f"\nExamples completed successfully!")
    print(f"Created {len([run1, run2])} runs and 1 session")


if __name__ == "__main__":
    main() 