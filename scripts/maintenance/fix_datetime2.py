#!/usr/bin/env python3
"""
Fix datetime issues in gui_display.py
"""
import fileinput
import sys
import re
import os

def fix_imports():
    """Fix the imports at the top of the file"""
    with open("src/display/gui_display.py", 'r') as file:
        content = file.read()
    
    # Remove the existing datetime imports
    content = re.sub(r'from datetime import datetime\s*', '', content)
    content = re.sub(r'import datetime\s*', '', content)
    
    # Add the correct import after other imports
    import_insertion_point = content.find("import threading")
    if import_insertion_point > 0:
        new_content = (
            content[:import_insertion_point + len("import threading")] + 
            "\nfrom datetime import datetime  # Fixed import" +
            content[import_insertion_point + len("import threading"):]
        )
        
        with open("src/display/gui_display.py", 'w') as file:
            file.write(new_content)
        
        print("Fixed datetime imports")
        return True
    else:
        print("Couldn't find the right place to insert the import")
        return False

def fix_usage():
    """Fix the datetime.now() usage"""
    replacement_count = 0
    
    with fileinput.FileInput("src/display/gui_display.py", inplace=True, backup='.bak4') as file:
        for line in file:
            if "datetime.now()" in line:
                new_line = line.replace("datetime.now()", "datetime.now()")
                print(new_line, end='')
                replacement_count += 1
            else:
                print(line, end='')
    
    print(f"Fixed {replacement_count} datetime.now() usages")
    return replacement_count > 0

def main():
    """Main function"""
    if not os.path.exists("src/display/gui_display.py"):
        print("Error: src/display/gui_display.py not found")
        return False
    
    # Make a backup
    os.system("cp src/display/gui_display.py src/display/gui_display.py.original_backup")
    print("Created backup at src/display/gui_display.py.original_backup")
    
    # Fix the imports
    if not fix_imports():
        return False
    
    # Fix the usage
    if not fix_usage():
        return False
    
    return True

if __name__ == "__main__":
    print("Fixing datetime issues in gui_display.py...")
    if main():
        print("Successfully fixed datetime issues!")
    else:
        print("Failed to fix datetime issues")
        sys.exit(1) 