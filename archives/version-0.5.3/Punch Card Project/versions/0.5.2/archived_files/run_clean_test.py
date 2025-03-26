#!/usr/bin/env python3
"""
Clean test runner for Punch Card Project.
This script runs the original test_leds.py command but redirects output
to prevent the glitchy terminal display issue.
"""

import os
import sys
import subprocess
import argparse

def main():
    """Run the test with clean output handling."""
    parser = argparse.ArgumentParser(description='Clean test runner for Punch Card Project')
    parser.add_argument('--test', choices=['minimal', 'simple', 'hardware', 'direct', 'integration', 'animations', 'all'],
                      default='all', help='Test to run')
    parser.add_argument('--char-set', choices=['default', 'block', 'circle', 'star', 'ascii'],
                      default='default', help='Character set to use for LED visualization')
    parser.add_argument('--verbose', action='store_true', default=False,
                      help='Print verbose output')
    
    args = parser.parse_args()
    
    # Find the test_leds.py file
    script_path = os.path.dirname(os.path.abspath(__file__))
    custom_cmd_args = []
    
    # Prepare the command to run
    if os.path.isfile(os.path.join(script_path, 'test_leds.py')):
        test_script = os.path.join(script_path, 'test_leds.py')
    else:
        print("Error: Cannot find test_leds.py. Using built-in test functions instead.")
        
        # Import functions from our stable test runner
        from run_stable_test import (
            test_minimal_led, 
            test_simple_led, 
            test_direct_led_control,
            test_hardware_verification,
            test_animations,
            test_punch_card_integration_stable
        )
        
        # Run the requested test directly
        if args.test == 'minimal':
            test_minimal_led()
        elif args.test == 'simple':
            test_simple_led()
        elif args.test == 'hardware':
            test_hardware_verification()
        elif args.test == 'direct':
            test_direct_led_control()
        elif args.test == 'animations':
            test_animations()
        elif args.test == 'integration':
            test_punch_card_integration_stable()
        elif args.test == 'all':
            print("Running all tests...\n")
            test_minimal_led()
            print()
            test_simple_led()
            print()
            test_direct_led_control()
            print()
            test_hardware_verification()
            print()
            test_animations()
            print()
            test_punch_card_integration_stable()
            print("\nAll tests completed successfully!")
        
        return 0
    
    # Set up environment variables to disable curses and other terminal UI
    # that might cause glitchy display behavior
    env = os.environ.copy()
    env['TERM'] = 'dumb'  # Set a basic terminal type to disable fancy features
    env['FORCE_CONSOLE'] = '1'  # Force console output instead of UI
    
    # Build the command line arguments
    cmd_args = [sys.executable, test_script, '--test', args.test]
    
    # Add character set if specified
    cmd_args.extend(['--char-set', args.char_set])
    
    # Add verbose flag if specified
    if args.verbose:
        cmd_args.append('--verbose')
    
    # Run the command with buffered output to prevent display glitches
    print(f"Running: {' '.join(cmd_args)}")
    process = subprocess.Popen(
        cmd_args,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )
    
    # Process and print the output line by line
    for line in process.stdout:
        print(line.rstrip())
    
    # Print any errors
    stderr_output = process.stderr.read()
    if stderr_output:
        print("Errors:")
        print(stderr_output)
    
    # Wait for the process to complete and get the return code
    return_code = process.wait()
    
    if return_code == 0:
        print("\nTest completed successfully!")
    else:
        print(f"\nTest failed with return code {return_code}")
    
    return return_code

if __name__ == "__main__":
    sys.exit(main()) 