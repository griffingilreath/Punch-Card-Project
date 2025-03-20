#!/usr/bin/env python3
"""
Terminal Display Manager for the Punch Card Project

This module provides a curses-based terminal UI with split-screen functionality
for displaying LED states and debug messages in separate windows.
"""

import curses
import time
from typing import List, Optional, Callable, Dict, Any
import threading
import queue
import signal
import os
import sys


class TerminalDisplay:
    """
    Manages the terminal display using curses to create multiple windows.
    Provides separate areas for LED visualization and debug messages.
    """
    
    def __init__(self, rows: int = 8, columns: int = 16, led_chars: Dict[bool, str] = None, verbose: bool = False):
        """
        Initialize the terminal display.
        
        Args:
            rows: Number of rows in the LED grid
            columns: Number of columns in the LED grid
            led_chars: Characters to use for LED visualization (on/off states)
            verbose: Whether to print verbose output in console mode
        """
        self.rows = rows
        self.columns = columns
        self.led_chars = led_chars or {True: '█', False: '·'}
        self.verbose = verbose
        
        # Enhanced character sets for better visualization
        self.enhanced_chars = {
            'default': {True: '█', False: '·'},
            'block': {True: '█', False: ' '},
            'circle': {True: '●', False: '○'},
            'star': {True: '★', False: '☆'},
            'ascii': {True: '#', False: '.'}
        }
        
        # Use default chars if not specified
        if led_chars is None:
            self.led_chars = self.enhanced_chars['default']
        
        # State variables
        self.running = False
        self.screen = None
        self.led_window = None
        self.debug_window = None
        self.status_window = None
        
        # Message queues for thread-safe updates
        self.led_queue = queue.Queue()
        self.debug_queue = queue.Queue()
        self.status_queue = queue.Queue()
        
        # Current state
        self.current_led_state = [[False for _ in range(columns)] for _ in range(rows)]
        self.debug_messages = []
        self.max_debug_messages = 20  # Number of debug messages to keep
        
        # Thread for UI updates
        self.update_thread = None
        
        # Original terminal state
        self.original_sigint_handler = None
    
    def start(self) -> None:
        """Start the terminal display."""
        if self.running:
            return
            
        # Save original SIGINT handler
        self.original_sigint_handler = signal.getsignal(signal.SIGINT)
        
        # Set a custom handler that will properly shut down curses
        def sigint_handler(sig, frame):
            self.stop()
            # Restore original handler and re-raise signal
            signal.signal(signal.SIGINT, self.original_sigint_handler)
            os.kill(os.getpid(), signal.SIGINT)
        
        signal.signal(signal.SIGINT, sigint_handler)
        
        self.running = True
        self.update_thread = threading.Thread(target=self._ui_thread, daemon=True)
        self.update_thread.start()
    
    def stop(self) -> None:
        """Stop the terminal display."""
        if not self.running:
            return
            
        self.running = False
        
        if self.update_thread:
            self.update_thread.join(timeout=1.0)
            self.update_thread = None
        
        # Restore original SIGINT handler
        if self.original_sigint_handler:
            signal.signal(signal.SIGINT, self.original_sigint_handler)
            self.original_sigint_handler = None
    
    def _ui_thread(self) -> None:
        """Thread function that manages the curses UI."""
        try:
            # Initialize curses
            self.screen = curses.initscr()
            curses.start_color()
            curses.use_default_colors()
            curses.curs_set(0)  # Hide cursor
            curses.noecho()
            curses.cbreak()
            self.screen.keypad(True)
            
            # Initialize color pairs
            curses.init_pair(1, curses.COLOR_WHITE, -1)  # Normal text
            curses.init_pair(2, curses.COLOR_GREEN, -1)   # LED on
            curses.init_pair(3, curses.COLOR_RED, -1)     # Error messages
            curses.init_pair(4, curses.COLOR_YELLOW, -1)  # Status/warnings
            curses.init_pair(5, curses.COLOR_CYAN, -1)    # Info messages
            
            # Get terminal dimensions
            max_y, max_x = self.screen.getmaxyx()
            
            # Check if the terminal is big enough
            if max_y < 12 or max_x < 40:
                raise ValueError(f"Terminal window too small ({max_x}x{max_y}). Need at least 40x12.")
            
            # Create windows
            led_height = min(self.rows + 2, max_y // 2)  # +2 for border
            led_width = min(self.columns * 2 + 2, max_x - 2)  # *2 for spacing, +2 for border
            
            debug_height = max(3, max_y - led_height - 3)  # -3 for status line, at least 3 rows
            
            try:
                self.led_window = curses.newwin(led_height, led_width, 0, 0)
                self.debug_window = curses.newwin(debug_height, max_x - 2, led_height, 0)
                self.status_window = curses.newwin(1, max_x - 2, max_y - 2, 0)
            except Exception as e:
                raise ValueError(f"Failed to create windows: {e}")
            
            # Set up window borders and titles
            self.led_window.box()
            self.debug_window.box()
            
            self.led_window.addstr(0, 2, " LED Display ", curses.A_BOLD)
            self.debug_window.addstr(0, 2, " Debug Messages ", curses.A_BOLD)
            
            self.led_window.refresh()
            self.debug_window.refresh()
            self.status_window.refresh()
            
            # Main UI loop
            while self.running:
                # Process messages in the queues
                self._process_messages()
                
                # Update windows
                self._update_led_display()
                self._update_debug_display()
                self._update_status_display()
                
                # Sleep a bit to reduce CPU usage
                time.sleep(0.05)
        
        except Exception as e:
            # If an error occurs, try to clean up and report it
            try:
                self._cleanup_curses()
                print(f"Error in terminal display: {e}")
                # Fall back to console output mode
                self._fallback_to_console_mode()
            except Exception as e2:
                print(f"Error while cleaning up curses: {e2}")
        
        finally:
            # Clean up curses
            self._cleanup_curses()
    
    def _cleanup_curses(self) -> None:
        """Clean up curses interface."""
        if curses:
            try:
                curses.echo()
                curses.nocbreak()
                if self.screen:
                    self.screen.keypad(False)
                curses.endwin()
            except:
                pass
    
    def _process_messages(self) -> None:
        """Process messages from the queues."""
        # Process LED updates
        while not self.led_queue.empty():
            try:
                message = self.led_queue.get_nowait()
                if message['type'] == 'grid':
                    self.current_led_state = message['grid']
                elif message['type'] == 'led':
                    row, col, state = message['row'], message['column'], message['state']
                    if 0 <= row < self.rows and 0 <= col < self.columns:
                        self.current_led_state[row][col] = state
                self.led_queue.task_done()
            except queue.Empty:
                break
        
        # Process debug messages
        while not self.debug_queue.empty():
            try:
                message = self.debug_queue.get_nowait()
                self.debug_messages.append(message)
                # Keep only the last N messages
                if len(self.debug_messages) > self.max_debug_messages:
                    self.debug_messages = self.debug_messages[-self.max_debug_messages:]
                self.debug_queue.task_done()
            except queue.Empty:
                break
        
        # Process status messages
        while not self.status_queue.empty():
            try:
                message = self.status_queue.get_nowait()
                self._update_status_message(message)
                self.status_queue.task_done()
            except queue.Empty:
                break
    
    def _update_led_display(self) -> None:
        """Update the LED display window."""
        if not self.led_window:
            return
            
        # Clear the LED display area (inside the border)
        for y in range(1, self.rows + 1):
            self.led_window.addstr(y, 1, " " * (self.columns * 2))
        
        # Draw current LED state
        for row in range(min(self.rows, self.led_window.getmaxyx()[0] - 2)):
            for col in range(min(self.columns, (self.led_window.getmaxyx()[1] - 2) // 2)):
                state = self.current_led_state[row][col]
                char = self.led_chars[state]
                color = curses.color_pair(2) if state else curses.color_pair(1)
                self.led_window.addstr(row + 1, col * 2 + 1, char, color)
        
        self.led_window.refresh()
    
    def _update_debug_display(self) -> None:
        """Update the debug message window."""
        if not self.debug_window:
            return
            
        # Clear the debug area (inside the border)
        max_y, max_x = self.debug_window.getmaxyx()
        for y in range(1, max_y - 1):
            self.debug_window.addstr(y, 1, " " * (max_x - 2))
        
        # Display debug messages
        line = 1
        for message in self.debug_messages[-max(1, max_y - 2):]:
            if line >= max_y - 1:
                break
                
            msg_text = message.get('text', '')
            msg_type = message.get('type', 'info')
            
            # Select color based on message type
            color = curses.color_pair(1)  # Default: white
            if msg_type == 'error':
                color = curses.color_pair(3)  # Red
            elif msg_type == 'warning':
                color = curses.color_pair(4)  # Yellow
            elif msg_type == 'info':
                color = curses.color_pair(5)  # Cyan
            
            # Truncate message if it's too long
            if len(msg_text) > max_x - 4:
                msg_text = msg_text[:max_x - 7] + "..."
            
            self.debug_window.addstr(line, 1, msg_text, color)
            line += 1
        
        self.debug_window.refresh()
    
    def _update_status_display(self) -> None:
        """Update the status line window."""
        if not self.status_window:
            return
            
        self.status_window.refresh()
    
    def _update_status_message(self, message: Dict[str, Any]) -> None:
        """Update the status message."""
        if not self.status_window:
            return
            
        max_y, max_x = self.status_window.getmaxyx()
        status_text = message.get('text', '')
        status_type = message.get('type', 'info')
        
        # Select color based on message type
        color = curses.color_pair(1)  # Default: white
        if status_type == 'error':
            color = curses.color_pair(3)  # Red
        elif status_type == 'warning':
            color = curses.color_pair(4)  # Yellow
        elif status_type == 'info':
            color = curses.color_pair(5)  # Cyan
        
        # Clear the status line
        self.status_window.clear()
        
        # Truncate message if it's too long
        if len(status_text) > max_x - 2:
            status_text = status_text[:max_x - 5] + "..."
        
        self.status_window.addstr(0, 1, status_text, color)
        self.status_window.refresh()
    
    def _fallback_to_console_mode(self) -> None:
        """Fall back to console output mode if curses fails."""
        print("Falling back to console output mode.")
        print("Debug messages will be printed to the console.")
        
        # Process any existing messages
        while not self.debug_queue.empty():
            try:
                message = self.debug_queue.get_nowait()
                msg_text = message.get('text', '')
                msg_type = message.get('type', 'info')
                prefix = "[INFO]"
                if msg_type == 'error':
                    prefix = "[ERROR]"
                elif msg_type == 'warning':
                    prefix = "[WARNING]"
                print(f"{prefix} {msg_text}")
                self.debug_queue.task_done()
            except queue.Empty:
                break
        
        # Set up a thread to handle future messages
        self._fallback_thread = threading.Thread(target=self._fallback_thread_func, daemon=True)
        self._fallback_thread.start()

    def _fallback_thread_func(self) -> None:
        """Handle messages in fallback console mode."""
        # Track grid updates to throttle visualization
        self.last_grid_print_time = 0
        
        while self.running:
            # Process debug messages
            while not self.debug_queue.empty():
                try:
                    message = self.debug_queue.get_nowait()
                    msg_text = message.get('text', '')
                    msg_type = message.get('type', 'info')
                    prefix = "[INFO]"
                    if msg_type == 'error':
                        prefix = "[ERROR]"
                    elif msg_type == 'warning':
                        prefix = "[WARNING]"
                    print(f"{prefix} {msg_text}")
                    self.debug_queue.task_done()
                except queue.Empty:
                    break
            
            # Process status messages
            while not self.status_queue.empty():
                try:
                    message = self.status_queue.get_nowait()
                    status_text = message.get('text', '')
                    status_type = message.get('type', 'info')
                    prefix = "[STATUS]"
                    print(f"{prefix} {status_text}")
                    self.status_queue.task_done()
                except queue.Empty:
                    break
            
            # Process LED updates - we'll handle grid updates in update_led_grid
            led_update_count = 0
            led_update_happened = False
            while not self.led_queue.empty() and led_update_count < 20:  # Limit how many we process at once
                try:
                    message = self.led_queue.get_nowait()
                    if message['type'] == 'led':
                        # For individual LED updates, we update our internal state
                        row, col, state = message['row'], message['column'], message['state']
                        if 0 <= row < self.rows and 0 <= col < self.columns:
                            self.current_led_state[row][col] = state
                            # Print information about LED state changes
                            if self.verbose:
                                print(f"[INFO] LED [{row},{col}] set to {state}")
                            led_update_happened = True
                    elif message['type'] == 'grid':
                        # Grid update will be handled in update_led_grid
                        self.current_led_state = message['grid']
                        led_update_happened = True
                    
                    self.led_queue.task_done()
                    led_update_count += 1
                except queue.Empty:
                    break
            
            # If there were LED updates, consider printing the grid
            current_time = time.time()
            if led_update_happened and current_time - self.last_grid_print_time > 2.0:
                self._print_led_grid_ascii()
                self.last_grid_print_time = current_time
            
            # Sleep a bit to reduce CPU usage
            time.sleep(0.1)

    def _print_led_grid_ascii(self):
        """Print a nicely formatted ASCII representation of the current LED grid."""
        if not self.current_led_state:
            return
            
        # Create column headers (numbers)
        header = "    " # Space for row numbers
        for col in range(min(16, self.columns)):
            header += f"{col:1d} "
        
        # Create a horizontal line
        hline = "   +" + "-" * (min(16, self.columns) * 2 - 1) + "+"
        
        print("\n" + header)
        print(hline)
        
        # Print each row with row number and LED states
        for row in range(min(8, self.rows)):
            row_str = f"{row:2d} | "
            for col in range(min(16, self.columns)):
                row_str += self.led_chars[self.current_led_state[row][col]] + " "
            row_str = row_str.rstrip() + " |"
            print(row_str)
        
        print(hline + "\n")
    
    def set_character_set(self, char_set: str = 'default'):
        """
        Set the character set to use for LED visualization.
        
        Args:
            char_set: Name of the character set to use ('default', 'block', 'circle', 'star', 'ascii')
        """
        if char_set in self.enhanced_chars:
            self.led_chars = self.enhanced_chars[char_set]
        else:
            print(f"[WARNING] Character set '{char_set}' not found. Using default.")
            self.led_chars = self.enhanced_chars['default']
    
    def set_verbose(self, verbose: bool):
        """
        Set whether to print verbose output in console mode.
        
        Args:
            verbose: Whether to print verbose output
        """
        self.verbose = verbose

    def update_led_grid(self, grid: List[List[bool]]) -> None:
        """
        Update the entire LED grid.
        
        Args:
            grid: 2D array of LED states (True = on, False = off)
        """
        if not self.running:
            return
        
        # For console fallback mode, print a text representation of the grid
        if self.screen is None and len(grid) > 0:
            # Only print full grid updates occasionally to avoid console spam
            current_time = time.time()
            if hasattr(self, 'last_grid_print_time') and current_time - self.last_grid_print_time < 0.5:
                # Don't print too often
                self.led_queue.put({
                    'type': 'grid',
                    'grid': grid
                })
                return
            
            self.last_grid_print_time = current_time
            self.current_led_state = grid
            
            # The actual grid printing is now handled in _fallback_thread_func
            # to avoid duplicating code and to make it available for individual LED updates too
        
        self.led_queue.put({
            'type': 'grid',
            'grid': grid
        })
    
    def update_led(self, row: int, column: int, state: bool) -> None:
        """
        Update a single LED.
        
        Args:
            row: Row index
            column: Column index
            state: New state (True = on, False = off)
        """
        if not self.running:
            return
            
        self.led_queue.put({
            'type': 'led',
            'row': row,
            'column': column,
            'state': state
        })
    
    def add_debug_message(self, message: str, message_type: str = 'info') -> None:
        """
        Add a debug message.
        
        Args:
            message: Message text
            message_type: Message type ('info', 'warning', 'error')
        """
        if not self.running:
            return
            
        self.debug_queue.put({
            'text': message,
            'type': message_type,
            'timestamp': time.time()
        })
    
    def set_status(self, message: str, message_type: str = 'info') -> None:
        """
        Set the status message.
        
        Args:
            message: Status message text
            message_type: Message type ('info', 'warning', 'error')
        """
        if not self.running:
            return
            
        self.status_queue.put({
            'text': message,
            'type': message_type,
            'timestamp': time.time()
        })


# Global instance for easy access
_instance = None

def get_instance(rows: int = 8, columns: int = 16, verbose: bool = False, char_set: str = 'default') -> TerminalDisplay:
    """
    Get or create the terminal display instance.
    
    Args:
        rows: Number of rows in the LED grid
        columns: Number of columns in the LED grid
        verbose: Whether to print verbose output in console mode
        char_set: Which character set to use ('default', 'block', 'circle', 'star', 'ascii')
    
    Returns:
        TerminalDisplay: The terminal display instance
    """
    global _instance
    if _instance is None:
        _instance = TerminalDisplay(rows, columns, verbose=verbose)
        if char_set != 'default':
            _instance.set_character_set(char_set)
    return _instance


# Example usage
if __name__ == "__main__":
    # Create and start the terminal display
    display = get_instance(8, 16)
    display.start()
    
    try:
        # Update LEDs with a pattern
        for i in range(8):
            for j in range(16):
                display.update_led(i, j, (i + j) % 2 == 0)
                time.sleep(0.02)
        
        # Add some debug messages
        display.add_debug_message("Test debug message")
        display.add_debug_message("Warning message", "warning")
        display.add_debug_message("Error message", "error")
        
        # Set status
        display.set_status("Running LED test...")
        
        # Show an animation
        for _ in range(10):
            # Clear all LEDs
            for i in range(8):
                for j in range(16):
                    display.update_led(i, j, False)
            
            # Draw a moving pattern
            for i in range(8):
                display.update_led(i, i, True)
                display.update_led(i, 15-i, True)
                time.sleep(0.1)
            
            time.sleep(0.5)
        
        # Final status
        display.set_status("Test completed successfully.", "info")
        
        # Wait for user to exit
        time.sleep(5)
    
    finally:
        # Stop the display
        display.stop() 