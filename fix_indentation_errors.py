#!/usr/bin/env python3
"""
Fix Indentation Errors Script - Corrects indentation issues in the file.
"""

import os
import re
import shutil
import logging
import tokenize
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Target file
MAIN_FILE = "simple_display.py"
BACKUP_SUFFIX = ".bak_indentation_fix"

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

def find_indentation_errors():
    """Find indentation errors using tokenize module."""
    try:
        errors = []
        with open(MAIN_FILE, 'rb') as f:
            try:
                tokens = list(tokenize.tokenize(f.readline))
                logging.info("No indentation errors found with tokenize")
            except tokenize.TokenError as e:
                lineno = e.args[1][0]
                errors.append(lineno)
                logging.info(f"Found indentation error at line {lineno}")
        
        return errors
    
    except Exception as e:
        logging.error(f"Failed to find indentation errors: {e}")
        return []

def fix_indentation_errors():
    """Fix indentation errors in the file."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Focus on the problematic area around line 6010
        # The issue appears to be mismatched else clauses
        if 6008 < len(lines) and 6010 < len(lines):
            # Check if there's a mismatched else clause
            if "else:" in lines[6008] and "else:" in lines[6012]:
                logging.info("Found mismatched else clauses around line 6010")
                
                # Fix the indentation by properly nesting the if-else blocks
                fixed_lines = lines[:6008]  # Add everything up to the first else
                
                # Handle the first else clause
                fixed_lines.append(lines[6008])  # Keep the first else
                
                # Add properly indented content for the first else
                content_indent = re.match(r'^\s*', lines[6008]).group(0) + '    '
                fixed_lines.append(content_indent + 'self.status_label.setText("")\n')
                
                # Skip the incorrectly indented lines
                fixed_lines.extend(lines[6012:])
                
                # Write the fixed content back to the file
                with open(MAIN_FILE, 'w') as f:
                    f.writelines(fixed_lines)
                
                logging.info("Fixed mismatched else clauses around line 6010")
                return True
        
        # General fix for indentation errors - check every line
        fixed = False
        for i in range(1, len(lines)):
            current_line = lines[i]
            if current_line.strip() == "":
                continue  # Skip empty lines
                
            if current_line.strip() == "else:":
                # Look for matching if statement
                j = i - 1
                found_if = False
                while j >= 0:
                    if re.match(r'^\s*if\s+', lines[j]):
                        # Found a matching if, check indentation
                        if_indent = len(re.match(r'^\s*', lines[j]).group(0))
                        else_indent = len(re.match(r'^\s*', current_line).group(0))
                        
                        if if_indent != else_indent:
                            # Fix else indentation to match if
                            lines[i] = ' ' * if_indent + current_line.lstrip()
                            fixed = True
                            logging.info(f"Fixed mismatched else at line {i+1}")
                        
                        found_if = True
                        break
                    j -= 1
        
        if fixed:
            # Write the fixed content back to the file
            with open(MAIN_FILE, 'w') as f:
                f.writelines(lines)
            
            logging.info("Fixed indentation errors in the file")
            return True
        
        logging.warning("No specific indentation errors found to fix")
        return False
    
    except Exception as e:
        logging.error(f"Failed to fix indentation errors: {e}")
        return False

def clean_and_normalize_file():
    """Clean and normalize the file to ensure consistent indentation."""
    try:
        with open(MAIN_FILE, 'r') as f:
            content = f.read()
        
        # Replace tabs with spaces
        content = content.replace('\t', '    ')
        
        # Fix line endings
        content = content.replace('\r\n', '\n')
        
        # Fix common indentation issues
        # 1. Fix dangling else statements without matching if
        content = re.sub(r'(\n[ \t]*else:)(?!\n[ \t]+\S)', r'\1\n    pass', content)
        
        # 2. Fix lines that might end with a colon but have no indented content after
        content = re.sub(r'([\n][ \t]*\w+.*:)[ \t]*\n(?![ \t]+)', r'\1\n    pass\n', content)
        
        # Write the cleaned content back to the file
        with open(MAIN_FILE, 'w') as f:
            f.write(content)
        
        logging.info("Cleaned and normalized the file")
        return True
    
    except Exception as e:
        logging.error(f"Failed to clean and normalize the file: {e}")
        return False

def create_fixed_file():
    """Create a fixed version of the file with PEP 8 indentation."""
    try:
        # Read the original file
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Create a new file with fixed indentation
        fixed_file = f"{MAIN_FILE}.fixed"
        with open(fixed_file, 'w') as f:
            # Track indentation level
            indent_level = 0
            for line in lines:
                stripped = line.strip()
                
                # Skip empty lines
                if not stripped:
                    f.write('\n')
                    continue
                
                # Check for dedent
                if stripped.startswith(('elif', 'else:', 'except', 'finally:', 'except:')):
                    indent_level = max(0, indent_level - 1)
                
                # Write the line with proper indentation
                f.write(' ' * (4 * indent_level) + stripped + '\n')
                
                # Check for indent
                if stripped.endswith(':') and not stripped.startswith(('elif', 'else:', 'except', 'finally:', 'except:')):
                    indent_level += 1
        
        logging.info(f"Created fixed file at {fixed_file}")
        return True
    
    except Exception as e:
        logging.error(f"Failed to create fixed file: {e}")
        return False

def fix_specific_area():
    """Fix the specific problematic area around line 6010."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Look for the specific pattern around line 6010
        for i in range(6000, min(6020, len(lines))):
            if i < len(lines) and "else:" in lines[i]:
                # Check if there's another else nearby
                for j in range(i+1, min(i+10, len(lines))):
                    if j < len(lines) and "else:" in lines[j]:
                        logging.info(f"Found potential mismatched else clauses at lines {i+1} and {j+1}")
                        
                        # Determine the correct indentation level for the first else
                        k = i - 1
                        while k >= 0 and k < len(lines):
                            if "if " in lines[k]:
                                if_indent = len(lines[k]) - len(lines[k].lstrip())
                                correct_else_indent = if_indent
                                
                                # Fix indentation of the first else
                                lines[i] = ' ' * correct_else_indent + lines[i].lstrip()
                                
                                # Remove the second else and its content or adjust it correctly
                                if j - i <= 5:  # Only if they're close together
                                    # Option 1: Remove the second else
                                    lines[j] = ''  # Remove the second else
                                    
                                    # Option 2: Add a nested if for the second else
                                    # lines[j] = ' ' * (correct_else_indent + 4) + "if True:  # Added to fix syntax\n"
                                
                                # Write the fixed content back to the file
                                with open(MAIN_FILE, 'w') as f:
                                    f.writelines(lines)
                                
                                logging.info(f"Fixed mismatched else clauses at lines {i+1} and {j+1}")
                                return True
                            k -= 1
        
        logging.warning("Could not find specific pattern to fix")
        return False
    
    except Exception as e:
        logging.error(f"Failed to fix specific area: {e}")
        return False

def main():
    """Main function to fix indentation errors."""
    print("IBM 026 Punch Card Display - Fix Indentation Errors")
    print("------------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # First try to fix the specific area
    if fix_specific_area():
        print("✅ Successfully fixed specific problematic area")
    else:
        # If specific fix fails, try general indentation fixes
        if fix_indentation_errors():
            print("✅ Successfully fixed indentation errors")
        else:
            # If all else fails, clean and normalize the file
            if clean_and_normalize_file():
                print("✅ Successfully cleaned and normalized the file")
            else:
                print("❌ Failed to fix indentation errors")
                print("Creating a separate fixed file for manual inspection...")
                if create_fixed_file():
                    print(f"✅ Created fixed file at {MAIN_FILE}.fixed")
                else:
                    print("❌ Failed to create fixed file")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 