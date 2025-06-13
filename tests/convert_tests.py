#!/usr/bin/env python3
"""
Convert pytest-style test_health_monitoring.py to unittest style.
"""

import re

def convert_test_file():
    # Read the file
    with open('auto_codex/tests/test_health_monitoring.py', 'r') as f:
        content = f.read()

    # Replace pytest-style assertions with unittest-style
    replacements = [
        # Complex assertions first
        (r'assert (\d+) <= (.+?) <= (\d+)', r'self.assertTrue(\1 <= \2 <= \3)'),
        (r'assert len\((.+?)\) == (.+)', r'self.assertEqual(len(\1), \2)'),
        (r'assert isinstance\((.+?), (.+?)\)', r'self.assertIsInstance(\1, \2)'),
        
        # Equality assertions
        (r'assert (.+?) == (.+)', r'self.assertEqual(\1, \2)'),
        
        # Identity assertions  
        (r'assert (.+?) is None', r'self.assertIsNone(\1)'),
        (r'assert (.+?) is not None', r'self.assertIsNotNone(\1)'),
        (r'assert (.+?) is (.+)', r'self.assertIs(\1, \2)'),
        (r'assert (.+?) is not (.+)', r'self.assertIsNot(\1, \2)'),
        
        # Boolean assertions
        (r'assert not (.+)', r'self.assertFalse(\1)'),
        (r'assert (.+)', r'self.assertTrue(\1)'),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    # Add unittest.TestCase inheritance to remaining classes
    content = re.sub(r'^class (Test\w+):$', r'class \1(unittest.TestCase):', content, flags=re.MULTILINE)

    # Write back
    with open('auto_codex/tests/test_health_monitoring.py', 'w') as f:
        f.write(content)

    print('Conversion completed successfully!')

if __name__ == '__main__':
    convert_test_file() 