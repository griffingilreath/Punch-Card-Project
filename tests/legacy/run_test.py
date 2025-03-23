#!/usr/bin/env python3
"""
Punch Card Test Runner

This script is a wrapper for running either the original test_leds.py script,
the new run_stable_test.py script, or the enhanced_punch_card.py script based on command line arguments.
"""

import os
import sys
import argparse
import subprocess

# Default constants
DEFAULT_LED_DELAY = 0.05
DEFAULT_MESSAGE_DELAY = 0.2

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Punch Card Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run stable test with hardware verification
  python3 run_test.py --stable --test hardware --char-set circle --use-ui
  
  # Run original test with animations
  python3 run_test.py --test animations --char-set ascii --use-ui
  
  # Run integration test with a custom message
  python3 run_test.py --integration --message "HELLO WORLD" --char-set block --use-ui
  
  # Run enhanced punch card with demo mode
  python3 run_test.py --enhanced --demo --char-set ascii --use-ui
  
  # Run quick message display with instant mode
  python3 run_test.py --quick-message --message "FAST TEST" --instant
  
  # Run full message display with settings and splash screen
  python3 run_test.py --full --message "COMPREHENSIVE TEST" --char-set ascii
        """
    )
    
    parser.add_argument("--stable", action="store_true", 
                        help="Use the stable version of the test script")
    parser.add_argument("--integration", action="store_true",
                        help="Run the integration test")
    parser.add_argument("--enhanced", action="store_true",
                        help="Run the enhanced punch card script")
    parser.add_argument("--quick-message", action="store_true",
                        help="Run the quick message display script")
    parser.add_argument("--full", action="store_true",
                        help="Run the full message display with settings and splash screen")
    parser.add_argument("--test", default="all",
                        choices=["minimal", "simple", "hardware", "direct", "animations", "all"],
                        help="Test to run")
    parser.add_argument("--char-set", default="default",
                        choices=["default", "block", "circle", "star", "ascii"],
                        help="Character set to use for LED visualization")
    parser.add_argument("--use-ui", action="store_true",
                        help="Use UI for visualization")
    parser.add_argument("--verbose", action="store_true",
                        help="Print verbose output")
    parser.add_argument("--message", type=str, default="HELLO WORLD!",
                        help="Message to display (integration test only)")
    parser.add_argument("--source", type=str, default="Test Script",
                        help="Source of the message (integration test only)")
    parser.add_argument("--skip-splash", action="store_true",
                        help="Skip splash screen (integration test only)")
    parser.add_argument("--fast-mode", action="store_true",
                        help="Run in fast mode with minimal delays (integration test only)")
    parser.add_argument("--demo", action="store_true",
                        help="Run demonstration mode (enhanced mode only)")
    parser.add_argument("--force-console", action="store_true",
                        help="Force console mode (no curses UI)")
    parser.add_argument("--quick", action="store_true",
                        help="Run in quick mode with minimal delays (quick message display only)")
    parser.add_argument("--instant", action="store_true",
                        help="Run in instant mode with no delays (quick message display only)")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug mode")
    parser.add_argument("--minimal", action="store_true",
                        help="Use minimal output mode (cleaner display)")
    parser.add_argument("--led-delay", type=float, default=DEFAULT_LED_DELAY,
                        help="Delay between LED updates (seconds)")
    parser.add_argument("--message-delay", type=float, default=DEFAULT_MESSAGE_DELAY,
                        help="Delay between message characters (seconds)")
    
    return parser.parse_args()

def build_command(args):
    """Build the command to run based on the arguments."""
    # Determine the base command
    if args.integration:
        base_cmd = ["python3", "src/integration_test.py"]
    elif args.stable:
        base_cmd = ["python3", "run_stable_test.py"]
    elif args.enhanced:
        base_cmd = ["python3", "enhanced_punch_card.py"]
    elif args.quick_message:
        base_cmd = ["python3", "quick_message.py"]
    elif args.full:
        base_cmd = ["python3", "full_message_display.py"]
    else:
        base_cmd = ["python3", "test_leds.py"]
    
    # Add common arguments
    if args.test != "all" and not args.integration and not args.enhanced and not args.quick_message and not args.full:
        base_cmd.extend(["--test", args.test])
    
    if args.char_set != "default":
        base_cmd.extend(["--char-set", args.char_set])
    
    if args.use_ui and not args.quick_message:  # quick_message doesn't use UI
        base_cmd.append("--use-ui")
    
    if args.verbose and not args.quick_message:  # quick_message is always non-verbose
        base_cmd.append("--verbose")
    
    # Add integration-specific arguments
    if args.integration or args.enhanced or args.full:
        if args.message:
            base_cmd.extend(["--message", args.message])
        
        if args.skip_splash:
            base_cmd.append("--skip-splash")
    
    # Message is required for quick message display
    if args.quick_message:
        if args.message:
            base_cmd.extend(["--message", args.message])
        else:
            # Default message if none provided
            base_cmd.extend(["--message", "QUICK MESSAGE TEST"])
        
        if args.quick:
            base_cmd.append("--quick")
        
        if args.instant:
            base_cmd.append("--instant")
    
    # Add full message display specific arguments
    if args.full:
        if args.quick:
            base_cmd.append("--quick")
        
        if args.instant:
            base_cmd.append("--instant")
        
        if args.debug:
            base_cmd.append("--debug")
        
        if args.minimal:
            base_cmd.append("--minimal")
    
    if args.integration:
        base_cmd.extend(["--source", args.source])
        
        if args.fast_mode:
            base_cmd.append("--fast-mode")
    
    # Add enhanced mode-specific arguments
    if (args.enhanced or args.full) and args.demo:
        base_cmd.append("--demo")
    
    # Set up environment variable for console mode if requested
    if args.force_console:
        os.environ['FORCE_CONSOLE'] = '1'
    
    return base_cmd

def main():
    """Main function."""
    args = parse_args()
    
    try:
        # Build the command
        cmd = build_command(args)
        
        # Print the command for reference
        print(f"Running command: {' '.join(cmd)}")
        
        # Run the command
        result = subprocess.run(cmd)
        
        # Return the exit code
        return result.returncode
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running test: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 