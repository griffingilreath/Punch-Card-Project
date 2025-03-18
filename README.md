# IBM Punch Card Display System

A sophisticated terminal-based simulator of an IBM 80-column punch card display system, featuring LED grid visualization and message processing capabilities with historical accuracy and modern integrations.

![IBM Punch Card](https://placeholder-for-punch-card-image.png)

## Overview

This project recreates the iconic IBM 80-column punch card system in a digital format, combining historical computing preservation with modern LED display technology. It simulates the character-by-character display process of punch cards while providing an interface for message generation, processing, and visualization.

## Historical Context

IBM's 80-column punch cards were a revolutionary data storage medium that dominated computing from the 1920s through the 1970s. Each card measured precisely 7⅜ × 3¼ inches (187mm × 82.5mm) and featured:

- 80 columns for character storage (numbered 1-80 from left to right)
- 12 punch positions per column (rows 12, 11, 0-9 from top to bottom)
- A clipped corner for orientation (typically upper-left on IBM cards)
- Rectangular holes (~1mm × 3mm) introduced in 1928 for tighter spacing

Each character was encoded using specific hole patterns (Hollerith code), with:
- Letters A-I: Zone punch in row 12 + digit rows 1-9
- Letters J-R: Zone punch in row 11 + digit rows 1-9
- Letters S-Z: Zone punch in row 0 + digit rows 2-9
- Digits 0-9: Single punch in respective rows
- Special characters: Various combinations of punches

Character codes varied slightly between systems (FORTRAN vs. Commercial/Symbolic), with later standards like EBCDIC expanding the character set while maintaining backward compatibility.

## Project Structure

```
punch_card_system/
├── src/                    # Source code
│   ├── __init__.py
│   ├── main.py             # Main application entry point
│   ├── punch_card.py       # Punch card visualization and processing
│   ├── database.py         # Database operations
│   ├── message_generator.py # Message generation (random & OpenAI)
│   ├── settings_menu.py    # Settings configuration interface
│   ├── message_database.py # Message storage and retrieval
│   └── test_display.py     # Testing utilities
├── scripts/                # Utility scripts
│   ├── version_manager.py  # Version management utilities
│   ├── punch_card_stats.py # Statistics processing script
│   └── Punch Card Cursor Test V1.py # Legacy test script
├── tests/                  # Test files
│   ├── test_punch_card.py  # Punch card display tests
│   ├── test_messages.py    # Message processing tests
│   └── test_messages.txt   # Test message samples
├── config/                 # Configuration files
│   ├── config.yaml         # Main configuration
│   └── credentials.yaml    # API credentials
├── data/                   # Data storage
│   ├── messages.db         # SQLite database
│   ├── punchcard_messages.db # Legacy message database
│   ├── message_history.json # Message history
│   ├── punch_card_stats.json # System statistics
│   ├── punch_card_stats.txt # Legacy statistics file
│   ├── punch_card_settings.json # User settings
│   └── concise_statements.txt # Thought-provoking one-liners for display
├── docs/                   # Documentation
│   ├── technical/          # Technical specifications and guides
│   │   ├── NEOPIXEL_INTEGRATION.md # NeoPixel LED integration specifications
│   │   ├── NEOPIXEL_PROTOTYPE.md   # NeoPixel prototype implementation
│   │   ├── DISPLAY_DEBUGGING.md    # Display positioning and debugging guide
│   │   ├── ROADMAP.md              # Project development roadmap
│   │   ├── INTEGRATION_SUMMARY.md  # Integration overview
│   │   └── WEB_INTEGRATION_EXAMPLE.py # Web API integration example
│   └── research/           # Research documents and reference materials
│       ├── PUNCH_CARD_ENCODING.md  # Detailed encoding specifications
│       ├── LED_IMPLEMENTATION.md   # LED hardware implementation guide
│       └── SOCIOLOGICAL_ASPECTS.md # Cultural impact analysis
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Features

- Terminal-based IBM 80-column punch card simulation with historical accuracy
- LED grid visualization with character-by-character display
- Message processing with authentic punch card encoding (Hollerith/EBCDIC)
- Statistics tracking and display
- Message generation:
  - Random sentence generation
  - OpenAI API integration for intelligent message generation
  - Historical punch card statements
- Diagnostic logging and system information display
- SQLite database for message storage and retrieval
- NeoPixel LED integration for physical display (planned)
- Web interface for remote monitoring (planned)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/griffingilreath/Punch-Card-Project.git
cd Punch-Card-Project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure credentials:
   - Copy `config/credentials.yaml.example` to `config/credentials.yaml`
   - Add your OpenAI API key to the credentials file

## Usage

Run the program:
```bash
python src/main.py
```

Command line arguments:
- `--test-message`: Custom test message
- `--led-delay`: Delay between LED updates (milliseconds)
- `--message-delay`: Delay between messages (seconds)
- `--random-delay`: Enable random delays between messages
- `--skip-splash`: Skip splash screen and startup sequence

## Message Processing

The system processes messages in the following order:
1. Test messages (if configured)
2. System diagnostic information (IP address, etc.)
3. Randomly generated sentences
4. OpenAI-generated messages (if configured)
5. Historical punch card statements (if enabled)

## Database Structure

The SQLite database (`messages.db`) contains:
- `messages` table: Stores all processed messages
- `diagnostics` table: Stores system diagnostic information
- `statistics` table: Stores usage statistics and system performance metrics

## Character Encoding

The system uses IBM 026/029 style punch card encoding with support for multiple character sets:

### FORTRAN Character Set
- A-I: Zone punch row 12 + digit rows 1-9
- J-R: Zone punch row 11 + digit rows 1-9
- S-Z: Zone punch row 0 + digit rows 2-9
- 0-9: Single punch in respective rows
- Limited special characters: +-*/=().,$

### Commercial/Symbolic Character Set
- Includes all FORTRAN characters
- Additional special characters: &!?#@%[]{}

### Extended Character Set (Modern)
- Support for lowercase letters and additional symbols based on ANSI X3.26

## Hardware Integration

### LED Grid Specifications
The project is designed to integrate with a physical 12×80 LED grid that matches the exact dimensions of an IBM punch card:

- Grid: 12 rows × 80 columns (960 LEDs total)
- LED Type: Individually addressable RGB LEDs (WS2812B/NeoPixels)
- Power Requirements: 5V DC, ~20A (worst case)
- Microcontroller: Teensy 4.0/4.1 or Raspberry Pi
- Physical Dimensions: Spacing to match IBM card (~0.087" horizontal, ~0.25" vertical)

See the [NeoPixel Integration Guide](docs/technical/NEOPIXEL_INTEGRATION.md) for detailed hardware specifications and implementation plans.

## Web Integration

The system features a web interface for:
- Remote monitoring of punch card display
- Historical statistics and message archiving
- SVG-based punch card visualization
- API for submitting new messages

See the [Web Integration Example](docs/technical/WEB_INTEGRATION_EXAMPLE.py) for implementation details.

## Documentation

### Technical Documentation
- [Project Roadmap](docs/technical/ROADMAP.md) - Development timeline and feature planning
- [NeoPixel Integration](docs/technical/NEOPIXEL_INTEGRATION.md) - LED hardware integration specifications
- [NeoPixel Prototype](docs/technical/NEOPIXEL_PROTOTYPE.md) - Prototype implementation guide
- [Display Debugging](docs/technical/DISPLAY_DEBUGGING.md) - Troubleshooting guide for display issues
- [Integration Summary](docs/technical/INTEGRATION_SUMMARY.md) - Overview of system integrations

### Research Documentation
- [Punch Card Encoding](docs/research/PUNCH_CARD_ENCODING.md) - Historical encoding specifications
- [LED Implementation](docs/research/LED_IMPLEMENTATION.md) - Hardware implementation details
- [Sociological Aspects](docs/research/SOCIOLOGICAL_ASPECTS.md) - Cultural impact analysis

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Version History

- v0.1.0 (2024-06-15): Project reorganization
  - Improved project structure and documentation
  - Added comprehensive research documentation
  - Enhanced hardware implementation guides
  - Consolidated technical specifications

- v0.1.0 (2024-03-18): Feature enhancement release
  - Display synchronization improvements
  - NeoPixel integration documentation
  - Web integration example code
  - Expanded project roadmap
  - Documentation updates

- v0.0.1 (2024-03-17): Initial release
  - Basic punch card display
  - Test message support
  - Statistics tracking
  - Random sentence generation
  - OpenAI integration
  - Diagnostic logging 

## References

- IBM Documentation: "IBM Punched Card Stock Specification" 
- Columbia University Computing History Archive
- "Two-Bit History: The Punched Card Tabulator"
- "The Craft of Coding: Understanding Historical Computing"
- University of Iowa Punch Card Collection (D. Jones)
- ANSI X3.26-1970: Hollerith Punched Card Code 