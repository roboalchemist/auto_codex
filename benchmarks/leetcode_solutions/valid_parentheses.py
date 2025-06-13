def is_valid(s):
    """
    Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', 
    determine if the input string is valid.
    
    Args:
        s: String containing only parentheses characters
        
    Returns:
        Boolean indicating if the string is valid
    """
    # Stack to keep track of opening brackets
    stack = []
    
    # Mapping of closing to opening brackets
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in mapping:
            # It's a closing bracket
            if not stack or stack.pop() != mapping[char]:
                return False
        else:
            # It's an opening bracket
            stack.append(char)
    
    # Valid if stack is empty (all brackets matched)
    return len(stack) == 0 