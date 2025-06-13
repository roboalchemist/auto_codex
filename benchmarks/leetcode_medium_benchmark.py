#!/usr/bin/env python3
"""
LeetCode Medium Benchmark for Auto-Codex
Tests whether agents can solve 10 intermediate-level LeetCode problems

This benchmark tests agents on popular medium-level LeetCode problems covering
various algorithmic concepts like two-pointers, sliding window, linked lists,
hash maps, arrays, matrices, binary search, and tree traversal.
"""

from .base_benchmark import BaseBenchmark, BenchmarkTest, run_benchmark_cli


class LeetCodeMediumBenchmark(BaseBenchmark):
    """LeetCode Medium problems benchmark"""
    
    def __init__(self, models=None, timeout=300):
        super().__init__("LeetCode Medium", models, timeout)
    
    def get_benchmark_prompt(self) -> str:
        """Get the LeetCode Medium benchmark environment prompt"""
        return """You are being tested on your ability to solve intermediate-level LeetCode problems. 
You will be given a series of coding challenges that test advanced programming concepts and algorithms.

Your task is to:
1. Create a Python file with the specified filename
2. Implement the required function with the exact name specified
3. Ensure your solution handles all the given test cases correctly
4. Write efficient algorithms that solve the problem optimally
5. Handle edge cases and complex scenarios

Each problem will specify the expected filename and function name. Make sure to follow these exactly.
Some problems may require helper classes like ListNode or TreeNode - implement these as needed."""
    
    def compare_results(self, actual, expected):
        """Custom comparison for medium problems that may have multiple valid solutions"""
        if isinstance(expected, list) and isinstance(actual, list):
            # For problems like 3Sum where order doesn't matter
            if all(isinstance(x, list) for x in expected) and all(isinstance(x, list) for x in actual):
                # Sort both lists of lists for comparison
                expected_sorted = [sorted(x) for x in expected]
                actual_sorted = [sorted(x) for x in actual]
                expected_sorted.sort()
                actual_sorted.sort()
                return expected_sorted == actual_sorted
        return actual == expected
    
    def create_test_suite(self):
        """Create 10 medium LeetCode problems"""
        return [
            BenchmarkTest(
                name="3Sum",
                problem_id="15",
                task_description="""Create a Python file called 'three_sum.py' with a function named 'threeSum' that solves LeetCode Problem #15.

Problem: Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0. Notice that the solution set must not contain duplicate triplets.

Example:
- Input: nums = [-1,0,1,2,-1,-4]
- Output: [[-1,-1,2],[-1,0,1]]

Algorithm hint: Sort the array first, then use two pointers to find triplets.""",
                filename="three_sum.py",
                function_name="threeSum",
                test_cases=[
                    (([-1, 0, 1, 2, -1, -4],), [[-1, -1, 2], [-1, 0, 1]]),
                    (([0, 1, 1],), []),
                    (([0, 0, 0],), [[0, 0, 0]]),
                    (([-2, 0, 1, 1, 2],), [[-2, 0, 2], [-2, 1, 1]])
                ]
            ),
            
            BenchmarkTest(
                name="Longest Substring Without Repeating Characters",
                problem_id="3",
                task_description="""Create a Python file called 'longest_substring.py' with a function named 'lengthOfLongestSubstring' that solves LeetCode Problem #3.

Problem: Given a string s, find the length of the longest substring without repeating characters.

Example:
- Input: s = "abcabcbb"
- Output: 3 (substring "abc")
- Input: s = "bbbbb"
- Output: 1 (substring "b")

Algorithm hint: Use sliding window technique with a hash map.""",
                filename="longest_substring.py",
                function_name="lengthOfLongestSubstring",
                test_cases=[
                    (("abcabcbb",), 3),
                    (("bbbbb",), 1),
                    (("pwwkew",), 3),
                    (("",), 0),
                    (("dvdf",), 3)
                ]
            ),
            
            BenchmarkTest(
                name="Add Two Numbers",
                problem_id="2",
                task_description="""Create a Python file called 'add_two_numbers.py' with a function named 'addTwoNumbers' that solves LeetCode Problem #2.

Problem: You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.

For this implementation, represent linked lists as Python lists where [2,4,3] represents 342.
Your function should take two lists and return a list representing the sum.

Example:
- Input: l1 = [2,4,3], l2 = [5,6,4]
- Output: [7,0,8] (342 + 465 = 807)""",
                filename="add_two_numbers.py",
                function_name="addTwoNumbers",
                test_cases=[
                    (([2, 4, 3], [5, 6, 4]), [7, 0, 8]),
                    (([0], [0]), [0]),
                    (([9, 9, 9], [9, 9, 9, 9]), [8, 9, 9, 0, 1])
                ]
            ),
            
            BenchmarkTest(
                name="Group Anagrams",
                problem_id="49",
                task_description="""Create a Python file called 'group_anagrams.py' with a function named 'groupAnagrams' that solves LeetCode Problem #49.

Problem: Given an array of strings strs, group the anagrams together. You can return the answer in any order.

Example:
- Input: strs = ["eat","tea","tan","ate","nat","bat"]
- Output: [["bat"],["nat","tan"],["ate","eat","tea"]]

Algorithm hint: Use sorted strings as keys in a hash map.""",
                filename="group_anagrams.py",
                function_name="groupAnagrams",
                test_cases=[
                    ((["eat", "tea", "tan", "ate", "nat", "bat"],), [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]),
                    (([""],), [[""]]),
                    ((["a"],), [["a"]])
                ]
            ),
            
            BenchmarkTest(
                name="Product of Array Except Self",
                problem_id="238",
                task_description="""Create a Python file called 'product_except_self.py' with a function named 'productExceptSelf' that solves LeetCode Problem #238.

Problem: Given an integer array nums, return an array answer such that answer[i] is equal to the product of all the elements of nums except nums[i]. You must write an algorithm that runs in O(n) time and without using the division operation.

Example:
- Input: nums = [1,2,3,4]
- Output: [24,12,8,6]

Algorithm hint: Use two passes - first for left products, then multiply by right products.""",
                filename="product_except_self.py",
                function_name="productExceptSelf",
                test_cases=[
                    (([1, 2, 3, 4],), [24, 12, 8, 6]),
                    (([-1, 1, 0, -3, 3],), [0, 0, 9, 0, 0]),
                    (([2, 3, 4, 5],), [60, 40, 30, 24])
                ]
            ),
            
            BenchmarkTest(
                name="Container With Most Water",
                problem_id="11",
                task_description="""Create a Python file called 'container_water.py' with a function named 'maxArea' that solves LeetCode Problem #11.

Problem: You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]). Find two lines that together with the x-axis form a container that contains the most water.

Example:
- Input: height = [1,8,6,2,5,4,8,3,7]
- Output: 49

Algorithm hint: Use two pointers from both ends.""",
                filename="container_water.py",
                function_name="maxArea",
                test_cases=[
                    (([1, 8, 6, 2, 5, 4, 8, 3, 7],), 49),
                    (([1, 1],), 1),
                    (([4, 3, 2, 1, 4],), 16),
                    (([1, 2, 1],), 2)
                ]
            ),
            
            BenchmarkTest(
                name="Rotate Image",
                problem_id="48",
                task_description="""Create a Python file called 'rotate_image.py' with a function named 'rotate' that solves LeetCode Problem #48.

Problem: You are given an n x n 2D matrix representing an image, rotate the image by 90 degrees (clockwise). You have to rotate the image in-place.

Example:
- Input: matrix = [[1,2,3],[4,5,6],[7,8,9]]
- Output: [[7,4,1],[8,5,2],[9,6,3]]

Algorithm hint: Transpose the matrix, then reverse each row.""",
                filename="rotate_image.py",
                function_name="rotate",
                test_cases=[
                    (([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [[7, 4, 1], [8, 5, 2], [9, 6, 3]]),
                    (([[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]],), 
                     [[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]]),
                    (([[1]],), [[1]])
                ]
            ),
            
            BenchmarkTest(
                name="Spiral Matrix",
                problem_id="54",
                task_description="""Create a Python file called 'spiral_matrix.py' with a function named 'spiralOrder' that solves LeetCode Problem #54.

Problem: Given an m x n matrix, return all elements of the matrix in spiral order.

Example:
- Input: matrix = [[1,2,3],[4,5,6],[7,8,9]]
- Output: [1,2,3,6,9,8,7,4,5]

Algorithm hint: Use four boundaries (top, bottom, left, right) and move in spiral.""",
                filename="spiral_matrix.py",
                function_name="spiralOrder",
                test_cases=[
                    (([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [1, 2, 3, 6, 9, 8, 7, 4, 5]),
                    (([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],), [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]),
                    (([[1]],), [1])
                ]
            ),
            
            BenchmarkTest(
                name="Search in Rotated Sorted Array",
                problem_id="33",
                task_description="""Create a Python file called 'search_rotated.py' with a function named 'search' that solves LeetCode Problem #33.

Problem: There is an integer array nums sorted in ascending order (with distinct values). Prior to being passed to your function, nums is possibly rotated at an unknown pivot index. Given the array nums after the possible rotation and an integer target, return the index of target if it is in nums, or -1 if it is not in nums. You must write an algorithm with O(log n) runtime complexity.

Example:
- Input: nums = [4,5,6,7,0,1,2], target = 0
- Output: 4

Algorithm hint: Use modified binary search to handle rotation.""",
                filename="search_rotated.py",
                function_name="search",
                test_cases=[
                    (([4, 5, 6, 7, 0, 1, 2], 0), 4),
                    (([4, 5, 6, 7, 0, 1, 2], 3), -1),
                    (([1], 0), -1),
                    (([1], 1), 0),
                    (([1, 3], 3), 1)
                ]
            ),
            
            BenchmarkTest(
                name="Validate Binary Search Tree",
                problem_id="98",
                task_description="""Create a Python file called 'validate_bst.py' with a function named 'isValidBST' that solves LeetCode Problem #98.

Problem: Given the root of a binary tree, determine if it is a valid binary search tree (BST).

For this implementation, represent the tree as a nested list where None represents null nodes.
Example: [2,1,3] represents a tree with root 2, left child 1, right child 3.

Example:
- Input: root = [2,1,3]
- Output: True
- Input: root = [5,1,4,null,null,3,6]
- Output: False

Algorithm hint: Use in-order traversal or bounds checking.""",
                filename="validate_bst.py",
                function_name="isValidBST",
                test_cases=[
                    (([2, 1, 3],), True),
                    (([5, 1, 4, None, None, 3, 6],), False),
                    (([1],), True),
                    (([1, 1],), False),
                    (([10, 5, 15, None, None, 6, 20],), False)
                ]
            )
        ]


if __name__ == "__main__":
    run_benchmark_cli(LeetCodeMediumBenchmark, "LeetCode Medium") 