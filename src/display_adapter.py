#!/usr/bin/env python3
"""
Display Adapter for the Punch Card Project

This module bridges the existing punch card display code with the new
LED state manager. It observes the punch card display and updates the
LED state manager accordingly, ensuring that what's shown in the terminal
is also reflected on the physical LEDs.
"""

import time
import threading
from typing import Optional, Dict, List, Any

# Import our modules
from src.led_state_manager import get_instance as get_led_manager


class PunchCardDisplayAdapter:
    """
    Adapter that connects the existing PunchCardDisplay with the LED state manager.
    
    This class observes state changes in the punch card display and 
    propagates them to the LED state manager, which in turn controls
    the physical LED hardware.
    """
    
    def __init__(self, char_mapping: Dict[str, List[int]]):
        """
        Initialize the adapter with the character mapping.
        
        Args:
            char_mapping: Mapping of characters to LED punch patterns
        """
        self.char_mapping = char_mapping
        self.led_manager = get_led_manager()
        self._running = False
        self._thread = None
        
        # We don't have direct access to the punch card grid, so we'll
        # maintain our own state to detect changes
        self.current_grid = [[False for _ in range(self.led_manager.columns)] 
                            for _ in range(self.led_manager.rows)]
        
    def connect_to_punch_card_display(self, punch_card_display: Any) -> None:
        """
        Connect to the existing punch card display.
        
        This method patches the relevant methods in the punch card display
        to intercept state changes and update the LED state manager.
        
        Args:
            punch_card_display: The PunchCardDisplay instance to connect to
        """
        # Store a reference to the punch card display
        self.punch_card_display = punch_card_display
        
        # Patch the methods that update the grid
        self._patch_display_methods()
        
        print("Connected adapter to punch card display")
    
    def _patch_display_methods(self) -> None:
        """
        Patch the methods in PunchCardDisplay that update the LED grid.
        
        This is done by preserving the original methods and extending them
        to also update the LED state manager.
        """
        # Save original methods
        original_set_led = getattr(self.punch_card_display, 'set_led', None)
        original_clear = getattr(self.punch_card_display, 'clear', None)
        original_show_message = getattr(self.punch_card_display, 'show_message', None)
        original_show_splash_screen = getattr(self.punch_card_display, 'show_splash_screen', None)
        
        # Define patched methods
        def patched_set_led(self_display, row, col, state):
            # Call original method
            if original_set_led:
                original_set_led(self_display, row, col, state)
            
            # Update LED state manager
            self.led_manager.set_led(row, col, bool(state))
        
        def patched_clear(self_display):
            # Call original method
            if original_clear:
                original_clear(self_display)
            
            # Update LED state manager
            self.led_manager.set_all_leds(False)
        
        # Apply patches if the methods exist
        if original_set_led:
            self.punch_card_display.set_led = lambda row, col, state: patched_set_led(self.punch_card_display, row, col, state)
        
        if original_clear:
            self.punch_card_display.clear = lambda: patched_clear(self.punch_card_display)
        
        # For these methods, we'll use the originals directly since all LED updates
        # will be caught by our patched set_led method or the monitor_grid_changes method
        
        # No need to patch show_message, as it will call set_led internally
        
        # No need to patch show_splash_screen
    
    def start_monitoring(self) -> None:
        """Start monitoring the punch card display for changes."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor_grid_changes, daemon=True)
        self._thread.start()
        
        print("Started monitoring punch card display")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring the punch card display."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
    
    def _monitor_grid_changes(self) -> None:
        """
        Monitor the punch card display grid for changes.
        
        This method is a fallback for catching changes that aren't
        directly made through the patched methods. It runs in a 
        background thread.
        """
        # Use the grid and current_message attributes from the punch card display
        # to detect changes that our method patching might have missed
        while self._running:
            try:
                # Check if the grid attribute exists
                if hasattr(self.punch_card_display, 'grid'):
                    # Convert the punch card grid to our format (bool)
                    new_grid = [[bool(self.punch_card_display.grid[row][col]) 
                               for col in range(self.led_manager.columns)] 
                               for row in range(self.led_manager.rows)]
                    
                    # Check for changes
                    changes_detected = False
                    for row in range(self.led_manager.rows):
                        for col in range(self.led_manager.columns):
                            if self.current_grid[row][col] != new_grid[row][col]:
                                # Update our state
                                self.current_grid[row][col] = new_grid[row][col]
                                # Update LED state manager
                                self.led_manager.set_led(row, col, new_grid[row][col])
                                changes_detected = True
                    
                    # If there were changes, we've already updated the LED state manager
                    # individually for each changed LED
                    if not changes_detected:
                        # Check if the current_message attribute exists and has changed
                        if hasattr(self.punch_card_display, 'current_message'):
                            message = self.punch_card_display.current_message
                            
                            # If the message is new, update our state and the LED state manager
                            if message:
                                for col, char in enumerate(message):
                                    if col < self.led_manager.columns:
                                        # Use the display_character method which uses the
                                        # character mapping to correctly set the LED pattern
                                        self.led_manager.display_character(col, char, self.char_mapping)
            
            except Exception as e:
                print(f"Error monitoring punch card display: {e}")
            
            # Sleep to avoid hogging CPU
            time.sleep(0.1)
    
    def update_message(self, message: str) -> None:
        """
        Update the LED state manager with a message.
        
        Args:
            message: The message to display
        """
        # Clear the grid first
        self.led_manager.set_all_leds(False)
        
        # Set each character
        for col, char in enumerate(message):
            if col < self.led_manager.columns:
                self.led_manager.display_character(col, char, self.char_mapping)


def create_punch_card_adapter(punch_card_display: Any, char_mapping: Dict[str, List[int]]) -> PunchCardDisplayAdapter:
    """
    Create and connect a punch card display adapter.
    
    Args:
        punch_card_display: The PunchCardDisplay instance
        char_mapping: Mapping of characters to LED patterns
        
    Returns:
        PunchCardDisplayAdapter: The connected adapter
    """
    adapter = PunchCardDisplayAdapter(char_mapping)
    adapter.connect_to_punch_card_display(punch_card_display)
    adapter.start_monitoring()
    return adapter


if __name__ == "__main__":
    # This would normally be imported from the punch_card module
    # For testing, we'll create a simple mock
    class MockPunchCardDisplay:
        def __init__(self):
            self.rows = 12
            self.columns = 80
            self.grid = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
            self.current_message = ""
        
        def set_led(self, row, col, state):
            if 0 <= row < self.rows and 0 <= col < self.columns:
                self.grid[row][col] = 1 if state else 0
        
        def clear(self):
            self.grid = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
            self.current_message = ""
        
        def show_message(self, message, source="", animate=True):
            self.current_message = message
            print(f"MockPunchCardDisplay: Showing message: {message}")
        
        def show_splash_screen(self):
            print("MockPunchCardDisplay: Showing splash screen")
    
    # Mock character mapping
    mock_char_mapping = {
        'A': [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        'B': [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
    }
    
    # Create mock display and adapter
    mock_display = MockPunchCardDisplay()
    adapter = create_punch_card_adapter(mock_display, mock_char_mapping)
    
    # Test it
    mock_display.show_message("AB")
    
    # Wait for a moment
    time.sleep(1)
    
    # Clean up
    adapter.stop_monitoring() 