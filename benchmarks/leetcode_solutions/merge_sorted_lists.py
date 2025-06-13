class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def merge_two_lists(list1, list2):
    """
    You are given the heads of two sorted linked lists list1 and list2.
    Merge the two lists into one sorted list. The list should be made by splicing 
    together the nodes of the first two lists.
    
    Args:
        list1: ListNode representing the head of the first sorted linked list
        list2: ListNode representing the head of the second sorted linked list
        
    Returns:
        ListNode representing the head of the merged sorted linked list
    """
    # Create a dummy node to simplify the logic
    dummy = ListNode(0)
    current = dummy
    
    # Merge the two lists
    while list1 and list2:
        if list1.val <= list2.val:
            current.next = list1
            list1 = list1.next
        else:
            current.next = list2
            list2 = list2.next
        current = current.next
    
    # Append the remaining nodes
    if list1:
        current.next = list1
    elif list2:
        current.next = list2
    
    # Return the head of the merged list (skip dummy node)
    return dummy.next 