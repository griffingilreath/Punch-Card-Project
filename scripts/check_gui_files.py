#!/usr/bin/env python3
"""
GUI File Check and Migration Utility

This script checks if all necessary GUI files are present in the clean project structure
and copies any missing files from the reference directories.
"""

import os
import sys
import shutil
from pathlib import Path
import json

# Define source and destination directories
SCRIPT_DIR = Path(__file__).parent.absolute()
SRC_DIR = SCRIPT_DIR / "src"
RESOURCES_DIR = SCRIPT_DIR / "resources"

# Reference directories
REFERENCE_DIR_053 = Path(__file__).parent.parent / "LOOK HERE Punch Card Project 0.5.3" / "Punch Card Project"
REFERENCE_DIR_CURSOR = Path(__file__).parent.parent / "Cursor" / "Punch Card Project"

# Essential files for GUI functionality
ESSENTIAL_FILES = [
    # Display modules
    {"src": "src/display/gui_display.py", "dest": "src/display/gui_display.py"},
    {"src": "src/display/display.py", "dest": "src/display/display.py"},
    {"src": "src/display/display_adapter.py", "dest": "src/display/display_adapter.py"},
    
    # Core modules
    {"src": "src/core/punch_card.py", "dest": "src/core/punch_card.py"},
    {"src": "src/core/message_generator.py", "dest": "src/core/message_generator.py"},
    
    # Utility modules
    {"src": "src/utils/gui_integration.py", "dest": "src/utils/gui_integration.py"},
    {"src": "src/utils/settings_menu.py", "dest": "src/utils/settings_menu.py"},
    
    # Main entry point
    {"src": "src/main.py", "dest": "src/main.py"},
    
    # Resources
    {"src": "src/punch_card_settings.json", "dest": "punch_card_settings.json"},
]

# Font files to check
FONTS = [
    "SpaceMono-Regular.ttf",
    "SpaceMono-Bold.ttf",
    "SpaceMono-Italic.ttf",
    "SpaceMono-BoldItalic.ttf"
]

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)

def check_file(file_info, reference_dir):
    """Check if a file exists and copy it if missing"""
    src_path = reference_dir / file_info["src"]
    dest_path = SCRIPT_DIR / file_info["dest"]
    
    # Check if the destination file exists
    if dest_path.exists():
        print(f"✅ {file_info['dest']} is present")
        return True
    
    # If destination doesn't exist but source does, copy it
    if src_path.exists():
        print(f"⚠️  {file_info['dest']} is missing - copying from reference")
        
        # Ensure the destination directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy the file
        shutil.copy2(src_path, dest_path)
        return True
    
    # Both source and destination don't exist
    print(f"❌ {file_info['dest']} is missing and not found in reference")
    return False

def check_fonts(reference_dir):
    """Check if font files are present and copy if missing"""
    font_dir = RESOURCES_DIR / "fonts"
    font_dir.mkdir(parents=True, exist_ok=True)
    
    for font in FONTS:
        dest_font = font_dir / font
        
        # Look for fonts in multiple possible locations
        possible_locations = [
            reference_dir / "fonts" / font,
            reference_dir / "resources" / "fonts" / font,
            reference_dir / "assets" / "fonts" / font,
        ]
        
        if dest_font.exists():
            print(f"✅ Font {font} is present")
            continue
            
        found = False
        for src_font in possible_locations:
            if src_font.exists():
                print(f"⚠️  Font {font} is missing - copying from reference")
                shutil.copy2(src_font, dest_font)
                found = True
                break
                
        if not found:
            print(f"❌ Font {font} is missing and not found in reference")

def check_settings_file():
    """Validate the settings file"""
    settings_path = SCRIPT_DIR / "punch_card_settings.json"
    
    if not settings_path.exists():
        print("❌ Settings file is missing")
        return
    
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        print("✅ Settings file is valid JSON")
    except json.JSONDecodeError:
        print("❌ Settings file is not valid JSON")

def main():
    """Main function to check and migrate files"""
    print_header("GUI File Check and Migration Utility")
    
    # Check if reference directories exist
    if not REFERENCE_DIR_053.exists() and not REFERENCE_DIR_CURSOR.exists():
        print("❌ No reference directories found. Cannot check or migrate files.")
        return 1
    
    # Determine which reference directory to use
    if REFERENCE_DIR_CURSOR.exists():
        print(f"Using reference directory: {REFERENCE_DIR_CURSOR}")
        reference_dir = REFERENCE_DIR_CURSOR
    else:
        print(f"Using reference directory: {REFERENCE_DIR_053}")
        reference_dir = REFERENCE_DIR_053
    
    print_header("Checking Essential Files")
    missing_files = 0
    for file_info in ESSENTIAL_FILES:
        if not check_file(file_info, reference_dir):
            missing_files += 1
    
    print_header("Checking Font Files")
    check_fonts(reference_dir)
    
    print_header("Validating Settings")
    check_settings_file()
    
    print_header("Summary")
    if missing_files == 0:
        print("All essential files are present! 🎉")
    else:
        print(f"Warning: {missing_files} essential files are missing.")
        print("Please check the output above for details.")
    
    print("\nCheckup complete.")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 