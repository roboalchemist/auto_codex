#!/usr/bin/env python3
"""Main entry point for the auto_codex.benchmarks package"""

import argparse
import sys
from .base_benchmark import BaseBenchmark
from .leetcode_easy_benchmark import LeetCodeEasyBenchmark

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", choices=["easy"], default="easy")
    args = parser.parse_args()
    print("Running benchmark...")
    benchmark = LeetCodeEasyBenchmark()
    benchmark.run_all_tests()

if __name__ == "__main__":
    main()
