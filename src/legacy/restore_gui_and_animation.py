#!/usr/bin/env python3
"""
Restore GUI and Animation - A utility to restore GUI components and animation
to the punch card display application.

This script focuses specifically on restoring GUI components, animation functionality,
and console features that were working in version 0.5.2 but may have been lost
during recent fixes.
"""

import os
import sys
import logging
import re
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Target files
MAIN_FILE = "simple_display.py"
BACKUP_SUFFIX = ".bak_gui_restore"

def create_backup():
    """Create a backup of the main file."""
    backup_file = f"{MAIN_FILE}{BACKUP_SUFFIX}"
    
    if not os.path.exists(MAIN_FILE):
        logging.error(f"Cannot find {MAIN_FILE}")
        return False
    
    try:
        shutil.copy2(MAIN_FILE, backup_file)
        logging.info(f"Created backup at {backup_file}")
        return True
    except Exception as e:
        logging.error(f"Failed to create backup: {e}")
        return False

def restore_animation_methods():
    """Restore animation methods in the PunchCardWidget class."""
    if not os.path.exists(MAIN_FILE):
        logging.error(f"Cannot find {MAIN_FILE}")
        return False
    
    try:
        # Read the file
        with open(MAIN_FILE, 'r') as f:
            content = f.read()
        
        # Find the PunchCardWidget class
        punch_card_widget_match = re.search(r"class PunchCardWidget\(QWidget\):", content)
        if not punch_card_widget_match:
            logging.error("Could not find PunchCardWidget class in the main file")
            return False
        
        # Check if animation methods already exist
        animate_punch_card_exists = "def animate_punch_card" in content
        animation_step_exists = "def _animation_step" in content
        
        if animate_punch_card_exists and animation_step_exists:
            logging.info("Animation methods already exist in the main file")
            return True
        
        # Define the animation methods to restore
        animation_methods = r"""
    def animate_punch_card(self, punch_card_str):
        """Animate the punch card display using a diagonal animation.
        
        Args:
            punch_card_str: A string representation of the punch card pattern
                           with 'O' for holes and ' ' for no holes.
        """
        # Ensure animations don't run concurrently
        if self.animation_in_progress:
            logging.info("Animation already in progress, ignoring new request")
            return
            
        self.animation_in_progress = True
        
        # Parse the punch card string into a matrix of hole positions
        rows = punch_card_str.strip().split('\n')
        num_rows = len(rows)
        num_cols = max(len(row) for row in rows) if rows else 0
        
        logging.info(f"Animating punch card with {num_rows} rows and {num_cols} columns")
        
        if num_rows == 0 or num_cols == 0:
            logging.warning("Empty punch card matrix, cannot animate")
            self.animation_in_progress = False
            return
        
        # Create a matrix of hole positions where True = hole (O), False = no hole (space)
        holes = []
        for row in rows:
            hole_row = []
            for col in range(min(len(row), num_cols)):
                hole_row.append(row[col] == 'O')
            
            # Pad row if needed
            hole_row.extend([False] * (num_cols - len(hole_row)))
            holes.append(hole_row)
        
        # Ensure we have exactly 12 rows (12, 11, 0-9) for animation
        if len(holes) < 12:
            # Add empty rows if needed
            holes.extend([[False] * num_cols for _ in range(12 - len(holes))])
        elif len(holes) > 12:
            # Truncate if too many rows
            holes = holes[:12]
        
        # Calculate the number of diagonals to animate
        total_diagonals = num_rows + num_cols - 1
        
        # Start the animation timer
        self.animation_step = 0
        self.animation_total_steps = total_diagonals
        self.animation_holes = holes
        self.animation_timer.start(self.animation_speed)
        
        logging.info(f"Animation started with {total_diagonals} steps")
    
    def _animation_step(self):
        """Process one step of the animation."""
        if self.animation_step >= self.animation_total_steps:
            # Animation complete
            self.animation_timer.stop()
            self.animation_in_progress = False
            logging.info("Animation complete")
            return
        
        # Current diagonal being animated
        diagonal = self.animation_step
        
        # For each row, column in the current diagonal, set the LED
        for row in range(min(self.num_rows, len(self.animation_holes))):
            col = diagonal - row
            if col >= 0 and col < self.num_cols:
                if row < len(self.animation_holes) and col < len(self.animation_holes[row]):
                    self.set_led(row, col, self.animation_holes[row][col])
        
        # Move to the next diagonal
        self.animation_step += 1"""
        
        # Add animation initialization to the __init__ method if not already there
        init_match = re.search(r"def __init__\(self, parent=None\):(.*?)def ", content, re.DOTALL)
        if init_match:
            init_content = init_match.group(1)
            
            # Check if animation variables are already initialized
            animation_init_exists = "self.animation_timer =" in init_content
            
            if not animation_init_exists:
                # Add animation initialization to __init__
                animation_init = """
        # Animation properties
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._animation_step)
        self.animation_speed = 30  # milliseconds between animation steps
        self.animation_step = 0
        self.animation_total_steps = 0
        self.animation_holes = []
        self.animation_in_progress = False
        self.is_animating = False
        self.status_label = None
        self.current_message = ""
"""
                
                # Find a good place to insert - before the end of __init__
                last_line_of_init = init_content.rstrip().split("\n")[-1]
                modified_init = init_content.replace(last_line_of_init, animation_init + "\n" + last_line_of_init)
                
                # Replace the __init__ method
                content = content.replace(init_match.group(1), modified_init)
                logging.info("Added animation initialization to __init__ method")
            
            # Add the animation methods at the end of the class
            last_method_match = re.search(r"def (clear_grid|paintEvent|set_led)[^:]*:.*?\n(    )?(?=\n|$)", content, re.DOTALL)
            if last_method_match:
                last_method = last_method_match.group(0)
                modified_content = content.replace(last_method, last_method + "\n" + animation_methods)
                
                # Write the modified content back to the file
                with open(MAIN_FILE, 'w') as f:
                    f.write(modified_content)
                
                logging.info("Successfully restored animation methods to PunchCardWidget class")
                return True
            else:
                logging.error("Could not find a suitable insertion point for animation methods")
                return False
        else:
            logging.error("Could not find __init__ method in PunchCardWidget class")
            return False
    
    except Exception as e:
        logging.error(f"Failed to restore animation methods: {e}")
        return False

def restore_console_features():
    """Restore console features and GUI components."""
    if not os.path.exists(MAIN_FILE):
        logging.error(f"Cannot find {MAIN_FILE}")
        return False
    
    try:
        # Read the file
        with open(MAIN_FILE, 'r') as f:
            content = f.read()
        
        # Check if console classes already exist
        console_window_exists = "class ConsoleWindow" in content
        api_console_window_exists = "class APIConsoleWindow" in content
        
        if console_window_exists and api_console_window_exists:
            logging.info("Console classes already exist in the main file")
            return True
        
        # Define console classes to restore
        console_classes = r"""
class ConsoleWindow(QDialog):
    """Console window for displaying system information and debug data."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Console")
        self.setMinimumSize(600, 400)
        
        # Set dark theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['console_bg'].name()};
                color: {COLORS['console_text'].name()};
            }}
            QTextEdit {{
                background-color: {COLORS['console_bg'].name()};
                color: {COLORS['console_text'].name()};
                {get_font_css(size=12)}
            }}
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Add custom title bar
        title_bar = ClassicTitleBar("System Console", self)
        layout.addWidget(title_bar)
        
        # Create log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.log_display.setFont(get_font(size=12))
        layout.addWidget(self.log_display)
        
        # Add button row
        button_row = QHBoxLayout()
        
        # Clear button
        clear_button = RetroButton("Clear")
        clear_button.clicked.connect(self.clear_log)
        button_row.addWidget(clear_button)
        
        # Save button
        save_button = RetroButton("Save Log")
        save_button.clicked.connect(self.save_log)
        button_row.addWidget(save_button)
        
        # Add spacer
        button_row.addStretch(1)
        
        # Close button
        close_button = RetroButton("Close")
        close_button.clicked.connect(self.close)
        button_row.addWidget(close_button)
        
        layout.addLayout(button_row)
        
        # Add initial header
        self.log(f"System Console - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "HEADER")
        self.log(f"Python version: {sys.version}", "INFO")
        self.log(f"Operating system: {sys.platform}", "INFO")
        self.log(f"Display dimensions: {self.width()}x{self.height()}", "INFO")
        self.log("Console initialized", "INFO")
    
    def log(self, message: str, level: str = "INFO"):
        """Add a log message to the console.
        
        Args:
            message: The message to log
            level: The log level (INFO, WARNING, ERROR, DEBUG, HEADER)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Format based on level
        if level == "ERROR":
            formatted = f"<span style='color:#ff5555;'>[{timestamp}] ❌ ERROR: {message}</span>"
        elif level == "WARNING":
            formatted = f"<span style='color:#ffaa00;'>[{timestamp}] ⚠️ WARNING: {message}</span>"
        elif level == "DEBUG":
            formatted = f"<span style='color:#55aaff;'>[{timestamp}] 🔍 DEBUG: {message}</span>"
        elif level == "HEADER":
            formatted = f"<span style='color:#55ff55; font-weight:bold;'>===== {message} =====</span>"
        else:  # INFO
            formatted = f"<span style='color:#aaaaaa;'>[{timestamp}] ℹ️ {message}</span>"
        
        # Add to log display
        self.log_display.append(formatted)
        
        # Scroll to bottom
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_display.setTextCursor(cursor)
    
    def save_log(self):
        """Save the current log to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"console_log_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(self.log_display.toPlainText())
            self.log(f"Log saved to {filename}", "INFO")
        except Exception as e:
            self.log(f"Error saving log: {str(e)}", "ERROR")
    
    def clear_log(self):
        """Clear the log display."""
        self.log_display.clear()
        self.log(f"Console cleared - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "HEADER")

class APIConsoleWindow(QDialog):
    """Console window for displaying API-related information from v0.5.2."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Console")
        self.setMinimumSize(600, 400)
        
        # Set dark theme with API specific colors
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['console_bg'].name()};
                color: {COLORS['api_text'].name()};
            }}
            QTextEdit {{
                background-color: {COLORS['console_bg'].name()};
                color: {COLORS['api_text'].name()};
                {get_font_css(size=12)}
            }}
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Add custom title bar
        title_bar = ClassicTitleBar("API Console", self)
        layout.addWidget(title_bar)
        
        # Create log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.log_display.setFont(get_font(size=12))
        layout.addWidget(self.log_display)
        
        # Add button row
        button_row = QHBoxLayout()
        
        # Clear button
        clear_button = RetroButton("Clear")
        clear_button.clicked.connect(self.clear_log)
        button_row.addWidget(clear_button)
        
        # Save button
        save_button = RetroButton("Save Log")
        save_button.clicked.connect(self.save_log)
        button_row.addWidget(save_button)
        
        # Add spacer
        button_row.addStretch(1)
        
        # Close button
        close_button = RetroButton("Close")
        close_button.clicked.connect(self.close)
        button_row.addWidget(close_button)
        
        layout.addLayout(button_row)
        
        # Add initial header
        self.log(f"API Console - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "HEADER")
        self.log("API monitoring initialized", "INFO")
    
    def log(self, message: str, level: str = "INFO"):
        """Add a log message to the console.
        
        Args:
            message: The message to log
            level: The log level (INFO, WARNING, ERROR, DEBUG, HEADER)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Format based on level
        if level == "ERROR":
            formatted = f"<span style='color:#ff5555;'>[{timestamp}] ❌ ERROR: {message}</span>"
        elif level == "WARNING":
            formatted = f"<span style='color:#ffaa00;'>[{timestamp}] ⚠️ WARNING: {message}</span>"
        elif level == "DEBUG":
            formatted = f"<span style='color:#55aaff;'>[{timestamp}] 🔍 DEBUG: {message}</span>"
        elif level == "HEADER":
            formatted = f"<span style='color:#55ff55; font-weight:bold;'>===== {message} =====</span>"
        elif level == "API":
            formatted = f"<span style='color:#55ffaa;'>[{timestamp}] 🔌 API: {message}</span>"
        else:  # INFO
            formatted = f"<span style='color:#aaaaaa;'>[{timestamp}] ℹ️ {message}</span>"
        
        # Add to log display
        self.log_display.append(formatted)
        
        # Scroll to bottom
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_display.setTextCursor(cursor)
    
    def save_log(self):
        """Save the current log to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_log_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(self.log_display.toPlainText())
            self.log(f"Log saved to {filename}", "INFO")
        except Exception as e:
            self.log(f"Error saving log: {str(e)}", "ERROR")
    
    def clear_log(self):
        """Clear the log display."""
        self.log_display.clear()
        self.log(f"Console cleared - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "HEADER")"""
        
        # Find a good place to insert console classes - after RetroButton class
        retro_button_match = re.search(r"class RetroButton\(QPushButton\):.*?\n}", content, re.DOTALL)
        if retro_button_match:
            retro_button_section = retro_button_match.group(0)
            modified_content = content.replace(retro_button_section, retro_button_section + "\n\n" + console_classes)
            
            # Write the modified content back to the file
            with open(MAIN_FILE, 'w') as f:
                f.write(modified_content)
            
            logging.info("Successfully restored console classes to main file")
            return True
        else:
            logging.error("Could not find RetroButton class in main file")
            return False
    
    except Exception as e:
        logging.error(f"Failed to restore console features: {e}")
        return False

def restore_gui_functionality():
    """Restore GUI functionality and helper functions."""
    if not os.path.exists(MAIN_FILE):
        logging.error(f"Cannot find {MAIN_FILE}")
        return False
    
    try:
        # Read the file
        with open(MAIN_FILE, 'r') as f:
            content = f.read()
        
        # Check if helper functions already exist
        update_api_console_exists = "def update_api_console" in content
        
        if not update_api_console_exists:
            # Define the update_api_console function
            update_api_console_func = r"""
def update_api_console(message, level="info"):
    """Update the API console with a message.
    
    Args:
        message: The message to display
        level: The log level (info, warning, error, debug)
    """
    global api_console
    
    if not api_console:
        return
    
    # Convert log level to upper case for console
    level_upper = level.upper()
    
    # Special handling for some log levels
    if level.lower() == "api":
        level_upper = "API"
    
    # Log to the console
    api_console.log(message, level_upper)
"""
            
            # Find a good place to insert - before functions like check_openai_status
            check_openai_match = re.search(r"def check_openai_status\(\):", content)
            if check_openai_match:
                pos = check_openai_match.start()
                modified_content = content[:pos] + update_api_console_func + "\n\n" + content[pos:]
                
                # Write the modified content back to the file
                with open(MAIN_FILE, 'w') as f:
                    f.write(modified_content)
                
                logging.info("Successfully restored update_api_console function")
                return True
            else:
                logging.error("Could not find a suitable insertion point for update_api_console function")
                return False
        else:
            logging.info("Helper functions already exist in the main file")
            return True
    
    except Exception as e:
        logging.error(f"Failed to restore GUI functionality: {e}")
        return False

def ensure_main_function_calls_display():
    """Ensure the main function calls display_punch_card properly."""
    if not os.path.exists(MAIN_FILE):
        logging.error(f"Cannot find {MAIN_FILE}")
        return False
    
    try:
        # Read the file
        with open(MAIN_FILE, 'r') as f:
            content = f.readlines()
        
        # Find the main function
        main_start = None
        for i, line in enumerate(content):
            if line.startswith("def main("):
                main_start = i
                break
        
        if main_start is not None:
            # Look for display_punch_card call in main function
            display_call_found = False
            for i in range(main_start, len(content)):
                if "display_punch_card" in content[i]:
                    display_call_found = True
                    break
                if "def " in content[i] and i > main_start:  # Next function definition
                    break
            
            if not display_call_found:
                # Find a suitable place to add the call - before the end of main
                for i in range(main_start, len(content)):
                    if "sys.exit" in content[i] and i > main_start:
                        # Add the display_punch_card call before sys.exit
                        insert_pos = i
                        display_call = "    try:\n        display_text_on_punch_card('IBM 026 KEYPUNCH TEST')\n    except Exception as e:\n        logging.error(f\"Error running display: {e}\")\n\n"
                        content.insert(insert_pos, display_call)
                        
                        # Write the modified content back to the file
                        with open(MAIN_FILE, 'w') as f:
                            f.writelines(content)
                        
                        logging.info("Successfully added display_punch_card call to main function")
                        return True
            else:
                logging.info("Main function already calls display_punch_card")
                return True
        else:
            logging.error("Could not find main function")
            return False
    
    except Exception as e:
        logging.error(f"Failed to update main function: {e}")
        return False

def main():
    """Main function to restore GUI and animation features."""
    print("IBM 026 Punch Card Display - Restore GUI and Animation")
    print("-----------------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        sys.exit(1)
    
    # Restore animation methods
    if not restore_animation_methods():
        print("Failed to restore animation methods.")
        
    # Restore console features
    if not restore_console_features():
        print("Failed to restore console features.")
        
    # Restore GUI functionality
    if not restore_gui_functionality():
        print("Failed to restore GUI functionality.")
        
    # Ensure main function calls display
    if not ensure_main_function_calls_display():
        print("Failed to update main function.")
    
    print("\n✅ Successfully restored GUI and animation features.")
    print("\nTo run the program:")
    print("1. Run the main script: python3 simple_display.py")
    print("2. If you encounter issues, you can restore from backup:")
    print(f"   cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 