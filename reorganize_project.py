#!/usr/bin/env python3
"""
Project Reorganization Script for Punch Card Project
This script reorganizes files into a cleaner directory structure.
"""

import os
import shutil
import re
import glob

def ensure_directory(dir_path):
    """Ensure a directory exists, creating it if necessary."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")

def move_file(src, dest_dir):
    """Move a file to a new directory, creating the directory if needed."""
    ensure_directory(dest_dir)
    dest_path = os.path.join(dest_dir, os.path.basename(src))
    if os.path.exists(src) and not os.path.exists(dest_path):
        shutil.move(src, dest_path)
        print(f"Moved {src} -> {dest_path}")
    elif os.path.exists(dest_path):
        print(f"Skipped {src}, destination already exists")
    else:
        print(f"Skipped {src}, file not found")

def main():
    """Reorganize the project structure."""
    # Define directories to ensure exist
    directories = [
        "assets",
        "backups",
        "config",
        "docs/versions",
        "logs",
        "release_notes",
        "resources",
        "scripts/deployment",
        "scripts/maintenance",
        "scripts/animation",
        "tests/animation",
        "tests/api",
        "tests/core",
        "tests/display",
    ]
    
    # Create all required directories
    for directory in directories:
        ensure_directory(directory)
    
    # Move test files to tests directory
    test_files = []
    test_files.extend(glob.glob("*_test.py"))
    test_files.extend(glob.glob("test_*.py"))
    test_files.extend(glob.glob("*_test_*.py"))
    
    for file in test_files:
        if 'animation' in file.lower():
            move_file(file, "tests/animation")
        elif 'api' in file.lower():
            move_file(file, "tests/api")
        elif 'display' in file.lower() or 'gui' in file.lower():
            move_file(file, "tests/display") 
        else:
            move_file(file, "tests")
    
    # Move log files to logs directory
    log_files = glob.glob("*.log")
    for file in log_files:
        move_file(file, "logs")
    
    # Move backup related files
    backup_files = glob.glob("*.bak*")
    for file in backup_files:
        move_file(file, "backups")
    
    # Move configuration files to config directory
    config_files = [
        "punch_card_settings.json",
    ]
    for file in config_files:
        move_file(file, "config")
    
    # Move version documentation to docs/versions
    version_docs = glob.glob("VERSION_*.md")
    for file in version_docs:
        move_file(file, "docs/versions")
    
    # Move scripts to scripts directory
    script_files = [
        "fix_datetime.py",
        "fix_datetime2.py",
        "datetime_fix.py",
        "update_to_v0.6.6.py",
        "create_release.sh",
    ]
    for file in script_files:
        move_file(file, "scripts/maintenance")
    
    # Move animation-related scripts
    animation_scripts = [
        "animation_integration.py",
        "animation_control_panel.py",
        "simple_animation_test.py",
        "launch_animation_panel.py",
    ]
    for file in animation_scripts:
        # Only move if not already a test file (which would have been moved to tests)
        if os.path.exists(file):
            move_file(file, "scripts/animation")
    
    # Move console logs to logs directory
    console_logs = glob.glob("console_log_*.txt")
    for file in console_logs:
        move_file(file, "logs")
    
    # Handle old test_fixes_backup if it exists and isn't already empty
    if os.path.exists("test_fixes_backup") and os.listdir("test_fixes_backup"):
        ensure_directory("backups/test_fixes")
        for file in os.listdir("test_fixes_backup"):
            src = os.path.join("test_fixes_backup", file)
            dest = os.path.join("backups/test_fixes", file)
            if os.path.isfile(src) and not os.path.exists(dest):
                shutil.move(src, dest)
                print(f"Moved {src} -> {dest}")
    
    # Create a .gitignore with improved rules if it doesn't exist
    if not os.path.exists(".gitignore") or os.path.getsize(".gitignore") < 100:
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/

# Logs
logs/
*.log

# IDE specific files
.idea/
.vscode/
*.swp
*.swo

# OS specific files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
secrets/
*.bak
*.bak_save
punch_card_stats.json
"""
        with open(".gitignore", "w") as f:
            f.write(gitignore_content)
        print("Created/Updated .gitignore file")
    
    print("\nProject reorganization complete!")
    print("\nMake sure to commit these changes to git with:")
    print("git add .")
    print('git commit -m "Reorganize project structure for better organization"')
    print("git push origin Beta")

if __name__ == "__main__":
    main() 