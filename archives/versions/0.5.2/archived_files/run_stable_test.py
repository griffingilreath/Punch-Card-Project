#!/usr/bin/env python3
"""
Stable Test Script for Punch Card Terminal Display
This script demonstrates the enhanced terminal display with the punch card system.
"""

import os
import sys
import time
import argparse
import random
from typing import List, Tuple, Dict, Any, Optional

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import from the src directory
from terminal_display import TerminalDisplay, CharacterSet
from display_adapter import PunchCardDisplayAdapter

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Stable Test for Punch Card Terminal Display")
    parser.add_argument("--char-set", default="default", choices=["default", "block", "circle", "star", "ascii"],
                        help="Character set to use for LED visualization")
    parser.add_argument("--test", default="all", choices=["minimal", "simple", "hardware", "direct", "animations", "all"],
                        help="Test to run")
    parser.add_argument("--use-ui", action="store_true", help="Use UI for visualization")
    parser.add_argument("--verbose", action="store_true", help="Print verbose output")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between updates (seconds)")
    return parser.parse_args()

def run_minimal_test(adapter, delay):
    """Run a minimal test to verify the adapter works."""
    adapter.log_message("Running minimal test", "info")
    
    # Test 1: Set a single LED
    adapter.set_led(0, 0, True)
    time.sleep(delay)
    
    # Test 2: Set another LED
    adapter.set_led(11, 79, True)
    time.sleep(delay)
    
    # Test 3: Clear all LEDs
    adapter.clear_all()
    time.sleep(delay)
    
    adapter.log_message("Minimal test completed successfully", "info")

def run_simple_test(adapter, delay):
    """Run a simple test with basic patterns."""
    adapter.log_message("Running simple test", "info")
    
    # Test 1: Horizontal line
    for col in range(adapter.num_cols):
        adapter.set_led(5, col, True)
        time.sleep(delay / 10)  # Faster animation
    
    time.sleep(delay)
    
    # Test 2: Vertical line
    adapter.clear_all()
    for row in range(adapter.num_rows):
        adapter.set_led(row, 40, True)
        time.sleep(delay / 10)  # Faster animation
    
    time.sleep(delay)
    
    # Test 3: Checkerboard pattern
    adapter.clear_all()
    for row in range(adapter.num_rows):
        for col in range(adapter.num_cols):
            if (row + col) % 2 == 0:
                adapter.set_led(row, col, True)
    
    time.sleep(delay)
    
    # Test 4: Clear all LEDs
    adapter.clear_all()
    time.sleep(delay)
    
    adapter.log_message("Simple test completed successfully", "info")

def run_hardware_test(adapter, delay):
    """Run a hardware verification test."""
    adapter.log_message("Running hardware verification test", "info")
    
    # Test 1: Border pattern
    adapter.log_message("Test 1: Border pattern", "debug")
    
    # Top and bottom borders
    for col in range(adapter.num_cols):
        adapter.set_led(0, col, True)
        adapter.set_led(adapter.num_rows - 1, col, True)
    
    # Left and right borders
    for row in range(adapter.num_rows):
        adapter.set_led(row, 0, True)
        adapter.set_led(row, adapter.num_cols - 1, True)
    
    time.sleep(delay)
    
    # Test 2: Diagonal pattern
    adapter.log_message("Test 2: Diagonal pattern", "debug")
    adapter.clear_all()
    
    # Main diagonal
    for i in range(min(adapter.num_rows, adapter.num_cols)):
        adapter.set_led(i, i, True)
    
    # Secondary diagonal
    for i in range(min(adapter.num_rows, adapter.num_cols)):
        if i < adapter.num_rows and (adapter.num_cols - 1 - i) >= 0:
            adapter.set_led(i, adapter.num_cols - 1 - i, True)
    
    time.sleep(delay)
    
    # Test 3: Letters "LED"
    adapter.log_message("Test 3: Letters LED", "debug")
    adapter.clear_all()
    
    # Letter L
    for row in range(2, 10):
        adapter.set_led(row, 10, True)
    for col in range(10, 15):
        adapter.set_led(9, col, True)
    
    # Letter E
    for row in range(2, 10):
        adapter.set_led(row, 20, True)
    for col in range(20, 25):
        adapter.set_led(2, col, True)
        adapter.set_led(5, col, True)
        adapter.set_led(9, col, True)
    
    # Letter D
    for row in range(2, 10):
        adapter.set_led(row, 30, True)
    for i in range(3):
        adapter.set_led(2, 31 + i, True)
        adapter.set_led(9, 31 + i, True)
    adapter.set_led(3, 33, True)
    adapter.set_led(4, 34, True)
    adapter.set_led(5, 34, True)
    adapter.set_led(6, 34, True)
    adapter.set_led(7, 34, True)
    adapter.set_led(8, 33, True)
    
    time.sleep(delay * 2)
    
    # Clear all LEDs
    adapter.clear_all()
    time.sleep(delay)
    
    adapter.log_message("Hardware verification test completed successfully", "info")

def run_direct_test(adapter, delay):
    """Run a direct test with LED pattern animations."""
    adapter.log_message("Running direct test", "info")
    
    # Test 1: Random lights
    adapter.log_message("Test 1: Random lights", "debug")
    
    for _ in range(100):
        row = random.randint(0, adapter.num_rows - 1)
        col = random.randint(0, adapter.num_cols - 1)
        state = random.choice([True, False])
        adapter.set_led(row, col, state)
        time.sleep(delay / 10)  # Faster animation
    
    time.sleep(delay)
    
    # Test 2: Wave pattern
    adapter.log_message("Test 2: Wave pattern", "debug")
    adapter.clear_all()
    
    import math
    for frame in range(50):
        adapter.clear_all()
        for col in range(adapter.num_cols):
            # Sine wave
            sin_val = math.sin(col / 10 + frame / 5)
            row = int((sin_val + 1) * (adapter.num_rows - 1) / 2)
            adapter.set_led(row, col, True)
        time.sleep(delay / 5)  # Faster animation
    
    # Test 3: Spiral pattern
    adapter.log_message("Test 3: Spiral pattern", "debug")
    adapter.clear_all()
    
    center_row = adapter.num_rows // 2
    center_col = adapter.num_cols // 2
    
    for radius in range(1, 25):
        for angle in range(0, 360, 10):
            rad = math.radians(angle)
            row = int(center_row + radius * math.sin(rad))
            col = int(center_col + radius * math.cos(rad) * 2)  # Adjust for aspect ratio
            
            if 0 <= row < adapter.num_rows and 0 <= col < adapter.num_cols:
                adapter.set_led(row, col, True)
        
        time.sleep(delay / 2)  # Medium animation speed
    
    time.sleep(delay)
    
    # Clear all LEDs
    adapter.clear_all()
    time.sleep(delay)
    
    adapter.log_message("Direct test completed successfully", "info")

def run_animations_test(adapter, delay):
    """Run animations test with predefined patterns."""
    adapter.log_message("Running animations test", "info")
    
    # Test 1: Splash animation (PC - Punch Card)
    adapter.log_message("Test 1: Splash animation", "debug")
    
    # Define splash animation frames
    splash_frames = []
    
    # Frame 1: Empty
    frame1 = [[False for _ in range(adapter.num_cols)] for _ in range(adapter.num_rows)]
    splash_frames.append(frame1)
    
    # Letter P
    frame2 = [[False for _ in range(adapter.num_cols)] for _ in range(adapter.num_rows)]
    for row in range(2, 10):
        frame2[row][15] = True
    for col in range(15, 20):
        frame2[2][col] = True
        frame2[5][col] = True
    frame2[3][20] = True
    frame2[4][20] = True
    splash_frames.append(frame2)
    
    # Letter P+C
    frame3 = [[False for _ in range(adapter.num_cols)] for _ in range(adapter.num_rows)]
    # Copy P from frame2
    for row in range(adapter.num_rows):
        for col in range(adapter.num_cols):
            frame3[row][col] = frame2[row][col]
    
    # Add letter C
    for row in range(2, 10):
        if row not in [2, 9]:
            frame3[row][25] = True
    for col in range(25, 30):
        frame3[2][col] = True
        frame3[9][col] = True
    splash_frames.append(frame3)
    
    # Show the splash animation
    for frame in splash_frames:
        adapter.update_grid_from_punch_card(frame)
        time.sleep(delay * 2)  # Slower animation
    
    time.sleep(delay)
    
    # Test 2: Spinner animation
    adapter.log_message("Test 2: Spinner animation", "debug")
    
    center_row = adapter.num_rows // 2
    center_col = adapter.num_cols // 2
    radius = 5
    
    for angle in range(0, 720, 10):  # Two complete rotations
        adapter.clear_all()
        
        # Draw spinner
        rad = math.radians(angle)
        row = int(center_row + radius * math.sin(rad))
        col = int(center_col + radius * math.cos(rad) * 2)  # Adjust for aspect ratio
        
        if 0 <= row < adapter.num_rows and 0 <= col < adapter.num_cols:
            adapter.set_led(row, col, True)
            
            # Add a trail effect
            for trail in range(1, 5):
                trail_angle = angle - trail * 10
                trail_rad = math.radians(trail_angle)
                trail_row = int(center_row + radius * math.sin(trail_rad))
                trail_col = int(center_col + radius * math.cos(trail_rad) * 2)
                
                if 0 <= trail_row < adapter.num_rows and 0 <= trail_col < adapter.num_cols:
                    adapter.set_led(trail_row, trail_col, True)
        
        time.sleep(delay / 2)  # Medium speed animation
    
    time.sleep(delay)
    
    # Clear all LEDs
    adapter.clear_all()
    time.sleep(delay)
    
    adapter.log_message("Animations test completed successfully", "info")

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_args()
    
    try:
        # Create the display adapter
        adapter = PunchCardDisplayAdapter(
            num_rows=12,
            num_cols=80,
            verbose=args.verbose,
            char_set_name=args.char_set,
            use_ui=args.use_ui
        )
        
        # Run the selected test(s)
        try:
            if args.test in ["minimal", "all"]:
                run_minimal_test(adapter, args.delay)
                
            if args.test in ["simple", "all"]:
                run_simple_test(adapter, args.delay)
                
            if args.test in ["hardware", "all"]:
                run_hardware_test(adapter, args.delay)
                
            if args.test in ["direct", "all"]:
                run_direct_test(adapter, args.delay)
                
            if args.test in ["animations", "all"]:
                run_animations_test(adapter, args.delay)
            
            # Final test complete message
            adapter.log_message(f"All selected tests completed successfully: {args.test}", "info")
            
            # Wait a moment for the final message to be seen
            time.sleep(1)
            
        finally:
            # Always clean up
            adapter.cleanup()
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running test: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 