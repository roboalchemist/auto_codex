#!/usr/bin/env python3
"""
End-to-End Example - auto_codex

Demonstrates a complete, end-to-end run where an agent solves a coding problem.
"""

import sys
import os
import tempfile
import shutil
import time
import threading
import importlib.util
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from auto_codex.core import CodexRun
from auto_codex.health import get_health_monitor
import pprint

# Add auto_codex to path for examples
sys.path.insert(0, '.')

from auto_codex import CodexRun
from examples.real_time_inspector_example import SimpleAgentInspector

# Load environment variables from .env file
load_dotenv()

def create_two_sum_prompt():
    """Creates a prompt to solve the Two Sum LeetCode problem."""
    return """
You are being tested on your ability to solve beginner-level LeetCode problems.
You will be given a series of coding challenges that test fundamental programming concepts.

Your task is to:
1. Create a Python file with the specified filename.
2. Implement the required function with the exact name specified.
3. Ensure your solution handles all the given test cases correctly.
4. Write clean, efficient code that solves the problem.

Each problem will specify the expected filename and function name. Make sure to follow these exactly.

Hint: To write the python code to a file, you can use `echo -e "your code here" >> your_file.py`.

Create a Python file called 'two_sum.py' with a function named 'two_sum' that solves LeetCode Problem #1.

Problem: Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.

Example:
- Input: nums = [2,7,11,15], target = 9
- Output: [0,1] (because nums[0] + nums[1] == 9)
"""

def verify_solution(directory: str) -> bool:
    """Verify that the agent correctly solved the Two Sum problem."""
    file_path = os.path.join(directory, "two_sum.py")
    if not os.path.exists(file_path):
        print("❌ Verification failed: 'two_sum.py' not found.")
        return False
    
    try:
        # Dynamically import the created module
        spec = importlib.util.spec_from_file_location("two_sum", file_path)
        two_sum_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(two_sum_module)
        
        # Get the function
        two_sum_func = getattr(two_sum_module, "two_sum", None)
        if not callable(two_sum_func):
            print("❌ Verification failed: 'two_sum' function not found or not callable.")
            return False
            
        # Run test case
        nums = [2, 7, 11, 15]
        target = 9
        expected = [0, 1]
        
        result = two_sum_func(nums, target)
        # Sort to handle any order
        if isinstance(result, list):
            result.sort()
        
        if result == expected:
            print(f"✅ Verification successful! `two_sum({nums}, {target})` returned `{result}`.")
            return True
        else:
            print(f"❌ Verification failed: `two_sum({nums}, {target})` returned `{result}`, expected `{expected}`.")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed with an error: {e}")
        return False

def print_json_line(line: dict):
    """Callback function to print JSON lines from the agent."""
    print("------ Agent Output ------")
    pprint.pprint(line)
    print("--------------------------")

def main():
    """Run the end-to-end example."""
    # Load .env file for API keys
    if not load_dotenv():
        print("⚠️  Warning: .env file not found. Please create one with your OPENAI_API_KEY.")
        sys.exit(1)

    print("Auto-Codex End-to-End Example")
    print("=============================================")

    # Use a temporary directory for the agent to work in
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📂 Working in temporary directory: {temp_dir}")

        # --- Prompt Definition ---
        # The benchmark separates the general instructions (system prompt) 
        # from the specific task. This is more effective.
        system_prompt = """You are a developer agent. You are being tested on your ability to solve LeetCode problems.
You will be given a coding challenge that test fundamental programming concepts.

Your task is to:
1. Read the problem carefully.
2. Write the Python code to solve the problem.
3. Use the `apply_patch` tool with the 'Add File' syntax to create the file. This is the most reliable method. For example: `apply_patch '*** Begin Patch\\n*** Add File: new_file.py\\n+...file content...\\n*** End Patch'`
- Pay close attention to formatting. The patch format is very strict; invisible characters or extra lines will cause it to fail.
4. Create a Python file with the specified filename and implement the required function.
5. Ensure your solution handles all the given test cases correctly.
6. Run flake8 linting on the file to ensure there are no errors. Fix any linting errors that do come up.

Each problem will specify the expected filename and function name. Make sure to follow these exactly."""

        task_prompt = """Create a Python file called 'two_sum.py' with a function named 'two_sum' that solves LeetCode Problem #1.

Problem: Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.

Example:
- Input: nums = [2,7,11,15], target = 9
- Output: [0,1] (because nums[0] + nums[1] == 9)"""

        # Combine the prompts
        prompt = f"{system_prompt}\n\n{task_prompt}"

        # --- Agent Execution ---
        # 1. Initialize the CodexRun
        run = CodexRun(
            prompt=prompt,
            model="gpt-4-1106-preview",
            provider="openai",
            writable_root=temp_dir,
            timeout=180,
            dangerously_auto_approve_everything=True,
            on_json_line=print_json_line
        )
        
        print(f"🚀 Starting agent run: {run.run_id}")
        
        # The execution is now synchronous and will print in real-time
        result = run.execute()

        # 4. Final status check
        print("\n🏁 Run complete!")
        print(f"   Success: {run.success}")
        print(f"   Error: {run.error}")

        # 5. Verify the solution
        print("\n🔍 Verifying the solution...")
        if verify_solution(temp_dir):
            print("✅✅✅ End-to-end test PASSED! ✅✅✅")
        else:
            print("❌❌❌ End-to-end test FAILED! ❌❌❌")

    print("\n✨ Example complete!")


if __name__ == "__main__":
    main() 