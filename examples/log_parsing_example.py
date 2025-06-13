#!/usr/bin/env python3
"""
Log Parsing and Data Extraction Example - auto_codex

Demonstrates log parsing and data extraction capabilities:
- Parsing existing Codex log files
- Extracting patches, commands, and tool usage
- Change detection and analysis
"""

import sys
import os
from typing import List, Dict

# Add auto_codex to path for examples
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auto_codex import (
    CodexLogParser, CodexOutputParser,
    PatchExtractor, CommandExtractor, ToolUsageExtractor, ChangeDetector,
    CodexRun, CodexSession
)


def log_parsing_example():
    """Parse existing Codex log files"""
    print("Log Parsing Example")
    print("=" * 30)
    
    # Create a sample run to generate logs
    run = CodexRun(
        prompt="Create a Python function to sort a list",
        model="gpt-4",
        provider="openai"
    )
    
    # Execute to generate log file
    result = run.execute(log_dir="./logs")
    print(f"Generated log: {run.log_file}")
    
    # Parse the log file
    parser = CodexLogParser(log_dir="./logs")
    parsed_runs = parser.parse_all_logs()
    
    print(f"Parsed {len(parsed_runs)} log files:")
    for parsed_run in parsed_runs:
        print(f"  Run ID: {parsed_run.run_id[:8]}...")
        print(f"  Success: {parsed_run.success}")
        print(f"  Duration: {parsed_run.duration_seconds:.1f}s")
        print(f"  Changes: {len(parsed_run.changes)}")
    
    return parsed_runs


def data_extraction_example():
    """Extract specific data types from logs"""
    print("\nData Extraction Example")
    print("=" * 30)
    
    # Create extractors
    patch_extractor = PatchExtractor()
    command_extractor = CommandExtractor()
    tool_extractor = ToolUsageExtractor()
    
    # Create a run that will generate extractable data
    run = CodexRun(
        prompt="Create a web scraper and run it to test functionality",
        model="gpt-4",
        provider="openai"
    )
    
    result = run.execute(log_dir="./logs")
    
    if run.log_file and os.path.exists(run.log_file):
        # Extract patches
        patches = patch_extractor.extract_from_file(run.log_file)
        print(f"Extracted {len(patches)} patches:")
        for patch in patches[:3]:  # Show first 3
            print(f"  File: {patch.file_path}")
            print(f"  Type: {patch.change_type}")
            print(f"  Lines: {len(patch.content.splitlines())}")
        
        # Extract commands
        commands = command_extractor.extract_from_file(run.log_file)
        print(f"\nExtracted {len(commands)} commands:")
        for cmd in commands[:3]:  # Show first 3
            print(f"  Command: {cmd.command[:50]}...")
            print(f"  Exit code: {cmd.exit_code}")
        
        # Extract tool usage
        tools = tool_extractor.extract_from_file(run.log_file)
        print(f"\nExtracted {len(tools)} tool usages:")
        for tool in tools[:3]:  # Show first 3
            print(f"  Tool: {tool.tool_name}")
            print(f"  Parameters: {len(tool.parameters)}")
    
    return patches, commands, tools


def output_parsing_example():
    """Parse and analyze Codex outputs"""
    print("\nOutput Parsing Example")
    print("=" * 30)
    
    parser = CodexOutputParser()
    
    # Sample Codex output with code blocks
    sample_output = '''
Here's a Python function to calculate fibonacci numbers:

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
print(fibonacci(10))
```

And here's how to use it:

```bash
python fibonacci.py
```
    '''
    
    # Parse the output
    parsed = parser.parse_output(sample_output)
    
    print(f"Parsed output:")
    print(f"  Code blocks: {len(parsed.code_blocks)}")
    print(f"  Text sections: {len(parsed.text_sections)}")
    
    # Analyze code blocks
    for i, block in enumerate(parsed.code_blocks, 1):
        print(f"  Block {i}: {block.language} ({len(block.content.splitlines())} lines)")
        if block.language == "python":
            print(f"    Contains 'def': {'def ' in block.content}")
            print(f"    Contains 'class': {'class ' in block.content}")
    
    return parsed


def change_detection_example():
    """Detect and analyze changes"""
    print("\nChange Detection Example")
    print("=" * 30)
    
    detector = ChangeDetector()
    
    # Create a session with multiple runs
    session = CodexSession(session_id="change-detection-demo")
    
    tasks = [
        "Create a calculator class",
        "Add error handling to the calculator",
        "Write tests for the calculator"
    ]
    
    for task in tasks:
        run = session.add_run(prompt=task, model="gpt-4", provider="openai")
    
    # Execute all runs
    session_result = session.execute_all()
    
    # Detect changes across all runs
    all_changes = []
    for run in session.runs:
        if run.log_file and os.path.exists(run.log_file):
            changes = detector.extract_from_file(run.log_file)
            all_changes.extend(changes)
    
    print(f"Detected {len(all_changes)} changes:")
    
    # Analyze changes by type
    change_types = {}
    for change in all_changes:
        change_type = change.change_type
        change_types[change_type] = change_types.get(change_type, 0) + 1
    
    print("Change types:")
    for change_type, count in change_types.items():
        print(f"  {change_type}: {count}")
    
    return all_changes


def main():
    """Run all log parsing and extraction examples"""
    print("Auto-Codex Log Parsing and Data Extraction Examples")
    print("=" * 55)
    
    # Ensure logs directory exists
    os.makedirs("./logs", exist_ok=True)
    
    parsed_runs = log_parsing_example()
    patches, commands, tools = data_extraction_example()
    parsed_output = output_parsing_example()
    changes = change_detection_example()
    
    print(f"\nLog parsing examples completed!")


if __name__ == "__main__":
    main()
 