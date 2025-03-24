#!/usr/bin/env python3
"""
Fix All Style Sheets Script - Comprehensively fixes all style sheets in the file.
"""

import os
import shutil
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Target file
MAIN_FILE = "simple_display.py"
BACKUP_SUFFIX = ".bak_all_styles_fix"

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

def fix_all_style_sheets():
    """Fix all style sheets in the file."""
    try:
        with open(MAIN_FILE, 'r') as f:
            content = f.read()
        
        # 1. First pass: Fix all f-string style sheets
        f_string_pattern = r'setStyleSheet\(f"""(.*?)"""\)'
        replacement = lambda m: convert_to_name_method(m.group(0), m.group(1))
        new_content = re.sub(f_string_pattern, replacement, content, flags=re.DOTALL)
        
        # 2. Manual fixes for specific areas
        # Button container style at lines 1334-1340
        button_container_style = [
            '                display.button_container.setStyleSheet(\n',
            '                    "background-color: " + UIStyleHelper.COLORS[\'bg\'].name() + ";" +\n',
            '                    "border: 1px solid " + UIStyleHelper.COLORS[\'border\'].name() + ";" +\n',
            '                    "border-radius: 3px;" +\n',
            '                    "padding: 5px;"\n',
            '                )\n'
        ]
        
        # Card display style at lines 1364-1374
        card_display_style = [
            '        # Apply style to the punch card display if possible\n',
            '        if hasattr(display, \'card_display\'):\n',
            '            display.card_display.setStyleSheet(\n',
            '                "background-color: " + UIStyleHelper.COLORS[\'bg\'].name() + ";" +\n',
            '                "color: " + UIStyleHelper.COLORS[\'fg\'].name() + ";" +\n',
            '                "border: 1px solid " + UIStyleHelper.COLORS[\'border\'].name() + ";" +\n',
            '                "padding: 8px;" +\n',
            '                "font-family: \'" + UIStyleHelper.FONTS[\'monospace\'] + "\';" +\n',
            '                "font-size: " + UIStyleHelper.FONTS[\'size_normal\'] + ";"\n',
            '            )\n'
        ]
        
        # Parent widget style at lines 1377-1381
        parent_style = [
            '        # Apply style to parent widgets if possible\n',
            '        if hasattr(display, \'parent\') and display.parent():\n',
            '            display.parent().setStyleSheet(\n',
            '                "background-color: " + UIStyleHelper.COLORS[\'bg\'].name() + ";" +\n',
            '                "color: " + UIStyleHelper.COLORS[\'fg\'].name() + ";"\n',
            '            )\n'
        ]
        
        # Split content into lines for specific replacements
        lines = new_content.splitlines(True)
        
        # Replace specific line ranges
        if len(lines) >= 1381:
            lines[1334:1340] = button_container_style
            lines[1364:1374] = card_display_style
            lines[1376:1382] = parent_style
            logging.info("Fixed specific style sheets at lines 1334-1340, 1364-1374, and 1376-1382")
        else:
            logging.warning("File doesn't have enough lines for specific replacements")
        
        # Join lines back into content
        new_content = ''.join(lines)
        
        # Write the fixed content back to the file
        with open(MAIN_FILE, 'w') as f:
            f.write(new_content)
        
        logging.info("Fixed all style sheets in the file")
        return True
    
    except Exception as e:
        logging.error(f"Failed to fix style sheets: {e}")
        return False

def convert_to_name_method(match_text, style_text):
    """Convert an f-string style sheet to use name() method for colors."""
    try:
        # Split the style into lines
        style_lines = style_text.strip().split('\n')
        
        # Convert each line to use name() method
        converted_lines = []
        for line in style_lines:
            # Skip empty lines
            if not line.strip():
                continue
                
            # Look for UIStyleHelper.COLORS patterns
            if 'UIStyleHelper.COLORS' in line:
                line = line.replace('{UIStyleHelper.COLORS', '" + UIStyleHelper.COLORS').replace('}', '.name() + "')
            
            # Look for UIStyleHelper.FONTS patterns
            if 'UIStyleHelper.FONTS' in line:
                line = line.replace('{UIStyleHelper.FONTS', '" + UIStyleHelper.FONTS').replace('}', ' + "')
                
            converted_lines.append(line)
        
        # Build the new setStyleSheet call
        result = 'setStyleSheet(\n'
        for i, line in enumerate(converted_lines):
            line = line.strip()
            if i == 0:
                result += '    "' + line
            else:
                result += ' +\n    "' + line
            
            if i < len(converted_lines) - 1:
                result += ';'
            result += '"'
            
        result += '\n)'
        
        return result
    except Exception as e:
        logging.error(f"Failed to convert style: {e}")
        return match_text

def main():
    """Main function to fix all style sheets."""
    print("IBM 026 Punch Card Display - Fix All Style Sheets")
    print("------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix all style sheets
    if fix_all_style_sheets():
        print("✅ Successfully fixed all style sheets in the file")
    else:
        print("❌ Failed to fix all style sheets")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 