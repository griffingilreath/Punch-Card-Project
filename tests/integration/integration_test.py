#!/usr/bin/env python3
"""
Integration test for the Punch Card display system.
This module demonstrates how to integrate the new terminal display
with the existing punch card system.
"""

import os
import sys
import time
import argparse
from typing import List, Optional, Dict, Any, Tuple, Callable

# Add the src directory to the path for running as a main script
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the punch card display class
from punch_card import PunchCardDisplay

# Import the new display adapter
from display_adapter import PunchCardDisplayAdapter

# Create mock classes for testing
class LEDStateManager:
    """Mock LED state manager for testing."""
    
    def __init__(self):
        """Initialize the LED state manager."""
        self.grid = [[False for _ in range(80)] for _ in range(12)]
    
    def set_led(self, row: int, col: int, state: bool) -> None:
        """Set the state of a single LED."""
        if 0 <= row < 12 and 0 <= col < 80:
            self.grid[row][col] = state
    
    def get_led(self, row: int, col: int) -> bool:
        """Get the state of a single LED."""
        if 0 <= row < 12 and 0 <= col < 80:
            return self.grid[row][col]
        return False
    
    def clear_all_leds(self) -> None:
        """Clear all LEDs."""
        self.grid = [[False for _ in range(80)] for _ in range(12)]
    
    def get_led_grid(self) -> List[List[bool]]:
        """Get the LED grid."""
        return self.grid

class SimulatedHardwareController:
    """Mock simulated hardware controller for testing."""
    
    def __init__(self):
        """Initialize the simulated hardware controller."""
        self.connected = False
        self.leds = [[False for _ in range(80)] for _ in range(12)]
    
    def connect(self) -> bool:
        """Connect to the hardware."""
        self.connected = True
        return True
    
    def disconnect(self) -> bool:
        """Disconnect from the hardware."""
        self.connected = False
        return True
    
    def is_connected(self) -> bool:
        """Check if the hardware is connected."""
        return self.connected
    
    def set_led(self, row: int, col: int, state: bool) -> bool:
        """Set the state of a single LED."""
        if 0 <= row < 12 and 0 <= col < 80:
            self.leds[row][col] = state
            return True
        return False
    
    def start(self) -> bool:
        """Start the hardware controller."""
        return True
    
    def stop(self) -> bool:
        """Stop the hardware controller."""
        return True

class EnhancedPunchCardDisplay(PunchCardDisplay):
    """
    Enhanced version of PunchCardDisplay that uses the new terminal display.
    This class overrides key methods to use the new display adapter.
    """
    
    def __init__(self, 
                 char_set_name: str = "default",
                 use_ui: bool = True,
                 verbose: bool = False,
                 led_delay: float = 0.01,
                 message_delay: float = 0.5,
                 random_delay: bool = True,
                 skip_splash: bool = False,
                 debug_mode: bool = False,
                 completion_delay: float = 1.0,
                 receive_duration: float = 5.0,
                 transition_steps: int = 10):
        """
        Initialize the enhanced punch card display.
        
        Args:
            char_set_name: Character set to use for LED visualization
            use_ui: Whether to use the UI
            verbose: Whether to print verbose debug information
            led_delay: Delay between LED updates
            message_delay: Delay between message characters
            random_delay: Whether to use random delays
            skip_splash: Whether to skip the splash screen
            debug_mode: Whether to enable debug mode
            completion_delay: Delay after message completion
            receive_duration: Duration of message reception
            transition_steps: Number of steps in transitions
        """
        # Initialize the parent class with standard parameters
        super().__init__(
            led_delay=led_delay,
            message_delay=message_delay,
            random_delay=random_delay,
            skip_splash=skip_splash,
            debug_mode=debug_mode
        )
        
        # Create display adapter
        self.display_adapter = PunchCardDisplayAdapter(
            num_rows=12,  # Match the punch card rows
            num_cols=80,  # Match the punch card columns
            verbose=verbose,
            char_set_name=char_set_name,
            use_ui=use_ui
        )
        
        # Store additional parameters
        self.verbose = verbose
        self.use_ui = use_ui
        
        # Override parent class settings that weren't in the constructor
        self.completion_delay = completion_delay
        self.receive_duration = receive_duration
        self.transition_steps = transition_steps
    
    def _display_grid(self, grid: List[List[bool]]) -> None:
        """
        Override the _display_grid method to use the display adapter.
        
        Args:
            grid: The LED grid to display
        """
        # Pass the grid to the display adapter
        self.display_adapter.update_grid_from_punch_card(grid)
        
        # Call the parent method to handle the hardware controller
        super()._display_grid(grid)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        # Clean up the display adapter
        self.display_adapter.cleanup()
        
        # Call the parent method to handle hardware cleanup
        super().cleanup()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Integration test for Punch Card display system")
    parser.add_argument("--char-set", default="default", 
                        choices=["default", "block", "circle", "star", "ascii"],
                        help="Character set to use for LED visualization")
    parser.add_argument("--use-ui", action="store_true", 
                        help="Use UI for visualization")
    parser.add_argument("--verbose", action="store_true", 
                        help="Print verbose output")
    parser.add_argument("--message", type=str, default="HELLO WORLD!",
                        help="Message to display")
    parser.add_argument("--source", type=str, default="Integration Test",
                        help="Source of the message")
    parser.add_argument("--skip-splash", action="store_true",
                        help="Skip splash screen")
    parser.add_argument("--fast-mode", action="store_true",
                        help="Run in fast mode with minimal delays")
    return parser.parse_args()

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_args()
    
    try:
        # Create the enhanced punch card display with appropriate settings
        if args.fast_mode:
            # Fast mode settings
            display = EnhancedPunchCardDisplay(
                char_set_name=args.char_set,
                use_ui=args.use_ui,
                verbose=args.verbose,
                led_delay=0.001,        # Very fast LED updates
                message_delay=0.05,     # Fast message display
                random_delay=False,     # No random delays
                skip_splash=args.skip_splash,
                debug_mode=True,        # Enable debug mode for more info
                completion_delay=0.5,   # Short completion delay
                receive_duration=1.0,   # Short receive duration
                transition_steps=3      # Few transition steps
            )
        else:
            # Normal mode settings
            display = EnhancedPunchCardDisplay(
                char_set_name=args.char_set,
                use_ui=args.use_ui,
                verbose=args.verbose,
                led_delay=0.01,         # Standard LED updates
                message_delay=0.1,      # Standard message display
                random_delay=True,      # Use random delays for realism
                skip_splash=args.skip_splash,
                debug_mode=args.verbose, # Debug mode if verbose
                completion_delay=1.0,    # Standard completion delay
                receive_duration=3.0,    # Standard receive duration
                transition_steps=10      # Standard transition steps
            )
        
        try:
            # Show the message
            display.show_message(args.message, source=args.source)
            
            # Wait a moment to see the final state
            time.sleep(2)
            
        finally:
            # Always clean up
            display.cleanup()
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running test: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 