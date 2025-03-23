#!/usr/bin/env python3
"""
Rich-based Punch Card Display

A modern terminal UI for displaying punch card messages using Rich.
"""

import os
import sys
import time
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from rich.style import Style
from rich.color import Color

class PunchCardDisplay:
    """A Rich-based punch card display."""
    
    REQUIRED_WIDTH = 100
    REQUIRED_HEIGHT = 35
    
    def __init__(self, num_rows=12, num_cols=80):
        """Initialize the display."""
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.grid = [[False for _ in range(num_cols)] for _ in range(num_rows)]
        
        # Ensure terminal size
        self._setup_terminal()
        
        # Create Rich console with appropriate size
        self.console = Console(force_terminal=True, width=self.REQUIRED_WIDTH)
        
        # Create the layout
        self.layout = Layout()
        self.layout.split_column(
            Layout(name="grid", size=25),
            Layout(name="legend", size=3),
            Layout(name="status", size=3)
        )
    
    def _setup_terminal(self):
        """Set up the terminal with proper dimensions."""
        # Get current terminal size
        current_size = shutil.get_terminal_size()
        
        if current_size.columns < self.REQUIRED_WIDTH or current_size.lines < self.REQUIRED_HEIGHT:
            # Try to resize terminal
            try:
                # First clear the screen
                os.system('clear')
                
                # Then resize
                os.system(f'printf "\033[8;{self.REQUIRED_HEIGHT};{self.REQUIRED_WIDTH}t"')
                time.sleep(0.5)  # Give terminal time to resize
                
                # Clear again after resize
                os.system('clear')
                
                # Verify new size
                new_size = shutil.get_terminal_size()
                if new_size.columns < self.REQUIRED_WIDTH or new_size.lines < self.REQUIRED_HEIGHT:
                    print(f"\n\nWarning: Terminal size is {new_size.columns}x{new_size.lines}, "
                          f"but {self.REQUIRED_WIDTH}x{self.REQUIRED_HEIGHT} is required.")
                    print("Please resize your terminal window manually and press Enter to continue...")
                    input()
                    os.system('clear')
            except Exception as e:
                print(f"\n\nWarning: Could not resize terminal: {e}")
                print("Please resize your terminal window manually and press Enter to continue...")
                input()
                os.system('clear')
    
    def _restore_terminal(self):
        """Restore original terminal size."""
        try:
            terminal_size = shutil.get_terminal_size()
            os.system('printf "\033[8;%d;%dt"' % (terminal_size.lines, terminal_size.columns))
        except Exception as e:
            print(f"Warning: Could not restore terminal size: {e}")
    
    def set_led(self, row: int, col: int, state: bool):
        """Set a single LED in the grid."""
        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            self.grid[row][col] = state
    
    def clear_grid(self):
        """Clear the entire grid."""
        self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
    
    def create_grid_display(self) -> Table:
        """Create the grid display table."""
        table = Table(show_header=False, box=None, padding=0, width=self.REQUIRED_WIDTH-4)
        
        # Define the correct row order for punch cards
        row_labels = ["12", "11", "0 ", "1 ", "2 ", "3 ", "4 ", "5 ", "6 ", "7 ", "8 ", "9 "]
        
        # Add top spacing (3 rows for better fit)
        for _ in range(3):
            table.add_row("  │" + "─" * self.num_cols + "│")
        
        # Add the actual punch card rows
        for i in range(12):
            row_content = []
            for j in range(80):
                row_content.append("█" if self.grid[i][j] else "░")
            table.add_row(f"{row_labels[i]}│{''.join(row_content)}│")
        
        # Add bottom spacing (3 rows for better fit)
        for _ in range(3):
            table.add_row("  │" + "─" * self.num_cols + "│")
        
        return table
    
    def create_legend(self) -> Table:
        """Create the legend table."""
        table = Table(show_header=False, box=None, width=self.REQUIRED_WIDTH-4)
        table.add_row(Align.center("[bold]█[/] = Punched hole    [bold]░[/] = No hole"))
        return table
    
    def display_message(self, message: str, delay: float = 0.1):
        """Display a message on the punch card."""
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
                            Align.center(self.create_grid_display()),
                            title="[bold blue]Punch Card Display[/]",
                            border_style="blue"
                        )
                    )
                    self.layout["legend"].update(
                        Panel(
                            Align.center(self.create_legend()),
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
                    time.sleep(delay)
                
                # Final update
                self.layout["status"].update(
                    Panel(
                        Align.center(Text("[bold green]Message display complete[/]")),
                        border_style="green"
                    )
                )
                live.refresh()
                time.sleep(1.0)
        except Exception as e:
            print(f"\n\nDisplay error: {e}")
            print("Please ensure your terminal window is large enough.")
            input("Press Enter to continue...")
            os.system('clear')
    
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
            self.set_led(1, col, True)  # Row 11
            self.set_led(2, col, True)  # Row 0

def main():
    """Main function."""
    try:
        # Create the display
        display = PunchCardDisplay()
        
        # Show test messages
        messages = [
            "TEST MESSAGE",
            "HELLO WORLD",
            "PUNCH CARD DISPLAY",
            "GOODBYE"
        ]
        
        for message in messages:
            display.display_message(message, delay=0.1)
            time.sleep(0.5)
        
    except KeyboardInterrupt:
        print("\nDisplay interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Restore terminal size
        display._restore_terminal()

if __name__ == "__main__":
    main() 