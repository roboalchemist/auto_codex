"""
LeetCode #15: 3Sum
Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] 
such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.

Notice that the solution set must not contain duplicate triplets.

Time Complexity: O(n^2)
Space Complexity: O(1) excluding output array
"""

def threeSum(nums):
    """
    Find all unique triplets in the array that sum to zero.
    
    Args:
        nums: List of integers
        
    Returns:
        List of lists containing unique triplets that sum to zero
    """
    if len(nums) < 3:
        return []
    
    nums.sort()  # Sort the array first
    result = []
    
    for i in range(len(nums) - 2):
        # Skip duplicate values for the first element
        if i > 0 and nums[i] == nums[i - 1]:
            continue
            
        left = i + 1
        right = len(nums) - 1
        
        while left < right:
            current_sum = nums[i] + nums[left] + nums[right]
            
            if current_sum == 0:
                result.append([nums[i], nums[left], nums[right]])
                
                # Skip duplicates for left pointer
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                # Skip duplicates for right pointer
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                    
                left += 1
                right -= 1
            elif current_sum < 0:
                left += 1
            else:
                right -= 1
                
    return result 