#!/usr/bin/env python3
"""
Fix datetime import issues in gui_display.py
"""

import os
import sys
import re

def fix_datetime_imports():
    """
    Fix datetime import issues in gui_display.py by:
    1. Removing duplicate imports
    2. Standardizing datetime usage
    """
    file_path = os.path.join('src', 'display', 'gui_display.py')
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = file_path + '.bak'
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Fix imports - make sure we only have one datetime import style
    # and it's the correct one
    content = re.sub(r'from datetime import datetime\s*', '', content)
    content = re.sub(r'import datetime\s*', '', content)
    
    # Add the correct import at the top (after other imports but before code)
    import_line = 'from datetime import datetime\n'
    import_section_end = content.find('try:')
    if import_section_end == -1:
        # If we can't find the try block, just add it near the top
        import_section_end = content.find('import')
        content = content[:import_section_end] + import_line + content[import_section_end:]
    else:
        content = content[:import_section_end] + import_line + content[import_section_end:]
    
    # Fix all datetime.now() calls
    content = content.replace('datetime.now()', 'datetime.now()')
    
    # Save the modified file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Successfully fixed datetime imports in {file_path}")
    return True

if __name__ == "__main__":
    print("Fixing datetime import issues...")
    if fix_datetime_imports():
        print("Done!")
    else:
        print("Failed to fix datetime imports")
        sys.exit(1) 