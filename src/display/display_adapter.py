"""
Display adapter for Punch Card Project.
This module provides an adapter to integrate the terminal display
with the existing punch card system.
"""

import time
import threading
from typing import List, Tuple, Dict, Any, Optional

# Import the terminal display module
from src.display.terminal_display import TerminalDisplay, CharacterSet

class DisplayAdapter:
    """Adapter to connect a display interface with the punch card system."""
    
    def __init__(self, punch_card, display):
        """
        Initialize the display adapter.
        
        Args:
            punch_card: The punch card instance
            display: The display instance (terminal or GUI)
        """
        self.punch_card = punch_card
        self.display = display
        self.running = False
        self.update_thread = None
    
    def start(self):
        """Start the display adapter."""
        self.running = True
        
        # Start the punch card system if needed
        if hasattr(self.punch_card, 'start') and callable(self.punch_card.start):
            self.punch_card.start()
            
        # Start the display if needed
        if hasattr(self.display, 'start') and callable(self.display.start):
            self.display.start()
        
        # Start update thread
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def stop(self):
        """Stop the display adapter."""
        self.running = False
        
        # Stop the punch card system if needed
        if hasattr(self.punch_card, 'stop') and callable(self.punch_card.stop):
            self.punch_card.stop()
            
        # Stop the display if needed
        if hasattr(self.display, 'stop') and callable(self.display.stop):
            self.display.stop()
        
        # Wait for update thread to finish
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
    
    def _update_loop(self):
        """Update loop to keep the display in sync with the punch card state."""
        try:
            while self.running:
                # Get data from punch card
                if hasattr(self.punch_card, 'get_display_data'):
                    data = self.punch_card.get_display_data()
                    
                    # Update display with data
                    if hasattr(self.display, 'update'):
                        self.display.update(data)
                
                # Sleep to avoid high CPU usage
                time.sleep(0.1)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(f"Error in display adapter update loop: {e}")
            # Exit the loop but don't crash the application
            self.running = False

# For backwards compatibility
PunchCardDisplayAdapter = DisplayAdapter

class PunchCardDisplayAdapter:
    """Adapter to integrate terminal display with punch card system."""
    
    def __init__(self, 
                 num_rows: int = 12, 
                 num_cols: int = 80, 
                 verbose: bool = False, 
                 char_set_name: str = "default",
                 use_ui: bool = True):
        """
        Initialize the punch card display adapter.
        
        Args:
            num_rows: Number of rows in the LED grid
            num_cols: Number of columns in the LED grid
            verbose: Whether to print verbose debug information
            char_set_name: Character set to use for LED visualization
            use_ui: Whether to use the UI (if False, will use console output)
        """
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.verbose = verbose
        self.use_ui = use_ui
        
        # Flag to suppress LED output for cleaner console display
        self._suppress_led_output = False
        
        # Map character set name to enum
        char_set_map = {
            "default": CharacterSet.DEFAULT,
            "block": CharacterSet.BLOCK,
            "circle": CharacterSet.CIRCLE,
            "star": CharacterSet.STAR,
            "ascii": CharacterSet.ASCII
        }
        char_set = char_set_map.get(char_set_name.lower(), CharacterSet.DEFAULT)
        
        # Initialize terminal display
        self.terminal_display = TerminalDisplay(verbose=verbose, char_set=char_set)
        
        # Initialize grid state
        self.grid_state = [[False for _ in range(num_cols)] for _ in range(num_rows)]
        
        # Start the terminal display
        if self.use_ui:
            self.terminal_display.start()
            self.terminal_display.set_status("Punch Card Display Adapter initialized")
    
    def cleanup(self):
        """Clean up resources."""
        if self.use_ui and self.terminal_display:
            self.terminal_display.stop()
    
    def set_led(self, row: int, col: int, state: bool):
        """
        Set the state of a single LED.
        
        Args:
            row: Row index (0-based)
            col: Column index (0-based)
            state: True to turn on, False to turn off
        """
        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            self.grid_state[row][col] = state
            
            if self.use_ui:
                self.terminal_display.update_led_grid(self.grid_state)
            elif self.verbose and not self._suppress_led_output:
                print(f"Set LED at ({row}, {col}) to {state}")
    
    def set_multiple_leds(self, led_states: List[Tuple[int, int, bool]]):
        """
        Set the state of multiple LEDs at once.
        
        Args:
            led_states: List of (row, col, state) tuples
        """
        for row, col, state in led_states:
            if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
                self.grid_state[row][col] = state
        
        if self.use_ui:
            self.terminal_display.update_led_grid(self.grid_state)
        elif self.verbose:
            print(f"Updated {len(led_states)} LEDs")
    
    def clear_all(self):
        """Clear all LEDs (turn them off)."""
        self.grid_state = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        if self.use_ui:
            self.terminal_display.update_led_grid(self.grid_state)
            self.terminal_display.set_status("Cleared all LEDs")
        elif self.verbose:
            print("Cleared all LEDs")
    
    def log_message(self, message: str, level: str = "info"):
        """
        Log a message to the terminal display.
        
        Args:
            message: Message to log
            level: Log level (info, warning, error, debug)
        """
        if self.use_ui:
            if level in ["info", "warning", "error"]:
                self.terminal_display.set_status(message, level)
            else:
                self.terminal_display.add_debug_message(message, level)
        elif self.verbose:
            print(f"[{level.upper()}] {message}")
    
    def get_grid_state(self) -> List[List[bool]]:
        """Get the current grid state."""
        return self.grid_state
    
    def update_grid_from_punch_card(self, punch_card_grid: List[List[bool]]):
        """
        Update the grid state from the punch card grid.
        This handles any differences in grid format between systems.
        
        Args:
            punch_card_grid: Punch card grid to update from
        """
        # Copy the grid data (with size checks)
        rows_to_copy = min(len(punch_card_grid), self.num_rows)
        
        for i in range(rows_to_copy):
            row = punch_card_grid[i]
            cols_to_copy = min(len(row), self.num_cols)
            for j in range(cols_to_copy):
                self.grid_state[i][j] = row[j]
        
        if self.use_ui:
            self.terminal_display.update_led_grid(self.grid_state)
            self.terminal_display.add_debug_message(f"Updated grid from punch card ({rows_to_copy}x{cols_to_copy})")
        elif self.verbose:
            print(f"Updated grid from punch card ({rows_to_copy}x{cols_to_copy})") 