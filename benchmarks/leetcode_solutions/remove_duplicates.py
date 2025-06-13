def remove_duplicates(nums):
    """
    Given an integer array nums sorted in non-decreasing order, remove the duplicates 
    in-place such that each unique element appears only once. The relative order of 
    the elements should be kept the same. Return the number of unique elements in nums.
    
    Args:
        nums: List of integers sorted in non-decreasing order (modified in-place)
        
    Returns:
        Integer representing the number of unique elements
    """
    if not nums:
        return 0
    
    # Two-pointer approach
    # slow pointer tracks the position for next unique element
    slow = 0
    
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    
    # Return the length of unique elements
    return slow + 1 