#!/usr/bin/env python3
"""
Generic Benchmark Framework for Auto-Codex

Provides a base framework for creating coding benchmarks that can be extended
for different types of challenges (LeetCode, HackerRank, custom problems, etc.)
"""

import os
import sys
import importlib.util
import tempfile
import shutil
import traceback
import time
import argparse
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
from auto_codex.core import CodexRun
from dotenv import load_dotenv


class BenchmarkTest:
    """Generic test case for any coding benchmark"""
    
    def __init__(self, 
                 name: str,
                 problem_id: str,
                 task_description: str,
                 filename: str,
                 function_name: str,
                 test_cases: List[Tuple],
                 helper_statement: str = None):
        """
        Initialize a benchmark test case.
        
        Args:
            name: Human-readable name of the problem
            problem_id: Unique identifier for the problem
            task_description: Full description of the task
            filename: Expected output filename
            function_name: Expected function name to implement
            test_cases: List of (inputs, expected_output) tuples
            helper_statement: Environmental hints for the agent
        """
        self.name = name
        self.problem_id = problem_id
        self.task_description = task_description
        self.filename = filename
        self.function_name = function_name
        self.test_cases = test_cases
        self.helper_statement = helper_statement or "The apply_patch method with 'Add File' syntax works reliably in sandboxed environments for creating new files."
        
        # Results tracking
        self.file_created = False
        self.function_exists = False
        self.input_output_correct = False
        self.functionality_works = False
        self.execution_time = 0
        self.error_message = None
        self.attempts_used = 0


class BaseBenchmark(ABC):
    """Abstract base class for coding benchmarks"""
    
    def __init__(self, 
                 benchmark_name: str,
                 models: Optional[List[str]] = None, 
                 timeout: int = 300):
        """
        Initialize the benchmark.
        
        Args:
            benchmark_name: Name of this benchmark
            models: List of model names to test
            timeout: Timeout in seconds for each test
        """
        self.benchmark_name = benchmark_name
        self.models = models or ['gpt-4.1-mini']
        self.timeout = timeout
        self.debug = True
        self.all_results = {}
    
    @abstractmethod
    def create_test_suite(self) -> List[BenchmarkTest]:
        """Create the test suite for this benchmark"""
        pass
    
    @abstractmethod
    def get_benchmark_prompt(self) -> str:
        """Get the initial prompt that describes the benchmark environment"""
        pass
    
    def run_single_test(self, 
                       test: BenchmarkTest, 
                       test_dir: str, 
                       model: str, 
                       provider: str = 'openai', 
                       max_attempts: int = 3) -> BenchmarkTest:
        """
        Run a single test case.
        
        Args:
            test: The test case to run
            test_dir: Directory to run the test in
            model: Model name to use
            provider: AI provider to use
            max_attempts: Maximum number of attempts
            
        Returns:
            Updated test object with results
        """
        if self.debug:
            print(f"\n{'='*60}")
            print(f"Running Test: {test.name} (Problem {test.problem_id})")
            print(f"Model: {model}")
            print(f"{'='*60}")
        
        start_time = time.time()
        
        # Construct full prompt
        full_prompt = f"{self.get_benchmark_prompt()}\n\n{test.task_description}\n\nHINT: {test.helper_statement}"
        
        for attempt in range(max_attempts):
            test.attempts_used = attempt + 1
            
            if self.debug:
                print(f"\nAttempt {attempt + 1}/{max_attempts}")
            
            try:
                # Create CodexRun
                run = CodexRun(
                    prompt=full_prompt,
                    model=model,
                    provider=provider,
                    writable_root=test_dir,
                    timeout=self.timeout,
                    debug=self.debug
                )
                
                # Execute the run
                result = run.execute()
                
                if self.debug:
                    print(f"Run completed. Success: {result.success}")
                
                # Test the implementation
                if self.test_implementation(test, test_dir):
                    break
                    
            except Exception as e:
                test.error_message = str(e)
                if self.debug:
                    print(f"Error in attempt {attempt + 1}: {e}")
                    traceback.print_exc()
        
        test.execution_time = time.time() - start_time
        
        if self.debug:
            self.print_test_results(test)
        
        return test
    
    def test_implementation(self, test: BenchmarkTest, test_dir: str) -> bool:
        """
        Test if the implementation works correctly.
        
        Args:
            test: The test case
            test_dir: Directory containing the implementation
            
        Returns:
            True if all tests pass, False otherwise
        """
        file_path = os.path.join(test_dir, test.filename)
        
        # Check if file was created
        test.file_created = os.path.exists(file_path)
        if not test.file_created:
            test.error_message = f"File {test.filename} was not created"
            return False
        
        # Check function implementation
        if not self.test_function_implementation(test, file_path):
            return False
        
        # Test functionality
        return self.test_function_correctness(test, file_path)
    
    def test_function_implementation(self, test: BenchmarkTest, file_path: str) -> bool:
        """Test if the function exists and is callable"""
        try:
            spec = importlib.util.spec_from_file_location("test_module", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, test.function_name):
                func = getattr(module, test.function_name)
                if callable(func):
                    test.function_exists = True
                    return True
                else:
                    test.error_message = f"'{test.function_name}' exists but is not callable"
            else:
                test.error_message = f"Function '{test.function_name}' not found in {test.filename}"
            
        except Exception as e:
            test.error_message = f"Error importing {test.filename}: {str(e)}"
        
        return False
    
    def test_function_correctness(self, test: BenchmarkTest, file_path: str) -> bool:
        """Test if the function produces correct outputs"""
        try:
            spec = importlib.util.spec_from_file_location("test_module", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            func = getattr(module, test.function_name)
            
            # Test all test cases
            passed_tests = 0
            for inputs, expected in test.test_cases:
                try:
                    if isinstance(inputs, tuple):
                        result = func(*inputs)
                    else:
                        result = func(inputs)
                    
                    if self.compare_results(result, expected):
                        passed_tests += 1
                    else:
                        test.error_message = f"Test failed: input {inputs}, expected {expected}, got {result}"
                        break
                        
                except Exception as e:
                    test.error_message = f"Runtime error with input {inputs}: {str(e)}"
                    break
            
            if passed_tests == len(test.test_cases):
                test.input_output_correct = True
                test.functionality_works = True
                return True
            
        except Exception as e:
            test.error_message = f"Error testing function: {str(e)}"
        
        return False
    
    def compare_results(self, actual: Any, expected: Any) -> bool:
        """Compare actual and expected results (can be overridden for custom comparison)"""
        return actual == expected
    
    def run_all_tests(self) -> Dict[str, List[BenchmarkTest]]:
        """Run all tests for all models"""
        test_suite = self.create_test_suite()
        
        print(f"\n{'='*80}")
        print(f"{self.benchmark_name} Benchmark")
        print(f"Testing {len(test_suite)} problems with {len(self.models)} model(s)")
        print(f"{'='*80}")
        
        for model in self.models:
            print(f"\n🤖 Testing model: {model}")
            model_results = []
            
            for i, test in enumerate(test_suite, 1):
                print(f"\n📝 Test {i}/{len(test_suite)}: {test.name}")
                
                # Create temporary directory for this test
                with tempfile.TemporaryDirectory() as test_dir:
                    result = self.run_single_test(test, test_dir, model)
                    model_results.append(result)
            
            self.all_results[model] = model_results
            self.print_model_summary(model, model_results)
        
        self.print_comparative_summary()
        return self.all_results
    
    def print_test_results(self, test: BenchmarkTest):
        """Print results for a single test"""
        print(f"\nTest Results for {test.name}:")
        print(f"  ✅ File Created: {test.file_created}")
        print(f"  ✅ Function Exists: {test.function_exists}")
        print(f"  ✅ I/O Correct: {test.input_output_correct}")
        print(f"  ✅ Functionality: {test.functionality_works}")
        print(f"  ⏱️  Execution Time: {test.execution_time:.2f}s")
        print(f"  🔄 Attempts Used: {test.attempts_used}")
        if test.error_message:
            print(f"  ❌ Error: {test.error_message}")
    
    def print_model_summary(self, model: str, results: List[BenchmarkTest]):
        """Print summary for a single model"""
        total_tests = len(results)
        file_created = sum(1 for r in results if r.file_created)
        function_exists = sum(1 for r in results if r.function_exists)
        io_correct = sum(1 for r in results if r.input_output_correct)
        functionality = sum(1 for r in results if r.functionality_works)
        avg_time = sum(r.execution_time for r in results) / total_tests
        avg_attempts = sum(r.attempts_used for r in results) / total_tests
        
        print(f"\n📊 {model} Summary:")
        print(f"  File Creation: {file_created}/{total_tests} ({file_created/total_tests*100:.1f}%)")
        print(f"  Function Implementation: {function_exists}/{total_tests} ({function_exists/total_tests*100:.1f}%)")
        print(f"  I/O Correctness: {io_correct}/{total_tests} ({io_correct/total_tests*100:.1f}%)")
        print(f"  Full Functionality: {functionality}/{total_tests} ({functionality/total_tests*100:.1f}%)")
        print(f"  Average Time: {avg_time:.2f}s")
        print(f"  Average Attempts: {avg_attempts:.1f}")
    
    def print_comparative_summary(self):
        """Print comparative summary across all models"""
        if len(self.models) <= 1:
            return
        
        print(f"\n{'='*80}")
        print(f"Comparative Summary - {self.benchmark_name}")
        print(f"{'='*80}")
        
        print(f"{'Model':<20} {'Files':<8} {'Functions':<10} {'I/O':<8} {'Full':<8} {'Time':<8} {'Attempts':<8}")
        print("-" * 80)
        
        for model in self.models:
            results = self.all_results[model]
            total = len(results)
            files = sum(1 for r in results if r.file_created)
            funcs = sum(1 for r in results if r.function_exists)
            io = sum(1 for r in results if r.input_output_correct)
            full = sum(1 for r in results if r.functionality_works)
            avg_time = sum(r.execution_time for r in results) / total
            avg_attempts = sum(r.attempts_used for r in results) / total
            
            print(f"{model:<20} {files}/{total:<6} {funcs}/{total:<8} {io}/{total:<6} {full}/{total:<6} {avg_time:<6.1f}s {avg_attempts:<6.1f}")


def create_cli_parser(benchmark_name: str) -> argparse.ArgumentParser:
    """Create a generic CLI parser for benchmarks"""
    parser = argparse.ArgumentParser(description=f'{benchmark_name} Benchmark for Auto-Codex')
    parser.add_argument('--models', nargs='+', default=['gpt-4.1-mini'],
                        help='Models to test (default: gpt-4.1-mini)')
    parser.add_argument('--provider', default='openai',
                       help='AI provider to use (default: openai)')
    parser.add_argument('--timeout', type=int, default=300,
                       help='Timeout in seconds per test (default: 300)')
    parser.add_argument('--max-attempts', type=int, default=3,
                       help='Maximum attempts per test (default: 3)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    return parser


def run_benchmark_cli(benchmark_class, benchmark_name: str):
    """Generic CLI runner for benchmarks"""

    # Load environment variables from .env file
    if not load_dotenv():
        print("⚠️  Warning: .env file not found. Please create one with your API keys (e.g., OPENAI_API_KEY).")
    
    parser = create_cli_parser(benchmark_name)
    args = parser.parse_args()
    
    print(f"🚀 Starting {benchmark_name} Benchmark")
    print(f"Models: {args.models}")
    print(f"Provider: {args.provider}")
    print(f"Timeout: {args.timeout}s")
    print(f"Max Attempts: {args.max_attempts}")
    
    # Create and run benchmark
    benchmark = benchmark_class(
        models=args.models,
        timeout=args.timeout
    )
    benchmark.debug = args.debug
    
    try:
        results = benchmark.run_all_tests()
        print(f"\n✅ {benchmark_name} Benchmark completed successfully!")
        return results
    except KeyboardInterrupt:
        print(f"\n⚠️ {benchmark_name} Benchmark interrupted by user")
        return None
    except Exception as e:
        print(f"\n❌ {benchmark_name} Benchmark failed: {e}")
        if args.debug:
            traceback.print_exc()
        return None 