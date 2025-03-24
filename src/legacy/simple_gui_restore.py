#!/usr/bin/env python3
"""
Simple GUI Restore - A utility to restore essential GUI components
to the punch card display application.
"""

import os
import sys
import logging
import shutil
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Target file
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

def ensure_animation_initialization():
    """Ensure animation properties are initialized in PunchCardWidget."""
    try:
        with open(MAIN_FILE, 'r') as f:
            content = f.read()
        
        # Check if PunchCardWidget class exists
        if "class PunchCardWidget" not in content:
            logging.error("PunchCardWidget class not found in main file")
            return False
        
        # Find the __init__ method in PunchCardWidget
        match = re.search(r"(class PunchCardWidget.*?def __init__\(self, parent=None\):.*?)def ", 
                          content, re.DOTALL)
        
        if not match:
            logging.error("Could not find __init__ method in PunchCardWidget class")
            return False
        
        # Check if animation properties already exist
        init_section = match.group(1)
        if "self.animation_timer" in init_section:
            logging.info("Animation properties already initialized")
            return True
        
        # Add animation properties before the end of __init__
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
        
        # Add to the end of __init__
        last_line_pattern = r"(\s+)(\S.*?)(\n\s+def )"
        modified_content = re.sub(
            last_line_pattern, 
            r"\1\2\n" + animation_init + r"\3", 
            init_section, 
            count=1, 
            flags=re.DOTALL
        )
        
        # Replace the old initialization
        new_content = content.replace(init_section, modified_content)
        
        with open(MAIN_FILE, 'w') as f:
            f.write(new_content)
        
        logging.info("Successfully added animation initialization")
        return True
        
    except Exception as e:
        logging.error(f"Failed to ensure animation initialization: {e}")
        return False

def create_animation_methods():
    """Create animation methods in a separate file to be added manually."""
    animation_file = "animation_methods.py"
    
    try:
        animation_methods = """
# Animation methods to be added to the PunchCardWidget class
# Add these methods to the PunchCardWidget class in simple_display.py

def animate_punch_card(self, punch_card_str):
    \"\"\"Animate the punch card display using a diagonal animation.
    
    Args:
        punch_card_str: A string representation of the punch card pattern
                       with 'O' for holes and ' ' for no holes.
    \"\"\"
    # Ensure animations don't run concurrently
    if self.animation_in_progress:
        logging.info("Animation already in progress, ignoring new request")
        return
        
    self.animation_in_progress = True
    
    # Parse the punch card string into a matrix of hole positions
    rows = punch_card_str.strip().split('\\n')
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
    \"\"\"Process one step of the animation.\"\"\"
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
    self.animation_step += 1
"""
        
        with open(animation_file, 'w') as f:
            f.write(animation_methods)
        
        logging.info(f"Created {animation_file} with animation methods to be added manually")
        return True
    
    except Exception as e:
        logging.error(f"Failed to create animation methods file: {e}")
        return False

def ensure_imports():
    """Ensure all necessary imports are present."""
    try:
        with open(MAIN_FILE, 'r') as f:
            content = f.readlines()
        
        # Find the imports section
        import_end = 0
        for i, line in enumerate(content):
            if line.startswith("import ") or line.startswith("from "):
                import_end = i + 1
        
        # Check for necessary imports
        qt_imports = "from PyQt6.QtCore import QTimer, Qt, QPoint, QRectF, QRect\n"
        if qt_imports not in content[:import_end]:
            content.insert(import_end, qt_imports)
            logging.info("Added missing PyQt6 imports")
        
        # Write the updated content
        with open(MAIN_FILE, 'w') as f:
            f.writelines(content)
        
        logging.info("Successfully ensured required imports")
        return True
    
    except Exception as e:
        logging.error(f"Failed to ensure imports: {e}")
        return False

def fix_main_function():
    """Fix the main function to properly call display_text_on_punch_card."""
    try:
        with open(MAIN_FILE, 'r') as f:
            content = f.readlines()
        
        # Find the main function
        main_start = None
        for i, line in enumerate(content):
            if line.strip() == "def main():":
                main_start = i
                break
        
        if main_start is not None:
            # Check for display_punch_card call
            display_call_found = False
            sys_exit_pos = None
            
            # Look for display_punch_card call and sys.exit
            for i in range(main_start, len(content)):
                if "display_" in content[i] and "punch_card" in content[i]:
                    display_call_found = True
                if "sys.exit" in content[i]:
                    sys_exit_pos = i
                if i < len(content) - 1 and content[i+1].strip().startswith("def "):
                    # End of main function
                    break
            
            # Add display call before sys.exit if needed
            if not display_call_found and sys_exit_pos is not None:
                display_call = """
    try:
        # Try to display a test message on the punch card
        if 'display_text_on_punch_card' in globals():
            display_text_on_punch_card("IBM 026 KEYPUNCH TEST")
        elif 'display_punch_card' in globals():
            display_punch_card("IBM 026 KEYPUNCH TEST")
    except Exception as e:
        logging.error(f"Error displaying test message: {e}")

"""
                content.insert(sys_exit_pos, display_call)
                
                # Write the updated content
                with open(MAIN_FILE, 'w') as f:
                    f.writelines(content)
                
                logging.info("Successfully updated main function to call display function")
                return True
            elif display_call_found:
                logging.info("Main function already has display call")
                return True
            else:
                logging.error("Could not find appropriate location to add display call")
                return False
        else:
            logging.error("Could not find main function")
            return False
    
    except Exception as e:
        logging.error(f"Failed to fix main function: {e}")
        return False

def create_update_api_console_function():
    """Create the update_api_console function in a separate file."""
    api_console_file = "api_console_functions.py"
    
    try:
        api_console_functions = """
# API console functions to be added to simple_display.py

def update_api_console(message, level="info"):
    \"\"\"Update the API console with a message.
    
    Args:
        message: The message to display
        level: The log level (info, warning, error, debug)
    \"\"\"
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
        
        with open(api_console_file, 'w') as f:
            f.write(api_console_functions)
        
        logging.info(f"Created {api_console_file} with API console functions to be added manually")
        return True
    
    except Exception as e:
        logging.error(f"Failed to create API console functions file: {e}")
        return False

def main():
    """Main function to restore GUI features."""
    print("IBM 026 Punch Card Display - Simple GUI Restore")
    print("----------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        sys.exit(1)
    
    # Ensure necessary imports
    if not ensure_imports():
        print("Failed to ensure necessary imports.")
    
    # Ensure animation initialization
    if not ensure_animation_initialization():
        print("Failed to ensure animation initialization.")
    
    # Create animation methods file
    if not create_animation_methods():
        print("Failed to create animation methods file.")
    
    # Fix main function
    if not fix_main_function():
        print("Failed to fix main function.")
    
    # Create API console functions file
    if not create_update_api_console_function():
        print("Failed to create API console functions file.")
    
    print("\n✅ GUI restore completed with the following outputs:")
    print("1. Added missing imports to main file")
    print("2. Added animation initialization to PunchCardWidget class")
    print("3. Created animation_methods.py - copy these methods to the PunchCardWidget class")
    print("4. Created api_console_functions.py - copy these functions to the main file")
    print("5. Updated main function to call display_text_on_punch_card")
    print("\nTo run the program:")
    print("1. Copy the methods from animation_methods.py to the PunchCardWidget class in simple_display.py")
    print("2. Copy the functions from api_console_functions.py to simple_display.py")
    print("3. Run the main script: python3 simple_display.py")
    print("4. If you encounter issues, you can restore from backup:")
    print(f"   cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 