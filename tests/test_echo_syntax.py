#!/usr/bin/env python3
"""
Test script to verify the echo command syntax issue and test with better prompts.
"""

import tempfile
import os
from auto_codex.core import CodexRun

def test_with_better_prompt():
    """Test with a more explicit prompt that should avoid echo syntax issues."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f'=== Testing with Better Prompt ===')
        print(f'Testing in directory: {temp_dir}')
        
        # Set 777 permissions
        os.chmod(temp_dir, 0o777)
        print(f'Set permissions to 777')
        
        # Test with a more explicit prompt
        better_prompt = '''Create a text file named "hello.txt" containing exactly the text "Hello World". 
Use proper shell redirection syntax like: echo "Hello World" > hello.txt
Make sure to use the correct redirection operator > (not as part of the quoted string).'''
        
        run = CodexRun(
            prompt=better_prompt,
            model='gpt-4.1-nano',
            provider='openai',
            writable_root=temp_dir,
            timeout=30,
            approval_mode='full-auto',
            dangerously_auto_approve_everything=True,
            debug=True
        )
        
        result = run.execute(log_dir=temp_dir)
        
        print(f'Success: {result.success}')
        print(f'Duration: {result.duration:.1f}s')
        
        # Check if file was created
        test_file = os.path.join(temp_dir, 'hello.txt')
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            print(f'✅ File created successfully with content: {repr(content)}')
            return True
        else:
            print('❌ File was NOT created')
            
        # Show log file content for debugging
        if result.log_file and os.path.exists(result.log_file):
            print(f'\nLog file: {result.log_file}')
            with open(result.log_file, 'r') as f:
                log_content = f.read()
            print('Last 10 lines of log:')
            print('\n'.join(log_content.split('\n')[-10:]))
            
        return False

def test_with_python_approach():
    """Test with a prompt that suggests using Python instead of shell commands."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f'\n=== Testing with Python Approach ===')
        print(f'Testing in directory: {temp_dir}')
        
        # Set 777 permissions
        os.chmod(temp_dir, 0o777)
        print(f'Set permissions to 777')
        
        # Test with Python-based prompt
        python_prompt = '''Create a text file named "python_test.txt" containing "Hello from Python".
Use Python to create the file like this:
python3 -c "with open('python_test.txt', 'w') as f: f.write('Hello from Python')"
Or use any other reliable method that works in your environment.'''
        
        run = CodexRun(
            prompt=python_prompt,
            model='gpt-4.1-nano',
            provider='openai',
            writable_root=temp_dir,
            timeout=30,
            approval_mode='full-auto',
            dangerously_auto_approve_everything=True,
            debug=True
        )
        
        result = run.execute(log_dir=temp_dir)
        
        print(f'Success: {result.success}')
        print(f'Duration: {result.duration:.1f}s')
        
        # Check if file was created
        test_file = os.path.join(temp_dir, 'python_test.txt')
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            print(f'✅ File created successfully with content: {repr(content)}')
            return True
        else:
            print('❌ File was NOT created')
            
        # Show log file content for debugging
        if result.log_file and os.path.exists(result.log_file):
            print(f'\nLog file: {result.log_file}')
            with open(result.log_file, 'r') as f:
                log_content = f.read()
            print('Last 5 lines of log:')
            print('\n'.join(log_content.split('\n')[-5:]))
            
        return False

def test_with_cat_approach():
    """Test with a prompt that suggests using cat with heredoc."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f'\n=== Testing with Cat Heredoc Approach ===')
        print(f'Testing in directory: {temp_dir}')
        
        # Set 777 permissions
        os.chmod(temp_dir, 0o777)
        print(f'Set permissions to 777')
        
        # Test with cat heredoc prompt
        cat_prompt = '''Create a text file named "cat_test.txt" containing "Hello from Cat".
Use the cat command with heredoc syntax like this:
cat > cat_test.txt << EOF
Hello from Cat
EOF
This approach should work reliably in most environments.'''
        
        run = CodexRun(
            prompt=cat_prompt,
            model='gpt-4.1-nano',
            provider='openai',
            writable_root=temp_dir,
            timeout=30,
            approval_mode='full-auto',
            dangerously_auto_approve_everything=True,
            debug=True
        )
        
        result = run.execute(log_dir=temp_dir)
        
        print(f'Success: {result.success}')
        print(f'Duration: {result.duration:.1f}s')
        
        # Check if file was created
        test_file = os.path.join(temp_dir, 'cat_test.txt')
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            print(f'✅ File created successfully with content: {repr(content)}')
            return True
        else:
            print('❌ File was NOT created')
            
        # Show log file content for debugging
        if result.log_file and os.path.exists(result.log_file):
            print(f'\nLog file: {result.log_file}')
            with open(result.log_file, 'r') as f:
                log_content = f.read()
            print('Last 5 lines of log:')
            print('\n'.join(log_content.split('\n')[-5:]))
            
        return False

if __name__ == "__main__":
    success1 = test_with_better_prompt()
    success2 = test_with_python_approach()
    success3 = test_with_cat_approach()
    
    print(f"\nResults:")
    print(f"Better echo prompt: {'PASSED' if success1 else 'FAILED'}")
    print(f"Python approach: {'PASSED' if success2 else 'FAILED'}")
    print(f"Cat heredoc approach: {'PASSED' if success3 else 'FAILED'}")
    print(f"Overall: {'PASSED' if (success1 or success2 or success3) else 'FAILED'}") 