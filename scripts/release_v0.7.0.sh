#!/bin/bash
# Release v0.7.0 to the testing branch

# Make sure we're in the project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

echo "===== Releasing v0.7.0 to testing branch ====="

# Check if we're on the main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Warning: You are not on the main branch. Current branch: $CURRENT_BRANCH"
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborting release process."
        exit 1
    fi
fi

# Create a new testing branch
git checkout -b testing-v0.7.0

# Add all files
git add .

# Commit with version message
git commit -m "v0.7.0: Component Architecture Refactoring
- Extracted all UI components into separate modules
- Added energy usage tracking
- Renamed gui_display.py to main_window.py
- Created components directory structure
- Improved maintainability and reduced code duplication"

# Create a version tag
git tag -a v0.7.0 -m "Version 0.7.0 - Component Architecture Refactoring"

echo "===== v0.7.0 has been committed to the testing-v0.7.0 branch ====="
echo "You can now push this branch to the remote repository with:"
echo "  git push -u origin testing-v0.7.0"
echo "  git push origin v0.7.0" 