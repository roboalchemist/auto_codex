"""
LeetCode #238: Product of Array Except Self
Given an integer array nums, return an array answer such that answer[i] is equal to 
the product of all the elements of nums except nums[i].

The product of any prefix or suffix of nums is guaranteed to fit in a 32-bit integer.
You must write an algorithm that runs in O(n) time and without using the division operation.

Time Complexity: O(n)
Space Complexity: O(1) excluding output array
"""

def productExceptSelf(nums):
    """
    Calculate product of array except self without using division.
    
    Args:
        nums: List of integers
        
    Returns:
        List where each element is the product of all other elements
    """
    n = len(nums)
    result = [1] * n
    
    # First pass: calculate left products
    # result[i] contains the product of all elements to the left of i
    for i in range(1, n):
        result[i] = result[i - 1] * nums[i - 1]
    
    # Second pass: multiply by right products
    # Use a variable to keep track of the product of elements to the right
    right_product = 1
    for i in range(n - 1, -1, -1):
        result[i] *= right_product
        right_product *= nums[i]
    
    return result 