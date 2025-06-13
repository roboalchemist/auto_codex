#!/usr/bin/env python3
"""
Test script to validate all LeetCode reference solutions
"""

import sys
import os

# Add the current directory to the path so we can import the solutions
sys.path.append(os.path.dirname(__file__))

from two_sum import two_sum
from valid_parentheses import is_valid
from max_subarray import max_sub_array
from buy_sell_stock import max_profit
from remove_duplicates import remove_duplicates
from climbing_stairs import climb_stairs
from plus_one import plus_one
from palindrome_number import is_palindrome
from reverse_linked_list import ListNode as ReverseListNode, reverse_list
from merge_sorted_lists import ListNode as MergeListNode, merge_two_lists

def test_two_sum():
    print("Testing Two Sum...")
    test_cases = [
        (([2, 7, 11, 15], 9), [0, 1]),
        (([3, 2, 4], 6), [1, 2]),
        (([3, 3], 6), [0, 1]),
        (([1, 2, 3, 4, 5], 8), [2, 4]),
        (([0, 4, 3, 0], 0), [0, 3])
    ]
    
    for i, ((nums, target), expected) in enumerate(test_cases, 1):
        result = two_sum(nums, target)
        # Check if result matches expected (order might vary)
        if sorted(result) == sorted(expected):
            print(f"  Test {i}: PASS - {result}")
        else:
            print(f"  Test {i}: FAIL - Expected {expected}, got {result}")

def test_valid_parentheses():
    print("Testing Valid Parentheses...")
    test_cases = [
        ("()", True),
        ("()[]{}", True),
        ("(]", False),
        ("([)]", False),
        ("{[]}", True),
        ("", True),
        ("(((", False)
    ]
    
    for i, (s, expected) in enumerate(test_cases, 1):
        result = is_valid(s)
        if result == expected:
            print(f"  Test {i}: PASS - '{s}' -> {result}")
        else:
            print(f"  Test {i}: FAIL - '{s}' -> Expected {expected}, got {result}")

def test_max_subarray():
    print("Testing Maximum Subarray...")
    test_cases = [
        ([-2, 1, -3, 4, -1, 2, 1, -5, 4], 6),
        ([1], 1),
        ([5, 4, -1, 7, 8], 23),
        ([-1], -1),
        ([-2, -1], -1)
    ]
    
    for i, (nums, expected) in enumerate(test_cases, 1):
        result = max_sub_array(nums)
        if result == expected:
            print(f"  Test {i}: PASS - {nums} -> {result}")
        else:
            print(f"  Test {i}: FAIL - {nums} -> Expected {expected}, got {result}")

def test_buy_sell_stock():
    print("Testing Best Time to Buy and Sell Stock...")
    test_cases = [
        ([7, 1, 5, 3, 6, 4], 5),
        ([7, 6, 4, 3, 1], 0),
        ([1, 2, 3, 4, 5], 4),
        ([2, 4, 1], 2),
        ([3, 2, 6, 5, 0, 3], 4)
    ]
    
    for i, (prices, expected) in enumerate(test_cases, 1):
        result = max_profit(prices)
        if result == expected:
            print(f"  Test {i}: PASS - {prices} -> {result}")
        else:
            print(f"  Test {i}: FAIL - {prices} -> Expected {expected}, got {result}")

def test_remove_duplicates():
    print("Testing Remove Duplicates from Sorted Array...")
    test_cases = [
        ([1, 1, 2], 2),
        ([0, 0, 1, 1, 1, 2, 2, 3, 3, 4], 5),
        ([1], 1),
        ([1, 2], 2),
        ([1, 1, 1], 1)
    ]
    
    for i, (nums, expected) in enumerate(test_cases, 1):
        nums_copy = nums.copy()  # Make a copy since function modifies in-place
        result = remove_duplicates(nums_copy)
        if result == expected:
            print(f"  Test {i}: PASS - {nums} -> {result}")
        else:
            print(f"  Test {i}: FAIL - {nums} -> Expected {expected}, got {result}")

def test_climbing_stairs():
    print("Testing Climbing Stairs...")
    test_cases = [
        (2, 2),
        (3, 3),
        (4, 5),
        (5, 8),
        (1, 1)
    ]
    
    for i, (n, expected) in enumerate(test_cases, 1):
        result = climb_stairs(n)
        if result == expected:
            print(f"  Test {i}: PASS - {n} -> {result}")
        else:
            print(f"  Test {i}: FAIL - {n} -> Expected {expected}, got {result}")

def test_plus_one():
    print("Testing Plus One...")
    test_cases = [
        ([1, 2, 3], [1, 2, 4]),
        ([4, 3, 2, 1], [4, 3, 2, 2]),
        ([9], [1, 0]),
        ([9, 9], [1, 0, 0]),
        ([0], [1])
    ]
    
    for i, (digits, expected) in enumerate(test_cases, 1):
        result = plus_one(digits.copy())  # Make a copy since function might modify
        if result == expected:
            print(f"  Test {i}: PASS - {digits} -> {result}")
        else:
            print(f"  Test {i}: FAIL - {digits} -> Expected {expected}, got {result}")

def test_palindrome_number():
    print("Testing Palindrome Number...")
    test_cases = [
        (121, True),
        (-121, False),
        (10, False),
        (0, True),
        (12321, True),
        (123, False)
    ]
    
    for i, (x, expected) in enumerate(test_cases, 1):
        result = is_palindrome(x)
        if result == expected:
            print(f"  Test {i}: PASS - {x} -> {result}")
        else:
            print(f"  Test {i}: FAIL - {x} -> Expected {expected}, got {result}")

def create_linked_list(arr):
    """Helper function to create linked list from array"""
    if not arr:
        return None
    head = ReverseListNode(arr[0])
    current = head
    for val in arr[1:]:
        current.next = ReverseListNode(val)
        current = current.next
    return head

def linked_list_to_array(head):
    """Helper function to convert linked list to array"""
    result = []
    current = head
    while current:
        result.append(current.val)
        current = current.next
    return result

def test_reverse_linked_list():
    print("Testing Reverse Linked List...")
    test_cases = [
        ([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]),
        ([1, 2], [2, 1]),
        ([], []),
        ([1], [1])
    ]
    
    for i, (input_arr, expected) in enumerate(test_cases, 1):
        head = create_linked_list(input_arr)
        result_head = reverse_list(head)
        result = linked_list_to_array(result_head)
        if result == expected:
            print(f"  Test {i}: PASS - {input_arr} -> {result}")
        else:
            print(f"  Test {i}: FAIL - {input_arr} -> Expected {expected}, got {result}")

def create_merge_linked_list(arr):
    """Helper function to create linked list from array for merge function"""
    if not arr:
        return None
    head = MergeListNode(arr[0])
    current = head
    for val in arr[1:]:
        current.next = MergeListNode(val)
        current = current.next
    return head

def merge_linked_list_to_array(head):
    """Helper function to convert linked list to array for merge function"""
    result = []
    current = head
    while current:
        result.append(current.val)
        current = current.next
    return result

def test_merge_sorted_lists():
    print("Testing Merge Two Sorted Lists...")
    test_cases = [
        (([1, 2, 4], [1, 3, 4]), [1, 1, 2, 3, 4, 4]),
        (([1], []), [1]),
        (([], []), []),
        (([2], [1]), [1, 2])
    ]
    
    for i, ((list1_arr, list2_arr), expected) in enumerate(test_cases, 1):
        list1 = create_merge_linked_list(list1_arr)
        list2 = create_merge_linked_list(list2_arr)
        result_head = merge_two_lists(list1, list2)
        result = merge_linked_list_to_array(result_head)
        if result == expected:
            print(f"  Test {i}: PASS - {list1_arr} + {list2_arr} -> {result}")
        else:
            print(f"  Test {i}: FAIL - {list1_arr} + {list2_arr} -> Expected {expected}, got {result}")

if __name__ == "__main__":
    print("🧪 Testing all LeetCode reference solutions...")
    print("=" * 60)
    
    test_two_sum()
    print()
    test_valid_parentheses()
    print()
    test_max_subarray()
    print()
    test_buy_sell_stock()
    print()
    test_remove_duplicates()
    print()
    test_climbing_stairs()
    print()
    test_plus_one()
    print()
    test_palindrome_number()
    print()
    test_reverse_linked_list()
    print()
    test_merge_sorted_lists()
    
    print("=" * 60)
    print("✅ All reference solutions tested!") 