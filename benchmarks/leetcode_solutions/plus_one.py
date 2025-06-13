def plus_one(digits):
    """
    You are given a large integer represented as an integer array digits, where each digits[i] 
    is the ith digit of the integer. The digits are ordered from most significant to least 
    significant in left-to-right order. Increment the large integer by one and return the 
    resulting array of digits.
    
    Args:
        digits: List of integers representing digits of a large number
        
    Returns:
        List of integers representing the incremented number
    """
    # Start from the rightmost digit
    for i in range(len(digits) - 1, -1, -1):
        if digits[i] < 9:
            # No carry needed, just increment and return
            digits[i] += 1
            return digits
        else:
            # Carry needed, set current digit to 0 and continue
            digits[i] = 0
    
    # If we reach here, all digits were 9 (e.g., 999 -> 1000)
    return [1] + digits 