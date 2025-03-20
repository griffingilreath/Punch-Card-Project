# Release Notes - Version 0.1.1 (The Visualization Update)

## 🌟 Overview

Version 0.1.1 focuses on enhancing the terminal display system with multiple character sets, improved error handling, and a robust fallback console mode. This update significantly improves the user experience when working with LED visualizations in both graphical and text modes.

## ✨ New Features

### Multiple Character Sets

- Added support for multiple character sets for LED visualization:
  - `default`: Filled blocks and dots (█, ·)
  - `block`: Filled blocks and spaces (█, space)
  - `circle`: Filled and empty circles (●, ○)
  - `star`: Filled and empty stars (★, ☆)
  - `ascii`: ASCII characters (#, .)
- Character sets can be selected via command-line arguments:
  ```
  python3 test_leds.py --test hardware --use-ui --char-set star
  ```

### Enhanced Terminal UI

- Implemented a split-screen curses-based UI with:
  - LED grid visualization panel
  - Debug message panel
  - Status line with system information
- Added scrollable debug message history
- Improved visual formatting and alignment

### Robust Fallback Console Mode

- Added automatic fallback to console mode when:
  - Terminal window is too small (minimum 40x12 required)
  - Curses library initialization fails
  - Other terminal capability issues occur
- Fallback mode features:
  - Grid visualization with row and column coordinates
  - LED state representation using the selected character set
  - Timestamped status and debug messages
  - Rate-limited updates to prevent console flooding

## 🛠️ Improvements

### Error Handling

- Added graceful handling of curses initialization failures
- Implemented recovery from terminal dimension issues
- Added exception handling for window creation problems
- Created thread-safe message processing

### Terminal Size Detection

- Added automatic terminal size detection
- Implemented appropriate warnings when terminal is too small
- Added command-line options to override detected dimensions:
  ```
  python3 test_leds.py --test hardware --use-ui --term-width 80 --term-height 24
  ```

### Performance Optimizations

- Added rate limiting for LED grid updates in console mode
- Improved message queue processing
- Reduced CPU usage when in fallback mode

### Documentation

- Created dedicated TERMINAL_DISPLAY.md documentation
- Updated README.md with new command-line options
- Enhanced README_LED.md with visualization options
- Updated DISPLAY_DEBUGGING.md with troubleshooting information
- Revised ROADMAP.md to reflect completed items

## 🐛 Bug Fixes

- Resolved synchronization issues between LED state manager and hardware controller
- Fixed display positioning inconsistency in various modes
- Addressed potential memory leaks from unmanaged curses windows
- Fixed error when terminal was resized during test execution

## 📋 Command-Line Options

New command-line options available in this version:

| Option | Description |
|--------|-------------|
| `--use-ui` | Enable terminal UI with split-screen display |
| `--term-width WIDTH` | Override terminal width detection |
| `--term-height HEIGHT` | Override terminal height detection |
| `--char-set SET` | Character set to use (default, block, circle, star, ascii) |
| `--verbose` | Show detailed LED state changes |

## 📚 Example Usage

```bash
# Run hardware verification with star character set
python3 test_leds.py --test hardware --use-ui --char-set star

# Run animations with verbose output
python3 test_leds.py --test animations --use-ui --verbose

# Run all tests with ASCII character set (maximum compatibility)
python3 test_leds.py --test all --use-ui --char-set ascii
```

## 🔄 Upgrading from v0.1.0

No database schema changes or breaking API changes were introduced in this version. To upgrade:

1. Pull the latest changes from GitHub
2. Run `pip install -r requirements.txt` to ensure all dependencies are installed
3. Run tests to verify functionality: `python3 test_leds.py --test all`

## 🙏 Acknowledgements

Special thanks to all contributors who helped implement and test these improvements. 