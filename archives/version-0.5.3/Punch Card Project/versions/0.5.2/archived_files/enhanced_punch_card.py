#!/usr/bin/env python3
"""
Enhanced Punch Card Display

This script combines the new terminal display system with
the original punch card functionality, including the splash screen,
settings menu, and message display capabilities.
"""

import os
import sys
import time
import argparse
import random
import json
import shutil
from typing import List, Dict, Any, Optional, Tuple
import builtins

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import from the src directory
from src.terminal_display import TerminalDisplay, CharacterSet
from src.display_adapter import PunchCardDisplayAdapter

# Try to import components from the original code
try:
    from src.message_database import MessageDatabase
    from src.message_generator import MessageGenerator
    HAS_MESSAGE_COMPONENTS = True
except ImportError:
    print("Warning: Original message components not found. Some features will be limited.")
    HAS_MESSAGE_COMPONENTS = False

# Constants
DEFAULT_LED_DELAY = 0.05
DEFAULT_MESSAGE_DELAY = 0.2
DEFAULT_COMPLETION_DELAY = 1.0
DEFAULT_RECEIVE_DURATION = 3.0
DEFAULT_TRANSITION_STEPS = 10
SETTINGS_FILE = 'src/punch_card_settings.json'

class EnhancedPunchCardDisplay:
    """
    Enhanced punch card display that combines the new terminal display
    with the original punch card functionality.
    """
    
    def __init__(self, 
                 char_set_name: str = "default",
                 use_ui: bool = True,
                 verbose: bool = False,
                 led_delay: float = DEFAULT_LED_DELAY,
                 message_delay: float = DEFAULT_MESSAGE_DELAY,
                 random_delay: bool = True,
                 skip_splash: bool = False,
                 debug_mode: bool = False,
                 completion_delay: float = DEFAULT_COMPLETION_DELAY,
                 receive_duration: float = DEFAULT_RECEIVE_DURATION,
                 transition_steps: int = DEFAULT_TRANSITION_STEPS):
        """Initialize the enhanced punch card display."""
        # Create display adapter
        self.display_adapter = PunchCardDisplayAdapter(
            num_rows=12,  # Match the punch card rows
            num_cols=80,  # Match the punch card columns
            verbose=verbose,
            char_set_name=char_set_name,
            use_ui=use_ui
        )
        
        # Store parameters
        self.verbose = verbose
        self.use_ui = use_ui
        self.led_delay = led_delay
        self.message_delay = message_delay
        self.random_delay = random_delay
        self.skip_splash = skip_splash
        self.debug_mode = debug_mode
        self.completion_delay = completion_delay
        self.receive_duration = receive_duration
        self.transition_steps = transition_steps
        
        # Initialize message system if available
        self.message_db = None
        self.message_generator = None
        self.message_number = 0
        
        if HAS_MESSAGE_COMPONENTS:
            try:
                self.message_db = MessageDatabase()
                self.message_number = self.message_db.current_message_number
                self.message_generator = MessageGenerator()
            except Exception as e:
                if self.debug_mode:
                    print(f"Warning: Failed to initialize message system: {e}")
        
        # Load settings
        self.settings = self._load_settings()
        
        # Initialize the grid
        self.grid = [[False for _ in range(80)] for _ in range(12)]
        
        # Show splash screen if not skipped
        if not skip_splash:
            self.show_splash()
    
    def _load_settings(self) -> dict:
        """Load settings from file or return defaults."""
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'led_delay': DEFAULT_LED_DELAY,
                'message_delay': DEFAULT_MESSAGE_DELAY,
                'random_delay': True,
                'debug_mode': False,
                'completion_delay': DEFAULT_COMPLETION_DELAY,
                'receive_duration': DEFAULT_RECEIVE_DURATION,
                'transition_steps': DEFAULT_TRANSITION_STEPS
            }
    
    def _save_settings(self):
        """Save current settings to file."""
        settings = {
            'led_delay': self.led_delay,
            'message_delay': self.message_delay,
            'random_delay': self.random_delay,
            'debug_mode': self.debug_mode,
            'completion_delay': self.completion_delay,
            'receive_duration': self.receive_duration,
            'transition_steps': self.transition_steps
        }
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            if self.debug_mode:
                print(f"Warning: Could not save settings to file: {e}")
    
    def update_grid(self, grid: List[List[bool]]):
        """Update the grid state and display."""
        for row in range(len(grid)):
            for col in range(len(grid[row])):
                self.grid[row][col] = grid[row][col]
        
        self.display_adapter.update_grid_from_punch_card(self.grid)
    
    def set_led(self, row: int, col: int, state: bool):
        """Set a single LED in the grid."""
        if 0 <= row < 12 and 0 <= col < 80:
            self.grid[row][col] = state
            self.display_adapter.set_led(row, col, state)
            
            # Add delay if specified
            if self.led_delay > 0:
                time.sleep(self.led_delay)
    
    def clear_grid(self):
        """Clear the entire grid."""
        self.grid = [[False for _ in range(80)] for _ in range(12)]
        self.display_adapter.clear_all()
        
        # Log message
        self.display_adapter.log_message("Grid cleared", "info")
    
    def show_splash(self):
        """Show the punch card splash screen."""
        self.display_adapter.log_message("Showing splash screen", "info")
        
        # Clear the grid
        self.clear_grid()
        
        # Animate border
        for i in range(80):
            # Top and bottom borders
            self.set_led(0, i, True)
            self.set_led(11, i, True)
            
            # Left and right borders (if needed)
            if i < 12:
                self.set_led(i, 0, True)
                self.set_led(i, 79, True)
        
        # Short pause to see border
        time.sleep(0.5)
        
        # Show "PUNCH CARD" text
        # P
        for row in range(2, 10):
            self.set_led(row, 15, True)
        for col in range(15, 19):
            self.set_led(2, col, True)
            self.set_led(5, col, True)
        self.set_led(3, 19, True)
        self.set_led(4, 19, True)
        
        # U
        for row in range(2, 9):
            self.set_led(row, 21, True)
            self.set_led(row, 25, True)
        for col in range(22, 25):
            self.set_led(9, col, True)
        
        # N
        for row in range(2, 10):
            self.set_led(row, 27, True)
            self.set_led(row, 31, True)
        self.set_led(3, 28, True)
        self.set_led(4, 29, True)
        self.set_led(5, 29, True)
        self.set_led(6, 29, True)
        self.set_led(7, 30, True)
        self.set_led(8, 30, True)
        
        # C
        for row in range(2, 10):
            self.set_led(row, 33, True)
        for col in range(34, 37):
            self.set_led(2, col, True)
            self.set_led(9, col, True)
        
        # H
        for row in range(2, 10):
            self.set_led(row, 39, True)
            self.set_led(row, 43, True)
        for col in range(40, 43):
            self.set_led(5, col, True)
        
        # C
        for row in range(2, 10):
            self.set_led(row, 47, True)
        for col in range(48, 51):
            self.set_led(2, col, True)
            self.set_led(9, col, True)
        
        # A
        for row in range(3, 10):
            self.set_led(row, 53, True)
            self.set_led(row, 57, True)
        for col in range(54, 57):
            self.set_led(2, col, True)
            self.set_led(5, col, True)
        
        # R
        for row in range(2, 10):
            self.set_led(row, 59, True)
        for col in range(60, 63):
            self.set_led(2, col, True)
            self.set_led(5, col, True)
        self.set_led(3, 63, True)
        self.set_led(4, 63, True)
        self.set_led(6, 61, True)
        self.set_led(7, 62, True)
        self.set_led(8, 62, True)
        self.set_led(9, 63, True)
        
        # D
        for row in range(2, 10):
            self.set_led(row, 65, True)
        for col in range(66, 68):
            self.set_led(2, col, True)
            self.set_led(9, col, True)
        self.set_led(3, 68, True)
        self.set_led(4, 69, True)
        self.set_led(5, 69, True)
        self.set_led(6, 69, True)
        self.set_led(7, 69, True)
        self.set_led(8, 68, True)
        
        # Pause to display splash screen
        time.sleep(2.0)
        
        # Clear with a fancy animation
        for col in range(80):
            for row in range(12):
                self.set_led(row, col, False)
                
            # Speed up the clearing animation
            if col % 5 == 0:
                time.sleep(0.01)
    
    def show_message(self, message: str, source: str = "Test"):
        """Show a message on the punch card display."""
        self.display_adapter.log_message(f"Showing message: {message} (Source: {source})", "info")
        
        # Clear the grid
        self.clear_grid()
        
        # If message database is available, save the message
        if self.message_db is not None:
            self.message_number = self.message_db.add_message(message, source)
            self.display_adapter.log_message(f"Message #{self.message_number:07d} added to database", "debug")
        
        # Set status to TYPING
        self.display_adapter.log_message("Status: TYPING", "info")
        
        # Pad message to 80 columns if needed
        if len(message) < 80:
            message = message.ljust(80)
        elif len(message) > 80:
            message = message[:80]
        
        # Display message character by character
        for col, char in enumerate(message):
            # Convert character to punch card pattern
            self._display_character(char, col)
            
            # Random delay between characters if enabled
            if self.random_delay:
                delay = self.message_delay * (0.5 + random.random())
            else:
                delay = self.message_delay
            
            time.sleep(delay)
        
        # Set status to IDLE after message is shown
        self.display_adapter.log_message("Status: IDLE", "info")
        
        # Pause after message completion
        time.sleep(self.completion_delay)
    
    def _display_character(self, char: str, col: int):
        """Display a character on the punch card grid."""
        # Simple mapping for demonstration
        char = char.upper()
        
        # Clear the column first
        for row in range(12):
            self.set_led(row, col, False)
        
        # Handle different character types
        if char.isalpha():
            # Letters
            if char in "ABCDEFGHI":
                # A-I: row 12 + digit 1-9
                self.set_led(0, col, True)  # Row 12
                digit = ord(char) - ord('A') + 1
                self.set_led(digit + 2, col, True)  # Convert to punch card row
            elif char in "JKLMNOPQR":
                # J-R: row 11 + digit 1-9
                self.set_led(1, col, True)  # Row 11
                digit = ord(char) - ord('J') + 1
                self.set_led(digit + 2, col, True)  # Convert to punch card row
            else:
                # S-Z: row 0 + digit 2-9
                self.set_led(2, col, True)  # Row 0
                digit = ord(char) - ord('S') + 2
                if digit <= 9:
                    self.set_led(digit + 2, col, True)  # Convert to punch card row
        
        elif char.isdigit():
            # Digits 0-9
            digit = int(char)
            if digit == 0:
                self.set_led(2, col, True)  # Row 0
            else:
                self.set_led(digit + 2, col, True)  # Convert to punch card row
        
        elif char == ' ':
            # Space - no punches
            pass
        
        else:
            # Special characters - simplified version
            # For demonstration, just punch row 11 and 0
            self.set_led(1, col, True)  # Row 11
            self.set_led(2, col, True)  # Row 0
    
    def run_animations(self):
        """Run a series of animations on the punch card display."""
        self.display_adapter.log_message("Running animations", "info")
        
        # Clear the grid
        self.clear_grid()
        
        # Animation 1: Wave
        self.display_adapter.log_message("Animation: Wave", "debug")
        
        import math
        for frame in range(50):
            self.clear_grid()
            for col in range(80):
                # Sine wave
                sin_val = math.sin(col / 10 + frame / 5)
                row = int((sin_val + 1) * 5) + 1  # Map to rows 1-11
                self.set_led(row, col, True)
            
            # Short delay between frames
            time.sleep(0.05)
        
        # Short pause between animations
        time.sleep(0.5)
        
        # Animation 2: Spinner
        self.display_adapter.log_message("Animation: Spinner", "debug")
        
        center_row = 6
        center_col = 40
        radius = 5
        
        for angle in range(0, 720, 10):  # Two complete rotations
            self.clear_grid()
            
            # Draw spinner
            rad = math.radians(angle)
            row = int(center_row + radius * math.sin(rad))
            col = int(center_col + radius * math.cos(rad) * 2)  # Adjust for aspect ratio
            
            if 0 <= row < 12 and 0 <= col < 80:
                self.set_led(row, col, True)
                
                # Add a trail effect
                for trail in range(1, 5):
                    trail_angle = angle - trail * 10
                    trail_rad = math.radians(trail_angle)
                    trail_row = int(center_row + radius * math.sin(trail_rad))
                    trail_col = int(center_col + radius * math.cos(trail_rad) * 2)
                    
                    if 0 <= trail_row < 12 and 0 <= trail_col < 80:
                        self.set_led(trail_row, trail_col, True)
            
            # Short delay between frames
            time.sleep(0.05)
        
        # Clear the grid
        self.clear_grid()
        
        # Animation 3: Typewriter
        self.display_adapter.log_message("Animation: Typewriter", "debug")
        
        message = "PUNCH CARD SYSTEM V3 - READY FOR INPUT..."
        for i, char in enumerate(message):
            self._display_character(char, i)
            time.sleep(0.1)
        
        # Pause to see the message
        time.sleep(1.0)
        
        # Clear the grid
        self.clear_grid()
    
    def generate_and_show_message(self):
        """Generate and show a random message if message generator is available."""
        if self.message_generator is None:
            self.display_adapter.log_message("Message generator not available", "warning")
            return
        
        try:
            # Generate a random message
            message = self.message_generator.generate_random_sentence()
            source = "Random Generator"
            
            # Show the message
            self.show_message(message, source)
            
            return True
        except Exception as e:
            self.display_adapter.log_message(f"Error generating message: {e}", "error")
            return False
    
    def run_demo(self, messages: List[str] = None):
        """Run a demonstration with the provided messages or generated ones."""
        if messages:
            # Show each provided message
            for i, message in enumerate(messages):
                self.show_message(message, f"Demo Message {i+1}")
                time.sleep(1.0)
        
        elif HAS_MESSAGE_COMPONENTS and self.message_generator:
            # Generate and show 3 random messages
            for i in range(3):
                if not self.generate_and_show_message():
                    break
                time.sleep(1.0)
        
        else:
            # Show a default message if no messages provided and no generator
            self.show_message("PUNCH CARD SYSTEM INITIALIZED", "System")
            time.sleep(1.0)
            self.show_message("READY FOR INPUT", "System")
            time.sleep(1.0)
        
        # Run animations at the end
        self.run_animations()
    
    def cleanup(self):
        """Clean up resources."""
        self.display_adapter.cleanup()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Enhanced Punch Card Display")
    parser.add_argument("--char-set", default="default", 
                        choices=["default", "block", "circle", "star", "ascii"],
                        help="Character set to use for LED visualization")
    parser.add_argument("--use-ui", action="store_true", 
                        help="Use UI for visualization")
    parser.add_argument("--verbose", action="store_true", 
                        help="Print verbose output")
    parser.add_argument("--led-delay", type=float, default=DEFAULT_LED_DELAY,
                        help="Delay between LED updates (seconds)")
    parser.add_argument("--message-delay", type=float, default=DEFAULT_MESSAGE_DELAY,
                        help="Delay between message characters (seconds)")
    parser.add_argument("--skip-splash", action="store_true",
                        help="Skip splash screen")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug mode")
    parser.add_argument("--message", type=str, default=None,
                        help="Message to display")
    parser.add_argument("--demo", action="store_true",
                        help="Run demonstration mode")
    parser.add_argument("--force-console", action="store_true",
                        help="Force console mode (no curses UI)")
    return parser.parse_args()

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_args()
    
    # Set up environment variable for console mode if requested
    if args.force_console:
        os.environ['FORCE_CONSOLE'] = '1'
        # Also reduce the verbosity of PunchCardDisplayAdapter's console output
        if not args.verbose:
            # Create a backup of the original print function
            original_print = print
            # Define a custom print function that filters LED set messages
            def filtered_print(*args, **kwargs):
                if len(args) > 0 and isinstance(args[0], str) and "Set LED at" in args[0]:
                    return  # Skip LED set messages
                original_print(*args, **kwargs)
            # Replace the built-in print function
            builtins.__dict__['print'] = filtered_print
    
    try:
        # Create the enhanced punch card display
        display = EnhancedPunchCardDisplay(
            char_set_name=args.char_set,
            use_ui=args.use_ui,
            verbose=args.verbose,
            led_delay=args.led_delay,
            message_delay=args.message_delay,
            skip_splash=args.skip_splash,
            debug_mode=args.debug
        )
        
        try:
            if args.message:
                # Show a specific message if provided
                display.show_message(args.message, "Command Line")
            
            elif args.demo:
                # Run demonstration mode
                display.run_demo()
            
            else:
                # Default action: show system initialization message
                display.show_message("PUNCH CARD SYSTEM INITIALIZED", "System")
            
            # Wait a moment to see the final state
            time.sleep(1.0)
            
        finally:
            # Always clean up
            display.cleanup()
            # Restore original print function if it was replaced
            if args.force_console and not args.verbose:
                builtins.__dict__['print'] = original_print
            
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running program: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 