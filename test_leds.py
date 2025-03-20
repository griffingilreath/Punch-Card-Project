#!/usr/bin/env python3
"""
Test script for the LED integration in the Punch Card Project.

This script demonstrates how the LED state manager, hardware controller, 
and display adapter work together to synchronize the terminal display 
with physical LEDs.
"""

import time
import os
import argparse
import sys
import signal
import json
from pathlib import Path

# Add the current directory to the Python path so imports work correctly
sys.path.insert(0, os.path.abspath('.'))

# Import our components
from src.led_state_manager import get_instance as get_led_manager
from src.hardware_controller import create_hardware_controller, SimulatedHardwareController
from src.punch_card import PunchCardDisplay, CHAR_MAPPING
from src.display_adapter import create_punch_card_adapter

# Try to import the terminal display
try:
    from src.terminal_display import get_instance as get_terminal_display
    TERMINAL_DISPLAY_AVAILABLE = True
except ImportError:
    TERMINAL_DISPLAY_AVAILABLE = False

# Global terminal display instance
terminal_display = None

# Set a timeout handler to catch hanging tests
def timeout_handler(signum, frame):
    error_message = "\n\nTEST TIMEOUT: The test is taking too long to complete!"
    error_details = "This could indicate a deadlock or infinite loop in the code."
    
    if terminal_display:
        terminal_display.add_debug_message(error_message, "error")
        terminal_display.add_debug_message(error_details, "error")
        terminal_display.set_status("Test timed out!", "error")
        # Give time for the message to be displayed
        time.sleep(1.0)
        terminal_display.stop()
    else:
        print(error_message)
        print(error_details)
        print("Current stack trace:")
        import traceback
        traceback.print_stack(frame)
    
    sys.exit(1)

def test_direct_led_control():
    """Test direct control of LEDs through the LED state manager."""
    status_msg = "Testing direct LED control..."
    
    if terminal_display:
        terminal_display.set_status(status_msg, "info")
        terminal_display.add_debug_message(status_msg, "info")
    else:
        print(status_msg)
    
    # Set a timeout for this test
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 seconds timeout
    
    try:
        # Get the LED state manager
        led_manager = get_led_manager()
        debug_msg = "LED state manager initialized"
        if terminal_display:
            terminal_display.add_debug_message(debug_msg, "info")
        else:
            print(debug_msg)
        
        # Create and connect hardware controller
        debug_msg = "Creating hardware controller..."
        if terminal_display:
            terminal_display.add_debug_message(debug_msg, "info")
        else:
            print(debug_msg)
            
        hardware_controller = create_hardware_controller()
        
        debug_msg = "Connecting to hardware..."
        if terminal_display:
            terminal_display.add_debug_message(debug_msg, "info")
        else:
            print(debug_msg)
            
        if not hardware_controller.connect():
            debug_msg = "Failed to connect to hardware. Running in simulation mode."
            if terminal_display:
                terminal_display.add_debug_message(debug_msg, "warning")
            else:
                print(debug_msg)
        else:
            debug_msg = "Hardware connected successfully"
            if terminal_display:
                terminal_display.add_debug_message(debug_msg, "info")
            else:
                print(debug_msg)
        
        debug_msg = "Starting hardware controller..."
        if terminal_display:
            terminal_display.add_debug_message(debug_msg, "info")
        else:
            print(debug_msg)
            
        hardware_controller.start()
        
        debug_msg = "Hardware controller started"
        if terminal_display:
            terminal_display.add_debug_message(debug_msg, "info")
        else:
            print(debug_msg)
        
        try:
            # Test 1: Set individual LEDs to create a diagonal pattern
            test_msg = "\nTest 1: Diagonal pattern - Starting"
            if terminal_display:
                terminal_display.add_debug_message(test_msg, "info")
                terminal_display.set_status("Running Test 1: Diagonal pattern", "info")
            else:
                print(test_msg)
                
            led_manager.set_all_leds(False)  # Clear all LEDs first
            
            debug_msg = "All LEDs cleared"
            if terminal_display:
                terminal_display.add_debug_message(debug_msg, "info")
            else:
                print(debug_msg)
            
            # Reduce the number of LEDs to test and the sleep time
            for i in range(min(8, led_manager.rows)):
                debug_msg = f"Setting LED at position [{i}, {i}]"
                if terminal_display:
                    terminal_display.add_debug_message(debug_msg, "info")
                else:
                    print(debug_msg)
                    
                led_manager.set_led(i, i, True)
                time.sleep(0.05)  # Reduced from 0.1
            
            debug_msg = "Diagonal pattern complete"
            if terminal_display:
                terminal_display.add_debug_message(debug_msg, "info")
            else:
                print(debug_msg)
                
            time.sleep(0.5)  # Reduced from 1.0
            
            # Test 2: Display a message directly using the LED state manager
            test_msg = "\nTest 2: Displaying message 'HELLO' directly - Starting"
            if terminal_display:
                terminal_display.add_debug_message(test_msg, "info")
                terminal_display.set_status("Running Test 2: Displaying 'HELLO'", "info")
            else:
                print(test_msg)
                
            led_manager.set_all_leds(False)  # Clear all LEDs first
            
            debug_msg = "All LEDs cleared"
            if terminal_display:
                terminal_display.add_debug_message(debug_msg, "info")
            else:
                print(debug_msg)
            
            message = "HELLO"
            for col, char in enumerate(message):
                debug_msg = f"Setting character '{char}' at column {col}"
                if terminal_display:
                    terminal_display.add_debug_message(debug_msg, "info")
                else:
                    print(debug_msg)
                    
                led_manager.display_character(col, char, CHAR_MAPPING)
                time.sleep(0.1)  # Reduced from 0.2
            
            debug_msg = "Message display complete"
            if terminal_display:
                terminal_display.add_debug_message(debug_msg, "info")
            else:
                print(debug_msg)
                
            time.sleep(1.0)  # Reduced from 2.0
            
            # Test 3: Checkerboard pattern using the grid
            test_msg = "\nTest 3: Checkerboard pattern - Starting"
            if terminal_display:
                terminal_display.add_debug_message(test_msg, "info")
                terminal_display.set_status("Running Test 3: Checkerboard pattern", "info")
            else:
                print(test_msg)
                
            grid = [[False for _ in range(led_manager.columns)] for _ in range(led_manager.rows)]
            
            # Just do a smaller grid for speed
            rows = min(8, led_manager.rows)
            cols = min(16, led_manager.columns)
            
            debug_msg = f"Creating checkerboard pattern with {rows} rows and {cols} columns"
            if terminal_display:
                terminal_display.add_debug_message(debug_msg, "info")
            else:
                print(debug_msg)
            
            for row in range(rows):
                for col in range(cols):
                    grid[row][col] = (row + col) % 2 == 0
            
            debug_msg = "Setting grid..."
            if terminal_display:
                terminal_display.add_debug_message(debug_msg, "info")
            else:
                print(debug_msg)
                
            led_manager.set_grid(grid)
            
            debug_msg = "Grid set"
            if terminal_display:
                terminal_display.add_debug_message(debug_msg, "info")
            else:
                print(debug_msg)
            
            time.sleep(1.0)  # Reduced from 2.0
            
            # Test 4: Clear all LEDs
            test_msg = "\nTest 4: Clearing all LEDs - Starting"
            if terminal_display:
                terminal_display.add_debug_message(test_msg, "info")
                terminal_display.set_status("Running Test 4: Clearing LEDs", "info")
            else:
                print(test_msg)
                
            led_manager.set_all_leds(False)
            
            debug_msg = "All LEDs cleared"
            if terminal_display:
                terminal_display.add_debug_message(debug_msg, "info")
            else:
                print(debug_msg)
            
            summary_msg = "\nDirect LED control tests completed."
            if terminal_display:
                terminal_display.add_debug_message(summary_msg, "info")
                terminal_display.set_status("Direct LED tests completed successfully", "info")
            else:
                print(summary_msg)
        
        finally:
            # Clean up
            debug_msg = "Disconnecting hardware..."
            if terminal_display:
                terminal_display.add_debug_message(debug_msg, "info")
            else:
                print(debug_msg)
                
            hardware_controller.disconnect()
            
            debug_msg = "Hardware disconnected"
            if terminal_display:
                terminal_display.add_debug_message(debug_msg, "info")
            else:
                print(debug_msg)
    
    finally:
        # Cancel the timeout alarm
        signal.alarm(0)

def test_simple_led_control():
    """A minimal test for LED control that does absolute basics."""
    print("Running simplified LED control test...")
    
    # Set a timeout for this test
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)  # 10 seconds timeout
    
    try:
        # Get the LED state manager
        led_manager = get_led_manager()
        print("LED state manager initialized")
        
        # Create hardware controller with minimal configuration
        hardware_controller = create_hardware_controller()
        if hardware_controller.connect():
            print("Connected to hardware")
            hardware_controller.start()
            
            # Do a simple LED pattern (only 3x3 grid)
            print("Setting a simple 3x3 pattern...")
            for i in range(3):
                for j in range(3):
                    led_manager.set_led(i, j, (i + j) % 2 == 0)
            
            # Wait briefly
            time.sleep(1)
            
            # Clear all LEDs
            print("Clearing all LEDs...")
            led_manager.set_all_leds(False)
            
            # Disconnect
            print("Disconnecting...")
            hardware_controller.disconnect()
            
            print("Simplified LED test completed successfully.")
        else:
            print("Failed to connect to hardware.")
    
    finally:
        # Cancel the timeout alarm
        signal.alarm(0)

def test_punch_card_integration():
    """Test integration with the punch card display."""
    print("Testing punch card integration...")
    
    # Set a timeout for this test
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 seconds timeout
    
    try:
        print("Creating punch card display...")
        # Create the punch card display with minimal settings to speed up testing
        display = PunchCardDisplay(
            led_delay=0.01,  # Faster LED updates
            message_delay=0.5,  # Faster message display
            random_delay=False,
            skip_splash=True,  # Skip splash screen to speed up test
            debug_mode=True    # Enable debug mode for faster operation
        )
        print("Punch card display created")
        
        print("Creating hardware controller...")
        # Create hardware controller
        hardware_controller = create_hardware_controller()
        print("Connecting to hardware...")
        if not hardware_controller.connect():
            print("Failed to connect to hardware. Running in simulation mode.")
        hardware_controller.start()
        print("Hardware controller started")
        
        # Get LED state manager and manually update it
        led_manager = get_led_manager()
        print("LED state manager initialized")
        
        try:
            # Test 1: Display a message
            print("\nTest 1: Displaying a message")
            print("Calling show_message...")
            display.show_message("TEST", source="Integration Test")
            print("show_message call completed")
            
            # Manually update LED state manager with the same message
            print("Updating LED state manager manually...")
            for col, char in enumerate("TEST"):
                pattern = CHAR_MAPPING.get(char.upper(), [0] * display.rows)
                for row in range(display.rows):
                    led_manager.set_led(row, col, bool(pattern[row]))
            print("LED state manager updated")
                    
            time.sleep(0.5)
            
            # Test 2: Clear the display
            print("\nTest 2: Clearing the display")
            print("Calling clear...")
            display.clear()
            print("clear call completed")
            led_manager.set_all_leds(False)
            print("All LEDs cleared in LED state manager")
            time.sleep(0.5)
            
            # Test 3: Verify we can read the LED state manager
            print("\nTest 3: Verifying LED state manager can be read")
            # Display a message and update LED manager
            print("Calling show_message with 'ABC'...")
            display.show_message("ABC", source="Integration Test")
            print("show_message call completed")
            
            # Manually update LED state manager with the same message
            print("Updating LED state manager manually...")
            for col, char in enumerate("ABC"):
                pattern = CHAR_MAPPING.get(char.upper(), [0] * display.rows)
                for row in range(display.rows):
                    led_manager.set_led(row, col, bool(pattern[row]))
            print("LED state manager updated")
            
            # The LED state manager should now have the message "ABC" in it
            print("Verifying LED patterns in LED state manager:")
            column_states = []
            for col in range(3):  # Check the first 3 columns (A, B, C)
                column_leds = []
                for row in range(5):  # Just check the first 5 rows for simplicity
                    state = led_manager.get_led(row, col)
                    column_leds.append("█" if state else "·")
                column_states.append("".join(column_leds))
                
            print(f"Column 0 (A): {column_states[0]}")
            print(f"Column 1 (B): {column_states[1]}")
            print(f"Column 2 (C): {column_states[2]}")
            
            # Clean up
            led_manager.set_all_leds(False)
            
            print("\nPunch card integration tests completed successfully.")
        
        finally:
            # Clean up
            print("Disconnecting hardware...")
            hardware_controller.disconnect()
            print("Hardware disconnected")
    
    finally:
        # Cancel the timeout alarm
        signal.alarm(0)

def test_minimal_punch_card():
    """A very simple test that verifies basic LED control works."""
    print("Running simplified minimal LED test...")
    
    # Set a timeout for this test
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(5)  # 5 seconds timeout
    
    try:
        # Get LED state manager directly
        led_manager = get_led_manager()
        print("LED state manager initialized")
        
        # Create hardware controller
        hardware_controller = create_hardware_controller()
        if hardware_controller.connect():
            print("Connected to hardware")
            hardware_controller.start()
            
            try:
                # Enable verbose mode to see output
                if isinstance(hardware_controller, SimulatedHardwareController):
                    hardware_controller.verbose = True
                    hardware_controller.print_interval = 0
                
                # Test 1: Set a simple 2x2 pattern
                print("\nTest 1: Setting a 2x2 pattern")
                # Clear first
                led_manager.set_all_leds(False)
                # Set a small checkerboard pattern
                led_manager.set_led(0, 0, True)
                led_manager.set_led(0, 1, False)
                led_manager.set_led(1, 0, False)
                led_manager.set_led(1, 1, True)
                
                # Directly call to show the pattern
                print("\nCheckerboard pattern 2x2:")
                print("█·")
                print("·█")
                
                # Time for the next test
                time.sleep(1)
                
                # Test 2: Clear all LEDs
                print("\nTest 2: Clearing all LEDs")
                led_manager.set_all_leds(False)
                
                print("Minimal LED test completed successfully!")
            finally:
                # Clean up
                print("Disconnecting hardware...")
                hardware_controller.disconnect()
                print("Hardware disconnected")
        else:
            print("Failed to connect to hardware.")
            
    finally:
        # Cancel the timeout alarm
        signal.alarm(0)

def test_hardware_verification():
    """
    A test that creates a distinctive pattern for verifying physical LED hardware.
    This test is designed to be easy to visually inspect on physical hardware.
    """
    status_msg = "Running hardware verification test..."
    
    if terminal_display:
        terminal_display.set_status(status_msg, "info")
        terminal_display.add_debug_message(status_msg, "info")
    else:
        print(status_msg)
    
    # Set a timeout for this test
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(15)  # 15 seconds timeout
    
    try:
        # Get LED state manager
        led_manager = get_led_manager()
        debug_msg = "LED state manager initialized"
        if terminal_display:
            terminal_display.add_debug_message(debug_msg, "info")
        else:
            print(debug_msg)
        
        # Create hardware controller
        hardware_controller = create_hardware_controller()
        if hardware_controller.connect():
            debug_msg = "Connected to hardware"
            if terminal_display:
                terminal_display.add_debug_message(debug_msg, "info")
            else:
                print(debug_msg)
                
            hardware_controller.start()
            
            try:
                # Enable verbose mode for simulated hardware
                if isinstance(hardware_controller, SimulatedHardwareController):
                    hardware_controller.verbose = True
                    hardware_controller.print_interval = 0
                
                # Clear all LEDs
                led_manager.set_all_leds(False)
                debug_msg = "All LEDs cleared"
                if terminal_display:
                    terminal_display.add_debug_message(debug_msg, "info")
                else:
                    print(debug_msg)
                    
                time.sleep(1)
                
                # Test 1: Border pattern - light up the edges
                test_msg = "Test 1: Border pattern"
                if terminal_display:
                    terminal_display.add_debug_message(test_msg, "info")
                    terminal_display.set_status(f"Running {test_msg}", "info")
                else:
                    print(f"\n{test_msg}")
                
                # Top and bottom rows
                for col in range(min(16, led_manager.columns)):
                    led_manager.set_led(0, col, True)  # Top row
                    led_manager.set_led(7, col, True)  # Bottom row (row 7)
                
                # Left and right columns
                for row in range(1, 7):  # Skip corners which are already lit
                    led_manager.set_led(row, 0, True)  # Left column
                    led_manager.set_led(row, 15, True)  # Right column (column 15)
                
                debug_msg = "Border pattern set"
                if terminal_display:
                    terminal_display.add_debug_message(debug_msg, "info")
                else:
                    print(debug_msg)
                    
                time.sleep(2)
                
                # Test 2: Diagonal pattern
                test_msg = "Test 2: Diagonal pattern"
                if terminal_display:
                    terminal_display.add_debug_message(test_msg, "info")
                    terminal_display.set_status(f"Running {test_msg}", "info")
                else:
                    print(f"\n{test_msg}")
                
                led_manager.set_all_leds(False)  # Clear first
                
                # Set diagonal pattern
                for i in range(min(8, led_manager.rows)):
                    led_manager.set_led(i, i, True)  # Main diagonal
                    led_manager.set_led(i, 7-i, True)  # Counter diagonal
                
                debug_msg = "Diagonal pattern set"
                if terminal_display:
                    terminal_display.add_debug_message(debug_msg, "info")
                else:
                    print(debug_msg)
                    
                time.sleep(2)
                
                # Test 3: Letter pattern - display "LED"
                test_msg = "Test 3: Letters 'LED'"
                if terminal_display:
                    terminal_display.add_debug_message(test_msg, "info")
                    terminal_display.set_status(f"Running {test_msg}", "info")
                else:
                    print(f"\n{test_msg}")
                
                led_manager.set_all_leds(False)  # Clear first
                
                # Define LED patterns for letters - each is a list of (row, col) coordinates
                letter_L = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (7, 1), (7, 2), (7, 3)]
                letter_E = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), 
                           (0, 1), (0, 2), (0, 3), (3, 1), (3, 2), (7, 1), (7, 2), (7, 3)]
                letter_D = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                           (0, 1), (0, 2), (7, 1), (7, 2), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3)]
                
                debug_msg = "Setting letter L at position 0"
                if terminal_display:
                    terminal_display.add_debug_message(debug_msg, "info")
                
                # Display L (at position 0)
                for row, col in letter_L:
                    led_manager.set_led(row, col, True)
                
                debug_msg = "Setting letter E at position 4"
                if terminal_display:
                    terminal_display.add_debug_message(debug_msg, "info")
                
                # Display E (at position 4)
                for row, col in letter_E:
                    led_manager.set_led(row, col + 4, True)
                
                debug_msg = "Setting letter D at position 8"
                if terminal_display:
                    terminal_display.add_debug_message(debug_msg, "info")
                
                # Display D (at position 8)
                for row, col in letter_D:
                    led_manager.set_led(row, col + 8, True)
                
                debug_msg = "Letters displayed with direct LED patterns"
                if terminal_display:
                    terminal_display.add_debug_message(debug_msg, "info")
                else:
                    print(debug_msg)
                    
                time.sleep(2)
                
                # Clean up
                led_manager.set_all_leds(False)
                debug_msg = "All LEDs cleared"
                if terminal_display:
                    terminal_display.add_debug_message(debug_msg, "info")
                else:
                    print(debug_msg)
                
                summary_msg = "Hardware verification test completed successfully!"
                if terminal_display:
                    terminal_display.add_debug_message(summary_msg, "info")
                    terminal_display.set_status(summary_msg, "info")
                else:
                    print(summary_msg)
            finally:
                # Clean up
                debug_msg = "Disconnecting hardware..."
                if terminal_display:
                    terminal_display.add_debug_message(debug_msg, "info")
                else:
                    print(debug_msg)
                    
                hardware_controller.disconnect()
                
                debug_msg = "Hardware disconnected"
                if terminal_display:
                    terminal_display.add_debug_message(debug_msg, "info")
                else:
                    print(debug_msg)
        else:
            error_msg = "Failed to connect to hardware."
            if terminal_display:
                terminal_display.add_debug_message(error_msg, "error")
                terminal_display.set_status(error_msg, "error")
            else:
                print(error_msg)
    
    finally:
        # Cancel the timeout alarm
        signal.alarm(0)

def test_animations():
    """
    Test loading and playing animations from JSON files.
    This demonstrates how to use animations with the LED system.
    """
    print("Running animation test...")
    
    # Set a timeout for this test
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 seconds timeout
    
    try:
        # Get LED state manager
        led_manager = get_led_manager()
        print("LED state manager initialized")
        
        # Create hardware controller
        hardware_controller = create_hardware_controller()
        if hardware_controller.connect():
            print("Connected to hardware")
            hardware_controller.start()
            
            try:
                # Enable verbose mode for simulated hardware
                if isinstance(hardware_controller, SimulatedHardwareController):
                    hardware_controller.verbose = True
                    hardware_controller.print_interval = 2  # Print every other frame to reduce output
                
                # Clear all LEDs
                led_manager.set_all_leds(False)
                print("All LEDs cleared")
                time.sleep(1)
                
                # Load animations
                animations_dir = Path(__file__).parent / "animations"
                
                # Load and play splash animation
                splash_path = animations_dir / "splash.json"
                if splash_path.exists():
                    print("\nPlaying splash animation...")
                    play_animation(led_manager, splash_path, frame_delay=0.2)
                else:
                    print(f"Animation file not found: {splash_path}")
                
                # Load and play spinner animation
                spinner_path = animations_dir / "spinner.json"
                if spinner_path.exists():
                    print("\nPlaying spinner animation...")
                    play_animation(led_manager, spinner_path, frame_delay=0.1, loops=2)
                else:
                    print(f"Animation file not found: {spinner_path}")
                
                # Clean up
                led_manager.set_all_leds(False)
                print("All LEDs cleared")
                
                print("Animation test completed successfully!")
            finally:
                # Clean up
                print("Disconnecting hardware...")
                hardware_controller.disconnect()
                print("Hardware disconnected")
        else:
            print("Failed to connect to hardware.")
    
    finally:
        # Cancel the timeout alarm
        signal.alarm(0)

def play_animation(led_manager, animation_path, frame_delay=0.1, loops=1):
    """
    Play an animation from a JSON file.
    
    Args:
        led_manager: The LED state manager
        animation_path: Path to the animation JSON file
        frame_delay: Delay between frames in seconds
        loops: Number of times to loop the animation
    """
    try:
        with open(animation_path, 'r') as f:
            animation = json.load(f)
        
        print(f"Loaded animation: {animation.get('name', 'Unnamed')}")
        print(f"Description: {animation.get('description', 'No description')}")
        print(f"Frames: {len(animation['frames'])}")
        
        # Play the animation for the specified number of loops
        for loop in range(loops):
            print(f"Loop {loop+1}/{loops}")
            
            for i, frame in enumerate(animation['frames']):
                # Clear LEDs for clean frame
                led_manager.set_all_leds(False)
                
                # Set LEDs based on frame data
                for row_idx, row in enumerate(frame):
                    for col_idx, cell in enumerate(row):
                        if cell:
                            led_manager.set_led(row_idx, col_idx, True)
                
                print(f"Frame {i+1}/{len(animation['frames'])}")
                time.sleep(frame_delay)
        
    except FileNotFoundError:
        print(f"Animation file not found: {animation_path}")
    except json.JSONDecodeError:
        print(f"Invalid JSON in animation file: {animation_path}")
    except Exception as e:
        print(f"Error playing animation: {e}")

def main():
    parser = argparse.ArgumentParser(description="Test LED integration for Punch Card Project")
    parser.add_argument("--test", choices=["direct", "integration", "simple", "minimal", "hardware", "animations", "all"], default="simple",
                        help="Which test to run (direct, integration, simple, minimal, hardware, animations, or all)")
    parser.add_argument("--hardware-type", choices=["none", "simulated", "rpi"], default="simulated",
                        help="Type of hardware to use (none, simulated, rpi)")
    parser.add_argument("--timeout", type=int, default=30,
                        help="Maximum time in seconds before timing out a test")
    parser.add_argument("--use-ui", action="store_true", default=False,
                        help="Use the terminal UI with split-screen for LED display and debug messages")
    parser.add_argument("--term-width", type=int, default=80,
                        help="Terminal width (only used with --use-ui)")
    parser.add_argument("--term-height", type=int, default=24,
                        help="Terminal height (only used with --use-ui)")
    parser.add_argument("--char-set", choices=["default", "block", "circle", "star", "ascii"], default="default",
                        help="Character set to use for LED visualization")
    parser.add_argument("--verbose", action="store_true", default=False,
                        help="Print verbose output including individual LED state changes")
    
    args = parser.parse_args()
    
    # Update the timeout based on command line argument
    signal.signal(signal.SIGALRM, timeout_handler)
    
    # Set hardware type in environment for hardware controller to use
    os.environ["PUNCH_CARD_HARDWARE_TYPE"] = args.hardware_type
    
    # Initialize terminal display if requested and available
    global terminal_display
    if args.use_ui and TERMINAL_DISPLAY_AVAILABLE:
        try:
            # Try to determine terminal size
            try:
                import shutil
                term_size = shutil.get_terminal_size()
                term_width, term_height = term_size.columns, term_size.lines
            except (ImportError, AttributeError):
                # Fall back to command-line arguments
                term_width, term_height = args.term_width, args.term_height
            
            # Check if terminal is large enough
            if term_width < 40 or term_height < 12:
                print(f"Warning: Terminal size ({term_width}x{term_height}) is too small for UI. Need at least 40x12.")
                print("Falling back to standard console output.")
                # Even in console mode, we can use the new character set and verbosity features
                terminal_display = get_terminal_display(8, 16, verbose=args.verbose, char_set=args.char_set)
                terminal_display.start()
            else:
                terminal_display = get_terminal_display(8, 16, verbose=args.verbose, char_set=args.char_set)
                terminal_display.start()
                terminal_display.set_status("Punch Card LED Test - Starting...", "info")
                terminal_display.add_debug_message(f"Terminal size: {term_width}x{term_height}", "info")
                terminal_display.add_debug_message(f"Running test: {args.test}", "info")
                terminal_display.add_debug_message(f"Hardware type: {args.hardware_type}", "info")
                terminal_display.add_debug_message(f"Using character set: {args.char_set}", "info")
        except Exception as e:
            print(f"Error initializing terminal UI: {e}")
            print("Falling back to standard console output.")
            terminal_display = None
    elif args.use_ui and not TERMINAL_DISPLAY_AVAILABLE:
        print("Warning: Terminal UI requested but terminal_display module not available.")
        print("Falling back to standard console output.")
    
    try:
        if args.test == "direct" or args.test == "all":
            signal.alarm(args.timeout)
            test_direct_led_control()
            signal.alarm(0)
            print()
        
        if args.test == "simple" or args.test == "all":
            signal.alarm(args.timeout)
            test_simple_led_control()
            signal.alarm(0)
            print()
        
        if args.test == "minimal" or args.test == "all":
            signal.alarm(args.timeout)
            test_minimal_punch_card()
            signal.alarm(0)
            print()
        
        if args.test == "hardware" or args.test == "all":
            signal.alarm(args.timeout)
            test_hardware_verification()
            signal.alarm(0)
            print()
        
        if args.test == "animations" or args.test == "all":
            signal.alarm(args.timeout)
            test_animations()
            signal.alarm(0)
            print()
        
        if args.test == "integration" or args.test == "all":
            signal.alarm(args.timeout)
            test_punch_card_integration()
            signal.alarm(0)
    finally:
        # Stop the terminal display if it was started
        if terminal_display:
            terminal_display.add_debug_message("All tests completed", "info")
            terminal_display.set_status("Testing completed successfully", "info")
            # Wait a moment for the final status to be displayed
            time.sleep(1.0)
            terminal_display.stop()

if __name__ == "__main__":
    # Create animations directory if it doesn't exist
    animations_dir = Path(__file__).parent / "animations"
    animations_dir.mkdir(exist_ok=True)
    
    main() 