#!/usr/bin/env python3
"""
Unified Punch Card Display Module

A simplified, consolidated display module for the Punch Card Project.
Provides both terminal (Rich-based) and GUI (PyQt6-based) display options.

Usage:
    from display import PunchCardDisplay
    
    # Create a display with default settings (Rich terminal display)
    display = PunchCardDisplay()
    
    # To use GUI mode
    display = PunchCardDisplay(use_gui=True)
    
    # Display a message
    display.show_message("HELLO WORLD")
"""

import os
import time
import shutil
from typing import List, Tuple, Callable, Optional, Dict, Union, Any
from functools import partial

# Rich imports for terminal display
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.table import Table
    from rich.text import Text
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# PyQt6 imports for GUI display
try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QPushButton, QTextEdit, QSplitter)
    from PyQt6.QtCore import Qt, QTimer, QSize, QTime
    from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPalette, QBrush
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

class PunchCardDisplay:
    """
    Unified Punch Card Display with support for both terminal and GUI modes.
    
    This class provides a common interface for displaying punch card messages
    in either terminal (Rich-based) or GUI (PyQt6-based) mode.
    """
    
    def __init__(self, use_gui: bool = False, 
                num_rows: int = 12, num_cols: int = 80,
                led_delay: float = 0.1, message_delay: float = 2.0,
                random_delay: bool = False, skip_splash: bool = False,
                debug_mode: bool = False):
        """
        Initialize the punch card display.
        
        Args:
            use_gui: Whether to use the GUI display (PyQt6) instead of terminal (Rich)
            num_rows: Number of rows in the punch card grid
            num_cols: Number of columns in the punch card grid
            led_delay: Delay between LED updates in seconds
            message_delay: Delay between messages in seconds
            random_delay: Whether to use random delays between messages
            skip_splash: Whether to skip the splash screen
            debug_mode: Whether to enable debug output
        """
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.grid = [[False for _ in range(num_cols)] for _ in range(num_rows)]
        self.led_delay = led_delay
        self.message_delay = message_delay
        self.random_delay = random_delay
        self.skip_splash = skip_splash
        self.debug_mode = debug_mode
        
        # Statistics for tracking operations
        self.stats = {
            "start_time": time.time(),
            "messages_displayed": 0,
            "total_characters": 0,
            "total_holes": 0
        }
        
        # Initialize the appropriate display mode
        if use_gui and QT_AVAILABLE:
            self.display_mode = "gui"
            self._init_gui_display()
        elif RICH_AVAILABLE:
            self.display_mode = "rich"
            self._init_rich_display()
        else:
            self.display_mode = "simple"
            self._init_simple_display()
    
    def _init_rich_display(self) -> None:
        """Initialize the Rich-based terminal display."""
        # Terminal size requirements for Rich display
        self.required_width = 100
        self.required_height = 35
        
        # Set up terminal size
        self._setup_terminal()
        
        # Create Rich console with appropriate size
        self.console = Console(force_terminal=True, width=self.required_width)
        
        # Create the layout
        self.layout = Layout()
        self.layout.split_column(
            Layout(name="grid", size=25),
            Layout(name="legend", size=3),
            Layout(name="status", size=3)
        )
    
    def _init_gui_display(self) -> None:
        """Initialize the PyQt6-based GUI display."""
        # Initialize the QApplication if not already running
        self.app = QApplication.instance() if QApplication.instance() else QApplication([])
        
        # Create main window and configure it
        self.window = self._create_main_window()
        
        # Show the window
        self.window.show()
    
    def _init_simple_display(self) -> None:
        """Initialize a simple terminal display as fallback."""
        # Simple display doesn't need much initialization
        pass
    
    def _setup_terminal(self) -> None:
        """Set up the terminal with proper dimensions for Rich display."""
        # Get current terminal size
        current_size = shutil.get_terminal_size()
        
        if current_size.columns < self.required_width or current_size.lines < self.required_height:
            # Try to resize terminal
            try:
                # First clear the screen
                os.system('clear')
                
                # Then resize
                os.system(f'printf "\033[8;{self.required_height};{self.required_width}t"')
                time.sleep(0.5)  # Give terminal time to resize
                
                # Clear again after resize
                os.system('clear')
                
                # Verify new size
                new_size = shutil.get_terminal_size()
                if new_size.columns < self.required_width or new_size.lines < self.required_height:
                    print(f"\n\nWarning: Terminal size is {new_size.columns}x{new_size.lines}, "
                          f"but {self.required_width}x{self.required_height} is required.")
                    print("Please resize your terminal window manually and press Enter to continue...")
                    input()
                    os.system('clear')
            except Exception as e:
                print(f"\n\nWarning: Could not resize terminal: {e}")
                print("Please resize your terminal window manually and press Enter to continue...")
                input()
                os.system('clear')
    
    def _create_main_window(self) -> 'QMainWindow':
        """Create the main window for GUI display."""
        if not QT_AVAILABLE:
            raise ImportError("PyQt6 is required for GUI display")
            
        # Define GUI colors
        self.colors = {
            'background': QColor(25, 25, 35),
            'card_bg': QColor(0, 0, 0),
            'grid': QColor(40, 40, 40),
            'hole': QColor(255, 255, 255),
            'hole_outline': QColor(255, 255, 255),
            'text': QColor(200, 200, 200),
            'border': QColor(100, 100, 120),
            'button_bg': QColor(45, 45, 55),
            'button_hover': QColor(60, 60, 70),
            'console_bg': QColor(20, 20, 25),
            'console_text': QColor(0, 255, 0),
            'card_edge': QColor(150, 150, 170)
        }
        
        # Create main window
        window = QMainWindow()
        window.setWindowTitle("Punch Card Display System")
        window.setMinimumSize(1200, 800)
        
        # Set window style
        window.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background'].name()};
            }}
        """)
        
        # Implementation details go here - simplified for brevity
        # Full implementation would create all the widgets needed
        
        return window
    
    def set_led(self, row: int, col: int, state: bool) -> None:
        """
        Set a single LED in the grid.
        
        Args:
            row: Row index
            col: Column index
            state: True for on, False for off
        """
        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            self.grid[row][col] = state
            
            # Update display if necessary
            if self.display_mode == "gui":
                # In GUI mode, refresh the display
                if hasattr(self, 'window') and hasattr(self.window, 'punch_card'):
                    self.window.punch_card.update()
    
    def clear_grid(self) -> None:
        """Clear the entire grid."""
        self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        # Update display if necessary
        if self.display_mode == "gui":
            # In GUI mode, refresh the display
            if hasattr(self, 'window') and hasattr(self.window, 'punch_card'):
                self.window.punch_card.update()
    
    def show_message(self, message: str, source: str = "") -> None:
        """
        Display a message on the punch card.
        
        Args:
            message: Message to display
            source: Source of the message (for logging)
        """
        # Update statistics
        self.stats["messages_displayed"] += 1
        self.stats["total_characters"] += len(message)
        
        # Log the message if in debug mode
        if self.debug_mode:
            print(f"Displaying message: {message}")
            if source:
                print(f"Source: {source}")
        
        # Display message based on display mode
        if self.display_mode == "rich":
            self._show_message_rich(message)
        elif self.display_mode == "gui":
            self._show_message_gui(message)
        else:
            self._show_message_simple(message)
    
    def _show_message_rich(self, message: str) -> None:
        """Display a message using Rich terminal display."""
        try:
            with Live(self.layout, refresh_per_second=10, auto_refresh=False, console=self.console) as live:
                # Clear the grid
                self.clear_grid()
                
                # Display message character by character
                for i, char in enumerate(message):
                    # Update the grid
                    self._display_character(char, i)
                    
                    # Update the display
                    self.layout["grid"].update(
                        Panel(
                            Align.center(self._create_rich_grid_display()),
                            title="[bold blue]Punch Card Display[/]",
                            border_style="blue"
                        )
                    )
                    self.layout["legend"].update(
                        Panel(
                            Align.center(self._create_rich_legend()),
                            title="[bold green]Legend[/]",
                            border_style="green"
                        )
                    )
                    self.layout["status"].update(
                        Panel(
                            Align.center(Text(f"[bold]Displaying:[/] {message[:i+1]}", style="blue")),
                            border_style="yellow"
                        )
                    )
                    
                    # Refresh the display
                    live.refresh()
                    time.sleep(self.led_delay)
                
                # Final update
                self.layout["status"].update(
                    Panel(
                        Align.center(Text("[bold green]Message display complete[/]")),
                        border_style="green"
                    )
                )
                live.refresh()
                time.sleep(self.message_delay)
        except Exception as e:
            print(f"\n\nDisplay error: {e}")
            print("Please ensure your terminal window is large enough.")
            input("Press Enter to continue...")
            os.system('clear')
    
    def _show_message_gui(self, message: str) -> None:
        """Display a message using PyQt6 GUI display."""
        # Implementation would depend on the GUI components
        # For now, just print to console if in debug mode
        if self.debug_mode:
            print(f"GUI display not fully implemented. Would display: {message}")
    
    def _show_message_simple(self, message: str) -> None:
        """Display a message using simple terminal display."""
        # Clear the screen
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Print a header
        print("=" * 80)
        print("PUNCH CARD DISPLAY".center(80))
        print("=" * 80)
        
        # Clear the grid
        self.clear_grid()
        
        # Display message character by character
        for i, char in enumerate(message):
            # Update the grid
            self._display_character(char, i)
            
            # Print the current state
            self._print_simple_grid()
            print(f"Displaying: {message[:i+1]}")
            
            # Delay
            time.sleep(self.led_delay)
        
        # Final message
        print("\nMessage display complete")
        time.sleep(self.message_delay)
    
    def _create_rich_grid_display(self) -> Table:
        """Create the grid display table for Rich display."""
        table = Table(show_header=False, box=None, padding=0, width=self.required_width-4)
        
        # Define the correct row order for punch cards
        row_labels = ["12", "11", "0 ", "1 ", "2 ", "3 ", "4 ", "5 ", "6 ", "7 ", "8 ", "9 "]
        
        # Add top spacing (3 rows for better fit)
        for _ in range(3):
            table.add_row("  │" + "─" * self.num_cols + "│")
        
        # Add the actual punch card rows
        for i in range(12):
            row_content = []
            for j in range(self.num_cols):
                row_content.append("█" if self.grid[i][j] else "░")
            table.add_row(f"{row_labels[i]}│{''.join(row_content)}│")
        
        # Add bottom spacing (3 rows for better fit)
        for _ in range(3):
            table.add_row("  │" + "─" * self.num_cols + "│")
        
        return table
    
    def _create_rich_legend(self) -> Table:
        """Create the legend table for Rich display."""
        table = Table(show_header=False, box=None, width=self.required_width-4)
        table.add_row(Align.center("[bold]█[/] = Punched hole    [bold]░[/] = No hole"))
        return table
    
    def _print_simple_grid(self) -> None:
        """Print the grid using simple ASCII characters."""
        # Define the correct row order for punch cards
        row_labels = ["12", "11", "0 ", "1 ", "2 ", "3 ", "4 ", "5 ", "6 ", "7 ", "8 ", "9 "]
        
        # Print top border
        print("   +" + "-" * self.num_cols + "+")
        
        # Print the grid rows
        for i in range(12):
            row_content = []
            for j in range(self.num_cols):
                row_content.append("#" if self.grid[i][j] else ".")
            print(f"{row_labels[i]} |{''.join(row_content)}|")
        
        # Print bottom border
        print("   +" + "-" * self.num_cols + "+")
    
    def _display_character(self, char: str, col: int) -> None:
        """
        Display a character on the punch card grid.
        
        Args:
            char: Character to display
            col: Column to display the character in
        """
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
            self.set_led(1, col, True)  # Row 11
            self.set_led(2, col, True)  # Row 0
        
        # Update the total hole count
        if char != ' ':
            self.stats["total_holes"] += 1
    
    def show_splash_screen(self) -> None:
        """Display the splash screen."""
        if self.skip_splash:
            return
            
        # Clear the grid first
        self.clear_grid()
        
        # Display the splash message
        splash_message = "PUNCH CARD SYSTEM INITIALIZED"
        self.show_message(splash_message)
        
        # Clear the grid after the message is displayed
        self.clear_grid()
        
        # Add a small delay to show the cleared state
        time.sleep(0.5)
    
    def clear(self) -> None:
        """Clear the display and reset resources."""
        self.clear_grid()
        
        if self.display_mode == "rich":
            # Attempt to restore terminal
            try:
                terminal_size = shutil.get_terminal_size()
                os.system('printf "\033[8;%d;%dt"' % (terminal_size.lines, terminal_size.columns))
            except Exception as e:
                if self.debug_mode:
                    print(f"Warning: Could not restore terminal size: {e}")
        
        elif self.display_mode == "gui":
            # Close the application cleanly
            if hasattr(self, 'app'):
                self.app.quit()

if __name__ == "__main__":
    # Simple example usage
    display = PunchCardDisplay()
    display.show_splash_screen()
    display.show_message("HELLO WORLD")
    display.show_message("PUNCH CARD DISPLAY")
    display.clear() 