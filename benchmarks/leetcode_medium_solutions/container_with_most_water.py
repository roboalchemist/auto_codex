"""
LeetCode #11: Container With Most Water
You are given an integer array height of length n. There are n vertical lines drawn 
such that the two endpoints of the ith line are (i, 0) and (i, height[i]).

Find two lines that together with the x-axis form a container that contains the most water.
Return the maximum amount of water a container can store.

Time Complexity: O(n)
Space Complexity: O(1)
"""

def maxArea(height):
    """
    Find the maximum area of water that can be contained.
    
    Args:
        height: List of integers representing heights of vertical lines
        
    Returns:
        Integer representing the maximum area
    """
    if len(height) < 2:
        return 0
    
    left = 0
    right = len(height) - 1
    max_area = 0
    
    while left < right:
        # Calculate current area
        width = right - left
        current_height = min(height[left], height[right])
        current_area = width * current_height
        
        # Update maximum area
        max_area = max(max_area, current_area)
        
        # Move the pointer with smaller height
        # This gives us the best chance to find a larger area
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    
    return max_area 