#!/usr/bin/env python3
"""
Utilities Example - auto_codex

Demonstrates utility features:
- Template processing for dynamic prompts
- File management operations
- Diff utilities for code analysis
"""

import sys
import os
import tempfile
from typing import Dict, List

# Add auto_codex to path for examples
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auto_codex import (
    TemplateProcessor, FileManager, DiffUtils,
    CodexRun, CodexSession
)


def template_processing_example():
    """Template-based prompt generation"""
    print("Template Processing Example")
    print("=" * 30)
    
    # Create template processor
    processor = TemplateProcessor()
    
    # Define a prompt template
    template = """
Create a {language} {project_type} with the following features:
- {feature1}
- {feature2}
- {feature3}

The project should be named "{project_name}" and include:
{additional_requirements}
    """
    
    # Template variables
    variables = {
        "language": "Python",
        "project_type": "web application",
        "feature1": "User authentication",
        "feature2": "Database integration",
        "feature3": "REST API endpoints",
        "project_name": "TaskManager",
        "additional_requirements": "- Unit tests\n- Documentation\n- Docker configuration"
    }
    
    # Process template
    processed_prompt = processor.process_template(template, variables)
    
    print("Template variables:")
    for key, value in variables.items():
        print(f"  {key}: {value}")
    
    print(f"\nProcessed prompt:")
    print(f"  Length: {len(processed_prompt)} characters")
    print(f"  Preview: {processed_prompt[:100]}...")
    
    # Use processed prompt in a run
    run = CodexRun(
        prompt=processed_prompt,
        model="gpt-4",
        provider="openai"
    )
    
    print(f"\nCreated run with templated prompt: {run.run_id[:8]}...")
    
    return processor, run


def file_management_example():
    """File management operations"""
    print("\nFile Management Example")
    print("=" * 30)
    
    # Create file manager
    file_manager = FileManager()
    
    # Create temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Working in: {temp_dir}")
        
        # Create some sample files
        sample_files = {
            "main.py": "def main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()",
            "config.json": '{\n  "app_name": "demo",\n  "version": "1.0.0"\n}',
            "README.md": "# Demo Project\n\nThis is a demo project."
        }
        
        # Save files
        for filename, content in sample_files.items():
            filepath = os.path.join(temp_dir, filename)
            file_manager.save_file(filepath, content)
            print(f"Created: {filename}")
        
        # List files
        files = file_manager.list_files(temp_dir)
        print(f"\nFiles in directory: {len(files)}")
        for file in files:
            print(f"  {os.path.basename(file)}")
        
        # Read file
        main_content = file_manager.read_file(os.path.join(temp_dir, "main.py"))
        print(f"\nRead main.py: {len(main_content)} characters")
        
        # Create CSV data
        csv_data = [
            ["Name", "Age", "City"],
            ["Alice", "30", "New York"],
            ["Bob", "25", "San Francisco"],
            ["Charlie", "35", "Chicago"]
        ]
        
        csv_file = os.path.join(temp_dir, "data.csv")
        file_manager.save_csv_file(csv_file, csv_data[0], csv_data[1:])
        print(f"Created CSV with {len(csv_data)-1} rows")
        
        # Backup directory
        backup_dir = os.path.join(temp_dir, "backup")
        file_manager.copy_directory_structure(temp_dir, backup_dir, "*.py")
        print(f"Backed up Python files to: backup/")
    
    return file_manager


def diff_utilities_example():
    """Code diff analysis"""
    print("\nDiff Utilities Example")
    print("=" * 30)
    
    # Sample code versions
    original_code = """def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

def main():
    nums = [1, 2, 3, 4, 5]
    result = calculate_sum(nums)
    print(result)
"""

    modified_code = """def calculate_sum(numbers):
    \"\"\"Calculate the sum of a list of numbers.\"\"\"
    if not numbers:
        return 0
    
    total = 0
    for num in numbers:
        if isinstance(num, (int, float)):
            total += num
    return total

def calculate_average(numbers):
    \"\"\"Calculate the average of a list of numbers.\"\"\"
    if not numbers:
        return 0
    return calculate_sum(numbers) / len(numbers)

def main():
    nums = [1, 2, 3, 4, 5]
    result = calculate_sum(nums)
    avg = calculate_average(nums)
    print(f"Sum: {result}, Average: {avg}")

if __name__ == "__main__":
    main()
"""
    
    # Generate diff
    diff_lines = DiffUtils.generate_diff(original_code, modified_code, "original.py", "modified.py")
    
    print(f"Generated diff with {len(diff_lines)} lines:")
    print("Changes summary:")
    
    # Analyze diff
    additions = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
    deletions = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
    
    print(f"  Additions: {additions} lines")
    print(f"  Deletions: {deletions} lines")
    
    # Show first few diff lines
    print(f"\nFirst 10 diff lines:")
    for line in diff_lines[:10]:
        print(f"  {line}")
    
    # Apply diff (simulation)
    print(f"\nDiff analysis:")
    if additions > deletions:
        print("  Code expanded (more additions than deletions)")
    elif deletions > additions:
        print("  Code reduced (more deletions than additions)")
    else:
        print("  Code refactored (equal additions and deletions)")
    
    return diff_lines


def batch_processing_example():
    """Batch processing with templates and file management"""
    print("\nBatch Processing Example")
    print("=" * 30)
    
    processor = TemplateProcessor()
    file_manager = FileManager()
    
    # Template for multiple similar tasks
    task_template = "Create a {language} function to {action} {data_type} data"
    
    # Batch data
    batch_tasks = [
        {"language": "Python", "action": "validate", "data_type": "JSON"},
        {"language": "Python", "action": "parse", "data_type": "CSV"},
        {"language": "Python", "action": "transform", "data_type": "XML"},
        {"language": "JavaScript", "action": "validate", "data_type": "form"},
        {"language": "JavaScript", "action": "format", "data_type": "date"}
    ]
    
    # Create session for batch processing
    session = CodexSession(session_id="batch-processing-demo")
    
    # Process each task
    for i, task_data in enumerate(batch_tasks, 1):
        # Generate prompt from template
        prompt = processor.process_template(task_template, task_data)
        
        # Add to session
        run = session.add_run(
            prompt=prompt,
            model="gpt-4",
            provider="openai"
        )
        
        print(f"Task {i}: {task_data['language']} {task_data['action']} {task_data['data_type']}")
    
    print(f"\nBatch processing setup complete:")
    print(f"  Total tasks: {len(batch_tasks)}")
    print(f"  Session runs: {len(session.runs)}")
    
    # Save batch configuration
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        import json
        config = {
            "session_id": session.session_id,
            "template": task_template,
            "tasks": batch_tasks
        }
        json.dump(config, f, indent=2)
        print(f"  Saved config: {f.name}")
    
    return session


def main():
    """Run all utility examples"""
    print("Auto-Codex Utilities Examples")
    print("=" * 35)
    
    processor, template_run = template_processing_example()
    file_manager = file_management_example()
    diff_lines = diff_utilities_example()
    batch_session = batch_processing_example()
    
    print(f"\nUtilities examples completed!")
    print(f"Demonstrated template processing, file management, and diff analysis")


if __name__ == "__main__":
    main()
