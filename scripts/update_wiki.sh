#!/bin/bash
# Script to update the Punch Card Project wiki content
# This script creates or updates wiki content in ~/punch_card_wiki

# Directory setup
WIKI_DIR="$HOME/punch_card_wiki"
mkdir -p "$WIKI_DIR"

# Get the current version
CURRENT_VERSION=$(python3 punch_card.py --version | head -n 1 | cut -d ' ' -f 4)
echo "Detected current version: $CURRENT_VERSION"

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

# Create the _Sidebar.md file with automatic version detection
echo "Creating _Sidebar.md..."
cat > "$WIKI_DIR/_Sidebar.md" << EOT
# Navigation

* [Home](Home)

## User Guides
* [Installation Guide](Installation-Guide)
* [Usage Guide](Usage-Guide)
* [Configuration](Configuration)
* [Command Line Arguments](Command-Line-Arguments)
* [API Key Security](API-Key-Security)

## Design Research
* [Design Language Overview](Design-Language)
* [Interface Design History](Interface-Design-History)
* [Early Apple UI Design](Early-Apple-UI-Design)
* [EPA's 1977 Design System](EPA-Design-System)
* [Cultural Design Trends](Cultural-Design-Trends)
* [Punch Card Encoding](Punch-Card-Encoding)
* [Sociological Aspects](Sociological-Aspects)

## Developer Documentation
* [Project Structure](Project-Structure)
* [Git Version Control](Git-Version-Control)
* [Testing](Testing)
* [Version History](Version-History)
* [System Architecture](System-Architecture)

## Version Releases
EOT

# Add version entries to the sidebar dynamically
# This extracts version information from Version-History.md and formats it properly
grep -E "^### v[0-9]+\.[0-9]+\.[0-9]+" "$WIKI_DIR/Version-History.md" | while read -r line; do
  # Extract version number (e.g., v0.6.5)
  version=$(echo "$line" | cut -d ' ' -f 2)
  
  # Extract title (e.g., GUI Default Interface)
  title=$(echo "$line" | sed -E 's/^### v[0-9]+\.[0-9]+\.[0-9]+ \([^)]+\) - (.*)$/\1/')
  
  # Create slug for the link (e.g., v0.6.5-gui-default)
  # Remove the v from version and replace spaces with dashes in title
  version_num=$(echo "$version" | sed 's/v//')
  slug=$(echo "$title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
  page_name="v${version_num}-${slug}"
  
  # Add to the sidebar
  echo "* [$version: $title]($page_name)" >> "$WIKI_DIR/_Sidebar.md"
done

# Finish the sidebar
cat >> "$WIKI_DIR/_Sidebar.md" << 'EOT'

## Hardware
* [LED Implementation](LED-Implementation)
* [Hardware Integration](Hardware-Integration)
* [Raspberry Pi Setup](Raspberry-Pi-Setup)

## Resources
* [Version Archives](Version-Archives)
* [References](References)
* [FAQ](FAQ)
EOT

# Create System Architecture diagram page
echo "Creating System Architecture page..."
cat > "$WIKI_DIR/System-Architecture.md" << 'EOT'
# Punch Card Project: System Architecture

This page provides comprehensive diagrams and explanations of the Punch Card Project's architecture.

## Overall System Architecture

```
┌───────────────────────────────────────────────────────────────────────────┐
│                            Punch Card Project                              │
└───────────────────────────────────────────────────────────────────────────┘
                                    │
                 ┌─────────────────┬┴┬─────────────────┐
                 │                 │  │                 │
       ┌─────────▼─────────┐      │  │      ┌──────────▼───────────┐
       │       GUI         │      │  │      │    Terminal Mode     │
       │   Interface       │      │  │      │    Interface         │
       └─────────┬─────────┘      │  │      └──────────┬───────────┘
                 │                │  │                 │
                 │         ┌──────▼──▼───────┐         │
                 │         │                 │         │
                 └────────►│   Core Engine   │◄────────┘
                           │                 │
                           └────────┬────────┘
                                    │
            ┌────────────┬──────────┼──────────┬────────────┐
            │            │          │          │            │
   ┌────────▼─────┐     ┌▼────────────┐     ┌──▼────┐     ┌─▼──────────┐
   │  LED State   │     │ Punch Card  │     │ API   │     │ Hardware   │
   │  Manager     │     │ Encoder     │     │ Client│     │ Controller │
   └──────────────┘     └─────────────┘     └───────┘     └────────────┘
                                                                │
                                                         ┌──────┴───────┐
                                                         │ Physical or  │
                                                         │ Simulated    │
                                                         │ Hardware     │
                                                         └──────────────┘
```

## Component Interactions

### UI Components
The Punch Card Project offers two primary user interfaces:

1. **GUI Interface** - Interactive graphical interface with:
   - Punch card visualization
   - Input options and controls
   - Status display and feedback
   - Interactive card editing

2. **Terminal Interface** - Text-based interface with:
   - ASCII representation of punch cards
   - Command-line options
   - Test modes and diagnostics
   - Hardware integration tools

Both interfaces communicate with the Core Engine, which manages all project functionality.

### Core Components

1. **Core Engine**
   - Central coordinator of the system
   - Manages application state
   - Routes commands between components
   - Handles configuration settings
   - Manages error handling and logging

2. **LED State Manager**
   - Maintains the state of all LEDs in memory
   - Provides APIs for manipulating LED states
   - Handles transitions and animations
   - Ensures consistent state representation

3. **Punch Card Encoder**
   - Converts text to punch card patterns
   - Implements IBM 026, IBM 029, and UNIVAC encoding standards
   - Handles character validation
   - Manages encoding/decoding operations

4. **API Client**
   - Communicates with external APIs (OpenAI)
   - Handles authentication and key management
   - Manages rate limiting and error recovery
   - Processes API responses

5. **Hardware Controller**
   - Abstracts physical hardware details
   - Supports Raspberry Pi GPIO for physical LEDs
   - Provides simulation mode for testing
   - Handles hardware initialization and shutdown

## Data Flow

```
┌─────────────┐    ┌───────────┐    ┌──────────────┐    ┌─────────────┐
│  User Input  │───►│ Interface │───►│ Core Engine  │───►│  Encoder    │
└─────────────┘    └───────────┘    └──────────────┘    └──────┬──────┘
                                                               │
                                                               ▼
┌─────────────┐    ┌───────────┐    ┌──────────────┐    ┌─────────────┐
│  Output     │◄───│ Hardware  │◄───│ LED Manager  │◄───│  Card Data  │
└─────────────┘    └───────────┘    └──────────────┘    └─────────────┘
```

1. **Input Processing Flow**:
   - User provides input via GUI or Terminal
   - Interface passes commands to Core Engine
   - Core Engine validates and processes input
   - Input is encoded into punch card patterns
   - LED states are updated based on patterns
   - Hardware controller updates physical or simulated hardware

2. **External API Flow**:
   - Core Engine requests external data (if needed)
   - API Client handles authentication and requests
   - Response is processed by Core Engine
   - Results are encoded and displayed

## Module Structure

The codebase is organized into logical modules:

```
src/
├── core/               # Core functionality
│   ├── engine.py       # Central coordination
│   ├── config.py       # Configuration management
│   └── utils.py        # Core utilities
├── display/            # Display components
│   ├── gui/            # GUI interface
│   │   ├── main_window.py
│   │   ├── widgets.py
│   │   └── controllers.py
│   └── terminal/       # Terminal interface
│       ├── ui.py
│       ├── console.py
│       └── formatters.py
├── hardware/           # Hardware abstraction
│   ├── controller.py   # Hardware controller base
│   ├── led_manager.py  # LED state management
│   ├── simulator.py    # Hardware simulation
│   └── rpi.py          # Raspberry Pi implementation
├── encoding/           # Card encoding
│   ├── ibm026.py       # IBM 026 encoding
│   ├── ibm029.py       # IBM 029 encoding
│   ├── univac.py       # UNIVAC encoding
│   └── custom.py       # Custom encoding support
└── api/                # External API integration
    ├── client.py       # API client base
    ├── openai.py       # OpenAI integration
    └── key_manager.py  # API key management
```

## Testing Architecture

The project includes a comprehensive testing infrastructure:

```
tests/
├── unit/              # Unit tests
│   ├── core/          # Core component tests
│   ├── display/       # Display component tests
│   ├── hardware/      # Hardware component tests
│   └── encoding/      # Encoding component tests
├── integration/       # Integration tests
│   ├── gui_tests.py   # GUI integration
│   ├── terminal_tests.py # Terminal integration
│   └── api_tests.py   # API integration
└── e2e/               # End-to-end tests
    ├── scenarios/     # Test scenarios
    └── fixtures/      # Test data
```

## Configuration Management

Configuration is managed through a hierarchical system:

1. **Command Line Arguments** - Highest priority
2. **Environment Variables** - Second priority
3. **Configuration Files** - Third priority
4. **Default Settings** - Lowest priority

---

This architecture document will be updated as the system evolves.
EOT

echo "Wiki content has been updated in $WIKI_DIR"
echo "To publish these changes to the GitHub wiki:"
echo "1. Clone the wiki repository (if not already done)"
echo "   git clone https://github.com/griffingilreath/Punch-Card-Project.wiki.git"
echo "2. Copy the content from $WIKI_DIR to the wiki repository"
echo "   cp -r $WIKI_DIR/* /path/to/Punch-Card-Project.wiki/"
echo "3. Commit and push the changes"
echo "   cd /path/to/Punch-Card-Project.wiki/"
echo "   git add ."
echo "   git commit -m \"Update wiki content with Version History and System Architecture\""
echo "   git push origin master" 