class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head):
    """
    Given the head of a singly linked list, reverse the list, and return the reversed list.
    
    Args:
        head: ListNode representing the head of the linked list
        
    Returns:
        ListNode representing the head of the reversed linked list
    """
    prev = None
    current = head
    
    while current:
        # Store the next node
        next_node = current.next
        # Reverse the link
        current.next = prev
        # Move pointers forward
        prev = current
        current = next_node
    
    # prev is now the new head of the reversed list
    return prev 