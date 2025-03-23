# Punch Card Display System v0.5.0 - The GUI Update

```
 ________ ___  ___  ___        ___  ___  ________  ________  ________  _________  _______      
|\  _____\\  \|\  \|\  \      |\  \|\  \|\   __  \|\   __  \|\   __  \|\___   ___\\  ___ \     
\ \  \__/\ \  \\\  \ \  \     \ \  \\\  \ \  \|\  \ \  \|\  \ \  \|\  \|___ \  \_\ \   __/|    
 \ \   __\\ \  \\\  \ \  \     \ \  \\\  \ \  \\\  \ \   __  \ \   ____\   \ \  \ \ \  \_|/__  
  \ \  \_| \ \  \\\  \ \  \____ \ \  \\\  \ \  \\\  \ \  \ \  \ \  \___|    \ \  \ \ \  \_|\ \ 
   \ \__\   \ \_______\ \_______\\ \_______\ \_______\ \__\ \__\ \__\        \ \__\ \ \_______\
    \|__|    \|_______|\|_______| \|_______|\|_______|\|__|\|__|\|__|         \|__|  \|_______|
```

**Status**: Beta - The GUI Update is still buggy and hasn't been thoroughly tested.

### What's New in v0.5.0:
- Enhanced GUI with black-background theme for better visibility 
- OpenAI integration working but API console isn't displaying properly
- System console works but needs visual improvements (less jittery)
- Added key press 'C' to toggle console visibility
- Service status monitoring for OpenAI and fly.io services
- Button styles updated to avoid being cut off

### Known Issues:
- API console is not showing messages correctly - outputs to terminal instead
- Visual consistency issues between different console types
- Menu bar/button toolbar may not appear in some configurations
- Occasional style application failures

### Future Improvements:
- Add database viewer for browsing saved messages
- Standardize all consoles to follow same design language
- Improve B&W color scheme with future support for additional colors 
- Planning single-color LED support as stepping stone to full color

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

3. Run the tests to verify functionality:
```bash
python test_leds.py --test all
```

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

---

<div align="center">

```
D O   N O T   F O L D   S P I N D L E   O R   M U T I L A T E
```

*Made with ❤️ by Griffin Gilreath*

</div> 
