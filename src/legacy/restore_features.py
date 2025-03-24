#!/usr/bin/env python3
"""
Restore Features - A utility to restore key features from the 0.5.2 version
while maintaining our IBM 026 punch card encoding fixes.

This script helps restore animation functionality and character mapping features
that were working in version 0.5.2 but may have been lost during the recent fixes.
It creates backup files before making any changes.
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
STANDALONE_FILE = "ibm_026_punch_card.py"
BACKUP_SUFFIX = ".bak_restore"

def create_backup(filename):
    """Create a backup of the specified file."""
    backup_file = f"{filename}{BACKUP_SUFFIX}"
    
    if not os.path.exists(filename):
        logging.error(f"Cannot find {filename}")
        return False
    
    try:
        shutil.copy2(filename, backup_file)
        logging.info(f"Created backup at {backup_file}")
        return True
    except Exception as e:
        logging.error(f"Failed to create backup: {e}")
        return False

def restore_animation_feature():
    """Restore the animation feature from the standalone file to the main file."""
    if not os.path.exists(MAIN_FILE):
        logging.error(f"Cannot find {MAIN_FILE}")
        return False
    
    if not os.path.exists(STANDALONE_FILE):
        logging.error(f"Cannot find {STANDALONE_FILE}")
        return False
    
    try:
        # Read both files
        with open(MAIN_FILE, 'r') as f:
            main_content = f.readlines()
        
        with open(STANDALONE_FILE, 'r') as f:
            standalone_content = f.readlines()
        
        # Find the PunchCardWidget class in both files
        main_widget_start = None
        main_widget_end = None
        
        for i, line in enumerate(main_content):
            if line.strip().startswith("class PunchCardWidget") and "QWidget" in line:
                main_widget_start = i
                logging.info(f"Found PunchCardWidget class in main file at line {i+1}")
                break
        
        if main_widget_start is not None:
            # Find the end of the PunchCardWidget class
            brace_level = 0
            for i, line in enumerate(main_content[main_widget_start:], main_widget_start):
                if "class " in line and i > main_widget_start:
                    main_widget_end = i - 1
                    logging.info(f"Found end of PunchCardWidget class at line {i}")
                    break
            
            if main_widget_end is None:
                main_widget_end = len(main_content) - 1
        
        # Find the animate_punch_card method in the standalone file
        standalone_animate_start = None
        standalone_animate_end = None
        standalone_animation_step = None
        standalone_animation_step_end = None
        
        for i, line in enumerate(standalone_content):
            if "def animate_punch_card" in line:
                standalone_animate_start = i
                logging.info(f"Found animate_punch_card method in standalone file at line {i+1}")
            
            if standalone_animate_start is not None and "def _animation_step" in line:
                standalone_animation_step = i
                logging.info(f"Found _animation_step method in standalone file at line {i+1}")
            
            if standalone_animation_step is not None and "def clear_display" in line:
                standalone_animation_step_end = i - 1
                logging.info(f"Found end of _animation_step method at line {i}")
                break
        
        if standalone_animate_start is not None and standalone_animation_step is not None:
            standalone_animate_end = standalone_animation_step - 1
            
            # Extract animation methods from standalone file
            animate_method = standalone_content[standalone_animate_start:standalone_animate_end+1]
            animation_step_method = standalone_content[standalone_animation_step:standalone_animation_step_end+1]
            
            # Prepare to insert animations into main file
            if main_widget_start is not None and main_widget_end is not None:
                # Check if the methods already exist in the main file
                animate_exists = False
                animation_step_exists = False
                
                for line in main_content[main_widget_start:main_widget_end]:
                    if "def animate_punch_card" in line:
                        animate_exists = True
                    if "def _animation_step" in line:
                        animation_step_exists = True
                
                # If animation methods don't exist, insert them before the end of the PunchCardWidget class
                insert_position = main_widget_end
                
                # Prepare the new content
                new_content = list(main_content)
                
                if not animate_exists:
                    logging.info(f"Inserting animate_punch_card method at line {insert_position+1}")
                    new_content[insert_position:insert_position] = animate_method
                    insert_position += len(animate_method)
                
                if not animation_step_exists:
                    logging.info(f"Inserting _animation_step method at line {insert_position+1}")
                    new_content[insert_position:insert_position] = animation_step_method
                
                # Write the updated content back to the main file
                with open(MAIN_FILE, 'w') as f:
                    f.writelines(new_content)
                
                logging.info(f"Successfully restored animation methods to {MAIN_FILE}")
                return True
            else:
                logging.error("Could not find PunchCardWidget class boundaries in main file")
                return False
        else:
            logging.error("Could not find animation methods in standalone file")
            return False
    
    except Exception as e:
        logging.error(f"Failed to restore animation feature: {e}")
        return False

def restore_character_mapping():
    """Ensure the IBM 026 character mapping is correctly implemented in the main file."""
    if not os.path.exists(MAIN_FILE):
        logging.error(f"Cannot find {MAIN_FILE}")
        return False
    
    try:
        # Read the main file
        with open(MAIN_FILE, 'r') as f:
            content = f.read()
        
        # Define the correct IBM 026 character mapping
        correct_mapping = """    # Define patterns based on IBM 026 standard - using IBM row numbers directly
    IBM_CHAR_MAPPING = {
        # Letters A–I: zone punch 12 + digit punches 1-9
        'A': [12, 1],    # 12 + 1
        'B': [12, 2],    # 12 + 2
        'C': [12, 3],    # 12 + 3
        'D': [12, 4],    # 12 + 4
        'E': [12, 5],    # 12 + 5
        'F': [12, 6],    # 12 + 6
        'G': [12, 7],    # 12 + 7
        'H': [12, 8],    # 12 + 8
        'I': [12, 9],    # 12 + 9

        # Letters J–R: zone punch 11 + digit punches 1-9
        'J': [11, 1],    # 11 + 1
        'K': [11, 2],    # 11 + 2
        'L': [11, 3],    # 11 + 3
        'M': [11, 4],    # 11 + 4
        'N': [11, 5],    # 11 + 5
        'O': [11, 6],    # 11 + 6
        'P': [11, 7],    # 11 + 7
        'Q': [11, 8],    # 11 + 8
        'R': [11, 9],    # 11 + 9

        # Letters S–Z: zone punch 0 + digit punches 2-9
        'S': [0, 2],     # 0 + 2
        'T': [0, 3],     # 0 + 3
        'U': [0, 4],     # 0 + 4
        'V': [0, 5],     # 0 + 5
        'W': [0, 6],     # 0 + 6
        'X': [0, 7],     # 0 + 7
        'Y': [0, 8],     # 0 + 8
        'Z': [0, 9],     # 0 + 9

        # Numbers (single punch in rows 0-9)
        '0': [0],        # 0 only
        '1': [1],        # 1 only
        '2': [2],        # 2 only
        '3': [3],        # 3 only
        '4': [4],        # 4 only
        '5': [5],        # 5 only
        '6': [6],        # 6 only
        '7': [7],        # 7 only
        '8': [8],        # 8 only
        '9': [9],        # 9 only
        
        # Common special characters
        ' ': [],                 # No punches
        '.': [12, 3, 8],         # 12 + 3 + 8
        ',': [0, 3, 8],          # 0 + 3 + 8
        '-': [11],               # 11 only (dash/hyphen)
        '/': [0, 1],             # 0 + 1
        '&': [12],               # 12 only (ampersand)
    }"""
        
        # Find the format_punch_card function
        format_punch_card_match = re.search(r"def format_punch_card\(.*?\)", content)
        
        if format_punch_card_match:
            start_pos = format_punch_card_match.start()
            
            # Check if IBM_CHAR_MAPPING is already defined correctly
            if "IBM_CHAR_MAPPING" in content[start_pos:start_pos+5000]:
                # Find where the mapping starts and ends
                mapping_start = content.find("IBM_CHAR_MAPPING", start_pos)
                mapping_end = content.find("}", mapping_start)
                
                if mapping_start > 0 and mapping_end > mapping_start:
                    # Check if the key characters are mapped correctly (E, I, J, S)
                    mapping_section = content[mapping_start:mapping_end+1]
                    
                    # Check if the problematic characters are correctly mapped
                    e_correct = "'E': [12, 5]" in mapping_section
                    i_correct = "'I': [12, 9]" in mapping_section
                    j_correct = "'J': [11, 1]" in mapping_section
                    s_correct = "'S': [0, 2]" in mapping_section
                    
                    if e_correct and i_correct and j_correct and s_correct:
                        logging.info("Character mapping is already correct in the main file")
                        return True
                    else:
                        # Replace the incorrect mapping with the correct one
                        old_mapping_section = content[mapping_start-4:mapping_end+1]
                        new_content = content.replace(old_mapping_section, correct_mapping)
                        
                        with open(MAIN_FILE, 'w') as f:
                            f.write(new_content)
                        
                        logging.info("Updated the character mapping in the main file")
                        return True
                else:
                    logging.error("Could not find the boundaries of IBM_CHAR_MAPPING")
                    return False
            else:
                logging.error("Could not find IBM_CHAR_MAPPING in the format_punch_card function")
                return False
        else:
            logging.error("Could not find format_punch_card function in the main file")
            return False
    
    except Exception as e:
        logging.error(f"Failed to restore character mapping: {e}")
        return False

def fix_syntax_errors():
    """Fix syntax errors in the main program file."""
    if not os.path.exists(MAIN_FILE):
        logging.error(f"Cannot find {MAIN_FILE}")
        return False
    
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Specific fixes for lines with indentation issues
        # Only adding the most critical fixes to restore functionality
        fixes = {
            # Fix indentation for save_message_to_database at line 553
            552: "        # Save message to database with source\n",
            553: "        save_message_to_database(message, \"openai\")\n",
            554: "        \n",
            555: "        return message\n",
            
            # Fix main entrypoint at line 8132
            8131: "        main()\n",
            8132: "    except Exception as e:\n", 
            8133: "        logging.error(f\"❌ Error in main function: {e}\")\n",
            8134: "        if 'args' in locals() and getattr(args, 'debug', False):\n",
            8135: "            import traceback\n",
            8136: "            traceback.print_exc()\n"
        }
        
        # Apply fixes
        for line_num, new_line in fixes.items():
            if 0 <= line_num < len(lines):
                lines[line_num] = new_line
        
        # Write the fixed content back to the file
        with open(MAIN_FILE, 'w') as f:
            f.writelines(lines)
        
        logging.info(f"Applied critical syntax fixes to {MAIN_FILE}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to fix syntax errors: {e}")
        return False

def copy_standalone_functions():
    """Copy useful standalone functions from the fix script to ensure they're available."""
    if not os.path.exists(MAIN_FILE):
        logging.error(f"Cannot find {MAIN_FILE}")
        return False
    
    if not os.path.exists(STANDALONE_FILE):
        logging.error(f"Cannot find {STANDALONE_FILE}")
        return False
    
    try:
        # Read both files
        with open(MAIN_FILE, 'r') as f:
            main_content = f.readlines()
        
        with open(STANDALONE_FILE, 'r') as f:
            standalone_content = f.readlines()
        
        # Find the display_text_on_punch_card function in standalone file
        display_function_start = None
        display_function_end = None
        
        for i, line in enumerate(standalone_content):
            if "def display_text_on_punch_card" in line:
                display_function_start = i
                logging.info(f"Found display_text_on_punch_card function in standalone file at line {i+1}")
                break
        
        if display_function_start is not None:
            # Find the end of the function
            for i, line in enumerate(standalone_content[display_function_start+1:], display_function_start+1):
                if line.startswith("def ") or i == len(standalone_content) - 1:
                    display_function_end = i - 1
                    logging.info(f"Found end of display_text_on_punch_card function at line {i}")
                    break
            
            # Check if the function already exists in the main file
            function_exists = False
            for line in main_content:
                if "def display_text_on_punch_card" in line:
                    function_exists = True
                    logging.info("display_text_on_punch_card function already exists in main file")
                    break
            
            if not function_exists and display_function_end is not None:
                # Extract the function from standalone file
                display_function = standalone_content[display_function_start:display_function_end+1]
                
                # Find a good position to insert the function in the main file
                # Look for the main function as a reference point
                insert_position = None
                for i, line in enumerate(main_content):
                    if line.startswith("def main("):
                        insert_position = i
                        logging.info(f"Found main function at line {i+1}")
                        break
                
                if insert_position is not None:
                    # Insert the display function before the main function
                    new_content = main_content[:insert_position] + ["\n"] + display_function + ["\n"] + main_content[insert_position:]
                    
                    # Write the updated content back to the main file
                    with open(MAIN_FILE, 'w') as f:
                        f.writelines(new_content)
                    
                    logging.info(f"Successfully copied display_text_on_punch_card function to {MAIN_FILE}")
                    return True
                else:
                    logging.error("Could not find appropriate insertion point in main file")
                    return False
            else:
                logging.info("No functions needed to be copied from standalone file")
                return True
        else:
            logging.error("Could not find display_text_on_punch_card function in standalone file")
            return False
    
    except Exception as e:
        logging.error(f"Failed to copy standalone functions: {e}")
        return False

def main():
    """Main function to restore features."""
    print("IBM 026 Punch Card Display - Restore Features")
    print("---------------------------------------------")
    
    # Create backups
    if not create_backup(MAIN_FILE):
        print("Failed to create backup of main file. Aborting.")
        sys.exit(1)
    
    # Fix critical syntax errors first
    if not fix_syntax_errors():
        print("Failed to fix syntax errors.")
        sys.exit(1)
    
    # Skip animation feature restoration since it's not in the standalone file
    print("Skipping animation feature restoration (not found in standalone file)")
    
    # Ensure correct character mapping
    if not restore_character_mapping():
        print("Failed to ensure correct character mapping.")
        sys.exit(1)
    
    # Copy useful standalone functions
    if not copy_standalone_functions():
        print("Failed to copy standalone functions.")
        sys.exit(1)
    
    print("\n✅ Successfully restored features to main program file.")
    print("\nTo run the program:")
    print("1. Run the main script: python3 simple_display.py")
    print("2. If you encounter issues, you can restore from backup:")
    print(f"   cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 