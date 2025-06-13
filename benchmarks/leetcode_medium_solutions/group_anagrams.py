"""
LeetCode #49: Group Anagrams
Given an array of strings strs, group the anagrams together. 
You can return the answer in any order.

An Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, 
typically using all the original letters exactly once.

Time Complexity: O(n * k * log k) where n is the number of strings and k is the maximum length of a string
Space Complexity: O(n * k)
"""

def groupAnagrams(strs):
    """
    Group anagrams together.
    
    Args:
        strs: List of strings
        
    Returns:
        List of lists where each inner list contains anagrams
    """
    if not strs:
        return []
    
    anagram_groups = {}
    
    for s in strs:
        # Sort the string to create a key for anagrams
        # All anagrams will have the same sorted string
        sorted_str = ''.join(sorted(s))
        
        # Add the string to the appropriate group
        if sorted_str not in anagram_groups:
            anagram_groups[sorted_str] = []
        anagram_groups[sorted_str].append(s)
    
    # Return all groups as a list of lists
    return list(anagram_groups.values()) 