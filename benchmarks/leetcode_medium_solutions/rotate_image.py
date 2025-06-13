"""
LeetCode #48: Rotate Image
You are given an n x n 2D matrix representing an image, rotate the image by 90 degrees (clockwise).
You have to rotate the image in-place, which means you have to modify the input 2D matrix directly. 
DO NOT allocate another 2D matrix and do the rotation.

Time Complexity: O(n^2)
Space Complexity: O(1)
"""

def rotate(matrix):
    """
    Rotate the matrix 90 degrees clockwise in-place.
    
    Args:
        matrix: 2D list representing the image (modified in-place)
        
    Returns:
        None (modifies matrix in-place)
    """
    n = len(matrix)
    
    # Step 1: Transpose the matrix (swap matrix[i][j] with matrix[j][i])
    for i in range(n):
        for j in range(i, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    
    # Step 2: Reverse each row
    for i in range(n):
        matrix[i].reverse()
    
    # Alternative approach: rotate layer by layer
    # Uncomment below for the layer-by-layer approach
    """
    n = len(matrix)
    
    # Process each layer (ring) of the matrix
    for layer in range(n // 2):
        first = layer
        last = n - 1 - layer
        
        for i in range(first, last):
            offset = i - first
            
            # Save top element
            top = matrix[first][i]
            
            # Top = Left
            matrix[first][i] = matrix[last - offset][first]
            
            # Left = Bottom
            matrix[last - offset][first] = matrix[last][last - offset]
            
            # Bottom = Right
            matrix[last][last - offset] = matrix[i][last]
            
            # Right = Top
            matrix[i][last] = top
    """ 