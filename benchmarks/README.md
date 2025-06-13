# Auto-Codex Benchmarks

This directory contains benchmark implementations for evaluating coding agents on various programming tasks and challenges.

## Available Benchmarks

### 1. LeetCode Easy Benchmark (`leetcode_easy_benchmark.py`)

Tests coding agents on 10 beginner-level LeetCode problems to evaluate basic programming capabilities.

**Problems Included:**
- Two Sum (#1)
- Valid Parentheses (#20) 
- Maximum Subarray (#53)
- Best Time to Buy and Sell Stock (#121)
- Remove Duplicates from Sorted Array (#26)
- Climbing Stairs (#70)
- Plus One (#66)
- Palindrome Number (#9)
- Reverse Linked List (#206)
- Merge Two Sorted Lists (#21)

### 2. LeetCode Medium Benchmark (`leetcode_medium_benchmark.py`)

Tests coding agents on 10 intermediate-level LeetCode problems to evaluate advanced programming skills.

**Problems Included:**
- 3Sum (#15)
- Longest Substring Without Repeating Characters (#3)
- Add Two Numbers (#2)
- Group Anagrams (#49)
- Product of Array Except Self (#238)
- Container With Most Water (#11)
- Rotate Image (#48)
- Spiral Matrix (#54)
- Search in Rotated Sorted Array (#33)
- Validate Binary Search Tree (#98)

### 3. Reference Solutions (`leetcode_medium_solutions/`)

Contains optimal reference implementations for all medium-level problems with:
- Comprehensive documentation
- Time/space complexity analysis
- Test cases with helper functions
- 100% validated correctness

## Usage

### Command Line Interface

Both benchmarks support the same command-line interface:

```bash
# Single model with default timeout (300s)
python leetcode_easy_benchmark.py

# Multiple models with custom timeout
python leetcode_easy_benchmark.py --models codex-mini-latest gpt-4.1 gpt-4.1-mini gpt-4.1-nano --timeout 300

# Medium benchmark
python leetcode_medium_benchmark.py --models codex-mini-latest gpt-4.1 --timeout 600

# Help
python leetcode_easy_benchmark.py --help
```

### Programmatic Usage

You can also use the benchmarks programmatically:

```python
from auto_codex.benchmarks import EasyBenchmark, MediumBenchmark

# Easy benchmark
easy_bench = EasyBenchmark(
    models=['codex-mini-latest', 'gpt-4.1'],
    timeout=300
)
easy_bench.run_all_tests()

# Medium benchmark  
medium_bench = MediumBenchmark(
    models=['codex-mini-latest'],
    timeout=600
)
medium_bench.run_benchmark()
```

## Metrics Measured

Both benchmarks evaluate:
- **File Creation Success** - Did the agent create the specified file?
- **Function Implementation** - Does the function exist with correct name?
- **Input/Output Correctness** - Does it handle specified inputs/outputs?
- **Overall Functionality** - Does it work correctly?
- **Algorithm Correctness** - Does it solve the problem optimally?
- **Retry Logic** - Up to 3 attempts per problem

## Advanced Features (Medium Benchmark)

- Automatic ListNode/TreeNode class injection
- In-place modification support
- Unordered result comparison logic
- Enhanced algorithm correctness validation
- Complex data structure handling

## Output and Reporting

Both benchmarks provide:
- Real-time progress tracking with heartbeat monitoring
- Detailed per-test summaries
- Individual model performance reports
- Multi-model comparative analysis
- Success rate, timing, and retry statistics

## Requirements

- Python 3.7+
- auto_codex library
- Access to configured AI models (OpenAI, etc.)
- Sufficient timeout allowances for complex problems

## Running from Package Root

From the auto_codex package root:

```bash
cd benchmarks
python leetcode_easy_benchmark.py --models codex-mini-latest --timeout 300
python leetcode_medium_benchmark.py --models codex-mini-latest --timeout 600
```

## Contributing

When adding new benchmarks:
1. Follow the established benchmark pattern
2. Include comprehensive documentation
3. Add reference solutions when applicable
4. Update this README with new benchmarks
5. Ensure command-line compatibility
6. Add appropriate test coverage 