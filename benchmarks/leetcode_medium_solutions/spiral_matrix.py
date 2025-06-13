"""
LeetCode #54: Spiral Matrix
Given an m x n matrix, return all elements of the matrix in spiral order.

Time Complexity: O(m * n)
Space Complexity: O(1) excluding output array
"""

def spiralOrder(matrix):
    """
    Return all elements of the matrix in spiral order.
    
    Args:
        matrix: 2D list of integers
        
    Returns:
        List of integers in spiral order
    """
    if not matrix or not matrix[0]:
        return []
    
    result = []
    top = 0
    bottom = len(matrix) - 1
    left = 0
    right = len(matrix[0]) - 1
    
    while top <= bottom and left <= right:
        # Traverse right along the top row
        for col in range(left, right + 1):
            result.append(matrix[top][col])
        top += 1
        
        # Traverse down along the right column
        for row in range(top, bottom + 1):
            result.append(matrix[row][right])
        right -= 1
        
        # Traverse left along the bottom row (if we still have rows)
        if top <= bottom:
            for col in range(right, left - 1, -1):
                result.append(matrix[bottom][col])
            bottom -= 1
        
        # Traverse up along the left column (if we still have columns)
        if left <= right:
            for row in range(bottom, top - 1, -1):
                result.append(matrix[row][left])
            left += 1
    
    return result 