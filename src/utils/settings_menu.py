import os
import time
import shutil
import sys
import tty
import termios
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Constants for terminal size
MIN_TERMINAL_WIDTH = 80
MIN_TERMINAL_HEIGHT = 30

@dataclass
class Setting:
    name: str
    value: Any
    description: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    options: Optional[list] = None
    default_value: Any = None  # Store default value

class SettingsMenu:
    def __init__(self, settings: Dict[str, Setting]):
        self.settings = settings
        self.current_setting_index = 0
        self.settings_list = list(settings.items())
        
        # Get terminal size
        self.terminal_width = shutil.get_terminal_size().columns
        self.terminal_height = shutil.get_terminal_size().lines
        
        # Check terminal size
        if self.terminal_width < MIN_TERMINAL_WIDTH or self.terminal_height < MIN_TERMINAL_HEIGHT:
            raise ValueError(f"Terminal size too small. Minimum required: {MIN_TERMINAL_WIDTH}x{MIN_TERMINAL_HEIGHT}")
            
        # Store default values
        for setting in settings.values():
            setting.default_value = setting.value
        
    def _clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def _display_card_frame(self, content_lines: list, show_row_numbers: bool = False):
        """Display content within the punch card rectangle"""
        # Calculate dimensions
        card_width = 80 + 4  # 80 columns + 2 borders + 2 spaces for row numbers
        x_offset = max(0, (self.terminal_width - card_width) // 2)
        y_offset = 2  # Reduced from 3 to fit better
        
        # Print empty lines for consistent vertical spacing
        print("\n" * y_offset)
        
        # Print top border
        print(" " * x_offset + "   ┌" + "─" * 79 + "─┐")
        
        # Define row order and labels
        row_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        row_labels = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        
        # Calculate text positioning
        total_lines = len(content_lines)
        start_row = (12 - total_lines) // 2
        
        # Print grid with text
        for i, row_idx in enumerate(row_order):
            row_num = row_labels[i] if show_row_numbers else "  "
            if start_row <= i < start_row + total_lines:
                text_line = content_lines[i - start_row]
                # Center the text within the card
                padding = (80 - len(text_line)) // 2
                row_content = " " * padding + text_line + " " * (80 - padding - len(text_line))
            else:
                row_content = " " * 80
            print(" " * x_offset + f"{row_num:2s} │{row_content}│")
        
        # Print bottom border
        print(" " * x_offset + "   └" + "─" * 79 + "─┘")
        
    def _format_value(self, setting: Setting) -> str:
        """Format the setting value for display"""
        if setting.options is not None:
            return str(setting.value)
        elif isinstance(setting.value, bool):
            return "ON" if setting.value else "OFF"
        elif isinstance(setting.value, float):
            return f"{setting.value:.2f}"
        else:
            return str(setting.value)
            
    def _adjust_setting(self, setting: Setting, direction: int):
        """Adjust the setting value based on its type"""
        if setting.options is not None:
            current_index = setting.options.index(setting.value)
            new_index = (current_index + direction) % len(setting.options)
            setting.value = setting.options[new_index]
        elif isinstance(setting.value, bool):
            setting.value = not setting.value
        elif isinstance(setting.value, (int, float)):
            if setting.step is not None:
                setting.value += setting.step * direction
            if setting.min_value is not None:
                setting.value = max(setting.min_value, setting.value)
            if setting.max_value is not None:
                setting.value = min(setting.max_value, setting.value)
                
    def _get_key(self):
        """Get a single keypress from the user"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            
            # Handle Escape key
            if ch == '\x1b':
                # Read the next character
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    # Arrow key
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return 'up'
                    if ch3 == 'B': return 'down'
                    if ch3 == 'C': return 'right'
                    if ch3 == 'D': return 'left'
                else:
                    # Just Escape key
                    return 'esc'
            
            # Handle Enter key
            if ch == '\r':
                return 'enter'
            
            # Handle other keys
            return ch.lower()
            
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
    def _show_confirmation(self, message: str) -> bool:
        """Show a confirmation dialog and return True if confirmed"""
        while True:
            self._clear_screen()
            menu_lines = [
                "CONFIRMATION",
                "",
                message,
                "",
                "Controls:",
                "Y: Yes",
                "N: No"
            ]
            self._display_card_frame(menu_lines)
            
            key = self._get_key()
            if key == 'y':
                return True
            elif key == 'n':
                return False
                
    def _restore_defaults(self):
        """Restore all settings to their default values"""
        for setting in self.settings.values():
            setting.value = setting.default_value
                
    def display_menu(self):
        """Display the settings menu and handle user input"""
        while True:
            self._clear_screen()
            
            # Prepare menu content
            menu_lines = [
                "SETTINGS MENU",
                "",
                f"Current Setting: {self.settings_list[self.current_setting_index][0]}",
                f"Value: {self._format_value(self.settings_list[self.current_setting_index][1])}",
                "",
                self.settings_list[self.current_setting_index][1].description,
                "",
                "Controls",
                "↑/↓ Navigate Settings  ←/→ Adjust Value",
                "R: Restore Defaults",
                "Enter: Save & Exit",
                "Esc: Cancel"
            ]
            
            # Display menu in punch card frame
            self._display_card_frame(menu_lines)
            
            # Handle user input
            key = self._get_key()
            if key == 'esc':
                return False
            elif key == 'enter':
                if self._show_confirmation("Save current settings and continue?"):
                    return True
            elif key == 'r':
                if self._show_confirmation("Restore all settings to defaults?"):
                    self._restore_defaults()
            elif key == 'up':
                self.current_setting_index = (self.current_setting_index - 1) % len(self.settings_list)
            elif key == 'down':
                self.current_setting_index = (self.current_setting_index + 1) % len(self.settings_list)
            elif key == 'right':
                self._adjust_setting(self.settings_list[self.current_setting_index][1], 1)
            elif key == 'left':
                self._adjust_setting(self.settings_list[self.current_setting_index][1], -1)
                
    def get_settings(self) -> Dict[str, Any]:
        """Get the current settings values"""
        return {name: setting.value for name, setting in self.settings.items()} 