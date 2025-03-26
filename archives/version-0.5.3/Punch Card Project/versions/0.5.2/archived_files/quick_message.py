#!/usr/bin/env python3
"""
Quick Message Display for Punch Card Project

This script provides a streamlined interface for displaying messages
on the punch card system with minimal console output.
"""

import os
import sys
import time
import argparse
from typing import List

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import necessary modules
from src.terminal_display import CharacterSet
from src.display_adapter import PunchCardDisplayAdapter

class QuickMessageDisplay:
    """
    Simple message display for the punch card system with minimal output.
    """
    
    def __init__(self,
                 char_set_name: str = "default",
                 use_ui: bool = True,
                 quick_mode: bool = False,
                 instant_mode: bool = False):
        """Initialize the display."""
        # Force console mode for clean output
        os.environ['FORCE_CONSOLE'] = '1'
        
        # Create display adapter with minimal verbosity
        self.display_adapter = PunchCardDisplayAdapter(
            num_rows=12,
            num_cols=80,
            verbose=False,  # No verbose output
            char_set_name=char_set_name,
            use_ui=use_ui
        )
        
        # Initialize grid
        self.grid = [[False for _ in range(80)] for _ in range(12)]
        
        # Set delays based on mode
        self.quick_mode = quick_mode
        self.instant_mode = instant_mode
        self.char_delay = 0.05 if not quick_mode else 0.01
        if instant_mode:
            self.char_delay = 0  # No delay in instant mode
        
        # Suppress adapter's output for set_led operations
        self.display_adapter._suppress_led_output = True
    
    def set_led(self, row: int, col: int, state: bool):
        """Set a single LED in the grid."""
        if 0 <= row < 12 and 0 <= col < 80:
            self.grid[row][col] = state
            self.display_adapter.set_led(row, col, state)
            
            # Only add delay in normal mode
            if not self.quick_mode:
                time.sleep(self.char_delay)
    
    def clear_grid(self):
        """Clear the entire grid."""
        self.grid = [[False for _ in range(80)] for _ in range(12)]
        self.display_adapter.clear_all()
        print("Grid cleared")
    
    def show_message(self, message: str):
        """Display a message on the punch card grid."""
        print(f"Displaying message: {message}")
        
        # Clear the grid first
        self.clear_grid()
        
        # Pad or truncate message to 80 columns
        if len(message) < 80:
            message = message.ljust(80)
        elif len(message) > 80:
            message = message[:80]
        
        # Display message character by character
        for col, char in enumerate(message):
            self._display_character(char, col)
        
        # Show grid summary
        self._display_grid_summary()
        
        print("Message display complete")
    
    def _display_character(self, char: str, col: int):
        """Display a character on the punch card grid."""
        # Convert to uppercase
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
    
    def _display_grid_summary(self):
        """Display a summary of the current grid state."""
        # Get on/off characters for the display
        on_char, off_char = "X", "."
        
        # Print grid with compact representation
        print("\nMessage Preview:")
        
        # Define the correct row order for punch cards: 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
        row_labels = ["12", "11", "0 ", "1 ", "2 ", "3 ", "4 ", "5 ", "6 ", "7 ", "8 ", "9 "]
        
        print("  ┌" + "─" * 80 + "┐")
        for i in range(12):
            row_content = []
            for j in range(80):
                row_content.append(on_char if self.grid[i][j] else off_char)
            print(f"{row_labels[i]}│{''.join(row_content)}│")
        print("  └" + "─" * 80 + "┘")
    
    def cleanup(self):
        """Clean up resources."""
        self.display_adapter.cleanup()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Quick Message Display for Punch Card Project")
    parser.add_argument("--message", type=str, required=True,
                        help="Message to display")
    parser.add_argument("--char-set", default="ascii", 
                        choices=["default", "block", "circle", "star", "ascii"],
                        help="Character set to use (default: ascii)")
    parser.add_argument("--quick", action="store_true",
                        help="Run in quick mode with minimal delays")
    parser.add_argument("--instant", action="store_true",
                        help="Run in instant mode with no delays")
    return parser.parse_args()

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_args()
    
    try:
        # Create display
        display = QuickMessageDisplay(
            char_set_name=args.char_set,
            use_ui=False,  # Always use console mode for this script
            quick_mode=args.quick,
            instant_mode=args.instant
        )
        
        try:
            # Show the message
            display.show_message(args.message)
            
            # Wait a moment to see the final state
            time.sleep(1.0)
            
        finally:
            # Clean up
            display.cleanup()
            
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running program: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 