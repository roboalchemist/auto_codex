def max_profit(prices):
    """
    You are given an array prices where prices[i] is the price of a given stock on the ith day.
    You want to maximize your profit by choosing a single day to buy one stock and choosing 
    a different day in the future to sell that stock.
    
    Args:
        prices: List of integers representing stock prices
        
    Returns:
        Integer representing the maximum profit achievable
    """
    if not prices or len(prices) < 2:
        return 0
    
    min_price = prices[0]
    max_profit = 0
    
    for price in prices[1:]:
        # Update minimum price seen so far
        min_price = min(min_price, price)
        # Calculate profit if we sell at current price
        profit = price - min_price
        # Update maximum profit
        max_profit = max(max_profit, profit)
    
    return max_profit 