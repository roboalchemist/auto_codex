#!/usr/bin/env python3
"""
LeetCode Easy Benchmark for Auto-Codex
Tests whether agents can solve 10 beginner-level LeetCode problems

Based on: https://medium.com/@YagmurE/10-easy-leetcode-questions-every-beginner-should-try-1f6191e7f5f0
"""

from .base_benchmark import BaseBenchmark, BenchmarkTest, run_benchmark_cli


class LeetCodeEasyBenchmark(BaseBenchmark):
    """LeetCode Easy problems benchmark"""
    
    def __init__(self, models=None, timeout=300):
        super().__init__("LeetCode Easy", models, timeout)
    
    def get_benchmark_prompt(self) -> str:
        """Get the LeetCode Easy benchmark environment prompt"""
        return """You are being tested on your ability to solve beginner-level LeetCode problems. 
You will be given a series of coding challenges that test fundamental programming concepts.

Your task is to:
1. Create a Python file with the specified filename
2. Implement the required function with the exact name specified
3. Ensure your solution handles all the given test cases correctly
4. Write clean, efficient code that solves the problem

Each problem will specify the expected filename and function name. Make sure to follow these exactly."""
    
    def create_test_suite(self):
        """Create 10 easy LeetCode problems from the Medium article"""
        return [
            BenchmarkTest(
                name="Two Sum",
                problem_id="1",
                task_description="""Create a Python file called 'two_sum.py' with a function named 'two_sum' that solves LeetCode Problem #1.

Problem: Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.

Example:
- Input: nums = [2,7,11,15], target = 9
- Output: [0,1] (because nums[0] + nums[1] == 9)""",
                filename="two_sum.py",
                function_name="two_sum",
                test_cases=[
                    (([2, 7, 11, 15], 9), [0, 1]),
                    (([3, 2, 4], 6), [1, 2]),
                    (([3, 3], 6), [0, 1]),
                    (([1, 2, 3, 4, 5], 8), [2, 4]),
                    (([0, 4, 3, 0], 0), [0, 3])
                ]
            ),
            
            BenchmarkTest(
                name="Valid Parentheses",
                problem_id="20",
                task_description="""Create a Python file called 'valid_parentheses.py' with a function named 'is_valid' that solves LeetCode Problem #20.

Problem: Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid. An input string is valid if: Open brackets must be closed by the same type of brackets, open brackets must be closed in the correct order, and every close bracket has a corresponding open bracket of the same type.

Example:
- Input: s = "()"
- Output: True
- Input: s = "()[]{}"
- Output: True
- Input: s = "(]"
- Output: False""",
                filename="valid_parentheses.py",
                function_name="is_valid",
                test_cases=[
                    (("()",), True),
                    (("()[]{}", ), True),
                    (("(]",), False),
                    (("([)]",), False),
                    (("{[]}",), True),
                    (("",), True),
                    (("(((",), False)
                ]
            ),
            
            BenchmarkTest(
                name="Maximum Subarray",
                problem_id="53",
                task_description="""Create a Python file called 'max_subarray.py' with a function named 'max_sub_array' that solves LeetCode Problem #53.

Problem: Given an integer array nums, find the subarray with the largest sum, and return its sum.

Example:
- Input: nums = [-2,1,-3,4,-1,2,1,-5,4]
- Output: 6 (subarray [4,-1,2,1] has the largest sum = 6)""",
                filename="max_subarray.py",
                function_name="max_sub_array",
                test_cases=[
                    (([-2, 1, -3, 4, -1, 2, 1, -5, 4],), 6),
                    (([1],), 1),
                    (([5, 4, -1, 7, 8],), 23),
                    (([-1],), -1),
                    (([-2, -1],), -1)
                ]
            ),
            
            BenchmarkTest(
                name="Best Time to Buy and Sell Stock",
                problem_id="121",
                task_description="""Create a Python file called 'buy_sell_stock.py' with a function named 'max_profit' that solves LeetCode Problem #121.

Problem: You are given an array prices where prices[i] is the price of a given stock on the ith day. You want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock. Return the maximum profit you can achieve from this transaction. If you cannot achieve any profit, return 0.

Example:
- Input: prices = [7,1,5,3,6,4]
- Output: 5 (buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5)""",
                filename="buy_sell_stock.py",
                function_name="max_profit",
                test_cases=[
                    (([7, 1, 5, 3, 6, 4],), 5),
                    (([7, 6, 4, 3, 1],), 0),
                    (([1, 2, 3, 4, 5],), 4),
                    (([2, 4, 1],), 2),
                    (([3, 2, 6, 5, 0, 3],), 4)
                ]
            ),
            
            BenchmarkTest(
                name="Remove Duplicates from Sorted Array",
                problem_id="26",
                task_description="""Create a Python file called 'remove_duplicates.py' with a function named 'remove_duplicates' that solves LeetCode Problem #26.

Problem: Given an integer array nums sorted in non-decreasing order, remove the duplicates in-place such that each unique element appears only once. The relative order of the elements should be kept the same. Then return the number of unique elements in nums.

Example:
- Input: nums = [1,1,2]
- Output: 2 (nums becomes [1,2,_])""",
                filename="remove_duplicates.py",
                function_name="remove_duplicates",
                test_cases=[
                    (([1, 1, 2],), 2),
                    (([0, 0, 1, 1, 1, 2, 2, 3, 3, 4],), 5),
                    (([1],), 1),
                    (([1, 2],), 2),
                    (([1, 1, 1],), 1)
                ]
            ),
            
            BenchmarkTest(
                name="Climbing Stairs",
                problem_id="70",
                task_description="""Create a Python file called 'climbing_stairs.py' with a function named 'climb_stairs' that solves LeetCode Problem #70.

Problem: You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?

Example:
- Input: n = 2
- Output: 2 (1 step + 1 step OR 2 steps)
- Input: n = 3
- Output: 3 (1+1+1 OR 1+2 OR 2+1)""",
                filename="climbing_stairs.py",
                function_name="climb_stairs",
                test_cases=[
                    ((2,), 2),
                    ((3,), 3),
                    ((4,), 5),
                    ((5,), 8),
                    ((1,), 1)
                ]
            ),
            
            BenchmarkTest(
                name="Merge Two Sorted Lists",
                problem_id="21",
                task_description="""Create a Python file called 'merge_lists.py' with a function named 'merge_two_lists' that solves LeetCode Problem #21.

Problem: You are given the heads of two sorted linked lists list1 and list2. Merge the two lists into one sorted list. The list should be made by splicing together the nodes of the first two lists. Return the head of the merged linked list.

For this implementation, use a simple list representation where each "node" is represented as [value, next_node] or None for the end.

Example:
- Input: list1 = [1,2,4], list2 = [1,3,4]
- Output: [1,1,2,3,4,4]""",
                filename="merge_lists.py",
                function_name="merge_two_lists",
                test_cases=[
                    (([1, 2, 4], [1, 3, 4]), [1, 1, 2, 3, 4, 4]),
                    (([], []), []),
                    (([], [0]), [0]),
                    (([1], [2]), [1, 2]),
                    (([1, 3, 5], [2, 4, 6]), [1, 2, 3, 4, 5, 6])
                ]
            ),
            
            BenchmarkTest(
                name="Plus One",
                problem_id="66",
                task_description="""Create a Python file called 'plus_one.py' with a function named 'plus_one' that solves LeetCode Problem #66.

Problem: You are given a large integer represented as an integer array digits, where each digits[i] is the ith digit of the integer. The digits are ordered from most significant to least significant in left-to-right order. The large integer does not contain any leading zero. Increment the large integer by one and return the resulting array of digits.

Example:
- Input: digits = [1,2,3]
- Output: [1,2,4]
- Input: digits = [9]
- Output: [1,0]""",
                filename="plus_one.py",
                function_name="plus_one",
                test_cases=[
                    (([1, 2, 3],), [1, 2, 4]),
                    (([4, 3, 2, 1],), [4, 3, 2, 2]),
                    (([9],), [1, 0]),
                    (([9, 9],), [1, 0, 0]),
                    (([0],), [1])
                ]
            ),
            
            BenchmarkTest(
                name="Search Insert Position",
                problem_id="35",
                task_description="""Create a Python file called 'search_insert.py' with a function named 'search_insert' that solves LeetCode Problem #35.

Problem: Given a sorted array of distinct integers and a target value, return the index if the target is found. If not, return the index where it would be if it were inserted in order. You must write an algorithm with O(log n) runtime complexity.

Example:
- Input: nums = [1,3,5,6], target = 5
- Output: 2
- Input: nums = [1,3,5,6], target = 2
- Output: 1""",
                filename="search_insert.py",
                function_name="search_insert",
                test_cases=[
                    (([1, 3, 5, 6], 5), 2),
                    (([1, 3, 5, 6], 2), 1),
                    (([1, 3, 5, 6], 7), 4),
                    (([1, 3, 5, 6], 0), 0),
                    (([1], 1), 0)
                ]
            ),
            
            BenchmarkTest(
                name="Length of Last Word",
                problem_id="58",
                task_description="""Create a Python file called 'last_word_length.py' with a function named 'length_of_last_word' that solves LeetCode Problem #58.

Problem: Given a string s consisting of words and spaces, return the length of the last word in the string. A word is a maximal substring consisting of non-space characters only.

Example:
- Input: s = "Hello World"
- Output: 5 (length of "World")
- Input: s = "   fly me   to   the moon  "
- Output: 4 (length of "moon")""",
                filename="last_word_length.py",
                function_name="length_of_last_word",
                test_cases=[
                    (("Hello World",), 5),
                    (("   fly me   to   the moon  ",), 4),
                    (("luffy is still joyboy",), 6),
                    (("a",), 1),
                    (("day",), 3)
                ]
            )
        ]


if __name__ == "__main__":
    run_benchmark_cli(LeetCodeEasyBenchmark, "LeetCode Easy") 