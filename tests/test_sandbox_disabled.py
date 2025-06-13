#!/usr/bin/env python3
"""
Test script to verify that the sandbox is disabled.
"""

import tempfile
import os
import stat
from auto_codex.core import CodexRun

def test_sandbox_disabled():
    """Test if sandbox is disabled by attempting file creation."""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f'Testing in directory: {temp_dir}')
        
        # Check directory permissions
        dir_stat = os.stat(temp_dir)
        print(f'Directory permissions: {oct(dir_stat.st_mode)[-3:]}')
        print(f'Directory owner: {dir_stat.st_uid}')
        print(f'Current user: {os.getuid()}')
        
        # Test if we can create a file directly (without Codex)
        test_direct_file = os.path.join(temp_dir, 'direct_test.txt')
        try:
            with open(test_direct_file, 'w') as f:
                f.write('Direct write test')
            print('✅ Direct file creation works')
            os.remove(test_direct_file)
        except Exception as e:
            print(f'❌ Direct file creation failed: {e}')
            return False
        
        # Test simple file creation with Codex
        run = CodexRun(
            prompt='Create a file called test.txt with the content "Hello World"',
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
        test_file = os.path.join(temp_dir, 'test.txt')
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            print(f'File created successfully with content: {repr(content)}')
            return True
        else:
            print('File was NOT created')
            
        # Show log file content for debugging
        if result.log_file and os.path.exists(result.log_file):
            print(f'\nLog file: {result.log_file}')
            with open(result.log_file, 'r') as f:
                log_content = f.read()
            print('Last 10 lines of log:')
            print('\n'.join(log_content.split('\n')[-10:]))
            
        return False

def test_with_777_permissions():
    """Test with 777 permissions on the folder."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f'\n=== Testing with 777 permissions ===')
        print(f'Testing in directory: {temp_dir}')
        
        # Set permissions to 777 (full access for everyone)
        os.chmod(temp_dir, 0o777)
        
        # Verify permissions were set
        dir_stat = os.stat(temp_dir)
        print(f'Directory permissions after chmod 777: {oct(dir_stat.st_mode)[-3:]}')
        
        # Test direct file creation with 777 permissions
        test_direct_file = os.path.join(temp_dir, 'direct_test_777.txt')
        try:
            with open(test_direct_file, 'w') as f:
                f.write('Direct write test with 777')
            print('✅ Direct file creation works with 777 permissions')
            os.remove(test_direct_file)
        except Exception as e:
            print(f'❌ Direct file creation failed with 777: {e}')
            return False
        
        # Test with Codex
        run = CodexRun(
            prompt='Create a file called test777.txt with the content "Hello World 777"',
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
        test_file = os.path.join(temp_dir, 'test777.txt')
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            print(f'File created successfully with content: {repr(content)}')
            return True
        else:
            print('File was NOT created with 777 permissions')
            
        # Show log file content for debugging
        if result.log_file and os.path.exists(result.log_file):
            print(f'\nLog file: {result.log_file}')
            with open(result.log_file, 'r') as f:
                log_content = f.read()
            print('Last 5 lines of log:')
            print('\n'.join(log_content.split('\n')[-5:]))
            
        return False

def test_with_different_flags():
    """Test with different command line flag combinations."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f'\n=== Testing with -w flag instead of --writable-root ===')
        print(f'Testing in directory: {temp_dir}')
        
        # Set 777 permissions
        os.chmod(temp_dir, 0o777)
        print(f'Set permissions to 777')
        
        # Modify the command construction to use -w instead
        run = CodexRun(
            prompt='Create a file called test2.txt with the content "Hello World 2"',
            model='gpt-4.1-nano',
            provider='openai',
            writable_root=temp_dir,
            timeout=30,
            approval_mode='full-auto',
            dangerously_auto_approve_everything=True,
            debug=True
        )
        
        # Manually override the command construction for testing
        original_execute = run._execute_codex
        
        def modified_execute():
            # Set environment variable to disable sandbox
            env = os.environ.copy()
            env['CODEX_UNSAFE_ALLOW_NO_SANDBOX'] = '1'
            
            # Try with -w flag instead of --writable-root
            cmd_parts = [
                "codex",
                f"--model={run.model}",
                f"--provider={run.provider}",
                f"-w", temp_dir,  # Use -w instead of --writable-root
                "--full-auto",
                "--dangerously-auto-approve-everything",
                "--quiet",
                run.prompt
            ]
            
            print(f"DEBUG: Modified command: {' '.join(cmd_parts)}")
            
            # Call original with modified command
            import subprocess
            import shlex
            import time
            
            try:
                with open(run.log_file, 'w') as log_f:
                    run.process = subprocess.Popen(
                        cmd_parts,
                        stdout=log_f,
                        stderr=subprocess.STDOUT,
                        text=True,
                        cwd=temp_dir,
                        env=env
                    )
                    
                    run.process.wait()
                
                # Give a moment for the file to be written
                time.sleep(0.1)
                
                # Read the output
                with open(run.log_file, 'r') as log_f:
                    run.output = log_f.read()
                
                if run.process.returncode != 0:
                    raise RuntimeError(f"Codex command failed with return code {run.process.returncode}")
                    
            except Exception as e:
                raise RuntimeError(f"Failed to execute Codex command: {e}")
        
        run._execute_codex = modified_execute
        
        result = run.execute(log_dir=temp_dir)
        
        print(f'Success: {result.success}')
        print(f'Duration: {result.duration:.1f}s')
        
        # Check if file was created
        test_file = os.path.join(temp_dir, 'test2.txt')
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            print(f'File created successfully with content: {repr(content)}')
            return True
        else:
            print('File was NOT created')
            
        # Show log file content for debugging
        if result.log_file and os.path.exists(result.log_file):
            print(f'\nLog file: {result.log_file}')
            with open(result.log_file, 'r') as f:
                log_content = f.read()
            print('Last 5 lines of log:')
            print('\n'.join(log_content.split('\n')[-5:]))
            
        return False

if __name__ == "__main__":
    success1 = test_sandbox_disabled()
    success2 = test_with_777_permissions()
    success3 = test_with_different_flags()
    
    print(f"\nResults:")
    print(f"Standard test (700 perms): {'PASSED' if success1 else 'FAILED'}")
    print(f"777 permissions test: {'PASSED' if success2 else 'FAILED'}")
    print(f"Modified flags test (777): {'PASSED' if success3 else 'FAILED'}")
    print(f"Overall: {'PASSED' if (success1 or success2 or success3) else 'FAILED'}") 