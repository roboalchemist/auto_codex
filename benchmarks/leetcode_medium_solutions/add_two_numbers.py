"""
LeetCode #2: Add Two Numbers
You are given two non-empty linked lists representing two non-negative integers. 
The digits are stored in reverse order, and each of their nodes contains a single digit. 
Add the two numbers and return the sum as a linked list.

Time Complexity: O(max(m, n))
Space Complexity: O(max(m, n))
"""

class ListNode:
    """Definition for singly-linked list."""
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def addTwoNumbers(l1, l2):
    """
    Add two numbers represented as linked lists.
    
    Args:
        l1: ListNode representing first number (digits in reverse order)
        l2: ListNode representing second number (digits in reverse order)
        
    Returns:
        ListNode representing the sum (digits in reverse order)
    """
    dummy = ListNode(0)  # Dummy node to simplify logic
    current = dummy
    carry = 0
    
    while l1 or l2 or carry:
        # Get values from current nodes (0 if node is None)
        val1 = l1.val if l1 else 0
        val2 = l2.val if l2 else 0
        
        # Calculate sum and new carry
        total = val1 + val2 + carry
        carry = total // 10
        digit = total % 10
        
        # Create new node with the digit
        current.next = ListNode(digit)
        current = current.next
        
        # Move to next nodes if they exist
        l1 = l1.next if l1 else None
        l2 = l2.next if l2 else None
    
    return dummy.next  # Return the actual head (skip dummy) 