def max_sub_array(nums):
    """
    Given an integer array nums, find the subarray with the largest sum, and return its sum.
    Uses Kadane's algorithm for optimal O(n) solution.
    
    Args:
        nums: List of integers
        
    Returns:
        Integer representing the maximum subarray sum
    """
    if not nums:
        return 0
    
    # Kadane's algorithm
    max_sum = nums[0]
    current_sum = nums[0]
    
    for i in range(1, len(nums)):
        # Either extend the existing subarray or start a new one
        current_sum = max(nums[i], current_sum + nums[i])
        # Update the maximum sum seen so far
        max_sum = max(max_sum, current_sum)
    
    return max_sum 