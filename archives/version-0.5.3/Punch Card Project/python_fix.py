#!/usr/bin/env python3
import sys
import os
import re

# File to fix
FILE_PATH = 'simple_display.py'
BACKUP_PATH = 'simple_display.py.bak_python'

# Create backup
with open(FILE_PATH, 'r') as f:
    original_content = f.read()

with open(BACKUP_PATH, 'w') as f:
    f.write(original_content)
print(f"Created backup at {BACKUP_PATH}")

# Read file line by line
with open(FILE_PATH, 'r') as f:
    lines = f.readlines()

# Fix indentation around line 463
if len(lines) >= 470:
    # Check the specific area around line 463
    if 'return False' in lines[462] and lines[462].startswith('    '):
        lines[462] = 'return False\n'
        print(f"Fixed indentation at line 463")

# Check and fix other areas that might have indentation issues - more general approach
fixed_lines = []

# Track indentation level changes
current_level = 0
for i, line in enumerate(lines):
    # Skip empty lines
    if not line.strip():
        fixed_lines.append(line)
        continue

    # Calculate current indentation
    indent = len(line) - len(line.lstrip())
    
    # Check for indentation decreases that are not in multiples of 4
    if indent < current_level and (current_level - indent) % 4 != 0:
        # This is likely an indentation error
        # Adjust to the appropriate indentation level
        expected_indent = max(0, current_level - 4 * ((current_level - indent + 3) // 4))
        
        # Only fix if the indentation is unexpected and the line is not starting a new block
        if not any(line.strip().startswith(s) for s in ['def ', 'class ', 'if ', 'else:', 'elif ', 'try:', 'except ', 'finally:']):
            # This is likely a continuation line with wrong indentation
            new_line = ' ' * expected_indent + line.lstrip()
            print(f"Fixed indentation at line {i+1}: {line.strip()}")
            fixed_lines.append(new_line)
            current_level = expected_indent
            continue

    # Update current_level for next iteration
    if line.strip().endswith(':'):
        # This line starts a new block, so increase indentation level
        current_level = indent + 4
    elif indent < current_level:
        # We've decreased indentation
        current_level = indent

    # Keep the line unchanged
    fixed_lines.append(line)

# Write the fixed content back to the file
with open(FILE_PATH, 'w') as f:
    f.writelines(fixed_lines)

print(f"Fixed indentation issues in {FILE_PATH}")
print("Done!") 