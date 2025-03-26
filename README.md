# Punch Card Project v0.6.4 - Major Project Reorganization

[![Wiki](https://img.shields.io/badge/wiki-documentation-informational)](https://github.com/griffingilreath/Punch-Card-Project/wiki)

┌──────────────────────────────────────────────────────────────────────────────────┐
│ ██████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗     ██████╗ █████╗ ██████╗ ██████╗   │
│ ██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║    ██╔════╝██╔══██╗██╔══██╗██╔══██╗  │
│ ██████╔╝██║   ██║██╔██╗ ██║██║     ███████║    ██║     ███████║██████╔╝██║  ██║  │
│ ██╔═══╝ ██║   ██║██║╚██╗██║██║     ██╔══██║    ██║     ██╔══██║██╔══██╗██║  ██║  │ 
│ ██║     ╚██████╔╝██║ ╚████║╚██████╗██║  ██║    ╚██████╗██║  ██║██║  ██║██████╔╝  │
│ ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝   │
│                                                                                  │
│ ██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████████╗                       │
│ ██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔════╝╚══██╔══╝                       │
│ ██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║        ██║                          │
│ ██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║        ██║                          │
│ ██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╗   ██║                          │
│ ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝                  v0.6.4  │
└──────────────────────────────────────────────────────────────────────────────────┘

> **⚠️ IMPORTANT API KEY SECURITY NOTICE ⚠️**
> 
> This project now includes enhanced security measures for API keys:
> 
> 1. Run the new `update_api_key.py` script to securely store your OpenAI API key
> 2. Your key will be saved in the `secrets/` directory which is **excluded from Git**
> 3. All test scripts have been updated to use this secure method
> 4. **Never commit API keys to GitHub** - the project is configured to help prevent this
>
> **If you previously had an API key in the codebase:**
> 1. Consider that key compromised and regenerate a new one
> 2. Update your key using the `update_api_key.py` script 
> 3. Only use the secure methods described in the installation section

**Status**: Beta - The Branching Update implements a comprehensive Git versioning strategy while building on v0.5.2's project organization.

**What's New in v0.6.4**

**Features**

Fixed README formatting and structure
Updated hardware integration documentation
Corrected file path references
Improved documentation clarity
Enhanced version history organization
Standardized section headers
Fixed duplicate sections
Updated component references
Improved code block formatting
Enhanced readability of technical sections

**Documentation**

Streamlined project structure documentation
Enhanced hardware integration guides
Improved code block formatting
Fixed duplicate sections
Standardized section headers
Updated file path references
Enhanced technical documentation clarity

**Organization**

Consolidated duplicate sections
Improved version history structure
Enhanced component documentation
Streamlined technical sections
Better organized project structure

**Project Overview**

This project provides a full GUI implementation of an IBM 80-column punch card system, allowing users to experiment with this historical computing technology in a modern environment. It's designed for educational purposes to help understand the foundations of computer programming and data processing.

**Features**

Interactive GUI with authentic punch card layout
Card visualization and encoding
Support for multiple character encodings
Import/export functionality
Historical reference materials
Hardware integration with LED matrix
Secure API key handling
Comprehensive testing framework

## Repository Organization

The project now uses a standardized directory structure that follows best practices for Python projects:

```
punch_card_project/
├── src/                    # Source code
│   ├── core/               # Core functionality modules
│   │   ├── punch_card.py   # Main punch card logic
│   │   ├── message_generator.py # Message generation
│   │   └── database.py     # Database interactions
│   ├── display/            # Display modules
│   │   ├── terminal_display.py  # Terminal UI
│   │   ├── gui_display.py  # GUI interface
│   │   └── display_adapter.py  # Display abstraction
│   └── utils/              # Utility functions
│       ├── settings_menu.py # Settings management
│       └── gui_integration.py # GUI utilities
├── docs/                   # Documentation
│   ├── research/           # Design research documents
│   └── technical/          # Technical documentation
├── tests/                  # Test files
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── api/                # API and external service tests
│   ├── display/            # Display and UI tests
│   └── legacy/             # Older tests kept for reference
├── config/                 # Configuration files
│   └── templates/          # Configuration templates
├── data/                   # Data storage
│   └── local/              # Local data files
├── logs/                   # Log files
├── scripts/                # Utility scripts
├── versions/               # Archive of previous versions
│   ├── 0.1.0/              # The initial version
│   ├── 0.5.0/              # The GUI Update
│   ├── 0.5.1/              # The Documentation Update
│   └── 0.5.2/              # The Reorganization Update
├── secrets/                # API keys (git-ignored)
├── simple_display.py       # Main application entry point
├── update_api_key.py       # API key management utility
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

### Versioning Strategy

The project follows a comprehensive versioning approach:

- Each version is tagged in Git with the format `v{major}.{minor}.{patch}`
- Complete snapshots of each version are preserved in the `versions/` directory
- The project follows a modified GitFlow branching strategy
- Version branches (e.g., `v0.5.3`) provide historical reference points
- The `git_version_manager.py` script in the scripts directory manages Git branches and version creation

For details on the branching strategy and version management workflow, see [VERSION_CONTROL.md](docs/VERSION_CONTROL.md).

Previous versions can be accessed by:
  1. Git tags: `git checkout v0.1.0`
  2. Version branches: `git checkout v0.5.0`
  3. Version archives: Explore the `versions/0.1.0/` directory

## What is the Punch Card Project?

This project implements a punch card system with LED integration for both simulated and physical hardware.

## Components

The project is structured around the following key components:

1. **LED State Manager** - Manages the state of LEDs in memory
2. **Hardware Controller** - Controls physical or simulated hardware
3. **Punch Card Display** - High-level API for displaying messages
4. **Display Adapter** - Connects the punch card display to hardware
5. **Terminal Display** - Provides terminal visualization of LED states

## Terminal Display Features

The terminal display provides visual feedback of LED states in two modes:

1. **Curses-based UI** - A split-screen interface showing LED grid and debug messages
2. **Fallback Console Mode** - ASCII representation of the LED grid with row/column indicators

### Character Sets

The terminal display supports multiple character sets for LED visualization:

- `default`: Filled and empty circles (█, ·)
- `block`: Filled blocks and spaces (█, space)
- `circle`: Filled and empty circles (●, ○)
- `star`: Filled and empty stars (★, ☆)
- `ascii`: ASCII characters (#, .)

You can select your preferred character set using the `--char-set` command-line argument.

### Fallback Console Mode

When the terminal window is too small or curses initialization fails, the system automatically falls back to console mode, providing:

- Row and column numbered grid display
- ASCII representation of the LED states using the selected character set
- Detailed status and debug messages
- Individual LED state change notifications (when verbose mode is enabled)

### Usage

```bash
# Run hardware verification test with star character set
python3 test_leds.py --test hardware --use-ui --char-set star

# Run animations test with verbose output (showing individual LED changes)
python3 test_leds.py --test animations --use-ui --verbose

# Run minimal LED test with ascii character set
python3 test_leds.py --test minimal --use-ui --char-set ascii

# Run all tests with circle character set
python3 test_leds.py --test all --use-ui --char-set circle
```

## Testing

Various test modes are available:

- `minimal`: A very simple test that verifies basic LED control
- `simple`: A more comprehensive test of direct LED control
- `hardware`: A test with distinctive patterns for verifying hardware visually
- `direct`: Tests direct control of LEDs through the LED state manager
- `integration`: Tests integration with the punch card display
- `animations`: Tests playing animations from JSON files
- `all`: Runs all tests in sequence

### Command Line Arguments

| Argument | Description |
|----------|-------------|
| `--test` | Test to run (`direct`, `integration`, `simple`, `minimal`, `hardware`, `animations`, `all`) |
| `--hardware-type` | Hardware type (`none`, `simulated`, `rpi`) |
| `--timeout` | Maximum time in seconds before timing out a test |
| `--use-ui` | Use the terminal UI with split-screen for LED display and debug messages |
| `--term-width` | Terminal width (only used when auto-detection fails) |
| `--term-height` | Terminal height (only used when auto-detection fails) |
| `--char-set` | Character set for LED visualization (`default`, `block`, `circle`, `star`, `ascii`) |
| `--verbose` | Print verbose output including individual LED state changes |

## Contributing

To contribute to this project:

1. Ensure all tests pass with `python3 test_leds.py --test all`
2. Add appropriate documentation for new features
3. Follow the existing code style

**Version History**

A summary of version changes is provided below. For more detailed information, see:
- [CHANGELOG.md](CHANGELOG.md) - Technical changelog with detailed changes
- [UPDATE_NOTES.md](UPDATE_NOTES.md) - User-focused update notes


v0.6.4 (Current)

Fixed README formatting and structure
Updated hardware integration documentation
Corrected file path references
Improved documentation clarity
Enhanced version history organization
Standardized section headers
Fixed duplicate sections
Updated component references
Improved code block formatting
Enhanced readability of technical sections
v0.6.3

Restored and reorganized testing documentation
Added comprehensive test suite with pytest integration
Updated command-line interface documentation
Improved test script organization and clarity
Removed outdated debug mode references
Added detailed test module descriptions
Added pytest and pytest-cov dependencies
Created dedicated test files for each component
Implemented both pytest and standalone test runners
Fixed inconsistencies in command-line arguments
Standardized test command formats
Enhanced test coverage reporting
Improved code organization
v0.6.2

Added support for multiple character encodings
Improved LED matrix visualization
Enhanced error handling for hardware integration
Updated documentation with detailed examples
Fixed GPIO pin mapping issues
Resolved character encoding edge cases
Improved error messages for invalid punch patterns
Added comprehensive hardware setup guide
Updated installation instructions
Expanded troubleshooting section
v0.6.1

Implemented secure API key handling
Added automated testing framework
Enhanced error reporting
Improved documentation clarity
Fixed minor UI bugs

### v0.6.0 (March 24, 2024) - Major Project Reorganization
- **Complete Directory Structure Reorganization**: Implemented a modern, well-organized directory structure
- **Module-Based Architecture**: Separated code into logical modules (display, api, core, animation, console)
- **Enhanced Maintainability**: Improved code organization for better maintainability and collaboration
- **Dedicated Module Directories**: Created specialized directories for each component
- **API Key Protection**: Implemented secure API key storage in the git-ignored `secrets/` directory
- **Backup File Management**: Added explicit patterns in `.gitignore` to prevent committing backup files
- **Documentation**: Added comprehensive security documentation in `SECURITY.md`
- **Clean Repository History**: Removed sensitive information from repository history
- **Centralized Configuration**: Moved all configuration files to the `config/` directory
- **Organized Documentation**: Consolidated documentation in the `docs/` directory
- **Legacy Code Management**: Preserved legacy code in a dedicated `src/legacy/` directory
- **Resource Organization**: Centralized resources in the `resources/` directory
- **Simplified Entry Point**: Created a clean main entry point at the project root (`punch_card.py`)
- **Organized Backups**: Moved all backup files to the `backups/` directory
- **Clean Project Root**: Significantly reduced clutter in the project root directory
- **Preserved Development History**: Maintained development history in an organized structure

### v0.5.9-security (March 24, 2024) - Security Enhancement
- **Security Documentation**: Added comprehensive `SECURITY.md` with API key management guidelines
- **Enhanced API Key Handling**: Improved documentation and practices for API key management

### v0.5.9 (March 24, 2024) - Security & Bug Fixes
- **Enhanced Git Security**: Updated `.gitignore` to exclude backup files that might contain API keys
- **Security Documentation**: Added comprehensive `SECURITY.md` with API key management guidelines
- **Visual Bug Fix**: Fixed issue with punch card holes not properly clearing

### v0.5.8 (March 24, 2024) - Enhanced Message Display
- **Message Display Enhancement**: Improved message display timing functionality
- **Visual Bug Fix**: Fixed issue with punch card holes display - holes now properly clear after display
- **Code Structure Improvements**: Enhanced code organization and readability
- **Switched to `repaint()`**: Changed from `update()` to `repaint()` for complete widget refresh

### v0.5.7 (March 23, 2024) - Non-Functional Save Point
- **Replaced Complex Implementation**: Simplified the main display module with a functional standalone version
- **Working Punch Card Visualization**: Successfully displays IBM 026 punch card patterns 
- **Command-Line Interface**: Preserved all command-line options from the original implementation
- **Preserved Original Functionality**: Maintains the core functionality of displaying text on punch cards
- **Fixed IBM 026 Encoding**: Properly encodes text into IBM 026 punch card format
- **Fixed LED Grid**: Proper visualization of the punch card's LED matrix
- **Streamlined Implementation**: Removed problematic code sections that caused syntax errors
- **Minimized Dependencies**: Reduced to essential PyQt6 components
- **Command Line Options**: Support for various display modes and test functions
- **Testing Functions**: Built-in tests for validating encoding accuracy
- **Character Encoding Display**: Visual representation of character-to-punch mapping 
- [IBM Documentation: "IBM Punched Card Stock Specification"](https://www.ibm.com/ibm/history/ibm100/us/en/icons/punchcard/) 
### v0.5.3 (March 24, 2024) - The Branching Update
- **Complete restructuring** of the project for optimal organization
- **Properly separated** core, display, and utility modules
- **Enhanced test organization** with specialized test directories
- **Consolidated and archived** all display-related modules
- **Created proper configuration and data directories** 
- **Reduced root directory** to only essential files
- **Moved database and JSON files** to dedicated data directory
- **Archived all legacy and duplicate test files** 
- **Comprehensive documentation** in VERSION_CONTROL.md
- **Enhanced GitHub Wiki** with improved organization and navigation

### v0.5.2 (March 24, 2024) - Project Structure Improvements
- **Reorganized code architecture**:
  - Properly separated core, display, and utility modules
  - Consolidated similar functionality
  - Enhanced import structure with proper module organization
- **Improved testing organization** with dedicated unit and integration test directories
- **Better configuration management** with centralized config directory
- **Streamlined data handling** with consolidated data storage
- **Standardized logging** with dedicated logs directory
- **Cleaner version archiving** with proper structure for previous versions
- **Fixed duplicate files** by archiving older versions

### v0.5.1 (March 23, 2024) - Documentation Enhancements
- **Comprehensive Interface Design History** document covering early computing design languages
- **Early Apple UI Design Language** research (1970s-1980s) including text-based origins and GUI evolution
- **EPA's 1977 Unified Visual Design System** case study for consistent design systems
- **Cultural and Societal Design Trends** analysis examining ASCII art, hardware design, and HCI evolution
- **Design Language summary document** acting as an index to design research resources
- **Updated references in README** with links to all research documentation

### v0.5.0 (March 23, 2024) - Visual Interface Overhaul
- **Enhanced GUI with black-background theme** for better visibility and authentic punch card aesthetic
- **Space Mono font** for consistent terminal-like appearance throughout the interface
- **Classic Mac-style menu bar** (where supported) or enhanced button toolbar with properly sized buttons
- **Fixed button layout issues** to prevent UI elements from being cut off
- **Improved widget visibility** with enhanced contrast for all UI elements
- **OpenAI integration** with model selection and prompt customization
- **Service status monitoring** for both OpenAI and fly.io connectivity
- **API console** with detailed connection information (toggle with 'C' key)
- **Keyboard shortcuts** for common functions including console visibility
- **Improved error handling** for service connectivity issues
- **API key management** with secure handling and environment variable support
- **Dedicated secrets directory** excluded from Git via .gitignore
- **Enhanced settings file structure** to prevent accidental API key exposure
- **Updated documentation** with security best practices
- [Columbia University Computing History Archive](https://www.columbia.edu/cu/computinghistory/)
- [Two-Bit History: The Punched Card Tabulator](https://twobithistory.org)
- [The Craft of Coding: Understanding Historical Computing](https://craftofcoding.wordpress.com/)
- [University of Iowa Punch Card Collection (D. Jones)](https://www.lib.uiowa.edu/sc/resources/punched-card-collections/)
- [ANSI X3.26-1970: Hollerith Punched Card Code](https://webstore.ansi.org/Standards/INCITS/ANSIINCITSAssociates1970) 

**Internal Documentation**

- [Interface Design History](/docs/research/INTERFACE_DESIGN_HISTORY.md) - Comprehensive research on early computer interface design, including:
  - Early Apple UI Design Language (1970s-1980s)
  - The EPA's 1977 Unified Visual Design System
  - Cultural and Societal Design Trends in Early Computing
- [Punch Card Encoding](/docs/research/PUNCH_CARD_ENCODING.md) - Technical details on punch card character encoding
- [LED Implementation](/docs/research/LED_IMPLEMENTATION.md) - Guide to LED matrix implementation
- [Sociological Aspects](/docs/research/SOCIOLOGICAL_ASPECTS.md) - The cultural impact of punch cards

---

<div align="center">

```
D O   N O T   F O L D   S P I N D L E   O R   M U T I L A T E
```

*Made with ❤️ by Griffin Gilreath*

</div> 
