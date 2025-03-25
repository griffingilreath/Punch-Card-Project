# Punch Card Project

[![Current Version](https://img.shields.io/badge/version-0.6.2-blue.svg)](https://github.com/griffingilreath/Punch-Card-Project/releases/tag/v0.6.2)

A modernized implementation of the IBM 80-column punch card system for historical and educational purposes.

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
│ │                                                                                  │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

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

## Project Overview

This project provides a full GUI implementation of an IBM 80-column punch card system, allowing users to experiment with this historical computing technology in a modern environment. It's designed for educational purposes to help understand the foundations of computer programming and data processing.

## Features

- Interactive GUI with authentic punch card layout
- Card visualization and encoding
- Support for multiple character encodings
- Import/export functionality
- Historical reference materials

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

## Historical Context

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

## Punch Card Encoding

The punch card system uses a specific encoding scheme for characters based on the IBM 80-column punch card format. Here's a detailed breakdown of the punch patterns:

```
Character Encoding Example (showing 'A' in column 1):
    ┌────────────────────────────────────────────────────────────────────────────────┐
 12 │■□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
 11 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  0 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  1 │■□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
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

Character encoding patterns:
- Letters A-I: Zone punch in row 12 + digit rows 1-9
- Letters J-R: Zone punch in row 11 + digit rows 1-9
- Letters S-Z: Zone punch in row 0 + digit rows 2-9
- Digits 0-9: Single punch in respective rows
- Special characters: Various combinations of punches

### Example Encodings

Here's "HELLO WORLD" encoded in punch card format:

```
    ┌────────────────────────────────────────────────────────────────────────────────┐
 12 │■□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
 11 │□□□□□□□□□□■□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  0 │□□□□□□□□□□□■□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  1 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  2 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  3 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  4 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  5 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  6 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  7 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  8 │■□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  9 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
    └────────────────────────────────────────────────────────────────────────────────┘
     012345678901234567890123456789012345678901234567890123456789012345678901234567890
     1         2         3         4         5         6         7         8
     H    E    L    L    O    _    W    O    R    L    D
```

### Special Characters

Common special characters and their punch patterns:

```
    ┌────────────────────────────────────────────────────────────────────────────────┐
 12 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
 11 │■□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ - (Minus/Hyphen)
  0 │□■□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ & (Ampersand)
  1 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  2 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
  3 │□□■□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ . (Period)
  4 │□□□■□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ $ (Dollar Sign)
  5 │□□□□■□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ * (Asterisk)
  6 │□□□□□■□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ , (Comma)
  7 │□□□□□□■□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ / (Forward Slash)
  8 │□□□□□□□■□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ = (Equals Sign)
  9 │□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│
    └────────────────────────────────────────────────────────────────────────────────┘
     012345678901234567890123456789012345678901234567890123456789012345678901234567890
     1         2         3         4         5         6         7         8
```

## What's New in v0.6.2

- **Restored OpenAI API settings tab** in the Settings dialog
- **Restored Statistics tab** with message tracking and service status
- **Added Card Dimensions settings tab** for controlling punch card size
- **Implemented usage and cost tracking** for OpenAI API
- Fixed the `run_gui_app` function to properly initialize the application
- Improved error handling in the GUI application

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

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required packages (see requirements.txt)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/griffingilreath/Punch-Card-Project.git
   cd Punch-Card-Project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python src/main.py
   ```

## Project Structure

The project follows a standardized directory structure:

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
├── secrets/                # API keys (git-ignored)
├── simple_display.py       # Main application entry point
├── update_api_key.py       # API key management utility
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Components

The project is structured around these key components:

1. **LED State Manager** - Manages the state of LEDs in memory
2. **Hardware Controller** - Controls physical or simulated hardware
3. **Punch Card Display** - High-level API for displaying messages
4. **Display Adapter** - Connects the punch card display to hardware
5. **Terminal Display** - Provides terminal visualization of LED states

### Terminal Display Features

The terminal display provides visual feedback of LED states in two modes:

1. **Curses-based UI** - A split-screen interface showing LED grid and debug messages
2. **Fallback Console Mode** - ASCII representation of the LED grid with row/column indicators

#### Character Sets

The terminal display supports multiple character sets for LED visualization:

- `default`: Filled and empty circles (█, ·)
- `block`: Filled blocks and spaces (█, space)
- `circle`: Filled and empty circles (●, ○)
- `star`: Filled and empty stars (★, ☆)
- `ascii`: ASCII characters (#, .)

You can select your preferred character set using the `--char-set` command-line argument.

#### Fallback Console Mode

When the terminal window is too small or curses initialization fails, the system automatically falls back to console mode, providing:

- Row and column numbered grid display
- ASCII representation of the LED states using the selected character set
- Detailed status and debug messages
- Individual LED state change notifications (when verbose mode is enabled)

## Development

This project follows a comprehensive versioning approach:

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

## Contributing

We welcome contributions! Please follow these steps:

1. Check out the `testing` branch
2. Make your changes
3. Submit a pull request

Please ensure your code follows our coding standards and includes appropriate tests.

## Version History

**Current Version: 0.6.2** - Restored OpenAI settings and Statistics tabs

### What's New in v0.6.2 (Released March 24, 2024):

- **Restored OpenAI API settings tab** in the Settings dialog
- **Restored Statistics tab** with message tracking and service status
- **Added Card Dimensions settings tab** for controlling punch card size
- **Implemented usage and cost tracking** for OpenAI API
- Fixed the `run_gui_app` function to properly initialize the application
- Improved error handling in the GUI application

### What's New in v0.6.0 (Released March 24, 2024):

Major project reorganization focusing on:
- Complete restructuring of the codebase for better maintainability
- Enhanced modular architecture
- Improved documentation structure
- Better separation of concerns between components

### What's New in v0.5.3 (Released March 24, 2024):

This version implements a comprehensive Git branching strategy based on GitFlow while preserving the project's existing version archiving system. It also includes a critical fix for the IBM 80-column punch card encoding display.

#### Punch Card Display Fix
- **Corrected Punch Card Encoding**: Fixed the mapping between characters and punch patterns to accurately reflect the standard IBM punch card format
- **New Display Script**: Added `ibm_026_punch_card.py` script for reliable visualization of punch card patterns 
- **Command Line Options**:
  - `--test-encoding`: Displays all characters and their corresponding punch patterns
  - `--show-alphabet`: Shows just the alphabet (A-Z) on the punch card display
  - `--show-alphanumeric`: Shows both the alphabet and numbers on the punch card
  - Direct text input: Pass any text as an argument to display it on the punch card
- **Improved Documentation**: Added clear comments about the punch card row mapping (rows 12, 11, 0-9) and character patterns

#### Git Versioning Improvements
- **Modified GitFlow Implementation**: A structured approach to version control
- **Branch Types**: 
  - `master`: Main production branch
  - `develop`: Integration branch for new features
  - `feature/*`: Feature branches for new development
  - `release/*`: Release preparation branches
  - `hotfix/*`: Emergency fix branches
  - `v*.*.*`: Version branches that preserve each release point
- **git_version_manager.py**: New command-line tool for branch and version management
- **Integrated workflow** with existing version_manager.py script
- **Automated version creation** with commit history analysis
- **Comprehensive documentation** in VERSION_CONTROL.md
- **Enhanced GitHub Wiki** with improved organization and navigation

### What's New in v0.5.2 (Released March 24, 2024):

This version significantly reorganized the project structure for better maintainability and developer experience while building on the design documentation added in v0.5.1.

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

This version added extensive documentation on early computer interface design history and enhanced the internal design language research that informs the project's aesthetic.

#### Documentation Enhancements
- **Comprehensive Interface Design History** document covering early computing design languages
- **Early Apple UI Design Language** research (1970s-1980s) including text-based origins and GUI evolution
- **EPA's 1977 Unified Visual Design System** case study for consistent design systems
- **Cultural and Societal Design Trends** analysis examining ASCII art, hardware design, and HCI evolution
- **Design Language summary document** acting as an index to design research resources
- **Updated references in README** with links to all research documentation

### What's New in v0.5.0 (Released March 23, 2024):

This version represented a significant visual overhaul of the Punch Card Display System.

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

### What's New in v0.1.0 (Released March 10, 2024):

Initial project structure with:
- Basic punch card simulation
- Terminal-based display
- Core encoding logic
- Initial documentation

For a complete history of versions, see:
- [Releases](https://github.com/griffingilreath/Punch-Card-Project/releases) - All released versions with notes
- [CHANGELOG.md](CHANGELOG.md) - Detailed history of changes

## Known Issues

- API console sometimes shows messages in terminal instead of GUI
- Visual consistency issues between different console types
- Menu bar/button toolbar may not appear in some configurations
- Occasional style application failures with certain PyQt versions
- Space Mono font may not be available on all systems, causing fallback to system fonts

## Future Improvements

- Add database viewer for browsing saved messages
- Standardize all consoles to follow same design language
- Improve B&W color scheme with future support for additional colors 
- Planning single-color LED support as stepping stone to full color
- Implementing a proper settings dialog for all configuration options
- Moving all sensitive configuration to environment variables

## References and Resources

### Historical Documentation
- [IBM Punch Card Systems Manual (1964)](https://archive.org/details/ibm-punch-card-systems)
- [Reference Manual: IBM 026 Printing Card Punch](https://archive.org/details/026_printing_card_punch)
- [IBM Card Summary - Columbia University](http://www.columbia.edu/cu/computinghistory/cards.html)
- [Computer History Museum - Punched Cards](http://www.computerhistory.org/revolution/punched-cards/2)

### Technical Resources
- [Hollerith Code Tables](https://homepage.divms.uiowa.edu/~jones/cards/codes.html)
- [EBCDIC Character Set](https://www.ibm.com/docs/en/zos-basic-skills?topic=mainframe-ebcdic-character-set)
- [Punched Card Codes](http://www.quadibloc.com/comp/cardint.htm)
- [Early Card Machine Documentation](https://archive.org/details/card-machine-manuals)

### Academic Papers
- ["From Punched Cards to Personal Computing"](https://doi.org/10.1109/MAHC.2012.45)
- ["The IBM Punched Card"](https://doi.org/10.1109/MAHC.1981.10025)
- ["Evolution of Punched Card Programming"](https://dl.acm.org/doi/10.1145/800233.807045)

### Related Projects
- [Virtual Keypunch Simulator](https://github.com/rpruiz/virtual-keypunch)
- [Punched Card Emulator](https://github.com/joshwilliams/punched-card-emulator)
- [Card Reader Project](https://github.com/cardreader/card-project)

### Design Guidelines
- [IBM Design Language History](https://www.ibm.com/design/language/ibm-logos/8-bar/)
- [Early Computer Interface Design](https://www.interaction-design.org/literature/book/early-computer-era)
- [Punch Card Visual Design Standards](https://www.computerhistory.org/collections/catalog/102646167)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- IBM for the original 026 Keypunch machine
- Various historical references on punch card systems
- All contributors to this project

---

```
D O   N O T   F O L D   S P I N D L E   O R   M U T I L A T E
```

_Made with ❤️ by Griffin Gilreath_ 