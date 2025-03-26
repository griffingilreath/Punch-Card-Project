#!/bin/bash
# Project Reorganization Script
# This script consolidates the Punch Card Project files into a clean, organized structure

# Exit on any error
set -e

echo "========================================================"
echo "  Punch Card Project - File Reorganization Script"
echo "========================================================"
echo
echo "This script will organize your project files into a clean structure."
echo "Original files will not be deleted until you confirm everything works."
echo

# Create main project directory
MAIN_PROJECT_DIR=~/Documents/Coding/PunchCardProject
CLEAN_PROJECT_DIR=~/Documents/Coding/PunchCardProject-Clean
CURSOR_PROJECT_DIR=~/Documents/Coding/Cursor/"Punch Card Project"
REF_PROJECT_DIR=~/Documents/Coding/"LOOK HERE Punch Card Project 0.5.3"

# Ask for confirmation before proceeding
read -p "Create new project structure at $MAIN_PROJECT_DIR? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operation canceled."
    exit 1
fi

# Step 1: Create the main project folder
echo
echo "Step 1: Creating main project folder..."
mkdir -p "$MAIN_PROJECT_DIR"

# Step 2: Copy the clean project structure
echo
echo "Step 2: Copying clean project structure..."
cp -R "$CLEAN_PROJECT_DIR"/* "$MAIN_PROJECT_DIR"/
cp -R "$CLEAN_PROJECT_DIR"/.git "$MAIN_PROJECT_DIR"/
echo "Project structure copied."

# Step 3: Create an archive directory and copy reference files
echo
echo "Step 3: Archiving previous versions..."
mkdir -p "$MAIN_PROJECT_DIR/archives"

if [ -d "$CURSOR_PROJECT_DIR/versions" ]; then
    echo "Copying version archives..."
    cp -R "$CURSOR_PROJECT_DIR/versions" "$MAIN_PROJECT_DIR/archives/"
fi

if [ -d "$REF_PROJECT_DIR" ]; then
    echo "Archiving version 0.5.3..."
    mkdir -p "$MAIN_PROJECT_DIR/archives/version-0.5.3"
    cp -R "$REF_PROJECT_DIR"/* "$MAIN_PROJECT_DIR/archives/version-0.5.3/"
fi

# Step 4: Clean up temporary files
echo
echo "Step 4: Removing temporary files..."
find "$MAIN_PROJECT_DIR" -name "__pycache__" -type d -exec rm -rf {} +
find "$MAIN_PROJECT_DIR" -name "*.pyc" -type f -delete
find "$MAIN_PROJECT_DIR" -name ".DS_Store" -type f -delete

# Step 5: Create a backup of old directories (optional)
echo
echo "Step 5: Creating backup of old directories..."
echo "This will create a ZIP backup at ~/Documents/Coding/punch_card_old_backup.zip"
read -p "Create backup? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    zip -r ~/Documents/Coding/punch_card_old_backup.zip "$CURSOR_PROJECT_DIR" "$REF_PROJECT_DIR"
    echo "Backup created."
else
    echo "Skipping backup."
fi

# Summary
echo
echo "========================================================"
echo "  Reorganization Complete!"
echo "========================================================"
echo
echo "Your project has been organized at: $MAIN_PROJECT_DIR"
echo
echo "Next steps:"
echo "1. Configure your IDE to use the new project folder"
echo "2. Verify that everything works correctly"
echo "3. Use the 'testing' branch for active development"
echo
echo "After confirming everything works, you can safely remove"
echo "the original project files if desired."
echo "========================================================" 