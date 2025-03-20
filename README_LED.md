# LED Integration for Punch Card Project

This document provides comprehensive information about the LED integration for the Punch Card Project, including setup, configuration, testing, and troubleshooting.

## Overview

The LED integration system allows the Punch Card simulator to display output on physical LED arrays, synchronizing the terminal display with physical LEDs. The system is designed to be flexible, configurable, and compatible with various hardware implementations.

## Components

The LED integration consists of the following components:

1. **LED State Manager** (`src/led_state_manager.py`): Manages the state of all LEDs and provides an interface for setting individual LEDs or patterns.

2. **Hardware Controller** (`src/hardware_controller.py`): Handles the connection to physical LED hardware or simulates LED output when physical hardware is unavailable.

3. **Punch Card Display Adapter** (`src/punch_card.py`): Connects the punch card display to the LED state manager to ensure synchronized output.

4. **Test Scripts** (`test_leds.py`): Provides various tests to verify LED functionality and integration with the punch card system.

5. **Configuration** (`config/led_config.yaml`): Allows customization of LED behavior, hardware settings, and mappings.

6. **Animations** (`animations/`): JSON-based animation definitions for splash screens and other dynamic displays.

## Configuration

The LED system is configured through the `config/led_config.yaml` file. Key configuration options include:

- **Hardware settings**: Type of hardware (none, simulated, Raspberry Pi)
- **LED layout**: Number of rows and columns in the LED array
- **Pin mappings**: For connecting to specific hardware pins
- **Display settings**: Brightness, refresh rate, etc.
- **Character mappings**: Patterns for displaying text on the LED display

Example configuration:

```yaml
hardware:
  type: simulated  # Options: none, simulated, rpi
  pins:
    data: 18
    clock: 23
    latch: 24
  
display:
  rows: 8
  columns: 16
  brightness: 0.5
  refresh_rate: 30  # Hz
  
animations:
  enabled: true
  splash_screen: "splash.json"
```

## Testing

The `test_leds.py` script provides several test modes to verify LED functionality:

1. **Minimal Test**: `python3 test_leds.py --test minimal`
   - A simple test that verifies basic LED control with a checkerboard pattern

2. **Hardware Verification**: `python3 test_leds.py --test hardware`
   - Displays various patterns (border, diagonal, text) to verify all LEDs are working correctly

3. **Direct LED Control**: `python3 test_leds.py --test direct`
   - Tests direct LED control functions without punch card integration

4. **Integration Test**: `python3 test_leds.py --test integration`
   - Tests full integration with the punch card display system

5. **All Tests**: `python3 test_leds.py --test all`
   - Runs all available tests in sequence

You can specify the hardware type using the `--hardware-type` flag:
```bash
python3 test_leds.py --test hardware --hardware-type simulated
```

## Hardware Support

The system currently supports the following hardware:

1. **Simulated Hardware**: Displays LED patterns in the terminal (default)
2. **Raspberry Pi GPIO**: Controls LED matrices connected to Raspberry Pi GPIO pins
3. **None**: Disables LED output for debugging purposes

To add support for new hardware:
1. Create a new subclass of `HardwareController` in `src/hardware_controller.py`
2. Implement the required methods: `connect()`, `disconnect()`, `start()`, `stop()`, and `_update_hardware()`
3. Update the factory method to create instances of your new controller

## Visualization Options

Version 0.1.1 adds significant improvements to LED visualization in both terminal and console modes:

### Character Sets

The system now supports multiple character sets for LED visualization:

- `default`: Filled blocks and dots (█, ·)
- `block`: Filled blocks and spaces (█, space)
- `circle`: Filled and empty circles (●, ○)
- `star`: Filled and empty stars (★, ☆)
- `ascii`: ASCII characters (#, .)

Select a character set based on your terminal compatibility and visual preference:

```bash
# Use circle characters for LED visualization
python3 test_leds.py --test hardware --use-ui --char-set circle

# Use ASCII characters for maximum terminal compatibility
python3 test_leds.py --test hardware --use-ui --char-set ascii
```

### Enhanced Terminal UI

The terminal UI provides:
- Split-screen interface with LED grid and debug messages
- Character set customization
- Status line with system information
- Scrollable debug message history

### Fallback Console Mode

When the terminal window is too small or curses initialization fails, the system automatically falls back to console mode, providing:

- Grid visualization with row and column coordinates
- LED state representation using the selected character set
- Detailed status and debug messages
- Rate-limited updates to prevent console flooding

Example fallback console output:
```
    0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 
   +-------------------------------+
 0 | # . # . # . # . # . # . # . # . |
 1 | . # . # . # . # . # . # . # . # |
 2 | # . # . # . # . # . # . # . # . |
 3 | . # . # . # . # . # . # . # . # |
   +-------------------------------+

[INFO] 14:32:15 - Connected to hardware
[DEBUG] 14:32:16 - Setting LED pattern: Checkerboard
```

## Additional Command-Line Options

Version 0.1.1 adds these command-line options for controlling the terminal display:

```
--use-ui             Enable terminal UI with split-screen display
--term-width WIDTH   Override terminal width detection
--term-height HEIGHT Override terminal height detection
--char-set SET       Character set for LED display (default, block, circle, star, ascii)
--verbose            Show detailed LED state changes
```

## Troubleshooting

Common issues and solutions:

1. **Timeout errors during tests**:
   - May indicate recursion or deadlock in the LED state manager
   - Try running with simpler patterns or the minimal test
   - Check that the hardware controller is properly connected

2. **LEDs not displaying correctly**:
   - Verify hardware connections
   - Check pin configurations in `led_config.yaml`
   - Try running the hardware verification test to check specific LED patterns

3. **Simulated output only shows partial display**:
   - Ensure that the rows and columns in the configuration match your hardware
   - The simulated display shows only the first 8x8 section by default

If you encounter display issues:

1. **Terminal Too Small Warning**: 
   - Increase your terminal window size (minimum 40x12)
   - Or use the fallback console mode

2. **Character Display Issues**:
   - Switch to the `ascii` character set for maximum compatibility
   - Ensure your terminal font supports Unicode characters

3. **Terminal Corruption**:
   - If your terminal becomes corrupted, type `reset` and press Enter

## Development

When developing new features for the LED integration:

1. Start with simulated hardware to validate your code
2. Use the test script to verify specific components
3. Maintain compatibility with the existing punch card display
4. Document any configuration changes in this README
5. Add tests for new functionality

## Animation Format

Animations are defined in JSON files in the `animations/` directory. The format is:

```json
{
  "name": "Animation Name",
  "description": "Description of what the animation shows",
  "frames": [
    [
      [false, false, false, false],
      [false, false, false, false]
    ],
    [
      [true, false, true, false],
      [false, true, false, true]
    ]
  ]
}
```

Each frame is a 2D array of boolean values indicating LED states. 