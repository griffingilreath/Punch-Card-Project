# LED Integration for Punch Card Project

This document explains how the LED hardware integration works for the Punch Card Project.

## Overview

The system is designed to synchronize physical LED displays with the terminal-based punch card visualization. The architecture ensures that when an LED is shown as "on" in the terminal interface, the corresponding physical LED is also illuminated.

## Components

The LED integration consists of four main components:

1. **LED State Manager**: The central component that maintains the state of all LEDs and serves as the single source of truth.
   - File: `src/led_state_manager.py`
   - Manages a 12x80 grid of LED states (matching the punch card format)
   - Provides methods to set individual LEDs, rows, columns, or the entire grid
   - Notifies observers when LED states change

2. **Hardware Controller**: Interfaces with physical LED hardware.
   - File: `src/hardware_controller.py`
   - Supports different hardware configurations (Raspberry Pi GPIO, etc.)
   - Observes the LED state manager and updates physical LEDs accordingly
   - Configurable through the YAML configuration file

3. **Display Adapter**: Bridges the existing punch card display with the LED state manager.
   - File: `src/display_adapter.py`
   - Patches methods in the `PunchCardDisplay` class to update the LED state manager
   - Monitors the punch card display for changes that might not be caught by method patching
   - Ensures animations and other visual effects are reflected on physical LEDs

4. **Main Application Integration**: Updates to integrate LED hardware with the main application.
   - File: `src/main.py`
   - Initializes and connects all components during startup
   - Provides command-line arguments for LED hardware configuration

## Configuration

LED hardware is configured through the YAML configuration file. A sample configuration file with detailed comments is provided in `config/led_config_example.yaml`.

Key configuration options:

```yaml
hardware:
  type: "simulated"    # "none", "simulated", or "rpi"
  brightness: 0.5      # LED brightness (0.0 to 1.0)
  update_rate: 30      # Hardware update rate (Hz)
  invert: false        # Invert LED states
```

## Supported Hardware

The system supports different hardware configurations:

1. **Terminal Only** (`hardware.type: "none"`): No physical LEDs, only the terminal display.

2. **Simulated Hardware** (`hardware.type: "simulated"`): Simulates physical LEDs by printing a representation to the console. Useful for testing.

3. **Raspberry Pi GPIO** (`hardware.type: "rpi"`): Controls physical LEDs using a Raspberry Pi's GPIO pins. Supports direct pin connections, shift registers, or LED matrix drivers.

## Hardware Connection Options

### Direct GPIO Connection (small grids)
- Connect LEDs directly to GPIO pins with appropriate resistors
- Good for testing with a small grid (e.g., 3x3)

### Shift Register Method (medium-sized grids)
- Use shift registers (e.g., 74HC595) to control more LEDs with fewer pins
- Good for grids up to 8x32

### LED Matrix Drivers (large grids)
- Use LED matrix driver ICs like MAX7219
- Recommended for full 12x80 grid
- Requires additional libraries (e.g., `luma.led_matrix`)

### Remote Controller
- Run the display software on one computer and LED control on a Raspberry Pi
- Configure using the `remote` section in the config file

## Animations

Animations are now synchronized between the terminal display and physical LEDs. The system includes:

1. **Splash Screen Animation**: Displayed when the application starts.
2. **Wave Animation**: Example animation that demonstrates LED synchronization.
3. **Custom Animations**: Can be defined in JSON files and loaded on startup.

## Adding New Animations

To create a new animation:

1. Create a JSON file in the `animations` directory:
```json
{
  "name": "my_animation",
  "frames": [
    [
      [true, false, ...],  // Row 1
      [false, true, ...],  // Row 2
      ...
    ],
    // Additional frames
  ]
}
```

2. Add it to the configuration:
```yaml
animations:
  custom:
    - "my_animation.json"
```

## Command-line Options

New command-line options for LED control:

```
--hardware-type {none,simulated,rpi}  # Type of hardware to use
```

## Examples

### Simple Example: Display "HELLO" on LEDs

```python
from led_state_manager import get_instance
from hardware_controller import create_hardware_controller
from punch_card import CHAR_MAPPING

# Get LED manager and create hardware controller
led_manager = get_instance()
controller = create_hardware_controller()

# Connect to hardware
if controller.connect():
    controller.start()
    
    # Display message
    message = "HELLO"
    for col, char in enumerate(message):
        led_manager.display_character(col, char, CHAR_MAPPING)
    
    # Wait for a while
    time.sleep(10)
    
    # Clean up
    controller.disconnect()
```

### Playing an Animation

```python
from led_state_manager import get_instance

# Get LED manager
led_manager = get_instance()

# Create a wave animation
led_manager.create_wave_animation("wave", frames=20)

# Play the animation
led_manager.play_animation("wave", repeat=3, frame_delay=0.1)
```

## Troubleshooting

If you encounter issues with the LED hardware:

1. Check your configuration file for correct settings.
2. Ensure the hardware is properly connected and powered.
3. Check the console for error messages related to hardware connections.
4. Try running with `--hardware-type simulated` to see if the issue is with the hardware or software.

## Future Improvements

Planned improvements for the LED integration:

1. Support for more hardware types (Arduino, Teensy, etc.)
2. Web interface for remote control and monitoring
3. More advanced animations and effects
4. Integration with music/sound for synchronized audio-visual effects

## Dependencies

- For Raspberry Pi GPIO: `pip install RPi.GPIO`
- For LED matrix drivers: `pip install luma.led_matrix`
- For remote connections: `pip install paho-mqtt` (if using MQTT)

## Credits

LED integration developed by Griffin Gilreath for the Punch Card Project. 