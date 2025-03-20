#!/usr/bin/env python3
"""
LED State Manager for the Punch Card Project

This module provides a simple, centralized state management system for LED states.
It acts as a source of truth for both the terminal display and physical LED hardware,
ensuring synchronization between what's displayed in the terminal and the physical LEDs.
"""

from typing import List, Dict, Callable, Set, Optional
import threading
import time
import json
from pathlib import Path


class LEDStateManager:
    """
    Central manager for LED states across the system.
    
    This class:
    1. Maintains the current state of all LEDs
    2. Provides methods to update LED states
    3. Notifies registered observers when states change
    """
    
    def __init__(self, rows: int = 12, columns: int = 80):
        """Initialize the LED state manager with grid dimensions matching the punch card."""
        self.rows = rows
        self.columns = columns
        # Initialize all LEDs to off (False)
        self._led_states = [[False for _ in range(columns)] for _ in range(rows)]
        # Lock for thread safety
        self._lock = threading.Lock()
        # Registered observers to notify on state changes
        self._observers: Set[Callable[[int, int, bool], None]] = set()
        
    def register_observer(self, observer: Callable[[int, int, bool], None]) -> None:
        """
        Register an observer to be notified of LED state changes.
        
        Args:
            observer: Function that accepts row, column, and state parameters
        """
        self._observers.add(observer)
        
    def unregister_observer(self, observer: Callable[[int, int, bool], None]) -> None:
        """
        Unregister a previously registered observer.
        
        Args:
            observer: The callback function to unregister
        """
        if observer in self._observers:
            self._observers.remove(observer)
    
    def set_led(self, row: int, column: int, state: bool) -> None:
        """
        Set the state of a single LED.
        
        Args:
            row: The row index (0-based)
            column: The column index (0-based)
            state: True for on, False for off
        """
        with self._lock:
            if 0 <= row < self.rows and 0 <= column < self.columns:
                # Only update if the state is actually changing
                if self._led_states[row][column] != state:
                    self._led_states[row][column] = state
                    self._notify_observers(row, column, state)
    
    def get_led(self, row: int, column: int) -> bool:
        """
        Get the current state of a single LED.
        
        Args:
            row: The row index (0-based)
            column: The column index (0-based)
            
        Returns:
            bool: True if the LED is on, False if off
        """
        with self._lock:
            if 0 <= row < self.rows and 0 <= column < self.columns:
                return self._led_states[row][column]
            return False
    
    def set_all_leds(self, state: bool) -> None:
        """
        Set all LEDs to the same state.
        
        Args:
            state: True for on, False for off
        """
        with self._lock:
            # Faster implementation - set entire rows at once
            for row in range(self.rows):
                self._led_states[row] = [state for _ in range(self.columns)]
        
        # Notify observers outside the lock
        for observer in self._observers:
            try:
                # Use a special signal (-1, -1) to indicate bulk update
                observer(-1, -1, state)
            except Exception as e:
                print(f"Error notifying observer: {e}")
    
    def set_grid(self, states: List[List[bool]]) -> None:
        """
        Set the state of the entire LED grid.
        
        Args:
            states: 2D list of states (True=on, False=off) for the entire grid
        """
        with self._lock:
            for row in range(min(len(states), self.rows)):
                for col in range(min(len(states[row]), self.columns)):
                    self._led_states[row][col] = states[row][col]
            
            # Notify observers with a special signal for a full grid update
            for observer in self._observers:
                try:
                    # Use a special signal (-1, -1) to indicate full grid update
                    observer(-1, -1, True)
                except Exception as e:
                    print(f"Error notifying observer: {e}")
    
    def get_grid(self) -> List[List[bool]]:
        """
        Get the current state of the entire LED grid.
        
        Returns:
            List[List[bool]]: 2D list of LED states
        """
        with self._lock:
            # Return a deep copy to prevent external modification
            return [row[:] for row in self._led_states]
    
    def _notify_observers(self, row: int, column: int, state: bool) -> None:
        """
        Notify all registered observers about a state change.
        
        Args:
            row: The row of the changed LED
            column: The column of the changed LED
            state: The new state of the LED
        """
        for observer in self._observers:
            try:
                observer(row, column, state)
            except Exception as e:
                print(f"Error notifying observer: {e}")

    def display_character(self, column: int, char: str, char_mapping: Dict[str, List[int]]) -> None:
        """
        Display a character at the specified column using the provided character mapping.
        
        Args:
            column: The column index to place the character
            char: The character to display
            char_mapping: Dictionary mapping characters to punch patterns
        """
        char = char.upper()
        pattern = char_mapping.get(char, [0] * self.rows)
        
        with self._lock:
            for row in range(self.rows):
                self._led_states[row][column] = bool(pattern[row])
                
            # Notify about column update
            for observer in self._observers:
                try:
                    # Use a special signal (-1, column) to indicate column update
                    observer(-1, column, True)
                except Exception as e:
                    print(f"Error notifying observer: {e}")


# Singleton instance for global access
_instance = None

def get_instance(rows: int = 12, columns: int = 80) -> LEDStateManager:
    """
    Get the singleton instance of the LEDStateManager.
    
    This ensures that all components are using the same LED state manager.
    
    Args:
        rows: Number of rows in the LED grid (only used on first call)
        columns: Number of columns in the LED grid (only used on first call)
        
    Returns:
        LEDStateManager: The shared instance
    """
    global _instance
    if _instance is None:
        _instance = LEDStateManager(rows, columns)
    return _instance


if __name__ == "__main__":
    # Example usage
    manager = get_instance()
    
    # Define a simple observer function that just prints changes
    def print_led_change(row, col, state):
        if row == -1 and col == -1:
            print(f"Full grid update, example LED at [0,0]: {manager.get_led(0, 0)}")
        elif row == -1:
            print(f"Column {col} update")
        elif col == -1:
            print(f"Row {row} update")
        else:
            print(f"LED at [{row},{col}] changed to {state}")
    
    # Register the observer
    manager.register_observer(print_led_change)
    
    # Test setting a single LED
    manager.set_led(5, 10, True)
    
    # Test setting all LEDs
    manager.set_all_leds(False)
    
    # Test setting a grid pattern
    test_grid = [[False for _ in range(80)] for _ in range(12)]
    for i in range(12):
        test_grid[i][i] = True  # Diagonal pattern
    
    manager.set_grid(test_grid) 