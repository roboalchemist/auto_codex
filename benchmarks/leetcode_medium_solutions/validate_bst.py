"""
LeetCode #98: Validate Binary Search Tree
Given the root of a binary tree, determine if it is a valid binary search tree (BST).

A valid BST is defined as follows:
- The left subtree of a node contains only nodes with keys less than the node's key.
- The right subtree of a node contains only nodes with keys greater than the node's key.
- Both the left and right subtrees must also be binary search trees.

Time Complexity: O(n)
Space Complexity: O(h) where h is the height of the tree
"""

class TreeNode:
    """Definition for a binary tree node."""
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def isValidBST(root):
    """
    Validate if a binary tree is a valid BST.
    
    Args:
        root: TreeNode representing the root of the binary tree
        
    Returns:
        Boolean indicating if the tree is a valid BST
    """
    def validate(node, min_val, max_val):
        """
        Helper function to validate BST with bounds.
        
        Args:
            node: Current node being validated
            min_val: Minimum allowed value for this node
            max_val: Maximum allowed value for this node
            
        Returns:
            Boolean indicating if subtree rooted at node is valid BST
        """
        if not node:
            return True
        
        # Check if current node violates BST property
        if node.val <= min_val or node.val >= max_val:
            return False
        
        # Recursively validate left and right subtrees with updated bounds
        return (validate(node.left, min_val, node.val) and 
                validate(node.right, node.val, max_val))
    
    # Start validation with infinite bounds
    return validate(root, float('-inf'), float('inf')) 