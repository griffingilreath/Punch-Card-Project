# Terminal Display Documentation

The Terminal Display is a key component of the Punch Card Project, providing real-time visualization of LED states and system messages. This document details how to use and customize the terminal display for different environments and preferences.

## Overview

The Terminal Display module (`src/terminal_display.py`) offers two primary display modes:

1. **Curses-based UI**: A full-featured split-screen interface with:
   - LED grid visualization panel
   - Debug message panel
   - Status line

2. **Fallback Console Mode**: A simplified ASCII-based visualization that activates automatically when:
   - The terminal window is too small (less than 40x12 characters)
   - The curses library fails to initialize
   - Other terminal capability issues occur

## Features

### Split-Screen UI

When running in full UI mode, the terminal display provides:

- **LED Grid Panel**: Visual representation of LED states
- **Debug Message Panel**: Scrollable history of system messages
- **Status Line**: Current system status and mode

### Character Sets

The terminal display supports multiple character sets for LED visualization:

| Character Set | On State | Off State | Example |
|---------------|----------|-----------|---------|
| `default`     | █ (block)| · (dot)   | █ · █ · |
| `block`       | █ (block)| (space)   | █  █   |
| `circle`      | ● (filled)| ○ (empty) | ● ○ ● ○ |
| `star`        | ★ (filled)| ☆ (empty) | ★ ☆ ★ ☆ |
| `ascii`       | # (hash) | . (dot)   | # . # . |

### Fallback Console Mode

When the terminal UI can't be initialized, the fallback console mode provides:

- Grid coordinates (row and column numbers)
- Bordered ASCII visualization
- LED state change messages (in verbose mode)
- Status and debug messages with type indicators

Example fallback console output:
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

## Usage

### Basic Usage

```python
from src.terminal_display import get_instance

# Get a terminal display instance with default settings
display = get_instance()

# Start the display
display.start()

try:
    # Set an LED state
    display.update_led(0, 0, True)
    
    # Add a debug message
    display.add_debug_message("LED at (0,0) activated", "info")
    
    # Set the status
    display.set_status("System operational", "info")
    
    # Update an entire grid
    grid = [[False for _ in range(16)] for _ in range(8)]
    grid[0][0] = True  # Set top-left LED on
    display.update_led_grid(grid)
    
finally:
    # Always stop the display when done
    display.stop()
```

### Customization

```python
# Get a terminal display with custom settings
display = get_instance(
    rows=8,            # Number of LED rows
    columns=16,        # Number of LED columns
    verbose=True,      # Enable verbose output
    char_set="star"    # Use star character set
)

# Change character set after initialization
display.set_character_set("circle")

# Enable/disable verbose mode
display.set_verbose(True)
```

### Command-Line Integration

When using the terminal display in command-line programs, add these arguments to your parser:

```python
parser.add_argument("--use-ui", action="store_true", default=False,
                    help="Use the terminal UI with split-screen for LED display and debug messages")
parser.add_argument("--term-width", type=int, default=80,
                    help="Terminal width (only used with --use-ui)")
parser.add_argument("--term-height", type=int, default=24,
                    help="Terminal height (only used with --use-ui)")
parser.add_argument("--char-set", choices=["default", "block", "circle", "star", "ascii"], 
                    default="default", help="Character set to use for LED visualization")
parser.add_argument("--verbose", action="store_true", default=False,
                    help="Print verbose output including individual LED state changes")
```

## API Reference

### Initialization

```python
display = get_instance(
    rows=8,            # Number of LED rows
    columns=16,        # Number of LED columns
    verbose=False,     # Whether to print verbose output
    char_set="default" # Character set to use
)
```

### Core Methods

| Method | Description |
|--------|-------------|
| `start()` | Start the terminal display |
| `stop()` | Stop the terminal display |
| `update_led(row, column, state)` | Update a single LED state |
| `update_led_grid(grid)` | Update the entire LED grid |
| `add_debug_message(message, message_type)` | Add a debug message |
| `set_status(message, message_type)` | Set the status message |
| `set_character_set(char_set)` | Change the character set |
| `set_verbose(verbose)` | Enable/disable verbose mode |

### Message Types

- `info`: Normal information (default)
- `warning`: Warning messages
- `error`: Error messages

## Advanced Features

### Custom Character Sets

You can define your own custom character set:

```python
display = get_instance()
display.led_chars = {True: '■', False: '□'}
```

### Terminal Size Detection

The system automatically detects terminal size, but you can override it:

```python
import os
os.environ['LINES'] = '40'
os.environ['COLUMNS'] = '100'
```

### Error Handling

The terminal display is designed to gracefully handle errors:

- Automatically falls back to console mode when issues occur
- Closes curses properly to avoid terminal corruption
- Handles SIGINT (Ctrl+C) cleanly

## Troubleshooting

### Common Issues

1. **Terminal Too Small Warning**
   - Increase your terminal window size (minimum 40x12)
   - Or use a terminal multiplexer like tmux or screen

2. **Display Corruption**
   - If your terminal becomes corrupted, type `reset` and press Enter

3. **Colors Not Displaying**
   - Check if your terminal supports colors: `echo $TERM`
   - Use a terminal that supports colors (e.g., xterm-256color)

4. **Character Set Issues**
   - If characters appear as squares or question marks, your terminal font doesn't support them
   - Try the `ascii` character set: `--char-set ascii`

## Implementation Details

The terminal display is implemented using:

- Python's standard `curses` library for the UI
- Separate threads for UI updates to avoid blocking
- Message queues for thread-safe communication
- Signal handlers to properly clean up on exit

### Thread Safety

All updates to the display are thread-safe through message queues:

- `led_queue`: For LED state updates
- `debug_queue`: For debug messages
- `status_queue`: For status updates

This allows the UI to be updated from any thread without race conditions. 