# Testing the Punch Card Project

This document provides information about testing the Punch Card Project, including how to run tests, what tests are available, and how to troubleshoot common issues.

## Available Test Scripts

The project includes several test scripts for different purposes:

1. **test_leds.py** - The main test script with integration to the project's components.
2. **run_stable_test.py** - A more stable version that handles terminal UI issues better.
3. **run_clean_test.py** - A wrapper script that runs tests with console output only.
4. **direct_led_test.py** - A standalone script that doesn't depend on project structure.

## Common Test Commands

```bash
# Run all tests with ASCII character set
python3 test_leds.py --test all --char-set ascii

# Run hardware verification test
python3 test_leds.py --test hardware --char-set default

# Run animations test
python3 test_leds.py --test animations --char-set block

# Run a stable version of the tests
python3 run_stable_test.py --char-set circle

# Run a clean version without terminal UI issues
python3 run_clean_test.py --test all --char-set ascii

# Run the standalone direct LED test
python3 direct_led_test.py --char-set ascii
```

## Available Character Sets

The tests support different character sets for LED visualization:

- **default**: Filled/empty circle (`●`, `○`)
- **block**: Block/space (`█`, ` `)
- **circle**: Filled/empty circle (`●`, `○`)
- **star**: Filled/empty star (`★`, `☆`)
- **ascii**: X/period (`X`, `.`)

## Troubleshooting Terminal Display Issues

When running tests, you might encounter glitchy terminal displays, especially with the curses-based UI. Here are some ways to resolve these issues:

### 1. Use a Different Character Set

If you're experiencing display issues, try using a different character set:

```bash
python3 test_leds.py --test all --char-set ascii
```

ASCII characters are the most compatible across different terminal emulators.

### 2. Use the Standalone LED Test

For basic LED pattern testing without the full project dependencies, use the standalone test script:

```bash
python3 direct_led_test.py --char-set ascii
```

This script provides a clean way to test LED patterns with minimal dependencies.

### 3. Disable the Terminal UI

If you're experiencing issues with the curses-based UI, you can force the test to use console output:

```bash
FORCE_CONSOLE=1 python3 test_leds.py --test all
```

### 4. Terminal Size Requirements

The curses-based UI requires a terminal size of at least 40x12 characters. If your terminal is smaller, the test will automatically fall back to console output.

To check your terminal size:

```bash
# Get terminal size on macOS/Linux
tput cols && tput lines
```

### 5. Run Test in Buffered Mode

The `run_clean_test.py` script runs the tests with buffered output, which can help prevent display glitches:

```bash
python3 run_clean_test.py --test all --char-set ascii
```

## Creating Custom Tests

You can create custom tests by extending the existing test scripts. The `direct_led_test.py` script provides a good starting point for creating custom LED pattern tests.

## Continuous Integration Testing

For automated testing in CI environments, use the `run_clean_test.py` script to ensure consistent output without terminal UI issues:

```bash
python3 run_clean_test.py --test all --char-set ascii
```

This script returns proper exit codes that can be used in CI pipelines to detect test failures. 