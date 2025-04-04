# Punch Card Project v0.5.2 - The Reorganization Update

```
┌─────────────────────────────── PUNCH CARD GUI UPDATE ───────────────────────────────┐
│ ┌──────────┐ ┌─────────────────────────────────────────────────────────────┐ ┌───┐ │
│ │   Menu   │ │                                                             │ │ × │ │
│ └──────────┘ └─────────────────────────────────────────────────────────────┘ └───┘ │
│ ┌──────────────────────────────────────────────────────────────────────────────────┐│
│ │                                                                                  ││
│ │  ████████  ███████  ████████ ██    ██    ███    ██    ██  ███████   █████  ████ ││
│ │     ██     ██    ██    ██    ██    ██   ██ ██   ██    ██  ██       ██   ██ ██ █ ││
│ │     ██     ██    ██    ██    ██    ██  ██   ██  ██    ██  █████    ███████ ██ █ ││
│ │     ██     ██    ██    ██    ██    ██ █████████ ██    ██  ██       ██   ██ ██ █ ││
│ │     ██      ██████     ██     ██████  ██     ██  ██████   ███████  ██   ██ ████ ││
│ │                                                                                  ││
│ └──────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                      │
│ ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌───────────────┐   ┌────────────────┐ │
│ │ Settings │   │  OpenAI  │   │ Database │   │ Toggle Console│   │ Black Background│ │
│ └──────────┘   └──────────┘   └──────────┘   └───────────────┘   └────────────────┘ │
│                                                                                      │
│ ┌──────────────────────────────────── CONSOLE ─────────────────────────────────────┐│
│ │ [21:45:32] API initialized                                                       ││
│ │ [21:45:33] OpenAI connection: ONLINE                                             ││
│ │ [21:45:34] Service status: All systems operational                               ││
│ │ [21:45:35] Press 'C' to toggle console visibility                                ││
│ └──────────────────────────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────────────────────────┘
```

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

**Status**: Beta - The Reorganization Update improves project structure while building on v0.5.1's design documentation.

### What's New in v0.5.2 (Released March 24, 2024):

This version significantly reorganizes the project structure for better maintainability and developer experience while building on the design documentation added in v0.5.1.

#### Project Structure Improvements
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

### What's New in v0.5.1 (Released March 23, 2024):

This version adds extensive documentation on early computer interface design history and enhances the internal design language research that informs the project's aesthetic.

#### Documentation Enhancements
- **Comprehensive Interface Design History** document covering early computing design languages
- **Early Apple UI Design Language** research (1970s-1980s) including text-based origins and GUI evolution
- **EPA's 1977 Unified Visual Design System** case study for consistent design systems
- **Cultural and Societal Design Trends** analysis examining ASCII art, hardware design, and HCI evolution
- **Design Language summary document** acting as an index to design research resources
- **Updated references in README** with links to all research documentation

### What's New in v0.5.0 (Released March 23, 2024):

This version represents a significant visual overhaul of the Punch Card Display System, focusing on improved GUI elements, better visibility with a black background theme, and enhanced service monitoring for OpenAI and fly.io connections.

#### Visual Interface Improvements
- **Enhanced GUI with black-background theme** for better visibility and authentic punch card aesthetic
- **Space Mono font** for consistent terminal-like appearance throughout the interface
- **Classic Mac-style menu bar** (where supported) or enhanced button toolbar with properly sized buttons
- **Fixed button layout issues** to prevent UI elements from being cut off
- **Improved widget visibility** with enhanced contrast for all UI elements

#### Functionality Enhancements
- **OpenAI integration** with model selection and prompt customization
- **Service status monitoring** for both OpenAI and fly.io connectivity
- **API console** with detailed connection information (toggle with 'C' key)
- **Keyboard shortcuts** for common functions including console visibility
- **Improved error handling** for service connectivity issues

#### Security Improvements
- **API key management** with secure handling and environment variable support
- **Dedicated secrets directory** excluded from Git via .gitignore
- **Enhanced settings file structure** to prevent accidental API key exposure
- **Updated documentation** with security best practices

### Known Issues:
- API console sometimes shows messages in terminal instead of GUI
- Visual consistency issues between different console types
- Menu bar/button toolbar may not appear in some configurations
- Occasional style application failures with certain PyQt versions
- Space Mono font may not be available on all systems, causing fallback to system fonts

### Future Improvements:
- Add database viewer for browsing saved messages
- Standardize all consoles to follow same design language
- Improve B&W color scheme with future support for additional colors 
- Planning single-color LED support as stepping stone to full color
- Implementing a proper settings dialog for all configuration options
- Moving all sensitive configuration to environment variables

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

- Each version is tagged in Git with the format `v{major}.{minor}.{patch}`
- Complete snapshots of each version are preserved in the `versions/` directory
- The version_manager.py script in the scripts directory handles creating new version snapshots
- Previous versions can be accessed by:
  1. Git tags: `git checkout v0.1.0`
  2. Version archives: Explore the `versions/0.1.0/` directory

## What is the Punch Card Display System?

A modern project that pays homage to the punch card era of computing through a simulated display system. It combines vintage computing aesthetics with modern technologies like AI-generated content.

# 💾 Punch Card Project 💾

This project implements a punch card display system with LED integration for both simulated and physical hardware.

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

```
 ___________________________________________________________________________________
/\                                                                                  \
\_|                                                                                  |
  |  ██████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗     ██████╗ █████╗ ██████╗ ██████╗  |
  |  ██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║    ██╔════╝██╔══██╗██╔══██╗██╔══██╗ |
  |  ██████╔╝██║   ██║██╔██╗ ██║██║     ███████║    ██║     ███████║██████╔╝██║  ██║ |
  |  ██╔═══╝ ██║   ██║██║╚██╗██║██║     ██╔══██║    ██║     ██╔══██║██╔══██╗██║  ██║ |
  |  ██║     ╚██████╔╝██║ ╚████║╚██████╗██║  ██║    ╚██████╗██║  ██║██║  ██║██████╔╝ |
  |  ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  |
  |                                                                                  |
  |  ██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████████╗                      |
  |  ██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔════╝╚══██╔══╝                      |
  |  ██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║        ██║                         |
  |  ██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║        ██║                         |
  |  ██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╗   ██║                         |
  |  ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝                         |
  |                                                                                  |
  |  DO  NOT  FOLD,  SPINDLE,  OR  MUTILATE                                          |
  |__________________________________________________________________________________|
```

*A sophisticated terminal-based simulator of an 80-column punch card display system, featuring LED grid visualization and message processing capabilities with historical accuracy and modern integrations.*

## 🔍 Overview

This project recreates the iconic IBM 80-column punch card system in a digital format, combining historical computing preservation with modern LED display technology. It simulates the character-by-character display process of punch cards while providing an interface for message generation, processing, and visualization.

<details>
<summary>🎲 Easter Egg: Try running with the secret flag <code>--vintage-mode</code> 🎲</summary>
<br>
Running the program with <code>--vintage-mode</code> activates a special display simulating a worn-out punch card reader with occasional misreads and mechanical sounds. There's also a 1 in 100 chance you'll trigger the "card jam" animation!
</details>

## 📚 Historical Context

```
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
```

IBM's 80-column punch cards were a revolutionary data storage medium that dominated computing from the 1920s through the 1970s. Each card measured precisely 7⅜ × 3¼ inches (187mm × 82.5mm) and featured:

- 80 columns for character storage (numbered 1-80 from left to right)
- 12 punch positions per column (rows 12, 11, 0-9 from top to bottom)
- A clipped corner for orientation (typically upper-left on IBM cards)
- Rectangular holes (~1mm × 3mm) introduced in 1928 for tighter spacing

```
             ┌────────────────────────────────────────────────────────────────────────────────┐
          12 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
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
              |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |
              5    10   15   20   25   30   35   40   45   50   55   60   65   70   75   80
```

Each character was encoded using specific hole patterns (Hollerith code), with:
- Letters A-I: Zone punch in row 12 + digit rows 1-9
- Letters J-R: Zone punch in row 11 + digit rows 1-9
- Letters S-Z: Zone punch in row 0 + digit rows 2-9
- Digits 0-9: Single punch in respective rows
- Special characters: Various combinations of punches

Character codes varied slightly between systems (FORTRAN vs. Commercial/Symbolic), with later standards like EBCDIC expanding the character set while maintaining backward compatibility.

> 💭 **Fun Fact**: The phrase "Do not fold, spindle, or mutilate" became a cultural touchstone of the punch card era. The term "spindle" referred to a spike often found at retail counters where receipts and papers were impaled for storage. Punch cards were processed by machines that required intact, undamaged cards - hence the warning!

## 🗂️ Project Structure

```
punch_card_system/
├── src/                    # Source code
│   ├── __init__.py
│   ├── hardware_controller.py  # Hardware control abstraction layer
│   ├── led_state_manager.py    # LED state management
│   ├── punch_card.py       # Punch card visualization and processing
│   ├── terminal_display.py # Terminal visualization with curses UI
│   └── display_adapter.py  # Adapter between punch card and hardware
├── animations/            # Animation JSON files
│   ├── splash.json         # Splash screen animation
│   └── spinner.json        # Loading spinner animation
├── tests/                  # Test files
│   └── test_leds.py        # LED testing and verification
└── README.md              # This file
```

## ✨ Features

- Terminal-based IBM 80-column punch card simulation with historical accuracy
- LED grid visualization in various display modes:
  - Curses-based split-screen UI for detailed visualization
  - Fallback console mode with ASCII grid representation
  - Multiple character sets for different visual preferences
- Hardware control abstraction layer supporting:
  - Simulated hardware (for development and testing)
  - Raspberry Pi GPIO (for physical LED matrix integration)
- LED state management with animation capabilities
- Error-resilient design with graceful fallbacks
- Comprehensive testing modes for verifying system functionality

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/griffingilreath/Punch-Card-Project.git
cd Punch-Card-Project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key (choose one method):

   **Method 1: Using the update_api_key.py script (RECOMMENDED)**
   ```bash
   # Run the script and follow the prompts - your key will never be displayed
   python update_api_key.py
   ```

   **Method 2: Manually edit the secrets file**
   ```bash
   # Create a copy of the template in the secrets directory
   cp secrets/api_keys.json.template secrets/api_keys.json
   
   # Edit the api_keys.json file with your actual API key
   # Replace "YOUR_OPENAI_API_KEY_HERE" with your real key
   ```

   **Method 3: Environment variables**
   ```bash
   # On macOS/Linux
   export OPENAI_API_KEY=your_api_key_here
   
   # On Windows
   set OPENAI_API_KEY=your_api_key_here
   ```
   
   **Method 4: Settings file (LEAST SECURE - not recommended)**
   - Edit the `punch_card_settings.json` file and replace "YOUR_API_KEY_HERE" with your actual key

4. Run the application with the new black background theme:
```bash
python simple_display.py --black-bg --openai --debug
```

### 🔐 API Key Security

The project now includes enhanced security for API keys with v0.5.0:

- A dedicated `secrets/` directory that is excluded from git via `.gitignore`
- Secure lookup hierarchy that prioritizes the safest storage methods:
  1. First checks the `secrets/api_keys.json` file
  2. Then falls back to environment variables
  3. Only uses settings file as a last resort
- The new `update_api_key.py` script for securely updating your API key
- Clear instructions in `secrets/README.md` for proper key management
- Additional `.gitignore` rules to prevent accidental commits of sensitive data

**Important**: Never commit real API keys to GitHub. The project is configured to help
prevent this, but always double-check your commits to ensure sensitive data isn't included.

## 🚀 Usage Examples

### Running Basic Tests

```bash
# Run a minimal test with ASCII character set
python test_leds.py --test minimal --use-ui --char-set ascii

# Run hardware verification with star characters and verbose output
python test_leds.py --test hardware --use-ui --char-set star --verbose

# Run animation test with circle characters
python test_leds.py --test animations --use-ui --char-set circle
```

### Terminal UI vs Console Output

The system provides two display modes:

1. **Terminal UI Mode** (requires a terminal at least 40x12 characters):
   ```
   ┌─ LED Display ─────────┐
   │ . # . # . # . # . # . │
   │ # . # . # . # . # . # │
   │ . # . # . # . # . # . │
   │ # . # . # . # . # . # │
   └──────────────────────┘
   ┌─ Debug Messages ─────────────────────┐
   │ Connected to hardware                │
   │ Setting LED pattern: Checkerboard    │
   │ Pattern set successfully             │
   │ LED test completed                   │
   └───────────────────────────────────────┘
   ```

2. **Fallback Console Mode** (automatic when terminal is too small):
   ```
       0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 
      +-------------------------------+
    0 | # . # . # . # . # . # . # . # . |
    1 | . # . # . # . # . # . # . # . # |
    2 | # . # . # . # . # . # . # . # . |
    3 | . # . # . # . # . # . # . # . # |
    4 | # . # . # . # . # . # . # . # . |
    5 | . # . # . # . # . # . # . # . # |
    6 | # . # . # . # . # . # . # . # . |
    7 | . # . # . # . # . # . # . # . # |
      +-------------------------------+
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

See the `RPiHardwareController` class in `hardware_controller.py` for details on pin mapping and configuration.

## 🗓️ Version History

- v0.5.2 (2024-03-24): **The Reorganization Update**
  - Complete restructuring of the project for optimal organization
  - Properly separated core, display, and utility modules
  - Enhanced test organization with specialized test directories
  - Consolidated and archived all display-related modules
  - Created proper configuration and data directories
  - Reduced root directory to only essential files
  - Moved database and JSON files to dedicated data directory
  - Archived all legacy and duplicate test files
  - Enhanced documentation with detailed directory structure
  - Standardized directory structure following best practices
  
- v0.5.1 (2024-03-23): **The Documentation Update**
  - Added comprehensive Interface Design History documentation
  - Created research on Early Apple UI Design Language (1970s-1980s)
  - Added case study on EPA's 1977 Unified Visual Design System
  - Documented Cultural and Societal Design Trends in early computing
  - Created a Design Language index document for all design resources
  - Updated README with links to new research documentation
  - Expanded the project's design language foundations

- v0.5.0 (2024-03-23): **The GUI Update**
  - Enhanced GUI with black-background theme for better visibility and authentic punch card aesthetic
  - Implemented OpenAI integration with model selection and prompt customization
  - Added real-time service status monitoring for both OpenAI and fly.io connectivity
  - Created API console with detailed connection information (toggle with 'C' key)
  - Implemented classic Mac-style menu bar with enhanced button toolbar fallback
  - Standardized on Space Mono font throughout the interface for consistent terminal-like appearance
  - Added keyboard shortcuts for common functions including console visibility
  - Fixed button layout issues to prevent UI elements from being cut off
  - Significantly improved error handling for service connectivity issues
  - Enhanced API key security with dedicated secrets directory and secure lookup hierarchy
  - Updated .gitignore to prevent sensitive information from being committed
  - *Secret feature: Service status indicators color coding*

- v0.1.1 (2024-08-12): **The Visualization Update**
  - Enhanced terminal display with multiple character sets
  - Improved fallback console mode with row/column indicators
  - Added verbose mode for detailed LED state tracking
  - Resolved synchronization issues between LED state manager and hardware controller
  - Improved error handling and terminal size detection
  - Added command-line arguments for customization

- v0.1.0 (2024-06-15): **The Renaissance Update**
  - Improved project structure and documentation
  - Added comprehensive research documentation
  - Enhanced hardware implementation guides
  - Consolidated technical specifications
  - *Secret feature: Message animation patterns*

- v0.0.1 (2024-03-17): **The Primordial Release**
  - Basic punch card display
  - Test message support
  - Statistics tracking
  - Random sentence generation
  - OpenAI integration
  - Diagnostic logging
  - *Secret feature: DOS mode easter egg*

## 📚 References

- [IBM Documentation: "IBM Punched Card Stock Specification"](https://www.ibm.com/ibm/history/ibm100/us/en/icons/punchcard/) 
- [Columbia University Computing History Archive](https://www.columbia.edu/cu/computinghistory/)
- [Two-Bit History: The Punched Card Tabulator](https://twobithistory.org)
- [The Craft of Coding: Understanding Historical Computing](https://craftofcoding.wordpress.com/)
- [University of Iowa Punch Card Collection (D. Jones)](https://www.lib.uiowa.edu/sc/resources/punched-card-collections/)
- [ANSI X3.26-1970: Hollerith Punched Card Code](https://webstore.ansi.org/Standards/INCITS/ANSIINCITSAssociates1970) 

### Internal Documentation

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
