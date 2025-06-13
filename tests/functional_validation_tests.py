#!/usr/bin/env python3
"""
Functional Validation Test Suite for Codex Agent
Tests whether agents can actually create working code that passes benchmark tests

Measures:
1. File Creation - Did the agent create the specified file?
2. Function Implementation - Does the function exist with correct name?
3. Input/Output Correctness - Does it handle specified inputs/outputs?
4. Functionality - Does it actually work and pass unit tests?
5. Multi-turn Capability - Can it handle follow-up prompts to complete tasks?
"""

import os
import sys
import importlib.util
import tempfile
import shutil
import traceback
from auto_codex.core import CodexRun, CodexSession
import time

class FunctionalTest:
    def __init__(self, name, task_description, filename, function_name, test_cases):
        self.name = name
        self.task_description = task_description
        self.filename = filename
        self.function_name = function_name
        self.test_cases = test_cases  # List of (inputs, expected_output) tuples
        
        # Results tracking
        self.file_created = False
        self.function_exists = False
        self.input_output_correct = False
        self.functionality_works = False
        self.execution_time = 0
        self.error_message = None
        self.attempts_used = 0

class MultiTurnTest:
    def __init__(self, name, prompts, filename, function_name, test_cases):
        self.name = name
        self.prompts = prompts  # List of prompts to send in sequence
        self.filename = filename
        self.function_name = function_name
        self.test_cases = test_cases  # List of (inputs, expected_output) tuples
        
        # Results tracking
        self.file_created = False
        self.function_exists = False
        self.input_output_correct = False
        self.functionality_works = False
        self.execution_time = 0
        self.error_message = None
        self.attempts_used = 0
        self.turns_completed = 0

class FunctionalValidator:
    def __init__(self, model='codex-mini-latest', provider='openai', timeout=60):
        self.model = model
        self.provider = provider
        self.timeout = timeout
        self.debug = True  # Enable debug mode for detailed logging
        self.results = []
        self.multi_turn_results = []
    
    def create_test_suite(self):
        """Create 5 simple math function tests"""
        return [
            FunctionalTest(
                name="Addition Function",
                task_description="""Create a Python file called 'math_ops.py' with a function named 'add' that takes two numbers (a, b) and returns their sum (a + b).

HINT: The apply_patch method with "Add File" syntax works reliably in sandboxed environments for creating new files.""",
                filename="math_ops.py",
                function_name="add",
                test_cases=[
                    ((2, 3), 5),
                    ((10, 5), 15),
                    ((-1, 1), 0),
                    ((0, 0), 0),
                    ((100, 200), 300)
                ]
            ),
            
            FunctionalTest(
                name="Subtraction Function",
                task_description="""Create a Python file called 'calculator.py' with a function named 'subtract' that takes two numbers (a, b) and returns a minus b (a - b).

HINT: The apply_patch method with "Add File" syntax works reliably in sandboxed environments for creating new files.""",
                filename="calculator.py",
                function_name="subtract",
                test_cases=[
                    ((10, 3), 7),
                    ((5, 5), 0),
                    ((1, 10), -9),
                    ((0, 5), -5),
                    ((100, 25), 75)
                ]
            ),
            
            FunctionalTest(
                name="Multiplication Function",
                task_description="""Create a Python file called 'multiply.py' with a function named 'multiply' that takes two numbers (x, y) and returns their product (x * y).

HINT: The apply_patch method with "Add File" syntax works reliably in sandboxed environments for creating new files.""",
                filename="multiply.py",
                function_name="multiply",
                test_cases=[
                    ((3, 4), 12),
                    ((5, 0), 0),
                    ((2, 2), 4),
                    ((-3, 2), -6),
                    ((10, 10), 100)
                ]
            ),
            
            FunctionalTest(
                name="Division Function",
                task_description="""Create a Python file called 'division.py' with a function named 'divide' that takes two numbers (a, b) and returns a divided by b (a / b). Return the result as a float.

HINT: The apply_patch method with "Add File" syntax works reliably in sandboxed environments for creating new files.""",
                filename="division.py",
                function_name="divide",
                test_cases=[
                    ((10, 2), 5.0),
                    ((15, 3), 5.0),
                    ((7, 2), 3.5),
                    ((1, 4), 0.25),
                    ((100, 10), 10.0)
                ]
            ),
            
            FunctionalTest(
                name="Square Function",
                task_description="""Create a Python file called 'square.py' with a function named 'square' that takes one number (n) and returns n squared (n * n).

HINT: The apply_patch method with "Add File" syntax works reliably in sandboxed environments for creating new files.""",
                filename="square.py",
                function_name="square",
                test_cases=[
                    ((3,), 9),
                    ((5,), 25),
                    ((0,), 0),
                    ((-4,), 16),
                    ((10,), 100)
                ]
            )
        ]

    def create_multi_turn_test_suite(self):
        """Create multi-turn tests that require follow-up prompts to complete"""
        return [
            MultiTurnTest(
                name="Calculator with Error Handling",
                prompts=[
                    """Create a Python file called 'safe_calculator.py' with a function named 'safe_divide' that takes two numbers (a, b) and returns a divided by b.

HINT: The apply_patch method with "Add File" syntax works reliably in sandboxed environments for creating new files.""",
                    
                    """The safe_divide function needs error handling for division by zero. Please update the function to return the string "Error: Division by zero" when b is 0, otherwise return the division result as a float.

HINT: Use apply_patch with "Update File" syntax to modify existing files."""
                ],
                filename="safe_calculator.py",
                function_name="safe_divide",
                test_cases=[
                    ((10, 2), 5.0),
                    ((15, 3), 5.0),
                    ((7, 0), "Error: Division by zero"),
                    ((0, 5), 0.0),
                    ((100, 0), "Error: Division by zero")
                ]
            ),
            
            MultiTurnTest(
                name="String Processor with Validation",
                prompts=[
                    """Create a Python file called 'text_processor.py' with a function named 'process_text' that takes a string and returns it in uppercase.

HINT: The apply_patch method with "Add File" syntax works reliably in sandboxed environments for creating new files.""",
                    
                    """The process_text function needs input validation. Please update it to:
1. Return "Error: Input must be a string" if the input is not a string
2. Return "Error: Empty string not allowed" if the input is an empty string
3. Otherwise return the text in uppercase

HINT: Use apply_patch with "Update File" syntax to modify existing files."""
                ],
                filename="text_processor.py",
                function_name="process_text",
                test_cases=[
                    (("hello",), "HELLO"),
                    (("world",), "WORLD"),
                    (("",), "Error: Empty string not allowed"),
                    ((123,), "Error: Input must be a string"),
                    (("Test String",), "TEST STRING")
                ]
            ),
            
            MultiTurnTest(
                name="List Utilities with Enhancement",
                prompts=[
                    """Create a Python file called 'list_utils.py' with a function named 'get_max' that takes a list of numbers and returns the maximum value.

HINT: The apply_patch method with "Add File" syntax works reliably in sandboxed environments for creating new files.""",
                    
                    """The get_max function needs to handle edge cases. Please update it to:
1. Return "Error: Empty list" if the list is empty
2. Return "Error: Invalid input" if the input is not a list
3. Otherwise return the maximum value

HINT: Use apply_patch with "Update File" syntax to modify existing files."""
                ],
                filename="list_utils.py",
                function_name="get_max",
                test_cases=[
                    (([1, 2, 3, 4, 5],), 5),
                    (([10, 5, 8, 2],), 10),
                    (([],), "Error: Empty list"),
                    (("not a list",), "Error: Invalid input"),
                    (([-1, -5, -2],), -1)
                ]
            )
        ]
    
    def run_single_test(self, test, test_dir, max_attempts=3):
        """Run a single functional validation test with up to 3 attempts"""
        print(f"\n🧪 Running Test: {test.name}")
        print(f"  Task: {test.task_description}")
        print(f"  Target: {test.filename} -> {test.function_name}()")
        print(f"  Max Attempts: {max_attempts}")
        print("=" * 60)
        
        overall_start_time = time.time()
        
        for attempt in range(1, max_attempts + 1):
            print(f"\n  Attempt {attempt}/{max_attempts}:")
            
            # Clean up any previous attempt files
            file_path = os.path.join(test_dir, test.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"   🧹 Cleaned up previous attempt file")
            
            attempt_start_time = time.time()
            
            try:
                # Step 1: Run codex agent
                run = CodexRun(
                    prompt=test.task_description,
                    model=self.model,
                    provider=self.provider,
                    writable_root=test_dir,
                    timeout=self.timeout,
                    debug=True,
                    dangerously_auto_approve_everything=True
                )
                
                print(f"     Executing codex agent...")
                result = run.execute(log_dir=test_dir)
                attempt_time = time.time() - attempt_start_time
                
                print(f"   ⏱️  Agent execution completed in {attempt_time:.1f}s")
                
                # Step 2: Check if file was created
                test.file_created = os.path.exists(file_path)
                print(f"     File Creation: {'✅ PASS' if test.file_created else '❌ FAIL'} - {test.filename}")
                
                if not test.file_created:
                    print(f"      Attempt {attempt} failed: File not created")
                    if attempt == max_attempts:
                        test.error_message = f"File {test.filename} was not created after {max_attempts} attempts"
                    continue
                
                # Step 3: Load the module and check if function exists
                try:
                    spec = importlib.util.spec_from_file_location("test_module", file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    test.function_exists = hasattr(module, test.function_name)
                    print(f"     Function Exists: {'✅ PASS' if test.function_exists else '❌ FAIL'} - {test.function_name}()")
                    
                    if not test.function_exists:
                        print(f"      Attempt {attempt} failed: Function not found")
                        if attempt == max_attempts:
                            test.error_message = f"Function {test.function_name} not found in {test.filename} after {max_attempts} attempts"
                        continue
                    
                    # Step 4: Test input/output correctness and functionality
                    func = getattr(module, test.function_name)
                    all_tests_passed = True
                    test_results = []
                    
                    for i, (inputs, expected) in enumerate(test.test_cases):
                        try:
                            if len(inputs) == 1:
                                actual = func(inputs[0])
                            else:
                                actual = func(*inputs)
                            
                            passed = abs(actual - expected) < 1e-10 if isinstance(expected, float) else actual == expected
                            test_results.append(passed)
                            
                            status = "✅ PASS" if passed else "❌ FAIL"
                            print(f"      Test {i+1}: {test.function_name}{inputs} = {actual} (expected {expected}) {status}")
                            
                            if not passed:
                                all_tests_passed = False
                                
                        except Exception as e:
                            test_results.append(False)
                            all_tests_passed = False
                            print(f"      Test {i+1}: {test.function_name}{inputs} = ERROR: {str(e)} ❌ FAIL")
                    
                    test.input_output_correct = all_tests_passed
                    test.functionality_works = all_tests_passed
                    
                    print(f"     Input/Output: {'✅ PASS' if test.input_output_correct else '❌ FAIL'} - {sum(test_results)}/{len(test_results)} tests passed")
                    print(f"   ✅ Functionality: {'✅ PASS' if test.functionality_works else '❌ FAIL'} - Overall function works correctly")
                    
                    if all_tests_passed:
                        test.execution_time = time.time() - overall_start_time
                        test.attempts_used = attempt
                        print(f"     SUCCESS on attempt {attempt}! Total time: {test.execution_time:.1f}s")
                        return test
                    else:
                        print(f"      Attempt {attempt} failed: Function tests failed")
                        if attempt == max_attempts:
                            test.error_message = f"Function tests failed after {max_attempts} attempts"
                    
                except Exception as e:
                    print(f"   ❌ Module Error on attempt {attempt}: {str(e)}")
                    if attempt == max_attempts:
                        test.error_message = f"Error loading/testing module after {max_attempts} attempts: {str(e)}"
                    
            except Exception as e:
                print(f"   ❌ Agent Error on attempt {attempt}: {str(e)}")
                if attempt == max_attempts:
                    test.error_message = f"Agent execution error after {max_attempts} attempts: {str(e)}"
        
        # If we get here, all attempts failed
        test.execution_time = time.time() - overall_start_time
        test.attempts_used = max_attempts
        print(f"   💥 All {max_attempts} attempts failed. Total time: {test.execution_time:.1f}s")
        return test

    def run_multi_turn_test(self, test, test_dir, max_attempts=3):
        """Run a multi-turn test that requires multiple prompts to complete"""
        print(f"\n  Running Multi-Turn Test: {test.name}")
        print(f"  Turns: {len(test.prompts)} prompts")
        print(f"  Target: {test.filename} -> {test.function_name}()")
        print(f"  Max Attempts: {max_attempts}")
        print("=" * 60)
        
        overall_start_time = time.time()
        
        for attempt in range(1, max_attempts + 1):
            print(f"\n  Attempt {attempt}/{max_attempts}:")
            
            # Clean up any previous attempt files
            file_path = os.path.join(test_dir, test.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"   🧹 Cleaned up previous attempt file")
            
            attempt_start_time = time.time()
            
            try:
                # Create a multi-turn session
                session = CodexSession(
                    session_id=f"multi_turn_test_{attempt}",
                    default_model=self.model,
                    default_provider=self.provider,
                    default_timeout=self.timeout,
                    debug=self.debug
                )
                
                # Execute all prompts in sequence
                print(f"     Executing multi-turn session with {len(test.prompts)} prompts...")
                
                for turn_num, prompt in enumerate(test.prompts, 1):
                    print(f"      Turn {turn_num}/{len(test.prompts)}: Sending prompt...")
                    session.add_run(
                        prompt=prompt,
                        writable_root=test_dir,
                        dangerously_auto_approve_everything=True
                    )
                
                # Execute the entire session
                session_result = session.execute_all()
                attempt_time = time.time() - attempt_start_time
                test.turns_completed = len(test.prompts)
                
                print(f"   ⏱️  Multi-turn session completed in {attempt_time:.1f}s")
                print(f"     Turns completed: {test.turns_completed}/{len(test.prompts)}")
                
                # Step 2: Check if file was created
                test.file_created = os.path.exists(file_path)
                print(f"     File Creation: {'✅ PASS' if test.file_created else '❌ FAIL'} - {test.filename}")
                
                if not test.file_created:
                    print(f"      Attempt {attempt} failed: File not created")
                    if attempt == max_attempts:
                        test.error_message = f"File {test.filename} was not created after {max_attempts} attempts"
                    continue
                
                # Step 3: Load the module and check if function exists
                try:
                    spec = importlib.util.spec_from_file_location("test_module", file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    test.function_exists = hasattr(module, test.function_name)
                    print(f"     Function Exists: {'✅ PASS' if test.function_exists else '❌ FAIL'} - {test.function_name}()")
                    
                    if not test.function_exists:
                        print(f"      Attempt {attempt} failed: Function not found")
                        if attempt == max_attempts:
                            test.error_message = f"Function {test.function_name} not found in {test.filename} after {max_attempts} attempts"
                        continue
                    
                    # Step 4: Test input/output correctness and functionality
                    func = getattr(module, test.function_name)
                    all_tests_passed = True
                    test_results = []
                    
                    for i, (inputs, expected) in enumerate(test.test_cases):
                        try:
                            if len(inputs) == 1:
                                actual = func(inputs[0])
                            else:
                                actual = func(*inputs)
                            
                            passed = actual == expected
                            test_results.append(passed)
                            
                            status = "✅ PASS" if passed else "❌ FAIL"
                            print(f"      Test {i+1}: {test.function_name}{inputs} = {actual} (expected {expected}) {status}")
                            
                            if not passed:
                                all_tests_passed = False
                                
                        except Exception as e:
                            test_results.append(False)
                            all_tests_passed = False
                            print(f"      Test {i+1}: {test.function_name}{inputs} = ERROR: {str(e)} ❌ FAIL")
                    
                    test.input_output_correct = all_tests_passed
                    test.functionality_works = all_tests_passed
                    
                    print(f"     Input/Output: {'✅ PASS' if test.input_output_correct else '❌ FAIL'} - {sum(test_results)}/{len(test_results)} tests passed")
                    print(f"   ✅ Functionality: {'✅ PASS' if test.functionality_works else '❌ FAIL'} - Overall function works correctly")
                    
                    if all_tests_passed:
                        test.execution_time = time.time() - overall_start_time
                        test.attempts_used = attempt
                        print(f"     MULTI-TURN SUCCESS on attempt {attempt}! Total time: {test.execution_time:.1f}s")
                        return test
                    else:
                        print(f"      Attempt {attempt} failed: Function tests failed")
                        if attempt == max_attempts:
                            test.error_message = f"Function tests failed after {max_attempts} attempts"
                    
                except Exception as e:
                    print(f"   ❌ Module Error on attempt {attempt}: {str(e)}")
                    if attempt == max_attempts:
                        test.error_message = f"Error loading/testing module after {max_attempts} attempts: {str(e)}"
                    
            except Exception as e:
                print(f"   ❌ Session Error on attempt {attempt}: {str(e)}")
                if attempt == max_attempts:
                    test.error_message = f"Multi-turn session error after {max_attempts} attempts: {str(e)}"
        
        # If we get here, all attempts failed
        test.execution_time = time.time() - overall_start_time
        test.attempts_used = max_attempts
        print(f"   💥 All {max_attempts} attempts failed. Total time: {test.execution_time:.1f}s")
        return test
    
    def run_all_tests(self):
        """Run all functional validation tests including multi-turn tests"""
        print("  FUNCTIONAL VALIDATION TEST SUITE")
        print("=" * 60)
        print("Testing whether codex agents can create working code that passes benchmarks")
        print()
        print("Measuring:")
        print("    File Creation - Did the agent create the specified file?")
        print("    Function Implementation - Does the function exist with correct name?")
        print("    Input/Output Correctness - Does it handle specified inputs/outputs?")
        print("  ✅ Functionality - Does it actually work and pass unit tests?")
        print("    Retry Logic - Up to 3 attempts per test")
        print("    Multi-turn Capability - Can it handle follow-up prompts?")
        print()
        
        # Run single-turn tests
        print("  SINGLE-TURN TESTS")
        print("=" * 60)
        tests = self.create_test_suite()
        
        for i, test in enumerate(tests, 1):
            # Create fresh test directory for each test
            test_dir = f"/tmp/codex_functional_test_{i}"
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
            os.makedirs(test_dir, exist_ok=True)
            
            try:
                completed_test = self.run_single_test(test, test_dir, max_attempts=3)
                self.results.append(completed_test)
                
                print(f"\n  Test {i} Summary:")
                print(f"     File Created: {'✅' if completed_test.file_created else '❌'}")
                print(f"     Function Exists: {'✅' if completed_test.function_exists else '❌'}")
                print(f"     I/O Correct: {'✅' if completed_test.input_output_correct else '❌'}")
                print(f"   ✅ Functionality: {'✅' if completed_test.functionality_works else '❌'}")
                print(f"     Attempts Used: {completed_test.attempts_used}/3")
                print(f"   ⏱️  Time: {completed_test.execution_time:.1f}s")
                if completed_test.error_message:
                    print(f"   ❌ Error: {completed_test.error_message}")
                
            except Exception as e:
                print(f"❌ Test {i} failed with exception: {str(e)}")
                traceback.print_exc()
            
            print("\n" + "="*60)
        
        # Run multi-turn tests
        print("\n  MULTI-TURN TESTS")
        print("=" * 60)
        multi_turn_tests = self.create_multi_turn_test_suite()
        
        for i, test in enumerate(multi_turn_tests, 1):
            # Create fresh test directory for each test
            test_dir = f"/tmp/codex_multi_turn_test_{i}"
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
            os.makedirs(test_dir, exist_ok=True)
            
            try:
                completed_test = self.run_multi_turn_test(test, test_dir, max_attempts=3)
                self.multi_turn_results.append(completed_test)
                
                print(f"\n  Multi-Turn Test {i} Summary:")
                print(f"     File Created: {'✅' if completed_test.file_created else '❌'}")
                print(f"     Function Exists: {'✅' if completed_test.function_exists else '❌'}")
                print(f"     I/O Correct: {'✅' if completed_test.input_output_correct else '❌'}")
                print(f"   ✅ Functionality: {'✅' if completed_test.functionality_works else '❌'}")
                print(f"     Turns Completed: {completed_test.turns_completed}/{len(test.prompts)}")
                print(f"     Attempts Used: {completed_test.attempts_used}/3")
                print(f"   ⏱️  Time: {completed_test.execution_time:.1f}s")
                if completed_test.error_message:
                    print(f"   ❌ Error: {completed_test.error_message}")
                
            except Exception as e:
                print(f"❌ Multi-Turn Test {i} failed with exception: {str(e)}")
                traceback.print_exc()
            
            print("\n" + "="*60)
        
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive test results summary"""
        print("\n  FUNCTIONAL VALIDATION SUMMARY")
        print("=" * 60)
        
        # Single-turn results
        total_tests = len(self.results)
        if total_tests > 0:
            print("  SINGLE-TURN RESULTS:")
            files_created = sum(1 for t in self.results if t.file_created)
            functions_exist = sum(1 for t in self.results if t.function_exists)
            io_correct = sum(1 for t in self.results if t.input_output_correct)
            functionality_works = sum(1 for t in self.results if t.functionality_works)
            
            avg_time = sum(t.execution_time for t in self.results) / total_tests
            avg_attempts = sum(t.attempts_used for t in self.results) / total_tests
            
            print(f"     File Creation: {files_created}/{total_tests} ({files_created/total_tests*100:.1f}%)")
            print(f"     Function Implementation: {functions_exist}/{total_tests} ({functions_exist/total_tests*100:.1f}%)")
            print(f"     Input/Output Correctness: {io_correct}/{total_tests} ({io_correct/total_tests*100:.1f}%)")
            print(f"   ✅ Full Functionality: {functionality_works}/{total_tests} ({functionality_works/total_tests*100:.1f}%)")
            print(f"   ⏱️  Average Execution Time: {avg_time:.1f}s")
            print(f"     Average Attempts Used: {avg_attempts:.1f}/3")
            
            complete_success = sum(1 for t in self.results if all([
                t.file_created, t.function_exists, t.input_output_correct, t.functionality_works
            ]))
            print(f"     Single-Turn Success Rate: {complete_success}/{total_tests} ({complete_success/total_tests*100:.1f}%)")
        
        # Multi-turn results
        total_multi_turn = len(self.multi_turn_results)
        if total_multi_turn > 0:
            print(f"\n  MULTI-TURN RESULTS:")
            mt_files_created = sum(1 for t in self.multi_turn_results if t.file_created)
            mt_functions_exist = sum(1 for t in self.multi_turn_results if t.function_exists)
            mt_io_correct = sum(1 for t in self.multi_turn_results if t.input_output_correct)
            mt_functionality_works = sum(1 for t in self.multi_turn_results if t.functionality_works)
            
            mt_avg_time = sum(t.execution_time for t in self.multi_turn_results) / total_multi_turn
            mt_avg_attempts = sum(t.attempts_used for t in self.multi_turn_results) / total_multi_turn
            mt_avg_turns = sum(t.turns_completed for t in self.multi_turn_results) / total_multi_turn
            
            print(f"     File Creation: {mt_files_created}/{total_multi_turn} ({mt_files_created/total_multi_turn*100:.1f}%)")
            print(f"     Function Implementation: {mt_functions_exist}/{total_multi_turn} ({mt_functions_exist/total_multi_turn*100:.1f}%)")
            print(f"     Input/Output Correctness: {mt_io_correct}/{total_multi_turn} ({mt_io_correct/total_multi_turn*100:.1f}%)")
            print(f"   ✅ Full Functionality: {mt_functionality_works}/{total_multi_turn} ({mt_functionality_works/total_multi_turn*100:.1f}%)")
            print(f"   ⏱️  Average Execution Time: {mt_avg_time:.1f}s")
            print(f"     Average Attempts Used: {mt_avg_attempts:.1f}/3")
            print(f"     Average Turns Completed: {mt_avg_turns:.1f}")
            
            mt_complete_success = sum(1 for t in self.multi_turn_results if all([
                t.file_created, t.function_exists, t.input_output_correct, t.functionality_works
            ]))
            print(f"     Multi-Turn Success Rate: {mt_complete_success}/{total_multi_turn} ({mt_complete_success/total_multi_turn*100:.1f}%)")
        
        # Overall summary
        if total_tests > 0 and total_multi_turn > 0:
            overall_total = total_tests + total_multi_turn
            overall_success = (complete_success if total_tests > 0 else 0) + (mt_complete_success if total_multi_turn > 0 else 0)
            
            print(f"\n  OVERALL SUCCESS RATE: {overall_success}/{overall_total} ({overall_success/overall_total*100:.1f}%)")
            
            if overall_success == overall_total:
                print("  PERFECT SCORE! All tests passed completely!")
            elif overall_success >= overall_total * 0.8:
                print("✅ EXCELLENT! Most tests passed successfully!")
            elif overall_success >= overall_total * 0.6:
                print("👍 GOOD! Majority of tests passed!")
            else:
                print("   NEEDS IMPROVEMENT! Many tests failed!")

if __name__ == '__main__':
    print("  Starting Functional Validation Test Suite...")
    
    validator = FunctionalValidator(
        model='codex-mini-latest',
        provider='openai',
        timeout=90
    )
    
    validator.run_all_tests()
    
    print("\n🏁 Functional validation testing complete!") 