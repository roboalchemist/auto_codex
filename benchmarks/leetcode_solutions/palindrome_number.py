def is_palindrome(x):
    """
    Given an integer x, return true if x is a palindrome, and false otherwise.
    An integer is a palindrome when it reads the same backward as forward.
    
    Args:
        x: Integer to check
        
    Returns:
        Boolean indicating if the number is a palindrome
    """
    # Negative numbers are not palindromes
    if x < 0:
        return False
    
    # Single digit numbers are palindromes
    if x < 10:
        return True
    
    # Convert to string and check if it reads the same forwards and backwards
    s = str(x)
    return s == s[::-1] 