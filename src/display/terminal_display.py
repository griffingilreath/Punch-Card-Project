"""
Terminal display module for Punch Card Project.
This module provides a more stable terminal UI for the Punch Card Project,
including fallback console output for environments where curses isn't ideal.
"""

import os
import sys
import time
import curses
import shutil
import threading
import queue
from enum import Enum, auto
from typing import List, Tuple, Dict, Any, Optional, Union

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
        CharacterSet.DEFAULT: ("█", "□"),  # Default: Filled/empty box
        CharacterSet.BLOCK: ("█", " "),    # Block: Block/space
        CharacterSet.CIRCLE: ("●", "○"),   # Circle: Filled/empty circle
        CharacterSet.STAR: ("★", "☆"),     # Star: Filled/empty star
        CharacterSet.ASCII: ("X", "."),    # ASCII: X/period
    }
    return mappings.get(char_set, mappings[CharacterSet.DEFAULT])

class TerminalDisplay:
    """Enhanced terminal display with fallback console output."""
    
    def __init__(self, verbose: bool = False, char_set: CharacterSet = CharacterSet.DEFAULT):
        """Initialize the terminal display."""
        self.verbose = verbose
        self.char_set = char_set
        self.message_queue = queue.Queue()
        self.running = False
        self.thread = None
        self.use_curses = True
        self.last_grid_update = 0
        self.update_interval = 0.1  # Limit grid updates to once per 0.1 seconds
        
        # Try to determine terminal size
        try:
            self.term_width, self.term_height = shutil.get_terminal_size()
        except:
            self.term_width, self.term_height = 80, 24
        
        # Check if terminal size is adequate for UI
        if self.term_width < 40 or self.term_height < 12:
            if verbose:
                print(f"Warning: Terminal size ({self.term_width}x{self.term_height}) is too small for UI. Need at least 40x12.")
                print("Falling back to standard console output.")
            self.use_curses = False
        
        # Check if FORCE_CONSOLE environment variable is set
        if os.environ.get('FORCE_CONSOLE', '0') == '1':
            if verbose:
                print("Console mode forced by environment variable.")
            self.use_curses = False
        
        # Get character set mapping
        self.on_char, self.off_char = get_char_set_mapping(char_set)
    
    def start(self):
        """Start the terminal display thread."""
        if self.running:
            return
        
        self.running = True
        
        if self.use_curses:
            self.thread = threading.Thread(target=self._curses_thread_func)
        else:
            self.thread = threading.Thread(target=self._fallback_thread_func)
        
        self.thread.daemon = True
        self.thread.start()
        
        if self.verbose:
            if self.use_curses:
                print("Terminal display started in curses mode.")
            else:
                print("Terminal display started in fallback console mode.")
    
    def stop(self):
        """Stop the terminal display thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
        
        if self.verbose:
            print("Terminal display stopped.")
    
    def set_status(self, message: str, level: str = "info"):
        """Set a status message."""
        self.message_queue.put(("status", message, level))
    
    def add_debug_message(self, message: str, level: str = "debug"):
        """Add a debug message."""
        self.message_queue.put(("debug", message, level))
    
    def update_led_grid(self, grid: List[List[bool]]):
        """Update the LED grid state."""
        # Limit how often we update the full grid to avoid console spam
        current_time = time.time()
        if current_time - self.last_grid_update >= self.update_interval:
            self.last_grid_update = current_time
            self.message_queue.put(("grid", grid))
    
    def _curses_thread_func(self):
        """Thread function for curses-based UI."""
        try:
            curses.wrapper(self._curses_main)
        except Exception as e:
            print(f"Error in curses UI: {e}")
            print("Falling back to standard console output.")
            self.use_curses = False
            self._fallback_thread_func()
    
    def _curses_main(self, stdscr):
        """Main function for curses-based UI."""
        # Setup curses
        curses.curs_set(0)  # Hide cursor
        curses.use_default_colors()
        
        # Initialize color pairs if available
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_GREEN, -1)  # Green for info
            curses.init_pair(2, curses.COLOR_RED, -1)    # Red for error
            curses.init_pair(3, curses.COLOR_YELLOW, -1) # Yellow for warning
            curses.init_pair(4, curses.COLOR_CYAN, -1)   # Cyan for debug
        
        # Initialize windows
        height, width = stdscr.getmaxyx()
        
        # Status window at top (2 lines)
        status_win = curses.newwin(2, width, 0, 0)
        status_win.box()
        
        # Debug window at bottom (5 lines)
        debug_win = curses.newwin(5, width, height - 5, 0)
        debug_win.box()
        
        # LED grid window in the middle
        grid_height = height - 7  # Minus status and debug windows
        grid_win = curses.newwin(grid_height, width, 2, 0)
        grid_win.box()
        
        # Initialize state
        status_message = "Terminal display initialized."
        debug_messages = []
        led_grid = None
        
        # Main loop
        while self.running:
            # Process messages from queue
            try:
                while not self.message_queue.empty():
                    msg_type, *args = self.message_queue.get(block=False)
                    
                    if msg_type == "status":
                        status_message, level = args
                    elif msg_type == "debug":
                        debug_message, level = args
                        debug_messages.append((debug_message, level))
                        # Keep only the last 3 debug messages
                        if len(debug_messages) > 3:
                            debug_messages.pop(0)
                    elif msg_type == "grid":
                        led_grid = args[0]
            except queue.Empty:
                pass
            
            # Update status window
            status_win.clear()
            status_win.box()
            status_win.addstr(1, 2, f"Status: {status_message}"[:width-4])
            
            # Update debug window
            debug_win.clear()
            debug_win.box()
            debug_win.addstr(0, 2, "Debug Messages")
            for i, (msg, level) in enumerate(debug_messages[-3:]):
                color = 0
                if curses.has_colors():
                    if level == "info":
                        color = curses.color_pair(1)
                    elif level == "error":
                        color = curses.color_pair(2)
                    elif level == "warning":
                        color = curses.color_pair(3)
                    elif level == "debug":
                        color = curses.color_pair(4)
                debug_win.addstr(i+1, 2, f"{msg}"[:width-4], color)
            
            # Update LED grid window
            grid_win.clear()
            grid_win.box()
            
            if led_grid is not None:
                rows = len(led_grid)
                cols = len(led_grid[0]) if rows > 0 else 0
                
                # Calculate offset to center grid
                x_offset = max(1, (width - cols * 2) // 2)
                y_offset = max(1, (grid_height - rows) // 2)
                
                # Draw row labels
                row_labels = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
                for i, label in enumerate(row_labels[:rows]):
                    if y_offset + i < grid_height - 1:
                        grid_win.addstr(y_offset + i, max(1, x_offset - 3), f"{label:>2s}")
                
                # Draw LED grid
                for y in range(rows):
                    if y_offset + y >= grid_height - 1:
                        break
                    for x in range(cols):
                        if x_offset + x*2 >= width - 2:
                            break
                        grid_win.addstr(y_offset + y, x_offset + x*2, 
                                        self.on_char if led_grid[y][x] else self.off_char)
            
            # Refresh windows
            status_win.refresh()
            grid_win.refresh()
            debug_win.refresh()
            
            # Sleep to avoid high CPU usage
            time.sleep(0.05)
    
    def _fallback_thread_func(self):
        """Thread function for fallback console mode."""
        status_message = "Terminal display initialized in fallback mode."
        debug_messages = []
        led_grid = None
        
        last_status_time = 0
        last_debug_time = 0
        
        # Process up to 10 messages at once to avoid getting stuck
        max_messages_per_cycle = 10
        
        while self.running:
            # Process messages from queue
            messages_processed = 0
            try:
                while not self.message_queue.empty() and messages_processed < max_messages_per_cycle:
                    msg_type, *args = self.message_queue.get(block=False)
                    messages_processed += 1
                    
                    if msg_type == "status":
                        status_message, level = args
                        # Print status message with timestamp
                        current_time = time.time()
                        if current_time - last_status_time >= 1.0:  # Limit status updates to once per second
                            last_status_time = current_time
                            print(f"[STATUS] {status_message}")
                    
                    elif msg_type == "debug":
                        debug_message, level = args
                        debug_messages.append((debug_message, level))
                        # Keep only the last 5 debug messages
                        if len(debug_messages) > 5:
                            debug_messages.pop(0)
                        
                        # Print debug message with timestamp and level
                        current_time = time.time()
                        if current_time - last_debug_time >= 0.5:  # Limit debug updates to twice per second
                            last_debug_time = current_time
                            print(f"[DEBUG] {debug_message}")
                    
                    elif msg_type == "grid":
                        led_grid = args[0]
                        
                        # Only print the grid occasionally to avoid console spam
                        current_time = time.time()
                        if current_time - self.last_grid_update >= 0.5:  # Limit grid updates to once per 0.5 seconds
                            self.last_grid_update = current_time
                            
                            if led_grid is not None:
                                rows = len(led_grid)
                                cols = len(led_grid[0]) if rows > 0 else 0
                                
                                # Print a bordered representation of the LED grid
                                print("\nLED Grid State:")
                                print("┌" + "─" * (cols * 2 - 1) + "┐")
                                
                                # Define the correct row order for punch cards: 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
                                row_labels = ["12", "11", "0 ", "1 ", "2 ", "3 ", "4 ", "5 ", "6 ", "7 ", "8 ", "9 "]
                                
                                for i in range(min(rows, len(row_labels))):
                                    row_content = []
                                    for j in range(cols):
                                        row_content.append(self.on_char if led_grid[i][j] else self.off_char)
                                    print(f"{row_labels[i]}│{''.join(row_content)}│")
                                
                                print("└" + "─" * (cols * 2 - 1) + "┘")
            
            except queue.Empty:
                pass
            
            # Sleep to avoid high CPU usage
            time.sleep(0.1)

def run_terminal_app():
    """
    Main entry point for the terminal application.
    """
    from src.core.punch_card import PunchCard
    from src.display.display_adapter import DisplayAdapter
    
    try:
        # Initialize the application
        punch_card = PunchCard()
        display = TerminalDisplay()
        adapter = DisplayAdapter(punch_card, display)
        
        # Run the terminal application
        adapter.start()
        
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f"Error in terminal application: {e}")
        print(f"\nAn error occurred: {e}")

# If run directly, start the terminal application
if __name__ == "__main__":
    run_terminal_app() 