#!/usr/bin/env python3
"""
Direct LED test for Punch Card Project.
This script provides a standalone test of the LED hardware
without complex dependencies, using only standard libraries.
"""

import os
import sys
import time
import math
import argparse
import random
import subprocess
from enum import Enum, auto
from typing import List, Tuple, Optional, Dict, Any, Union
from pathlib import Path

# Character set options for LED visualization
class CharacterSet(Enum):
    DEFAULT = auto()  # Default character set (●○)
    BLOCK = auto()    # Block character set (█ )
    CIRCLE = auto()   # Circle character set (●○)
    STAR = auto()     # Star character set (★☆)
    ASCII = auto()    # ASCII character set (X.)

# Get character set mapping
def get_char_set_mapping(char_set: CharacterSet) -> Tuple[str, str]:
    """Get character set mapping for LED visualization."""
    mappings = {
        CharacterSet.DEFAULT: ("●", "○"),  # Default: Filled/empty circle
        CharacterSet.BLOCK: ("█", " "),    # Block: Block/space
        CharacterSet.CIRCLE: ("●", "○"),   # Circle: Filled/empty circle
        CharacterSet.STAR: ("★", "☆"),     # Star: Filled/empty star
        CharacterSet.ASCII: ("X", "."),    # ASCII: X/period
    }
    return mappings.get(char_set, mappings[CharacterSet.DEFAULT])

class LEDGrid:
    """Simple LED grid implementation."""
    
    def __init__(self, rows: int = 8, cols: int = 8):
        """Initialize LED grid with specified dimensions."""
        self.rows = rows
        self.cols = cols
        self.grid = [[False for _ in range(cols)] for _ in range(rows)]
    
    def set_led(self, x: int, y: int, state: bool) -> None:
        """Set the state of an LED at position (x, y)."""
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.grid[y][x] = state
    
    def get_led(self, x: int, y: int) -> bool:
        """Get the state of an LED at position (x, y)."""
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.grid[y][x]
        return False
    
    def clear_all(self) -> None:
        """Clear all LEDs (set to False)."""
        for y in range(self.rows):
            for x in range(self.cols):
                self.grid[y][x] = False
    
    def display(self, char_set: CharacterSet = CharacterSet.DEFAULT) -> None:
        """Display the current state of the LED grid."""
        on_char, off_char = get_char_set_mapping(char_set)
        
        # Print the grid with borders
        print("┌" + "─" * (self.cols * 2 - 1) + "┐")
        for row in self.grid:
            print("│" + " ".join([on_char if led else off_char for led in row]) + "│")
        print("└" + "─" * (self.cols * 2 - 1) + "┘")
        print()  # Empty line after display

class SimulatedLEDHardware:
    """Simulated LED hardware controller."""
    
    def __init__(self):
        """Initialize the simulated hardware controller."""
        self.led_grid = LEDGrid()
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to simulated hardware."""
        self.connected = True
        print("Connected to simulated LED hardware")
        return True
    
    def disconnect(self) -> None:
        """Disconnect from simulated hardware."""
        self.connected = False
        print("Disconnected from simulated LED hardware")
    
    def set_led(self, x: int, y: int, state: bool) -> None:
        """Set the state of an LED at position (x, y)."""
        if self.connected:
            self.led_grid.set_led(x, y, state)
    
    def get_led(self, x: int, y: int) -> bool:
        """Get the state of an LED at position (x, y)."""
        if self.connected:
            return self.led_grid.get_led(x, y)
        return False
    
    def clear_all(self) -> None:
        """Clear all LEDs (set to False)."""
        if self.connected:
            self.led_grid.clear_all()
    
    def display(self, char_set: CharacterSet = CharacterSet.DEFAULT) -> None:
        """Display the current state of the LED grid."""
        if self.connected:
            self.led_grid.display(char_set)

def test_led_patterns(hardware, char_set: CharacterSet = CharacterSet.DEFAULT) -> None:
    """Test various LED patterns."""
    print("Testing LED patterns...")
    
    # Connect to hardware
    if not hardware.connect():
        print("Failed to connect to hardware. Exiting.")
        return
    
    try:
        # Test pattern 1: All LEDs on and off
        print("\nTest 1: All LEDs on and off")
        print("All LEDs on:")
        for y in range(8):
            for x in range(8):
                hardware.set_led(x, y, True)
        hardware.display(char_set)
        time.sleep(1.0)
        
        print("All LEDs off:")
        hardware.clear_all()
        hardware.display(char_set)
        time.sleep(1.0)
        
        # Test pattern 2: Border pattern
        print("\nTest 2: Border pattern")
        for x in range(8):
            hardware.set_led(x, 0, True)  # Top row
            hardware.set_led(x, 7, True)  # Bottom row
        for y in range(8):
            hardware.set_led(0, y, True)  # Left column
            hardware.set_led(7, y, True)  # Right column
        hardware.display(char_set)
        time.sleep(1.0)
        
        hardware.clear_all()
        
        # Test pattern 3: Diagonal pattern
        print("\nTest 3: Diagonal pattern")
        for i in range(8):
            hardware.set_led(i, i, True)  # Main diagonal
            hardware.set_led(i, 7-i, True)  # Anti-diagonal
        hardware.display(char_set)
        time.sleep(1.0)
        
        hardware.clear_all()
        
        # Test pattern 4: Display "LED"
        print("\nTest 4: Display 'LED'")
        
        # L
        for y in range(8):
            hardware.set_led(1, y, True)
        for x in range(1, 3):
            hardware.set_led(x, 7, True)
        
        # E
        for y in range(8):
            hardware.set_led(3, y, True)
        for x in range(3, 5):
            hardware.set_led(x, 0, True)
            hardware.set_led(x, 3, True)
            hardware.set_led(x, 7, True)
        
        # D
        for y in range(8):
            hardware.set_led(6, y, True)
        hardware.set_led(5, 0, True)
        hardware.set_led(5, 7, True)
        for y in range(1, 7):
            hardware.set_led(7, y, True)
        
        hardware.display(char_set)
        time.sleep(1.0)
        
        hardware.clear_all()
        
        # Test pattern 5: Animated spinner
        print("\nTest 5: Animated spinner")
        frames = 8
        for frame in range(frames):
            hardware.clear_all()
            
            # Simple rotating line animation
            angle = frame * (360 // frames)
            if angle < 45 or angle >= 315:
                # Right direction
                for y in range(3, 5):
                    for x in range(5, 8):
                        hardware.set_led(x, y, True)
            elif angle < 135:
                # Down direction
                for y in range(5, 8):
                    for x in range(3, 5):
                        hardware.set_led(x, y, True)
            elif angle < 225:
                # Left direction
                for y in range(3, 5):
                    for x in range(0, 3):
                        hardware.set_led(x, y, True)
            else:
                # Up direction
                for y in range(0, 3):
                    for x in range(3, 5):
                        hardware.set_led(x, y, True)
            
            hardware.display(char_set)
            time.sleep(0.2)
        
        hardware.clear_all()
        
        print("LED pattern tests completed successfully.")
        
    finally:
        # Ensure hardware is disconnected properly
        hardware.disconnect()

def test_punch_card_animation(hardware, char_set: CharacterSet = CharacterSet.DEFAULT) -> None:
    """Test simplified punch card animation."""
    print("Testing punch card animation...")
    
    # Connect to hardware
    if not hardware.connect():
        print("Failed to connect to hardware. Exiting.")
        return
    
    try:
        # Animation 1: Scanning pattern (top to bottom)
        print("\nAnimation 1: Scanning pattern")
        for row in range(8):
            hardware.clear_all()
            for col in range(8):
                hardware.set_led(col, row, True)
            hardware.display(char_set)
            time.sleep(0.2)
        
        hardware.clear_all()
        
        # Animation 2: Random punch card pattern
        print("\nAnimation 2: Random punch card pattern")
        for i in range(5):  # Show 5 random patterns
            hardware.clear_all()
            
            # Generate random pattern with 10-20 punches
            num_punches = random.randint(10, 20)
            for _ in range(num_punches):
                x = random.randint(0, 7)
                y = random.randint(0, 7)
                hardware.set_led(x, y, True)
            
            hardware.display(char_set)
            time.sleep(0.5)
        
        hardware.clear_all()
        
        # Animation 3: Wave pattern
        print("\nAnimation 3: Wave pattern")
        for frame in range(16):  # 16 frames of animation
            hardware.clear_all()
            
            # Create a sine wave pattern across the display
            for x in range(8):
                # Calculate y position based on sine wave
                # Adjust amplitude and frequency for 8x8 grid
                y = int(3.5 + 3 * math.sin((x + frame) * 0.5))
                if 0 <= y < 8:
                    hardware.set_led(x, y, True)
            
            hardware.display(char_set)
            time.sleep(0.1)
        
        hardware.clear_all()
        
        print("Punch card animation tests completed successfully.")
        
    finally:
        # Ensure hardware is disconnected properly
        hardware.disconnect()

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Direct LED test for Punch Card Project')
    parser.add_argument('--char-set', choices=['default', 'block', 'circle', 'star', 'ascii'],
                       default='default', help='Character set to use for LED visualization')
    parser.add_argument('--test', choices=['patterns', 'animation', 'all'],
                       default='all', help='Test to run')
    
    args = parser.parse_args()
    
    # Set up character set
    char_set_map = {
        'default': CharacterSet.DEFAULT,
        'block': CharacterSet.BLOCK,
        'circle': CharacterSet.CIRCLE,
        'star': CharacterSet.STAR,
        'ascii': CharacterSet.ASCII
    }
    char_set = char_set_map.get(args.char_set, CharacterSet.DEFAULT)
    
    # Create hardware controller
    hardware = SimulatedLEDHardware()
    
    # Run tests
    if args.test == 'patterns' or args.test == 'all':
        test_led_patterns(hardware, char_set)
        print()
    
    if args.test == 'animation' or args.test == 'all':
        # Only run animation tests if patterns didn't fail
        try:
            test_punch_card_animation(hardware, char_set)
        except ImportError:
            print("Math module not available, skipping animation tests.")
    
    print("\nAll tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 