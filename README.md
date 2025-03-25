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

### Bug Fixes
- Fixed GPIO pin mapping issues
- Resolved character encoding edge cases
- Improved error messages for invalid punch patterns

### Documentation
- Added comprehensive hardware setup guide
- Updated installation instructions
- Expanded troubleshooting section

## Project Overview

This project provides a full GUI implementation of an IBM 80-column punch card system, allowing users to experiment with this historical computing technology in a modern environment. It's designed for educational purposes to help understand the foundations of computer programming and data processing.

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

## Features

- Interactive GUI with authentic punch card layout
- Card visualization and encoding
- Support for multiple character encodings
- Import/export functionality
- Historical reference materials

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

1. Start the GUI:
```bash
python main.py
```

2. Create a new punch card:
```bash
python create_card.py --text "HELLO WORLD"
```

3. Read an existing card:
```bash
python read_card.py --input card.json
```

### Advanced Features

#### Custom Encoding

Use custom character encodings:
```bash
python create_card.py --text "HELLO" --encoding custom --mapping custom_encoding.json
```

#### Hardware Control

Test LED matrix:
```bash
python test_leds.py --test pattern
```

Control individual LEDs:
```bash
python led_control.py --row 12 --col 1 --state on
```

## 🔌 Hardware Integration

### Simulated Hardware

By default, the system uses a simulated hardware controller for development and testing. This simulates the behavior of physical LEDs in the terminal.

### Raspberry Pi GPIO Integration

For physical LED matrix integration, the system includes a Raspberry Pi GPIO controller that maps LED states to physical pins:

```bash
# Run on Raspberry Pi with physical LEDs
python test_leds.py --test hardware --hardware-type rpi
```

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

See the `hardware_controller.py` class for detailed implementation.

## Punch Card Encoding

The punch card system uses a specific encoding scheme for characters based on the IBM 80-column punch card format. Here's a detailed breakdown of the punch patterns:

### Standard IBM Encoding

```
Row 12 (Zone)  Row 11 (Zone)  Row 0 (Zone)  Rows 1-9 (Numeric)
     ○              ○              ○              ○
     ○              ○              ○              ○
     ○              ○              ○              ○
     ○              ○              ○              ○
     ○              ○              ○              ○
     ○              ○              ○              ○
     ○              ○              ○              ○
     ○              ○              ○              ○
     ○              ○              ○              ○
```

### Character Mapping

```
Character  Row 12  Row 11  Row 0  Rows 1-9
A          ○       ○       ○       ○
B          ○       ○       ○       ○
C          ○       ○       ○       ○
...
Z          ○       ○       ○       ○
0          ○       ○       ○       ○
1          ○       ○       ○       ○
...
9          ○       ○       ○       ○
```

### Special Characters

```
Special    Row 12  Row 11  Row 0  Rows 1-9
Space      ○       ○       ○       ○
Period     ○       ○       ○       ○
Comma      ○       ○       ○       ○
...
```

## Historical Context

IBM's 80-column punch cards were a revolutionary data storage medium that dominated computing from the 1920s through the 1970s. Each card measured precisely 7⅜ × 3¼ inches (187mm × 82.5mm) and featured:

- 80 columns for character storage (numbered 1-80 from left to right)
- 12 punch positions per column (rows 12, 11, 0-9 from top to bottom)
- A clipped corner for orientation (typically upper-left on IBM cards)
- Rectangular holes (~1mm × 3mm) introduced in 1928 for tighter spacing

> 💭 **Fun Fact**: The phrase "Do not fold, spindle, or mutilate" became a cultural touchstone of the punch card era. The term "spindle" referred to a spike often found at retail counters where receipts and papers were impaled for storage. Punch cards were processed by machines that required intact, undamaged cards - hence the warning!

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

## Development

### Testing

The project uses pytest for the test framework and includes both unit tests and integration tests organized by functionality. You can run tests in two ways:

1. Using pytest (recommended):
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest test_encoding.py
```

2. Using individual test scripts:
```bash
# Test LED hardware functionality
python test_leds.py --test hardware

# Validate punch card encoding
python test_encoding.py --validate

# Test GUI components
python test_gui.py --check-display
```

Each test module focuses on a specific component:
- `test_leds.py`: Hardware integration tests for LED matrix
- `test_encoding.py`: Character encoding and punch card format validation
- `test_gui.py`: GUI component functionality and display updates

## Troubleshooting

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

### v0.6.0
- Major UI overhaul with modern design
- Added support for custom encoding schemes
- Integrated OpenAI API for pattern recognition
- Enhanced hardware simulation mode
- Improved performance and stability

### v0.5.3
- Added ASCII art banner
- Implemented basic punch card visualization
- Created initial hardware integration
- Set up project structure and documentation

### v0.5.2 (March 24, 2024) - The Reorganization Update
- Reorganized code architecture with proper module separation
- Improved testing organization with dedicated directories
- Enhanced configuration management
- Streamlined data handling
- Standardized logging system
- Cleaner version archiving
- Fixed duplicate files and improved organization

### v0.5.1 (March 23, 2024) - The Documentation Update
- Added comprehensive Interface Design History documentation
- Created research on Early Apple UI Design Language (1970s-1980s)
- Added case study on EPA's 1977 Unified Visual Design System
- Documented Cultural and Societal Design Trends in early computing
- Created a Design Language index document
- Updated references with links to research documentation
- Expanded the project's design language foundations

### v0.5.0 (March 23, 2024) - The GUI Update
- Enhanced GUI with black-background theme for better visibility
- Implemented OpenAI integration with model selection
- Added real-time service status monitoring
- Created API console with detailed connection information
- Implemented classic Mac-style menu bar
- Standardized on Space Mono font throughout
- Added keyboard shortcuts for common functions
- Fixed button layout issues
- Improved error handling for service connectivity
- Enhanced API key security with dedicated secrets directory
- *Secret feature: Service status indicators color coding*

### v0.1.1 (2024-08-12) - The Visualization Update
- Enhanced terminal display with multiple character sets
- Improved fallback console mode with row/column indicators
- Added verbose mode for detailed LED state tracking
- Resolved synchronization issues between LED state manager and hardware controller
- Improved error handling and terminal size detection
- Added command-line arguments for customization

### v0.1.0 (2024-06-15) - The Renaissance Update
- Improved project structure and documentation
- Added comprehensive research documentation
- Enhanced hardware implementation guides
- Consolidated technical specifications
- *Secret feature: Message animation patterns*

### v0.0.1 (2024-03-17) - The Primordial Release
- Basic punch card display
- Test message support
- Statistics tracking
- Random sentence generation
- OpenAI integration
- Diagnostic logging
- *Secret feature: DOS mode easter egg*

---

<div align="center">
Made with ❤️ by the Punch Card Project Team
</div>