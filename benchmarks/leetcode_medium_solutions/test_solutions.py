#!/usr/bin/env python3
"""
Test script for LeetCode Medium reference solutions.
Validates that all implemented solutions work correctly.
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from three_sum import threeSum
from longest_substring_without_repeating import lengthOfLongestSubstring
from add_two_numbers import addTwoNumbers, ListNode
from group_anagrams import groupAnagrams
from product_except_self import productExceptSelf
from container_with_most_water import maxArea
from rotate_image import rotate
from spiral_matrix import spiralOrder
from search_rotated_sorted_array import search
from validate_bst import isValidBST, TreeNode

def create_linked_list(values):
    """Helper function to create a linked list from a list of values."""
    if not values:
        return None
    
    head = ListNode(values[0])
    current = head
    for val in values[1:]:
        current.next = ListNode(val)
        current = current.next
    return head

def linked_list_to_list(head):
    """Helper function to convert linked list to Python list."""
    result = []
    current = head
    while current:
        result.append(current.val)
        current = current.next
    return result

def create_binary_tree(values):
    """Helper function to create binary tree from level-order list."""
    if not values or values[0] is None:
        return None
    
    root = TreeNode(values[0])
    queue = [root]
    i = 1
    
    while queue and i < len(values):
        node = queue.pop(0)
        
        # Left child
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        
        # Right child
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    
    return root

def test_three_sum():
    """Test 3Sum solution."""
    print("Testing 3Sum...")
    
    # Test case 1
    nums1 = [-1, 0, 1, 2, -1, -4]
    result1 = threeSum(nums1)
    expected1 = [[-1, -1, 2], [-1, 0, 1]]
    # Sort for comparison since order doesn't matter
    result1.sort()
    expected1.sort()
    assert result1 == expected1, f"Test 1 failed: {result1} != {expected1}"
    
    # Test case 2
    nums2 = [0, 1, 1]
    result2 = threeSum(nums2)
    expected2 = []
    assert result2 == expected2, f"Test 2 failed: {result2} != {expected2}"
    
    # Test case 3
    nums3 = [0, 0, 0]
    result3 = threeSum(nums3)
    expected3 = [[0, 0, 0]]
    assert result3 == expected3, f"Test 3 failed: {result3} != {expected3}"
    
    print("✓ 3Sum tests passed")

def test_longest_substring():
    """Test Longest Substring Without Repeating Characters."""
    print("Testing Longest Substring Without Repeating Characters...")
    
    # Test case 1
    s1 = "abcabcbb"
    result1 = lengthOfLongestSubstring(s1)
    expected1 = 3  # "abc"
    assert result1 == expected1, f"Test 1 failed: {result1} != {expected1}"
    
    # Test case 2
    s2 = "bbbbb"
    result2 = lengthOfLongestSubstring(s2)
    expected2 = 1  # "b"
    assert result2 == expected2, f"Test 2 failed: {result2} != {expected2}"
    
    # Test case 3
    s3 = "pwwkew"
    result3 = lengthOfLongestSubstring(s3)
    expected3 = 3  # "wke"
    assert result3 == expected3, f"Test 3 failed: {result3} != {expected3}"
    
    # Test case 4
    s4 = ""
    result4 = lengthOfLongestSubstring(s4)
    expected4 = 0
    assert result4 == expected4, f"Test 4 failed: {result4} != {expected4}"
    
    print("✓ Longest Substring tests passed")

def test_add_two_numbers():
    """Test Add Two Numbers solution."""
    print("Testing Add Two Numbers...")
    
    # Test case 1: 342 + 465 = 807
    l1 = create_linked_list([2, 4, 3])
    l2 = create_linked_list([5, 6, 4])
    result1 = addTwoNumbers(l1, l2)
    expected1 = [7, 0, 8]
    assert linked_list_to_list(result1) == expected1, f"Test 1 failed"
    
    # Test case 2: 0 + 0 = 0
    l1 = create_linked_list([0])
    l2 = create_linked_list([0])
    result2 = addTwoNumbers(l1, l2)
    expected2 = [0]
    assert linked_list_to_list(result2) == expected2, f"Test 2 failed"
    
    # Test case 3: 999 + 9999 = 10998
    l1 = create_linked_list([9, 9, 9])
    l2 = create_linked_list([9, 9, 9, 9])
    result3 = addTwoNumbers(l1, l2)
    expected3 = [8, 9, 9, 0, 1]
    assert linked_list_to_list(result3) == expected3, f"Test 3 failed"
    
    print("✓ Add Two Numbers tests passed")

def test_group_anagrams():
    """Test Group Anagrams solution."""
    print("Testing Group Anagrams...")
    
    # Test case 1
    strs1 = ["eat", "tea", "tan", "ate", "nat", "bat"]
    result1 = groupAnagrams(strs1)
    # Sort each group and the groups themselves for comparison
    result1 = [sorted(group) for group in result1]
    result1.sort()
    expected1 = [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
    expected1 = [sorted(group) for group in expected1]
    expected1.sort()
    assert result1 == expected1, f"Test 1 failed: {result1} != {expected1}"
    
    # Test case 2
    strs2 = [""]
    result2 = groupAnagrams(strs2)
    expected2 = [[""]]
    assert result2 == expected2, f"Test 2 failed: {result2} != {expected2}"
    
    # Test case 3
    strs3 = ["a"]
    result3 = groupAnagrams(strs3)
    expected3 = [["a"]]
    assert result3 == expected3, f"Test 3 failed: {result3} != {expected3}"
    
    print("✓ Group Anagrams tests passed")

def test_product_except_self():
    """Test Product of Array Except Self solution."""
    print("Testing Product of Array Except Self...")
    
    # Test case 1
    nums1 = [1, 2, 3, 4]
    result1 = productExceptSelf(nums1)
    expected1 = [24, 12, 8, 6]
    assert result1 == expected1, f"Test 1 failed: {result1} != {expected1}"
    
    # Test case 2
    nums2 = [-1, 1, 0, -3, 3]
    result2 = productExceptSelf(nums2)
    expected2 = [0, 0, 9, 0, 0]
    assert result2 == expected2, f"Test 2 failed: {result2} != {expected2}"
    
    print("✓ Product Except Self tests passed")

def test_container_with_most_water():
    """Test Container With Most Water solution."""
    print("Testing Container With Most Water...")
    
    # Test case 1
    height1 = [1, 8, 6, 2, 5, 4, 8, 3, 7]
    result1 = maxArea(height1)
    expected1 = 49  # Between indices 1 and 8
    assert result1 == expected1, f"Test 1 failed: {result1} != {expected1}"
    
    # Test case 2
    height2 = [1, 1]
    result2 = maxArea(height2)
    expected2 = 1
    assert result2 == expected2, f"Test 2 failed: {result2} != {expected2}"
    
    print("✓ Container With Most Water tests passed")

def test_rotate_image():
    """Test Rotate Image solution."""
    print("Testing Rotate Image...")
    
    # Test case 1
    matrix1 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    rotate(matrix1)
    expected1 = [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
    assert matrix1 == expected1, f"Test 1 failed: {matrix1} != {expected1}"
    
    # Test case 2
    matrix2 = [[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]]
    rotate(matrix2)
    expected2 = [[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]]
    assert matrix2 == expected2, f"Test 2 failed: {matrix2} != {expected2}"
    
    print("✓ Rotate Image tests passed")

def test_spiral_matrix():
    """Test Spiral Matrix solution."""
    print("Testing Spiral Matrix...")
    
    # Test case 1
    matrix1 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    result1 = spiralOrder(matrix1)
    expected1 = [1, 2, 3, 6, 9, 8, 7, 4, 5]
    assert result1 == expected1, f"Test 1 failed: {result1} != {expected1}"
    
    # Test case 2
    matrix2 = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
    result2 = spiralOrder(matrix2)
    expected2 = [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]
    assert result2 == expected2, f"Test 2 failed: {result2} != {expected2}"
    
    print("✓ Spiral Matrix tests passed")

def test_search_rotated_sorted_array():
    """Test Search in Rotated Sorted Array solution."""
    print("Testing Search in Rotated Sorted Array...")
    
    # Test case 1
    nums1 = [4, 5, 6, 7, 0, 1, 2]
    target1 = 0
    result1 = search(nums1, target1)
    expected1 = 4
    assert result1 == expected1, f"Test 1 failed: {result1} != {expected1}"
    
    # Test case 2
    nums2 = [4, 5, 6, 7, 0, 1, 2]
    target2 = 3
    result2 = search(nums2, target2)
    expected2 = -1
    assert result2 == expected2, f"Test 2 failed: {result2} != {expected2}"
    
    # Test case 3
    nums3 = [1]
    target3 = 0
    result3 = search(nums3, target3)
    expected3 = -1
    assert result3 == expected3, f"Test 3 failed: {result3} != {expected3}"
    
    print("✓ Search in Rotated Sorted Array tests passed")

def test_validate_bst():
    """Test Validate Binary Search Tree solution."""
    print("Testing Validate Binary Search Tree...")
    
    # Test case 1: Valid BST
    #     2
    #    / \
    #   1   3
    root1 = create_binary_tree([2, 1, 3])
    result1 = isValidBST(root1)
    expected1 = True
    assert result1 == expected1, f"Test 1 failed: {result1} != {expected1}"
    
    # Test case 2: Invalid BST
    #     5
    #    / \
    #   1   4
    #      / \
    #     3   6
    root2 = create_binary_tree([5, 1, 4, None, None, 3, 6])
    result2 = isValidBST(root2)
    expected2 = False
    assert result2 == expected2, f"Test 2 failed: {result2} != {expected2}"
    
    # Test case 3: Single node
    root3 = create_binary_tree([1])
    result3 = isValidBST(root3)
    expected3 = True
    assert result3 == expected3, f"Test 3 failed: {result3} != {expected3}"
    
    print("✓ Validate BST tests passed")

def main():
    """Run all tests."""
    print("Running LeetCode Medium Reference Solution Tests...")
    print("=" * 50)
    
    try:
        test_three_sum()
        test_longest_substring()
        test_add_two_numbers()
        test_group_anagrams()
        test_product_except_self()
        test_container_with_most_water()
        test_rotate_image()
        test_spiral_matrix()
        test_search_rotated_sorted_array()
        test_validate_bst()
        
        print("=" * 50)
        print("  All tests passed! Reference solutions are working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 