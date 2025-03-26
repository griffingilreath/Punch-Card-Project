#!/bin/bash
# Script to update the Punch Card Project wiki content
# This script creates or updates wiki content in ~/punch_card_wiki

# Directory setup
WIKI_DIR="$HOME/punch_card_wiki"
mkdir -p "$WIKI_DIR"

# Create the Version-History.md file
echo "Creating Version-History.md..."
cat > "$WIKI_DIR/Version-History.md" << 'EOT'
# Version History

This page provides a comprehensive history of all versions of the Punch Card Project, from the latest release to the initial version.

## Recent Versions

### v0.6.5 (March 25, 2024) - GUI Default Interface
- Made the GUI the default interface when no arguments are provided
- Added clearer command-line options and documentation
- Updated usage examples to reflect new default behavior
- Improved error handling for GUI and terminal modes

### v0.6.4 (March 26, 2024) - Documentation Refinement
- Fixed README formatting and structure
- Updated hardware integration documentation with improved clarity
- Corrected file path references throughout documentation
- Improved documentation clarity with better examples
- Enhanced version history organization
- Standardized section headers for consistency
- Fixed duplicate sections
- Updated component references
- Improved code block formatting
- Enhanced readability of technical sections

### v0.6.3 (March 25, 2024) - Testing Infrastructure
- Restored and reorganized testing documentation
- Added comprehensive test suite with pytest integration
- Updated command-line interface documentation
- Improved test script organization and clarity
- Removed outdated debug mode references
- Added detailed test module descriptions
- Added pytest and pytest-cov dependencies
- Created dedicated test files for each component
- Implemented both pytest and standalone test runners
- Fixed inconsistencies in command-line arguments
- Standardized test command formats
- Enhanced test coverage reporting
- Improved code organization

### v0.6.2 (March 25, 2024) - Enhanced Character Support
- Added support for multiple character encodings
- Improved LED matrix visualization
- Enhanced error handling for hardware integration
- Updated documentation with detailed examples
- Fixed GPIO pin mapping issues
- Resolved character encoding edge cases
- Improved error messages for invalid punch patterns
- Added comprehensive hardware setup guide
- Updated installation instructions
- Expanded troubleshooting section

### v0.6.1 (March 24, 2024) - Security & Testing
- Implemented secure API key handling
- Added automated testing framework
- Enhanced error reporting
- Improved documentation clarity
- Fixed minor UI bugs

### v0.6.0 (March 24, 2024) - Major Project Reorganization
- Complete Directory Structure Reorganization
- Module-Based Architecture
- Enhanced Maintainability
- Dedicated Module Directories
- API Key Protection
- Backup File Management
- Documentation
- Clean Repository History
- Centralized Configuration
- Organized Documentation
- Legacy Code Management
- Resource Organization
- Simplified Entry Point
- Organized Backups
- Clean Project Root
- Preserved Development History

## Earlier Versions

### v0.5.9-security (March 24, 2024) - Security Enhancement
- Security Documentation
- Enhanced API Key Handling

### v0.5.9 (March 24, 2024) - Security & Bug Fixes
- Enhanced Git Security
- Security Documentation
- Visual Bug Fix

### v0.5.8 (March 24, 2024) - Enhanced Message Display
- Message Display Enhancement
- Visual Bug Fix
- Code Structure Improvements
- Switched to repaint()

### v0.5.7 (March 23, 2024) - Non-Functional Save Point
- Replaced Complex Implementation
- Working Punch Card Visualization
- Command-Line Interface
- Preserved Original Functionality
- Fixed IBM 026 Encoding
- Fixed LED Grid
- Streamlined Implementation
- Minimized Dependencies
- Command Line Options
- Testing Functions
- Character Encoding Display

### v0.5.3 (March 24, 2024) - The Branching Update
- Complete restructuring
- Properly separated modules
- Enhanced test organization
- Consolidated and archived display-related modules
- Created proper configuration and data directories
- Reduced root directory
- Moved database and JSON files
- Archived legacy and duplicate test files
- Comprehensive documentation
- Enhanced GitHub Wiki

### v0.5.2 (March 24, 2024) - Project Structure Improvements
- Reorganized code architecture
- Improved testing organization
- Better configuration management
- Streamlined data handling
- Standardized logging
- Cleaner version archiving
- Fixed duplicate files

### v0.5.1 (March 23, 2024) - Documentation Enhancements
- Comprehensive Interface Design History document
- Early Apple UI Design Language research
- EPAs 1977 Unified Visual Design System case study
- Cultural and Societal Design Trends analysis
- Design Language summary document
- Updated references in README

### v0.5.0 (March 23, 2024) - Visual Interface Overhaul
- Enhanced GUI with black-background theme
- Space Mono font
- Classic Mac-style menu bar
- Fixed button layout issues
- Improved widget visibility
- OpenAI integration
- Service status monitoring
- API console
- Keyboard shortcuts
- Improved error handling
- API key management
- Dedicated secrets directory
- Enhanced settings file structure
- Updated documentation

## Initial Versions

For earlier versions and more detailed technical changes, please see:
- [CHANGELOG.md](https://github.com/griffingilreath/Punch-Card-Project/blob/main/docs/versions/CHANGELOG.md) - Technical changelog with detailed changes
- [Release Notes](https://github.com/griffingilreath/Punch-Card-Project/blob/main/docs/versions/release_notes.md) - User-focused update notes
EOT

# Update the sidebar to include the Version History link
if [ -f "$WIKI_DIR/_Sidebar.md" ]; then
    echo "Updating _Sidebar.md to include Version History..."
    # Check if Version History is already in the sidebar
    if ! grep -q "Version-History" "$WIKI_DIR/_Sidebar.md"; then
        # Add Version History link in the Documentation section
        sed -i '' '/## Documentation/a\
- [Version History](Version-History)
' "$WIKI_DIR/_Sidebar.md"
    fi
else
    echo "Creating _Sidebar.md..."
    cat > "$WIKI_DIR/_Sidebar.md" << 'EOT'
# Wiki Navigation

## Getting Started
- [Home](Home)
- [Installation](Installation)
- [Quick Start Guide](Quick-Start-Guide)

## Documentation
- [Version History](Version-History)
- [User Guide](User-Guide)
- [API Reference](API-Reference)
- [Configuration](Configuration)

## Development
- [Contributing](Contributing)
- [Architecture](Architecture)
- [Testing](Testing)

## Research
- [Interface Design History](Interface-Design-History)
- [Punch Card Encoding](Punch-Card-Encoding)
- [LED Implementation](LED-Implementation)
- [Sociological Aspects](Sociological-Aspects)
EOT
fi

echo "Wiki content has been updated in $WIKI_DIR"
echo "To publish these changes to the GitHub wiki:"
echo "1. Clone the wiki repository (if not already done)"
echo "   git clone https://github.com/griffingilreath/Punch-Card-Project.wiki.git"
echo "2. Copy the content from $WIKI_DIR to the wiki repository"
echo "   cp -r $WIKI_DIR/* /path/to/Punch-Card-Project.wiki/"
echo "3. Commit and push the changes"
echo "   cd /path/to/Punch-Card-Project.wiki/"
echo "   git add ."
echo "   git commit -m \"Update wiki content with Version History\""
echo "   git push origin master" 