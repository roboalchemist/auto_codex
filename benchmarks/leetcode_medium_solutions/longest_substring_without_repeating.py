"""
LeetCode #3: Longest Substring Without Repeating Characters
Given a string s, find the length of the longest substring without repeating characters.

Time Complexity: O(n)
Space Complexity: O(min(m, n)) where m is the size of the charset
"""

def lengthOfLongestSubstring(s):
    """
    Find the length of the longest substring without repeating characters.
    
    Args:
        s: Input string
        
    Returns:
        Integer representing the length of the longest substring
    """
    if not s:
        return 0
    
    char_index = {}  # Dictionary to store character and its latest index
    max_length = 0
    start = 0  # Start of the current window
    
    for end in range(len(s)):
        char = s[end]
        
        # If character is already seen and is within current window
        if char in char_index and char_index[char] >= start:
            start = char_index[char] + 1
        
        # Update the character's latest index
        char_index[char] = end
        
        # Update max_length if current window is larger
        max_length = max(max_length, end - start + 1)
    
    return max_length 