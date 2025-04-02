#!/usr/bin/env python3
"""Hard fix for datetime issues"""

with open("src/display/gui_display.py", "r") as f:
    content = f.read()

# Fix all datetime.now() calls to use datetime.datetime.now()
fixed_content = content.replace("datetime.now()", "datetime.datetime.now()")

with open("src/display/gui_display.py", "w") as f:
    f.write(fixed_content)

print("Fixed datetime now calls") 