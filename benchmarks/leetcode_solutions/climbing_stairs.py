def climb_stairs(n):
    """
    You are climbing a staircase. It takes n steps to reach the top.
    Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?
    
    This is essentially the Fibonacci sequence: f(n) = f(n-1) + f(n-2)
    
    Args:
        n: Integer representing the number of steps
        
    Returns:
        Integer representing the number of distinct ways to climb
    """
    if n <= 2:
        return n
    
    # Dynamic programming approach - only need to track last two values
    prev2 = 1  # f(1)
    prev1 = 2  # f(2)
    
    for i in range(3, n + 1):
        current = prev1 + prev2
        prev2 = prev1
        prev1 = current
    
    return prev1 