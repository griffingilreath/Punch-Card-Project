#!/usr/bin/env python3
"""
Full Message Display for Punch Card Project

This script provides a comprehensive punch card display experience,
including settings loading, splash screen, and message display
with the improved formatting from quick_message.py.
"""

import os
import sys
import time
import argparse
import random
import json
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Container, Vertical
from textual.widgets import Static
from textual.reactive import reactive
from textual import events

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import necessary modules
from src.terminal_display import TerminalDisplay, CharacterSet
from src.display_adapter import PunchCardDisplayAdapter

# Try to import components from the original code
try:
    from src.message_database import MessageDatabase
    from src.message_generator import MessageGenerator
    HAS_MESSAGE_COMPONENTS = True
except ImportError:
    print("Warning: Original message components not found. Some features will be limited.")
    HAS_MESSAGE_COMPONENTS = False

# Constants
DEFAULT_LED_DELAY = 0.05
DEFAULT_MESSAGE_DELAY = 0.2
DEFAULT_COMPLETION_DELAY = 1.0
DEFAULT_RECEIVE_DURATION = 3.0
DEFAULT_TRANSITION_STEPS = 10
SETTINGS_FILE = 'src/punch_card_settings.json'

# Initialize Rich console
console = Console(force_terminal=True)

class FullMessageDisplay:
    """
    Comprehensive punch card display that includes settings, splash screen,
    and message display with improved formatting.
    """
    
    def __init__(self, 
                 char_set_name: str = "default",
                 use_ui: bool = True,
                 verbose: bool = False,
                 led_delay: float = DEFAULT_LED_DELAY,
                 message_delay: float = DEFAULT_MESSAGE_DELAY,
                 random_delay: bool = True,
                 skip_splash: bool = False,
                 debug_mode: bool = False,
                 minimal_output: bool = False,
                 quick_mode: bool = False,
                 instant_mode: bool = False,
                 completion_delay: float = DEFAULT_COMPLETION_DELAY,
                 receive_duration: float = DEFAULT_RECEIVE_DURATION,
                 transition_steps: int = DEFAULT_TRANSITION_STEPS):
        """Initialize the display."""
        # Set up environment for clean output if minimal output requested
        if minimal_output:
            os.environ['FORCE_CONSOLE'] = '1'
            verbose = False

        # Initialize Rich console with force_terminal for consistent display
        self.console = Console(force_terminal=True)
        
        # Create display adapter
        self.display_adapter = PunchCardDisplayAdapter(
            num_rows=12,
            num_cols=80,
            verbose=verbose,
            char_set_name=char_set_name,
            use_ui=use_ui
        )
        
        # Store parameters
        self.verbose = verbose
        self.use_ui = use_ui
        self.minimal_output = minimal_output
        self.quick_mode = quick_mode
        self.instant_mode = instant_mode
        self.random_delay = random_delay
        self.skip_splash = skip_splash
        self.debug_mode = debug_mode
        self.completion_delay = completion_delay
        self.receive_duration = receive_duration
        self.transition_steps = transition_steps
        
        # Set appropriate delays based on mode
        self.led_delay = led_delay
        self.message_delay = message_delay
        
        if quick_mode:
            self.led_delay = 0.01
            self.message_delay = 0.05
        
        if instant_mode:
            self.led_delay = 0
            self.message_delay = 0
        
        # Suppress adapter's output for set_led operations if minimal output
        if minimal_output:
            self.display_adapter._suppress_led_output = True
        
        # Initialize message system if available
        self.message_db = None
        self.message_generator = None
        self.message_number = 0
        
        if HAS_MESSAGE_COMPONENTS:
            try:
                self.message_db = MessageDatabase()
                self.message_number = self.message_db.current_message_number
                self.message_generator = MessageGenerator()
                if not self.minimal_output:
                    self.console.print(f"[blue]Initialized message system. Current message #: {self.message_number}[/blue]")
            except Exception as e:
                if self.debug_mode:
                    self.console.print(f"[yellow]Warning: Failed to initialize message system: {e}[/yellow]")
        
        # Load settings
        self.settings = self._load_settings()
        if not self.minimal_output and not self.debug_mode:
            self._print_settings()
        
        # Initialize the grid
        self.grid = [[False for _ in range(80)] for _ in range(12)]
        
        # Show splash screen if not skipped
        if not skip_splash:
            self.show_splash()
    
    def _load_settings(self) -> dict:
        """Load settings from file or return defaults."""
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                if not self.minimal_output:
                    print(f"Settings loaded from {SETTINGS_FILE}")
                return settings
        except (FileNotFoundError, json.JSONDecodeError):
            if not self.minimal_output:
                print(f"Settings file not found. Using defaults.")
            return {
                'led_delay': DEFAULT_LED_DELAY,
                'message_delay': DEFAULT_MESSAGE_DELAY,
                'random_delay': True,
                'debug_mode': False,
                'completion_delay': DEFAULT_COMPLETION_DELAY,
                'receive_duration': DEFAULT_RECEIVE_DURATION,
                'transition_steps': DEFAULT_TRANSITION_STEPS
            }
    
    def _print_settings(self):
        """Print the current settings using Rich."""
        settings_table = Table(title="Current Settings", show_header=False, box=None)
        settings_table.add_row("LED Delay", f"{self.settings['led_delay']} seconds")
        settings_table.add_row("Message Delay", f"{self.settings['message_delay']} seconds")
        settings_table.add_row("Random Delay", "Enabled" if self.settings['random_delay'] else "Disabled")
        settings_table.add_row("Debug Mode", "Enabled" if self.settings['debug_mode'] else "Disabled")
        settings_table.add_row("Completion Delay", f"{self.settings['completion_delay']} seconds")
        settings_table.add_row("Receive Duration", f"{self.settings['receive_duration']} seconds")
        settings_table.add_row("Transition Steps", str(self.settings['transition_steps']))
        
        self.console.print(Panel(settings_table, border_style="blue"))
    
    def _save_settings(self):
        """Save current settings to file."""
        settings = {
            'led_delay': self.led_delay,
            'message_delay': self.message_delay,
            'random_delay': self.random_delay,
            'debug_mode': self.debug_mode,
            'completion_delay': self.completion_delay,
            'receive_duration': self.receive_duration,
            'transition_steps': self.transition_steps
        }
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f)
            if not self.minimal_output:
                print(f"Settings saved to {SETTINGS_FILE}")
        except Exception as e:
            if self.debug_mode:
                print(f"Warning: Could not save settings to file: {e}")
    
    def set_led(self, row: int, col: int, state: bool):
        """Set a single LED in the grid."""
        if 0 <= row < 12 and 0 <= col < 80:
            self.grid[row][col] = state
            self.display_adapter.set_led(row, col, state)
            
            # Add delay if specified
            if self.led_delay > 0 and not self.instant_mode:
                time.sleep(self.led_delay)
    
    def clear_grid(self):
        """Clear the entire grid."""
        self.grid = [[False for _ in range(80)] for _ in range(12)]
        self.display_adapter.clear_all()
        
        # Log message
        if not self.minimal_output:
            self.display_adapter.log_message("Grid cleared", "info")
        else:
            print("Grid cleared")
    
    def _show_punch_card_text(self):
        """Show the PUNCH CARD text with animations."""
        # P
        for row in range(2, 10):
            self.set_led(row, 15, True)
            if not self.instant_mode:
                time.sleep(0.02)
        for col in range(15, 19):
            self.set_led(2, col, True)
            self.set_led(5, col, True)
            if not self.instant_mode:
                time.sleep(0.02)
        self.set_led(3, 19, True)
        self.set_led(4, 19, True)
        
        # U
        for row in range(2, 9):
            self.set_led(row, 21, True)
            self.set_led(row, 25, True)
            if not self.instant_mode:
                time.sleep(0.02)
        for col in range(22, 25):
            self.set_led(9, col, True)
            if not self.instant_mode:
                time.sleep(0.02)
        
        # N
        for row in range(2, 10):
            self.set_led(row, 27, True)
            self.set_led(row, 31, True)
            if not self.instant_mode:
                time.sleep(0.02)
        self.set_led(3, 28, True)
        self.set_led(4, 29, True)
        self.set_led(5, 29, True)
        self.set_led(6, 29, True)
        self.set_led(7, 30, True)
        self.set_led(8, 30, True)
        
        # C
        for row in range(2, 10):
            self.set_led(row, 33, True)
            if not self.instant_mode:
                time.sleep(0.02)
        for col in range(34, 37):
            self.set_led(2, col, True)
            self.set_led(9, col, True)
            if not self.instant_mode:
                time.sleep(0.02)
        
        # H
        for row in range(2, 10):
            self.set_led(row, 39, True)
            self.set_led(row, 43, True)
            if not self.instant_mode:
                time.sleep(0.02)
        for col in range(40, 43):
            self.set_led(5, col, True)
            if not self.instant_mode:
                time.sleep(0.02)
        
        # C
        for row in range(2, 10):
            self.set_led(row, 47, True)
            if not self.instant_mode:
                time.sleep(0.02)
        for col in range(48, 51):
            self.set_led(2, col, True)
            self.set_led(9, col, True)
            if not self.instant_mode:
                time.sleep(0.02)
        
        # A
        for row in range(3, 10):
            self.set_led(row, 53, True)
            self.set_led(row, 57, True)
            if not self.instant_mode:
                time.sleep(0.02)
        for col in range(54, 57):
            self.set_led(2, col, True)
            self.set_led(5, col, True)
            if not self.instant_mode:
                time.sleep(0.02)
        
        # R
        for row in range(2, 10):
            self.set_led(row, 59, True)
            if not self.instant_mode:
                time.sleep(0.02)
        for col in range(60, 63):
            self.set_led(2, col, True)
            self.set_led(5, col, True)
            if not self.instant_mode:
                time.sleep(0.02)
        self.set_led(3, 63, True)
        self.set_led(4, 63, True)
        self.set_led(6, 61, True)
        self.set_led(7, 62, True)
        self.set_led(8, 62, True)
        self.set_led(9, 63, True)
        
        # D
        for row in range(2, 10):
            self.set_led(row, 65, True)
            if not self.instant_mode:
                time.sleep(0.02)
        for col in range(66, 68):
            self.set_led(2, col, True)
            self.set_led(9, col, True)
            if not self.instant_mode:
                time.sleep(0.02)
        self.set_led(3, 68, True)
        self.set_led(4, 69, True)
        self.set_led(5, 69, True)
        self.set_led(6, 69, True)
        self.set_led(7, 69, True)
        self.set_led(8, 68, True)

    def _clear_with_animation(self):
        """Clear the grid with a fancy animation."""
        for col in range(80):
            for row in range(12):
                self.set_led(row, col, False)
                
            # Smoother clearing animation
            if not self.instant_mode:
                delay = 0.01 * (1 - (col / 80))  # Gradually decrease delay
                time.sleep(delay)

    def show_splash(self):
        """Show the punch card splash screen with Rich animations."""
        if not self.minimal_output:
            self.console.print("[blue]Showing splash screen...[/blue]")
        
        # Clear the grid
        self.clear_grid()
        
        # Animate border with a more polished effect
        for i in range(80):
            # Top and bottom borders with fade effect
            self.set_led(0, i, True)
            self.set_led(11, i, True)
            
            # Left and right borders with fade effect
            if i < 12:
                self.set_led(i, 0, True)
                self.set_led(i, 79, True)
            
            # Smoother animation with variable delay
            if not self.instant_mode:
                delay = 0.01 * (1 - (i / 80))  # Gradually decrease delay
                time.sleep(delay)
        
        # Show version and system info
        if not self.minimal_output and not self.instant_mode:
            self._show_version_info()
        
        # Show "PUNCH CARD" text
        self._show_punch_card_text()
        
        # Add version number
        self._add_version_number()
        
        # Display the current state
        self._display_grid_summary()
        
        # Pause to display splash screen
        if not self.instant_mode:
            time.sleep(2.0)
        
        # Clear with animation
        self._clear_with_animation()
        
        if not self.minimal_output:
            self.console.print("[green]Splash screen complete[/green]")
    
    def _add_version_number(self):
        """Add version number (V3) to the splash screen."""
        # V
        self.set_led(3, 71, True)
        self.set_led(4, 71, True)
        self.set_led(5, 72, True)
        self.set_led(6, 73, True)
        self.set_led(5, 74, True)
        self.set_led(4, 75, True)
        self.set_led(3, 75, True)
        
        # 3
        self.set_led(2, 77, True)
        self.set_led(2, 78, True)
        self.set_led(3, 79, True)
        self.set_led(4, 78, True)
        self.set_led(5, 77, True)
        self.set_led(5, 78, True)
        self.set_led(6, 79, True)
        self.set_led(7, 78, True)
        self.set_led(8, 77, True)
        self.set_led(8, 78, True)
    
    def _show_version_info(self):
        """Display version and system information."""
        version_msg = "PUNCH CARD V3.0.1"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Display system info at the bottom of the grid
        for col, char in enumerate(version_msg):
            self._display_character(char, col + 5, row_offset=7)  # Show in lower half
        
        # Display timestamp
        for col, char in enumerate(timestamp):
            self._display_character(char, col + 45, row_offset=7)  # Show on right side
            
        # Give time to read the info
        if not self.instant_mode:
            time.sleep(1.0)
    
    def show_message(self, message: str, source: str = "Test"):
        """Show a message on the punch card display with Rich progress."""
        if not self.minimal_output:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"[blue]Showing message: {message}[/blue]", total=100)
                
                # Clear the grid
                self.clear_grid()
                progress.update(task, advance=10)
                
                # If message database is available, save the message
                if self.message_db is not None:
                    self.message_number = self.message_db.add_message(message, source)
                    if not self.minimal_output:
                        self.console.print(f"[blue]Message #{self.message_number:07d} added to database[/blue]")
                
                # Display message character by character
                for i, char in enumerate(message):
                    self._display_character(char, i)
                    if not self.instant_mode:
                        if self.random_delay:
                            delay = self.message_delay * (0.5 + random.random())
                        else:
                            delay = self.message_delay
                        time.sleep(delay)
                    progress.update(task, advance=90/len(message))
                
                # Show grid summary if minimal output
                if self.minimal_output:
                    self._display_grid_summary()
                
                # Pause after message completion
                if not self.instant_mode:
                    time.sleep(self.completion_delay)
                    progress.update(task, advance=10)
        
        if not self.minimal_output:
            self.console.print("[green]Message display complete[/green]")
    
    def _display_character(self, char: str, col: int, row_offset: int = 0):
        """
        Display a character on the punch card grid.
        
        Args:
            char: The character to display
            col: The column position
            row_offset: Optional row offset for positioning (default: 0)
        """
        # Convert to uppercase
        char = char.upper()
        
        # Clear the column first (only the affected rows with offset)
        for row in range(max(0, row_offset), min(12, row_offset + 12)):
            self.set_led(row, col, False)
        
        # Handle different character types
        if char.isalpha():
            # Letters
            if char in "ABCDEFGHI":
                # A-I: row 12 + digit 1-9
                self.set_led(0 + row_offset, col, True)  # Row 12
                digit = ord(char) - ord('A') + 1
                self.set_led(digit + 2 + row_offset, col, True)  # Convert to punch card row
            elif char in "JKLMNOPQR":
                # J-R: row 11 + digit 1-9
                self.set_led(1 + row_offset, col, True)  # Row 11
                digit = ord(char) - ord('J') + 1
                self.set_led(digit + 2 + row_offset, col, True)  # Convert to punch card row
            else:
                # S-Z: row 0 + digit 2-9
                self.set_led(2 + row_offset, col, True)  # Row 0
                digit = ord(char) - ord('S') + 2
                if digit <= 9:
                    self.set_led(digit + 2 + row_offset, col, True)  # Convert to punch card row
        
        elif char.isdigit():
            # Digits 0-9
            digit = int(char)
            if digit == 0:
                self.set_led(2 + row_offset, col, True)  # Row 0
            else:
                self.set_led(digit + 2 + row_offset, col, True)  # Convert to punch card row
        
        elif char == ' ':
            # Space - no punches
            pass
        
        else:
            # Special characters - simplified version
            # For demonstration, just punch row 11 and 0
            self.set_led(1 + row_offset, col, True)  # Row 11
            self.set_led(2 + row_offset, col, True)  # Row 0
    
    def _display_grid_summary(self):
        """Display a summary of the current grid state with improved formatting using Rich."""
        # Get on/off characters for the display
        on_char, off_char = "█", "░"  # Using block characters for better visibility
        
        # Create a table for the grid
        table = Table(show_header=False, box=None, padding=0)
        
        # Define the correct row order for punch cards: 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
        row_labels = ["12", "11", "0 ", "1 ", "2 ", "3 ", "4 ", "5 ", "6 ", "7 ", "8 ", "9 "]
        
        # Add top spacing (11 rows)
        for _ in range(11):
            table.add_row("  │" + " " * 80 + "│")
        
        # Add the actual punch card rows
        for i in range(12):
            row_content = []
            for j in range(80):
                row_content.append(on_char if self.grid[i][j] else off_char)
            table.add_row(f"{row_labels[i]}│{''.join(row_content)}│")
        
        # Add bottom spacing (12 rows)
        for _ in range(12):
            table.add_row("  │" + " " * 80 + "│")
        
        # Create a panel for the grid
        grid_panel = Panel(
            table,
            title="Message Preview",
            border_style="blue",
            padding=(1, 2)
        )
        
        # Create a legend table
        legend_table = Table(show_header=False, box=None)
        legend_table.add_row(f"{on_char}", "Punched hole")
        legend_table.add_row(f"{off_char}", "No hole")
        
        # Create a panel for the legend
        legend_panel = Panel(
            legend_table,
            title="Legend",
            border_style="green",
            padding=(1, 2)
        )
        
        # Create a layout
        layout = Layout()
        layout.split_column(
            Layout(name="grid", size=35),
            Layout(name="legend", size=5)
        )
        
        # Update the layout
        layout["grid"].update(grid_panel)
        layout["legend"].update(legend_panel)
        
        # Display the layout
        self.console.print(layout)
        
        # Add column markers
        self.console.print("\n    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |")
        self.console.print("    5    10   15   20   25   30   35   40   45   50   55   60   65   70   75   80")
    
    def run_animations(self):
        """Run a series of animations on the punch card display."""
        if not self.minimal_output:
            self.display_adapter.log_message("Running animations", "info")
        else:
            print("Running animations...")
        
        # Clear the grid
        self.clear_grid()
        
        # Animation 1: Wave with improved smoothness
        if not self.minimal_output:
            self.display_adapter.log_message("Animation: Wave", "debug")
        
        import math
        for frame in range(25 if not self.quick_mode else 10):
            self.clear_grid()
            for col in range(80):
                # Smoother sine wave
                sin_val = math.sin(col / 10 + frame / 5)
                row = int((sin_val + 1) * 5) + 1  # Map to rows 1-11
                self.set_led(row, col, True)
            
            # Variable delay for smoother animation
            if not self.instant_mode:
                delay = 0.05 * (1 - (frame / 25))  # Gradually decrease delay
                time.sleep(delay)
        
        # Short pause between animations
        if not self.instant_mode:
            time.sleep(0.5)
        
        # Animation 2: Spinner with improved trail effect
        if not self.minimal_output:
            self.display_adapter.log_message("Animation: Spinner", "debug")
        
        center_row = 6
        center_col = 40
        radius = 5
        
        for angle in range(0, 360 if not self.quick_mode else 180, 10):
            self.clear_grid()
            
            # Draw spinner with improved trail
            rad = math.radians(angle)
            row = int(center_row + radius * math.sin(rad))
            col = int(center_col + radius * math.cos(rad) * 2)
            
            if 0 <= row < 12 and 0 <= col < 80:
                self.set_led(row, col, True)
                
                # Enhanced trail effect
                for trail in range(1, 8):  # Longer trail
                    trail_angle = angle - trail * 10
                    trail_rad = math.radians(trail_angle)
                    trail_row = int(center_row + radius * math.sin(trail_rad))
                    trail_col = int(center_col + radius * math.cos(trail_rad) * 2)
                    
                    if 0 <= trail_row < 12 and 0 <= trail_col < 80:
                        self.set_led(trail_row, trail_col, True)
            
            # Variable delay for smoother animation
            if not self.instant_mode:
                delay = 0.05 * (1 - (angle / 360))  # Gradually decrease delay
                time.sleep(delay)
        
        # Clear the grid
        self.clear_grid()
        
        # Animation 3: Typewriter with improved timing
        if not self.minimal_output:
            self.display_adapter.log_message("Animation: Typewriter", "debug")
        
        message = "PUNCH CARD SYSTEM V3 - READY FOR INPUT..."
        for i, char in enumerate(message):
            self._display_character(char, i)
            if not self.instant_mode:
                # Variable delay based on character type
                if char.isalpha():
                    delay = 0.1 if not self.quick_mode else 0.03
                elif char.isdigit():
                    delay = 0.08 if not self.quick_mode else 0.02
                else:
                    delay = 0.05 if not self.quick_mode else 0.01
                time.sleep(delay)
        
        # Pause to see the message
        if not self.instant_mode:
            time.sleep(1.0 if not self.quick_mode else 0.3)
        
        # Show final grid if minimal output
        if self.minimal_output:
            self._display_grid_summary()
        
        # Clear the grid with fade effect
        for col in range(80):
            for row in range(12):
                self.set_led(row, col, False)
            if not self.instant_mode:
                time.sleep(0.01)
        
        if not self.minimal_output:
            print("Animations complete")
    
    def generate_and_show_message(self):
        """Generate and show a random message if message generator is available."""
        if self.message_generator is None:
            if not self.minimal_output:
                self.display_adapter.log_message("Message generator not available", "warning")
            else:
                print("Message generator not available")
            return False
        
        try:
            # Generate a random message
            message = self.message_generator.generate_random_sentence()
            source = "Random Generator"
            
            # Show the message
            self.show_message(message, source)
            
            return True
        except Exception as e:
            if not self.minimal_output:
                self.display_adapter.log_message(f"Error generating message: {e}", "error")
            else:
                print(f"Error generating message: {e}")
            return False
    
    def run_demo(self, messages: List[str] = None):
        """Run a demonstration with the provided messages or generated ones."""
        if messages:
            # Show each provided message
            for i, message in enumerate(messages):
                self.show_message(message, f"Demo Message {i+1}")
                if not self.instant_mode:
                    time.sleep(1.0 if not self.quick_mode else 0.3)
        
        elif HAS_MESSAGE_COMPONENTS and self.message_generator:
            # Generate and show 3 random messages
            for i in range(3):
                if not self.generate_and_show_message():
                    break
                if not self.instant_mode:
                    time.sleep(1.0 if not self.quick_mode else 0.3)
        
        else:
            # Show a default message if no messages provided and no generator
            self.show_message("PUNCH CARD SYSTEM INITIALIZED", "System")
            if not self.instant_mode:
                time.sleep(1.0 if not self.quick_mode else 0.3)
            self.show_message("READY FOR INPUT", "System")
            if not self.instant_mode:
                time.sleep(1.0 if not self.quick_mode else 0.3)
        
        # Run animations at the end
        self.run_animations()
    
    def cleanup(self):
        """Clean up resources."""
        # Restore original terminal size
        try:
            import shutil
            terminal_size = shutil.get_terminal_size()
            os.system('printf "\033[8;%d;%dt"' % (terminal_size.lines, terminal_size.columns))
        except Exception as e:
            if self.debug_mode:
                print(f"Warning: Could not restore terminal size: {e}")
        
        self.display_adapter.cleanup()

class PunchCardGrid(Static):
    """A widget to display the punch card grid."""
    
    def __init__(self, display):
        super().__init__()
        self.display = display
    
    def render(self) -> str:
        """Render the grid."""
        # Create a table for the grid
        table = Table(show_header=False, box=None, padding=0)
        
        # Define the correct row order for punch cards
        row_labels = ["12", "11", "0 ", "1 ", "2 ", "3 ", "4 ", "5 ", "6 ", "7 ", "8 ", "9 "]
        
        # Add top spacing (11 rows)
        for _ in range(11):
            table.add_row("  │" + " " * 80 + "│")
        
        # Add the actual punch card rows
        for i in range(12):
            row_content = []
            for j in range(80):
                row_content.append("█" if self.display.grid[i][j] else "░")
            table.add_row(f"{row_labels[i]}│{''.join(row_content)}│")
        
        # Add bottom spacing (12 rows)
        for _ in range(12):
            table.add_row("  │" + " " * 80 + "│")
        
        return str(table)

class PunchCardLegend(Static):
    """A widget to display the legend."""
    
    def render(self) -> str:
        """Render the legend."""
        table = Table(show_header=False, box=None)
        table.add_row("█", "Punched hole")
        table.add_row("░", "No hole")
        return str(table)

class PunchCardStatus(Static):
    """A widget to display status messages."""
    
    message = reactive("")
    
    def render(self) -> str:
        """Render the status message."""
        return self.message

class PunchCardApp(App):
    """A Textual application for displaying punch card messages."""
    
    CSS = """
    Screen {
        align: center middle;
        background: $surface;
    }
    
    #main {
        height: 100%;
        width: 100%;
        padding: 1;
    }
    
    #grid {
        height: 35;
        width: 100%;
        border: solid blue;
        padding: 1;
    }
    
    #legend {
        height: 5;
        width: 100%;
        border: solid green;
        padding: 1;
    }
    
    #status {
        height: 3;
        width: 100%;
        background: $surface-darken-1;
        color: $text;
        padding: 1;
        text-align: center;
    }
    """
    
    def __init__(self, display):
        super().__init__()
        self.display = display
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        with Container(id="main"):
            yield PunchCardGrid(self.display, id="grid")
            yield PunchCardLegend(id="legend")
            yield PunchCardStatus(id="status")
        yield Footer()
    
    def on_mount(self) -> None:
        """Set up the layout when the app starts."""
        self.update_display()
    
    def update_display(self):
        """Update all display elements."""
        self.query_one("#grid").refresh()
        self.query_one("#legend").refresh()
        self.query_one("#status").refresh()
    
    def update_status(self, message: str):
        """Update the status message."""
        status = self.query_one("#status")
        status.message = message
        status.refresh()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Full Message Display for Punch Card Project")
    parser.add_argument("--char-set", default="default", 
                        choices=["default", "block", "circle", "star", "ascii"],
                        help="Character set to use for LED visualization")
    parser.add_argument("--use-ui", action="store_true", 
                        help="Use UI for visualization")
    parser.add_argument("--verbose", action="store_true", 
                        help="Print verbose output")
    parser.add_argument("--led-delay", type=float, default=DEFAULT_LED_DELAY,
                        help="Delay between LED updates (seconds)")
    parser.add_argument("--message-delay", type=float, default=DEFAULT_MESSAGE_DELAY,
                        help="Delay between message characters (seconds)")
    parser.add_argument("--skip-splash", action="store_true",
                        help="Skip splash screen")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug mode")
    parser.add_argument("--message", type=str, default=None,
                        help="Message to display")
    parser.add_argument("--demo", action="store_true",
                        help="Run demonstration mode")
    parser.add_argument("--minimal", action="store_true",
                        help="Use minimal output mode (cleaner display)")
    parser.add_argument("--quick", action="store_true",
                        help="Run in quick mode with minimal delays")
    parser.add_argument("--instant", action="store_true",
                        help="Run in instant mode with no delays")
    parser.add_argument("--force-console", action="store_true",
                        help="Force console mode (no curses UI)")
    return parser.parse_args()

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_args()
    
    # Set up environment variable for console mode if requested
    if args.force_console:
        os.environ['FORCE_CONSOLE'] = '1'
    
    try:
        # Create the display
        display = FullMessageDisplay(
            char_set_name=args.char_set,
            use_ui=args.use_ui,
            verbose=args.verbose,
            led_delay=args.led_delay,
            message_delay=args.message_delay,
            skip_splash=args.skip_splash,
            debug_mode=args.debug,
            minimal_output=args.minimal,
            quick_mode=args.quick,
            instant_mode=args.instant
        )
        
        # Create and run the Textual application
        app = PunchCardApp(display)
        
        try:
            # Show splash screen if not skipped
            if not args.skip_splash:
                display.show_splash()
                app.update_display()
                app.update_status("Splash screen complete")
            
            if args.message:
                # Show a specific message if provided
                display.show_message(args.message, "Command Line")
                app.update_display()
                app.update_status(f"Displaying message: {args.message}")
                
                # Run animations after the message
                if not args.instant:
                    display.run_animations()
                    app.update_display()
                    app.update_status("Animations complete")
            
            elif args.demo:
                # Run demonstration mode with animations
                display.run_demo()
                app.update_display()
                app.update_status("Demo complete")
            
            else:
                # Default action: show system initialization message
                display.show_message("PUNCH CARD SYSTEM INITIALIZED", "System")
                app.update_display()
                app.update_status("System initialized")
                
                # Run animations after initialization
                if not args.instant:
                    display.run_animations()
                    app.update_display()
                    app.update_status("Animations complete")
            
            # Run the app
            app.run()
            
        finally:
            # Always clean up
            display.cleanup()
            
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running program: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 