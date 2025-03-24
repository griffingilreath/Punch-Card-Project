#!/usr/bin/env python3
import sys
import os

# File to fix
FILE_PATH = 'simple_display.py'
BACKUP_PATH = 'simple_display.py.bak_try_except'

# Create backup
with open(FILE_PATH, 'r') as f:
    original_content = f.read()

with open(BACKUP_PATH, 'w') as f:
    f.write(original_content)
print(f"Created backup at {BACKUP_PATH}")

# Read file line by line
with open(FILE_PATH, 'r') as f:
    lines = f.readlines()

# Fix the try-except block at line 518
if len(lines) >= 525:
    # Find the start of the try block
    try_line = None
    for i in range(510, 520):
        if 'try:' in lines[i]:
            try_line = i
            print(f"Found try statement at line {i+1}")
            break
    
    if try_line is not None:
        # Check for the completion line that should be inside the try block
        completion_line = None
        for i in range(try_line + 1, try_line + 10):
            if 'completion =' in lines[i]:
                completion_line = i
                print(f"Found completion statement at line {i+1}")
                break
        
        if completion_line is not None:
            # Fix the indentation to make it part of the try block
            # We need to indent the completion line and all related lines
            start_line = completion_line
            end_line = completion_line
            
            # Find where the completion block ends
            for i in range(completion_line + 1, completion_line + 10):
                if i >= len(lines):
                    break
                if ')' in lines[i] and not lines[i].strip().startswith('#'):
                    end_line = i
                    print(f"Found end of completion block at line {i+1}")
                    break
            
            # Fix indentation for these lines
            for i in range(start_line, end_line + 1):
                # Get the current indentation
                current_indent = len(lines[i]) - len(lines[i].lstrip())
                
                # Add 4 spaces to ensure it's inside the try block
                if current_indent < 12:  # Assuming try block is at indent level 8
                    lines[i] = ' ' * 12 + lines[i].lstrip()
                    print(f"Fixed indentation at line {i+1}")
            
            # Search for a matching except block
            except_found = False
            for i in range(end_line + 1, end_line + 10):
                if i >= len(lines):
                    break
                if 'except' in lines[i] and ':' in lines[i]:
                    except_found = True
                    print(f"Found existing except block at line {i+1}")
                    break
            
            # If no except block found, add one
            if not except_found:
                # Add an except block after the completion block
                except_line = "        except Exception as e:\n"
                except_body = "            debug_log(f\"OpenAI API error: {e}\", \"error\")\n"
                except_body2 = "            return None\n"
                
                lines.insert(end_line + 1, "\n")
                lines.insert(end_line + 2, except_line)
                lines.insert(end_line + 3, except_body)
                lines.insert(end_line + 4, except_body2)
                print(f"Added missing except block after line {end_line+1}")

# Write back to file
with open(FILE_PATH, 'w') as f:
    f.writelines(lines)

print(f"Fixed try-except block in {FILE_PATH}")
print("Done!") 