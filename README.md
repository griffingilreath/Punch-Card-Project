# Punch Card Project

[![Current Version](https://img.shields.io/badge/version-0.6.4-blue.svg)](https://github.com/griffingilreath/Punch-Card-Project/releases/tag/v0.6.4)

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

A implementation of the IBM 80-column punch card system for a fine art object.

> **⚠️ IMPORTANT API KEY SECURITY NOTICE ⚠️**
> 
> This project includes enhanced security measures for API keys:
> 
> 1. Run the `update_api_key.py` script to securely store your OpenAI API key
> 2. Your key will be saved in the `secrets/` directory which is **excluded from Git**
> 3. All test scripts have been updated to use this secure method
> 4. **Never commit API keys to GitHub** - the project is configured to help prevent this
>
> **If you previously had an API key in the codebase:**
> 1. Consider that key compromised and regenerate a new one
> 2. Update your key using the `update_api_key.py` script 
> 3. Only use the secure methods described in the installation section

## What's New in v0.6.4

### Features
- Fixed README formatting and structure
- Updated hardware integration documentation
- Corrected file path references
- Improved documentation clarity
- Enhanced version history organization
- Standardized section headers
- Fixed duplicate sections
- Updated component references
- Improved code block formatting
- Enhanced readability of technical sections

### Documentation
- Streamlined project structure documentation
- Enhanced hardware integration guides
- Improved code block formatting
- Fixed duplicate sections
- Standardized section headers
- Updated file path references
- Enhanced technical documentation clarity

### Organization
- Consolidated duplicate sections
- Improved version history structure
- Enhanced component documentation
- Streamlined technical sections
- Better organized project structure

## Project Overview

This project provides a full GUI implementation of an IBM 80-column punch card system, allowing users to experiment with this historical computing technology in a modern environment. It's designed for educational purposes to help understand the foundations of computer programming and data processing.

```
┌─────────────────────────────── PUNCH CARD GUI UPDATE ────────────────────────────────┐
│ ┌──────────┐ ┌───────────────────────────────────────────────────────────────┐ ┌───┐ │
│ │   Menu   │ │                                                               │ │ × │ │
│ └──────────┘ └───────────────────────────────────────────────────────────────┘ └───┘ │
│ ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│ │                                                                                  │ │
│ │  ████████  ███████  ████████ ██    ██    ███    ██    ██  ███████   █████  ████  │ │
│ │     ██     ██    ██    ██    ██    ██   ██ ██   ██    ██  ██       ██   ██ ██ █  │ │
│ │     ██     ██    ██    ██    ██    ██  ██   ██  ██    ██  █████    ███████ ██ █  │ │
│ │     ██     ██    ██    ██    ██    ██ █████████ ██    ██  ██       ██   ██ ██ █  │ │
│ │     ██      ██████     ██     ██████  ██     ██  ██████   ███████  ██   ██ ████  │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
│ ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌────────────────┐   ┌────────────────┐ │
│ │ Settings │   │  OpenAI  │   │ Database │   │ Toggle Console │   │Black Background│ │
│ └──────────┘   └──────────┘   └──────────┘   └────────────────┘   └────────────────┘ │
│                                                                                      │
│ ┌──────────────────────────────────── CONSOLE ─────────────────────────────────────┐ │
│ │ [21:45:32] API initialized                                                       │ │
│ │ [21:45:33] OpenAI connection: ONLINE                                             │ │
│ │ [21:45:34] Service status: All systems operational                               │ │
│ │ [21:45:35] Press 'C' to toggle console visibility                                │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

## Features

- Interactive GUI with authentic punch card layout
- Card visualization and encoding
- Support for multiple character encodings
- Import/export functionality
- Historical reference materials

## Repository Organization

The project now uses a standardized directory structure that follows best practices for Python projects:

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
├── logs/                   # Log files
├── scripts/                # Utility scripts
├── versions/               # Archive of previous versions
│   ├── 0.1.0/              # The initial version
│   ├── 0.5.0/              # The GUI Update
│   ├── 0.5.1/              # The Documentation Update
│   └── 0.5.2/              # The Reorganization Update
├── secrets/                # API keys (git-ignored)
├── run.py                  # Main application entry point
├── update_api_key.py       # API key management utility
├── requirements.txt        # Python dependencies
└── README.md               # This file


## Installation

1. Clone the repository:
```bash
git clone https://github.com/griffingilreath/Punch-Card-Project.git
cd Punch-Card-Project
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your API key (if using OpenAI integration):
```bash
python update_api_key.py
```

5. Run the tests to verify installation:
```bash
python -m pytest tests/
```

## Usage

### Basic Operation

1. Start the application:
```bash
python run.py
```

2. Run tests to verify functionality:
```bash
python -m pytest tests/
```

### Advanced Features

#### Testing Hardware Integration

Test LED matrix:
```bash
python test_leds.py --test pattern
```

Test GUI components:
```bash
python test_gui.py
```

Test character encoding:
```bash
python test_encoding.py
```

#### Hardware Control

The hardware control functionality is implemented in the `src/core/hardware_controller.py` module. See the documentation in that file for detailed usage instructions.

## 🔌 Hardware Integration

### Simulated Hardware

By default, the system uses a simulated hardware controller for development and testing. This simulates the behavior of physical LEDs in the terminal.

### Raspberry Pi GPIO Integration

For physical LED matrix integration, the system includes a Raspberry Pi GPIO controller that maps LED states to physical pins:

```bash
# Run on Raspberry Pi with physical LEDs
python test_leds.py --test hardware --hardware-type rpi
```

See the `RPiHardwareController` class in `src/core/hardware_controller.py` for details on pin mapping and configuration.

### LED Matrix Configuration

The LED matrix is arranged in a 12x80 grid to match the standard IBM punch card layout:

```
LED Matrix Layout (12 rows × 80 columns)
┌────────────────────────────────────────────┐
│ Row 12 (Zone Punch)      ○ ○ ○ ○ ○ ○ ... ○ │
│ Row 11 (Zone Punch)      ○ ○ ○ ○ ○ ○ ... ○ │
│ Row 0  (Zone Punch)      ○ ○ ○ ○ ○ ○ ... ○ │
│ Row 1  (Digit)           ○ ○ ○ ○ ○ ○ ... ○ │
│ Row 2  (Digit)           ○ ○ ○ ○ ○ ○ ... ○ │
│ Row 3  (Digit)           ○ ○ ○ ○ ○ ○ ... ○ │
│ Row 4  (Digit)           ○ ○ ○ ○ ○ ○ ... ○ │
│ Row 5  (Digit)           ○ ○ ○ ○ ○ ○ ... ○ │
│ Row 6  (Digit)           ○ ○ ○ ○ ○ ○ ... ○ │
│ Row 7  (Digit)           ○ ○ ○ ○ ○ ○ ... ○ │
│ Row 8  (Digit)           ○ ○ ○ ○ ○ ○ ... ○ │
│ Row 9  (Digit)           ○ ○ ○ ○ ○ ○ ... ○ │
└────────────────────────────────────────────┘
   Col: 1 2 3 4 5 6 ... 80
```

### GPIO Pinout

The Raspberry Pi GPIO pins are mapped as follows:

```
GPIO Pin Mapping
┌─────────┬────────────┬───────────────────┐
│ Purpose │ GPIO Pins  │     Function      │
├─────────┼────────────┼───────────────────┤
│ Data    │ 2-13       │ LED Matrix Data   │
│ Clock   │ 14         │ Shift Register    │
│ Latch   │ 15         │ Data Latch        │
│ Enable  │ 18         │ Output Enable     │
└─────────┴────────────┴───────────────────┘
```

### Hardware Components

Required components for physical implementation:
- Raspberry Pi (3B+ or newer recommended)
- 12x80 LED Matrix (960 LEDs total)
- Shift Registers (74HC595 or similar)
- Current-limiting resistors
- 5V power supply

See the `src/core/hardware_controller.py` class for detailed implementation.

## Components

The project is structured around the following key components:

- **LED State Manager**: Manages the state of LEDs in memory
- **Hardware Controller**: Controls physical or simulated hardware
- **Punch Card Display**: High-level API for displaying messages
- **Display Adapter**: Connects the punch card display to hardware
- **Terminal Display**: Provides terminal visualization of LED states

## Historical Context

    ┌────────────────────────────────────────────────────────────────────────────────┐
 12 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
 11 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  0 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  1 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  2 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  3 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  4 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  5 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  6 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  7 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  8 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  9 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
    └────────────────────────────────────────────────────────────────────────────────┘
     012345678901234567890123456789012345678901234567890123456789012345678901234567890
     1         2         3         4         5         6         7         8

IBM's 80-column punch cards were a revolutionary data storage medium that dominated computing from the 1920s through the 1970s. Each card measured precisely 7⅜ × 3¼ inches (187mm × 82.5mm) and featured:

- 80 columns for character storage (numbered 1-80 from left to right)
- 12 punch positions per column (rows 12, 11, 0-9 from top to bottom)
- A clipped corner for orientation (typically upper-left on IBM cards)
- Rectangular holes (~1mm × 3mm) introduced in 1928 for tighter spacing

Each character was encoded using specific hole patterns (Hollerith code), with:

Letters A-I: Zone punch in row 12 + digit rows 1-9
Letters J-R: Zone punch in row 11 + digit rows 1-9
Letters S-Z: Zone punch in row 0 + digit rows 2-9
Digits 0-9: Single punch in respective rows
Special characters: Various combinations of punches
Character codes varied slightly between systems (FORTRAN vs. Commercial/Symbolic), with later standards like EBCDIC expanding the character set while maintaining backward compatibility.

> 💭 **Fun Fact**: The phrase "Do not fold, spindle, or mutilate" became a cultural touchstone of the punch card era. The term "spindle" referred to a spike often found at retail counters where receipts and papers were impaled for storage. Punch cards were processed by machines that required intact, undamaged cards - hence the warning!


🔌 Hardware Integration

Simulated Hardware

By default, the system uses a simulated hardware controller for development and testing. This simulates the behavior of physical LEDs in the terminal.

Raspberry Pi GPIO Integration

For physical LED matrix integration, the system includes a Raspberry Pi GPIO controller that maps LED states to physical pins:

# Run on Raspberry Pi with physical LEDs
python test_leds.py --test hardware --hardware-type rpi
See the RPiHardwareController class in hardware_controller.py for details on pin mapping and configuration.

🔐 API Key Security

The project now includes enhanced security for API keys with v0.5.0:

A dedicated secrets/ directory that is excluded from git via .gitignore
Secure lookup hierarchy that prioritizes the safest storage methods:
First checks the secrets/api_keys.json file
Then falls back to environment variables
Only uses settings file as a last resort
The new update_api_key.py script for securely updating your API key
Clear instructions in secrets/README.md for proper key management
Additional .gitignore rules to prevent accidental commits of sensitive data
Important: Never commit real API keys to GitHub. The project is configured to help prevent this, but always double-check your commits to ensure sensitive data isn't included.

### Common Issues

1. LED Matrix Not Responding
   - Check GPIO connections
   - Verify power supply
   - Test with `test_leds.py --test hardware`

2. Encoding Errors
   - Verify character support
   - Check encoding configuration
   - Run validation tests

3. GUI Issues
   - Update dependencies
   - Check system requirements
   - Clear cache files

## Version History

### v0.6.4 (Current)
- Fixed README formatting and structure
- Updated hardware integration documentation
- Corrected file path references
- Improved documentation clarity
- Enhanced version history organization
- Standardized section headers
- Fixed duplicate sections
- Updated component references
- Improved code block formatting
- Enhanced readability of technical sections

### v0.6.3
- Restored comprehensive testing documentation
- Added pytest integration for automated testing
- Enhanced code organization and structure
- Improved documentation clarity and completeness
- Fixed version tracking and release management
- Added automated version update system
- Restored historical context and usage examples
- Enhanced hardware integration documentation
- Improved project structure documentation
- Added comprehensive reference materials

### v0.6.2
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

### v0.6.1
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
- Documentation Improvements
- Clean Repository History
- Centralized Configuration
- Organized Documentation
- Legacy Code Management
- Resource Organization
- Simplified Entry Point
- Organized Backups
- Clean Project Root
- Preserved Development History

### v0.5.9-security (March 24, 2024)
- Security Documentation
- Enhanced API Key Handling

### v0.5.9 (March 24, 2024)
- Enhanced Git Security
- Security Documentation
- Visual Bug Fixes

### v0.5.8 (March 24, 2024)
- Message Display Enhancement
- Visual Bug Fixes
- Code Structure Improvements

### v0.5.7 (March 23, 2024)
- Replaced Complex Implementation
- Working Punch Card Visualization
- Command-Line Interface
- Preserved Original Functionality
- Fixed IBM 026 Encoding
- Fixed LED Grid
- Streamlined Implementation
- Minimized Dependencies
- Testing Functions
- Character Encoding Display
- IBM Documentation

### v0.5.3 (March 24, 2024) - The Branching Update
- Complete restructuring of the project
- Properly separated core, display, and utility modules
- Enhanced test organization
- Consolidated and archived display modules
- Created proper configuration and data directories
- Reduced root directory to essential files
- Moved database and JSON files
- Archived legacy and duplicate test files
- Comprehensive documentation
- Enhanced GitHub Wiki

### v0.5.2 (March 24, 2024) - The Reorganization Update
- Reorganized code architecture
- Properly separated core, display, and utility modules
- Consolidated similar functionality
- Enhanced import structure
- Improved testing organization
- Better configuration management
- Streamlined data handling
- Standardized logging
- Cleaner version archiving
- Fixed duplicate files

### v0.5.1 (March 23, 2024) - The Documentation Update
- Added comprehensive Interface Design History
- Created research on Early Apple UI Design Language
- Added EPA's 1977 Unified Visual Design System case study
- Documented Cultural and Societal Design Trends
- Created Design Language index document
- Updated references
- Expanded design language foundations

### v0.5.0 (March 23, 2024) - The GUI Update
- Enhanced GUI with black-background theme
- Implemented OpenAI integration
- Added real-time service status monitoring
- Created API console
- Implemented classic Mac-style menu bar
- Standardized on Space Mono font
- Added keyboard shortcuts
- Fixed button layout issues
- Improved error handling
- Enhanced API key security
- Added service status indicators

### v0.1.1 (2024-08-12) - The Visualization Update
- Enhanced terminal display
- Improved fallback console mode
- Added verbose mode
- Resolved synchronization issues
- Improved error handling
- Added command-line arguments

### v0.1.0 (2024-06-15) - The Renaissance Update
- Improved project structure
- Added comprehensive research documentation
- Enhanced hardware implementation guides
- Consolidated technical specifications
- Added message animation patterns

### v0.0.1 (2024-03-17) - The Primordial Release
- Basic punch card display
- Test message support
- Statistics tracking
- Random sentence generation
- OpenAI integration
- Diagnostic logging
- Added DOS mode easter egg

## References and Resources

### Historical Documentation
- [IBM Punch Card Systems Manual](https://archive.org/details/ibm-manuals)
- [Early Computing Archive](https://www.computerhistory.org/collections/punch-cards/)
- [Hollerith Machine Documentation](https://www.census.gov/history/hollerith.html)

### Technical Resources
- [IBM 80-Column Card Codes](https://www.ibm.com/support/pages/punched-card-codes)
- [EBCDIC Reference](https://www.ibm.com/docs/en/zos-basic-skills?topic=ebcdic-ascii-character-sets)
- [Punch Card Design Specifications](https://www.computerhistory.org/collections/catalog/102646121)

### Academic Papers
- "The Evolution of Punch Card Programming" (Computer History Review, 2019)
- "Impact of Early Data Processing Methods" (IEEE Annals, 2020)
- "Hollerith's Electric Tabulating System" (Technology Review, 2018)

### Related Projects
- [Virtual Punch Card Reader](https://github.com/virtual-punch-reader)
- [Punch Card Emulator](https://github.com/punch-emulator)
- [Historical Computing Tools](https://github.com/historical-computing)

### Design Guidelines
- [IBM Hardware Interface Standards](https://www.ibm.com/design/standards)
- [Punch Card Manufacturing Specs](https://www.nist.gov/standards/punch-cards)
- [LED Matrix Design Patterns](https://www.led-guidelines.org)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Project Status

Active development - see [CHANGELOG.md](CHANGELOG.md) for updates.

---

<div align="center">
D O   N O T   F O L D   S P I N D L E   O R   M U T I L A T E
Made with ❤️ by Griffin Gilreath
</div>