#!/usr/bin/env python3
"""
Simple Demo for Punch Card Terminal Display

This script demonstrates the terminal display system with a simple
message display without relying on the punch card system.
"""

import os
import sys
import time
import argparse
import random
from typing import List, Dict, Any, Optional

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import our terminal display modules
from terminal_display import TerminalDisplay, CharacterSet
from display_adapter import PunchCardDisplayAdapter

# Character mappings for a simple demo
CHAR_TO_PATTERN = {
    'A': [
        [0, 1, 1, 0],
        [1, 0, 0, 1],
        [1, 1, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1]
    ],
    'B': [
        [1, 1, 1, 0],
        [1, 0, 0, 1],
        [1, 1, 1, 0],
        [1, 0, 0, 1],
        [1, 1, 1, 0]
    ],
    'C': [
        [0, 1, 1, 1],
        [1, 0, 0, 0],
        [1, 0, 0, 0],
        [1, 0, 0, 0],
        [0, 1, 1, 1]
    ],
    'D': [
        [1, 1, 1, 0],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 1, 1, 0]
    ],
    'E': [
        [1, 1, 1, 1],
        [1, 0, 0, 0],
        [1, 1, 1, 0],
        [1, 0, 0, 0],
        [1, 1, 1, 1]
    ],
    'F': [
        [1, 1, 1, 1],
        [1, 0, 0, 0],
        [1, 1, 1, 0],
        [1, 0, 0, 0],
        [1, 0, 0, 0]
    ],
    'G': [
        [0, 1, 1, 1],
        [1, 0, 0, 0],
        [1, 0, 1, 1],
        [1, 0, 0, 1],
        [0, 1, 1, 1]
    ],
    'H': [
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 1, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1]
    ],
    'I': [
        [1, 1, 1],
        [0, 1, 0],
        [0, 1, 0],
        [0, 1, 0],
        [1, 1, 1]
    ],
    'J': [
        [0, 0, 1],
        [0, 0, 1],
        [0, 0, 1],
        [1, 0, 1],
        [0, 1, 0]
    ],
    'K': [
        [1, 0, 0, 1],
        [1, 0, 1, 0],
        [1, 1, 0, 0],
        [1, 0, 1, 0],
        [1, 0, 0, 1]
    ],
    'L': [
        [1, 0, 0, 0],
        [1, 0, 0, 0],
        [1, 0, 0, 0],
        [1, 0, 0, 0],
        [1, 1, 1, 1]
    ],
    'M': [
        [1, 0, 0, 0, 1],
        [1, 1, 0, 1, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1]
    ],
    'N': [
        [1, 0, 0, 1],
        [1, 1, 0, 1],
        [1, 0, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1]
    ],
    'O': [
        [0, 1, 1, 0],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [0, 1, 1, 0]
    ],
    'P': [
        [1, 1, 1, 0],
        [1, 0, 0, 1],
        [1, 1, 1, 0],
        [1, 0, 0, 0],
        [1, 0, 0, 0]
    ],
    'Q': [
        [0, 1, 1, 0],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 0, 1, 1],
        [0, 1, 1, 1]
    ],
    'R': [
        [1, 1, 1, 0],
        [1, 0, 0, 1],
        [1, 1, 1, 0],
        [1, 0, 1, 0],
        [1, 0, 0, 1]
    ],
    'S': [
        [0, 1, 1, 1],
        [1, 0, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 1],
        [1, 1, 1, 0]
    ],
    'T': [
        [1, 1, 1, 1, 1],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0]
    ],
    'U': [
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [0, 1, 1, 0]
    ],
    'V': [
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [0, 1, 1, 0],
        [0, 0, 1, 0]
    ],
    'W': [
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1],
        [1, 1, 0, 1, 1],
        [1, 0, 0, 0, 1]
    ],
    'X': [
        [1, 0, 0, 1],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 1, 1, 0],
        [1, 0, 0, 1]
    ],
    'Y': [
        [1, 0, 0, 1],
        [0, 1, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 0]
    ],
    'Z': [
        [1, 1, 1, 1],
        [0, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [1, 1, 1, 1]
    ],
    '0': [
        [0, 1, 1, 0],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [0, 1, 1, 0]
    ],
    '1': [
        [0, 1, 0],
        [1, 1, 0],
        [0, 1, 0],
        [0, 1, 0],
        [1, 1, 1]
    ],
    '2': [
        [0, 1, 1, 0],
        [1, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [1, 1, 1, 1]
    ],
    '3': [
        [1, 1, 1, 0],
        [0, 0, 0, 1],
        [0, 1, 1, 0],
        [0, 0, 0, 1],
        [1, 1, 1, 0]
    ],
    '4': [
        [0, 0, 1, 1],
        [0, 1, 0, 1],
        [1, 0, 0, 1],
        [1, 1, 1, 1],
        [0, 0, 0, 1]
    ],
    '5': [
        [1, 1, 1, 1],
        [1, 0, 0, 0],
        [1, 1, 1, 0],
        [0, 0, 0, 1],
        [1, 1, 1, 0]
    ],
    '6': [
        [0, 1, 1, 0],
        [1, 0, 0, 0],
        [1, 1, 1, 0],
        [1, 0, 0, 1],
        [0, 1, 1, 0]
    ],
    '7': [
        [1, 1, 1, 1],
        [0, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [0, 1, 0, 0]
    ],
    '8': [
        [0, 1, 1, 0],
        [1, 0, 0, 1],
        [0, 1, 1, 0],
        [1, 0, 0, 1],
        [0, 1, 1, 0]
    ],
    '9': [
        [0, 1, 1, 0],
        [1, 0, 0, 1],
        [0, 1, 1, 1],
        [0, 0, 0, 1],
        [0, 1, 1, 0]
    ],
    ' ': [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ],
    '.': [
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [1, 0]
    ],
    ',': [
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 1],
        [1, 0]
    ],
    '!': [
        [1],
        [1],
        [1],
        [0],
        [1]
    ],
    '?': [
        [0, 1, 1, 0],
        [1, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 1, 0]
    ],
    '-': [
        [0, 0, 0],
        [0, 0, 0],
        [1, 1, 1],
        [0, 0, 0],
        [0, 0, 0]
    ],
    '+': [
        [0, 0, 0],
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
        [0, 0, 0]
    ],
    '/': [
        [0, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [1, 0, 0, 0],
        [0, 0, 0, 0]
    ],
    '*': [
        [1, 0, 1],
        [0, 1, 0],
        [1, 0, 1],
        [0, 0, 0],
        [0, 0, 0]
    ],
    '=': [
        [0, 0, 0],
        [1, 1, 1],
        [0, 0, 0],
        [1, 1, 1],
        [0, 0, 0]
    ],
    '(': [
        [0, 1],
        [1, 0],
        [1, 0],
        [1, 0],
        [0, 1]
    ],
    ')': [
        [1, 0],
        [0, 1],
        [0, 1],
        [0, 1],
        [1, 0]
    ],
    ':': [
        [0],
        [1],
        [0],
        [1],
        [0]
    ],
    ';': [
        [0, 0],
        [0, 1],
        [0, 0],
        [0, 1],
        [1, 0]
    ]
}

class SimpleMessageDisplay:
    """Simple message display using the terminal display."""
    
    def __init__(self, 
                 char_set_name: str = "default",
                 use_ui: bool = True,
                 verbose: bool = False,
                 char_delay: float = 0.1,
                 skip_splash: bool = False):
        """Initialize the message display."""
        # Create display adapter
        self.display_adapter = PunchCardDisplayAdapter(
            num_rows=12,  # Standard punch card rows
            num_cols=80,  # Standard punch card columns
            verbose=verbose,
            char_set_name=char_set_name,
            use_ui=use_ui
        )
        
        # Store settings
        self.verbose = verbose
        self.use_ui = use_ui
        self.char_delay = char_delay
        self.skip_splash = skip_splash
        
        # Initialize the grid state
        self.grid = [[False for _ in range(80)] for _ in range(12)]
        
        # Display splash screen if requested
        if not skip_splash:
            self.show_splash()
    
    def clear_grid(self):
        """Clear the grid."""
        self.grid = [[False for _ in range(80)] for _ in range(12)]
        self.display_adapter.update_grid_from_punch_card(self.grid)
        self.display_adapter.log_message("Grid cleared", "info")
    
    def set_grid_region(self, row: int, col: int, pattern: List[List[int]]):
        """Set a region of the grid based on a pattern."""
        for y, row_pattern in enumerate(pattern):
            for x, cell in enumerate(row_pattern):
                if 0 <= row + y < 12 and 0 <= col + x < 80:
                    self.grid[row + y][col + x] = bool(cell)
        
        # Update the display
        self.display_adapter.update_grid_from_punch_card(self.grid)
    
    def show_splash(self):
        """Show splash screen: PC (Punch Card)"""
        self.display_adapter.log_message("Showing splash screen", "info")
        
        # Clear the grid
        self.clear_grid()
        
        # Show P
        self.set_grid_region(3, 30, CHAR_TO_PATTERN['P'])
        time.sleep(0.5)
        
        # Show PC
        self.set_grid_region(3, 36, CHAR_TO_PATTERN['C'])
        time.sleep(1.0)
        
        # Show animated border
        for i in range(80):
            # Top and bottom borders
            self.grid[0][i] = True
            self.grid[11][i] = True
            
            # Left and right borders if at the edges
            if i < 12:
                self.grid[i][0] = True
                self.grid[i][79] = True
            
            # Update every few steps to see animation
            if i % 5 == 0:
                self.display_adapter.update_grid_from_punch_card(self.grid)
                time.sleep(0.05)
        
        # Final update
        self.display_adapter.update_grid_from_punch_card(self.grid)
        time.sleep(0.5)
        
        # Clear the grid with fade effect
        for i in range(12):
            for j in range(80):
                if random.random() < 0.2:  # Randomly clear cells for fade effect
                    self.grid[i][j] = False
            
            # Update every row for animation
            self.display_adapter.update_grid_from_punch_card(self.grid)
            time.sleep(0.05)
        
        # Ensure grid is fully cleared
        self.clear_grid()
        time.sleep(0.2)
    
    def show_message(self, message: str, row: int = 3, col: int = 5):
        """Show a message on the grid."""
        self.display_adapter.log_message(f"Showing message: {message}", "info")
        
        # Clear the grid
        self.clear_grid()
        
        # Convert message to uppercase (our patterns are uppercase)
        message = message.upper()
        
        # Display each character with a delay
        current_col = col
        for char in message:
            if char in CHAR_TO_PATTERN:
                pattern = CHAR_TO_PATTERN[char]
                self.set_grid_region(row, current_col, pattern)
                
                # Update column position for next character (width of pattern + 1)
                current_col += len(pattern[0]) + 1
                
                # Add delay between characters
                time.sleep(self.char_delay)
            else:
                # Skip unknown characters
                current_col += 3  # Default width for unknown chars
        
        # Log completion
        self.display_adapter.log_message("Message display completed", "info")
    
    def show_animation(self, frames: int = 20):
        """Show a simple animation."""
        self.display_adapter.log_message("Showing animation", "info")
        
        # Clear the grid
        self.clear_grid()
        
        # Create a simple spinning line animation
        center_row = 6
        center_col = 40
        radius = 5
        
        for i in range(frames):
            # Clear previous frame
            self.clear_grid()
            
            # Calculate angle based on frame
            angle = i * (360 / frames)
            radian = angle * (3.14159 / 180)
            
            # Draw line from center in current angle
            for r in range(radius):
                row = int(center_row + r * math.sin(radian))
                col = int(center_col + r * math.cos(radian))
                
                if 0 <= row < 12 and 0 <= col < 80:
                    self.grid[row][col] = True
            
            # Update display
            self.display_adapter.update_grid_from_punch_card(self.grid)
            
            # Short delay between frames
            time.sleep(0.1)
    
    def cleanup(self):
        """Clean up resources."""
        self.display_adapter.cleanup()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Simple Demo for Punch Card Terminal Display")
    parser.add_argument("--char-set", default="default", 
                        choices=["default", "block", "circle", "star", "ascii"],
                        help="Character set to use for LED visualization")
    parser.add_argument("--use-ui", action="store_true", 
                        help="Use UI for visualization")
    parser.add_argument("--verbose", action="store_true", 
                        help="Print verbose output")
    parser.add_argument("--message", type=str, default="HELLO WORLD!",
                        help="Message to display")
    parser.add_argument("--delay", type=float, default=0.1,
                        help="Delay between characters")
    parser.add_argument("--skip-splash", action="store_true",
                        help="Skip splash screen")
    parser.add_argument("--animation", action="store_true",
                        help="Show animation after message")
    return parser.parse_args()

def main():
    """Main function."""
    # Import math module for animations
    import math
    
    # Parse command line arguments
    args = parse_args()
    
    try:
        # Create the message display
        display = SimpleMessageDisplay(
            char_set_name=args.char_set,
            use_ui=args.use_ui,
            verbose=args.verbose,
            char_delay=args.delay,
            skip_splash=args.skip_splash
        )
        
        try:
            # Show the message
            display.show_message(args.message)
            
            # Show animation if requested
            if args.animation:
                time.sleep(0.5)  # Brief pause
                display.show_animation()
            
            # Wait a moment to see the final state
            time.sleep(1.0)
            
        finally:
            # Always clean up
            display.cleanup()
            
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running demo: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 