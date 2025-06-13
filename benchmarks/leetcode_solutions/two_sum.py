def two_sum(nums, target):
    """
    Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.
    
    Args:
        nums: List of integers
        target: Integer target sum
        
    Returns:
        List of two indices that sum to target
    """
    # Use a hash map to store value -> index mapping
    num_map = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    
    return []  # Should not reach here given problem constraints 