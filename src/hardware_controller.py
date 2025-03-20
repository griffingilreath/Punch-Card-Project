#!/usr/bin/env python3
"""
Hardware Controller for the Punch Card Project

This module provides a hardware abstraction layer for controlling physical LED hardware.
It integrates with the LED state manager to ensure that physical LEDs reflect the
same state as what's displayed in the terminal.

The controller is designed to be flexible and easily extended to support different
hardware configurations (Raspberry Pi GPIO, Teensy, etc.).
"""

import time
from typing import List, Dict, Optional, Callable
import threading
import json
import os
from pathlib import Path

# Import the LED state manager
from src.led_state_manager import get_instance as get_led_manager

# Import the terminal display (if available)
try:
    from src.terminal_display import get_instance as get_terminal_display
    TERMINAL_DISPLAY_AVAILABLE = True
except ImportError:
    TERMINAL_DISPLAY_AVAILABLE = False
    print("Terminal display module not available. Using standard console output.")


class HardwareController:
    """
    Base class for hardware controllers. 
    
    This class provides common functionality and a standard interface
    for different hardware implementations.
    """
    
    def __init__(self, rows: int = 12, columns: int = 80, config_path: Optional[str] = None):
        """
        Initialize the hardware controller.
        
        Args:
            rows: Number of rows in the LED grid
            columns: Number of columns in the LED grid
            config_path: Path to configuration file (optional)
        """
        self.rows = rows
        self.columns = columns
        self.is_connected = False
        self._running = False
        self._thread = None
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Get the LED state manager
        self.led_manager = get_led_manager(rows, columns)
        
        # Register with the LED state manager to receive updates
        self.led_manager.register_observer(self._on_led_state_changed)
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dict: Configuration dictionary
        """
        default_config = {
            'hardware': {
                'type': 'none',  # 'none', 'rpi', 'teensy'
                'brightness': 0.5,
                'update_rate': 30,  # Hz
                'invert': False,  # Invert LED states (True = off, False = on)
                'enabled': True
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    if config_path.endswith('.json'):
                        loaded_config = json.load(f)
                    elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
                        try:
                            import yaml
                            loaded_config = yaml.safe_load(f)
                        except ImportError:
                            print("Warning: YAML module not installed, using default config")
                            return default_config
                    else:
                        print(f"Warning: Unsupported config file format: {config_path}")
                        return default_config
                
                # Update default config with loaded values
                if 'hardware' in loaded_config:
                    default_config['hardware'].update(loaded_config['hardware'])
                
                return default_config
            except Exception as e:
                print(f"Error loading config from {config_path}: {e}")
                return default_config
        else:
            return default_config
    
    def connect(self) -> bool:
        """
        Connect to the physical hardware.
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        # Base implementation does nothing
        self.is_connected = True
        return True
    
    def disconnect(self) -> None:
        """Disconnect from the physical hardware."""
        self.is_connected = False
        self.stop()
    
    def start(self) -> None:
        """Start the hardware controller in a background thread."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop the hardware controller."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
    
    def _update_loop(self) -> None:
        """
        Update loop that runs in a background thread.
        
        This keeps the physical hardware in sync with the LED state manager.
        """
        update_interval = 1.0 / self.config['hardware']['update_rate']
        last_update = time.time()
        
        while self._running:
            # Calculate time since last update
            current_time = time.time()
            elapsed = current_time - last_update
            
            # Update hardware state if enough time has passed
            if elapsed >= update_interval:
                self._update_hardware()
                last_update = current_time
            
            # Sleep a bit to prevent CPU thrashing
            time.sleep(max(0.001, update_interval / 10))
    
    def _update_hardware(self) -> None:
        """
        Update the physical hardware state.
        
        This method should be overridden by subclasses to implement
        hardware-specific updates.
        """
        # Base implementation does nothing
        pass
    
    def _on_led_state_changed(self, row: int, column: int, state: bool) -> None:
        """
        Handle LED state changes from the state manager.
        
        Args:
            row: Row index (-1 for special signals)
            column: Column index (-1 for special signals)
            state: New state
        """
        # Special signal (-1, -1): Full grid update
        if row == -1 and column == -1:
            self._update_hardware()
        # Special signal (-1, column): Column update
        elif row == -1:
            self._update_column(column)
        # Special signal (row, -1): Row update
        elif column == -1:
            self._update_row(row)
        # Single LED update
        else:
            self._update_single_led(row, column, state)
    
    def _update_single_led(self, row: int, column: int, state: bool) -> None:
        """
        Update a single LED on the physical hardware.
        
        Args:
            row: Row index
            column: Column index
            state: New state (True = on, False = off)
        """
        # Base implementation just triggers a full update
        self._update_hardware()
    
    def _update_row(self, row: int) -> None:
        """
        Update an entire row on the physical hardware.
        
        Args:
            row: Row index
        """
        # Base implementation just triggers a full update
        self._update_hardware()
    
    def _update_column(self, column: int) -> None:
        """
        Update an entire column on the physical hardware.
        
        Args:
            column: Column index
        """
        # Base implementation just triggers a full update
        self._update_hardware()
    
    def set_brightness(self, brightness: float) -> None:
        """
        Set the brightness of all LEDs.
        
        Args:
            brightness: Brightness level (0.0 to 1.0)
        """
        if 0.0 <= brightness <= 1.0:
            self.config['hardware']['brightness'] = brightness


class RPiHardwareController(HardwareController):
    """
    Hardware controller implementation for Raspberry Pi GPIO.
    
    This controller uses the RPi.GPIO library to control LED matrices
    connected to the Raspberry Pi's GPIO pins.
    """
    
    def __init__(self, rows: int = 12, columns: int = 80, config_path: Optional[str] = None):
        """Initialize the Raspberry Pi hardware controller."""
        super().__init__(rows, columns, config_path)
        
        # RPi-specific initialization
        self.gpio_available = False
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.gpio_available = True
        except ImportError:
            print("Warning: RPi.GPIO module not available. Hardware control disabled.")
            print("If you're running on a Raspberry Pi, install with: pip install RPi.GPIO")
    
    def connect(self) -> bool:
        """
        Connect to the Raspberry Pi GPIO.
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        if not self.gpio_available:
            return False
        
        try:
            # Setup GPIO - this is just a placeholder, you'll need to customize
            # this based on your actual hardware configuration
            self.GPIO.setmode(self.GPIO.BCM)
            
            # Example pin setup - replace with your actual pin mapping
            # In a real implementation, you'd likely use a shift register or
            # LED matrix driver IC to control all 12x80=960 LEDs
            
            # This is just a simplified example where we'd control a subset
            # For example, controlling a 8x8 LED matrix at the start
            self.led_pins = []
            for row in range(min(8, self.rows)):
                row_pins = []
                for col in range(min(8, self.columns)):
                    # Calculate pin number based on row and column
                    # This is just an example, replace with your actual mapping
                    pin = (row * 8 + col) % 20 + 2  # Using pins 2-21 as an example
                    self.GPIO.setup(pin, self.GPIO.OUT)
                    row_pins.append(pin)
                self.led_pins.append(row_pins)
            
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Error connecting to Raspberry Pi GPIO: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the Raspberry Pi GPIO."""
        if self.gpio_available and self.is_connected:
            self.stop()
            self.GPIO.cleanup()
        self.is_connected = False
    
    def _update_hardware(self) -> None:
        """Update all LEDs connected to the Raspberry Pi GPIO."""
        if not self.gpio_available or not self.is_connected:
            return
        
        # Get current LED states from the manager
        led_states = self.led_manager.get_grid()
        
        # Update GPIO pins based on LED states
        # This is just an example for a small subset of LEDs
        try:
            for row in range(min(len(self.led_pins), self.rows)):
                for col in range(min(len(self.led_pins[row]), self.columns)):
                    state = led_states[row][col]
                    if self.config['hardware']['invert']:
                        state = not state
                    self.GPIO.output(self.led_pins[row][col], self.GPIO.HIGH if state else self.GPIO.LOW)
        except Exception as e:
            print(f"Error updating Raspberry Pi GPIO: {e}")
    
    def _update_single_led(self, row: int, column: int, state: bool) -> None:
        """
        Update a single LED on the Raspberry Pi GPIO.
        
        Args:
            row: Row index
            column: Column index
            state: New state (True = on, False = off)
        """
        if not self.gpio_available or not self.is_connected:
            return
        
        try:
            if (row < len(self.led_pins) and 
                column < len(self.led_pins[row])):
                
                if self.config['hardware']['invert']:
                    state = not state
                
                self.GPIO.output(self.led_pins[row][column], 
                               self.GPIO.HIGH if state else self.GPIO.LOW)
        except Exception as e:
            print(f"Error updating single LED: {e}")


class SimulatedHardwareController(HardwareController):
    """
    Simulated hardware controller for development and testing.
    
    This controller doesn't control physical hardware but simulates it
    by printing LED states to the console.
    """
    
    def __init__(self, rows: int = 12, columns: int = 80, config_path: Optional[str] = None):
        """Initialize the simulated hardware controller."""
        super().__init__(rows, columns, config_path)
        # For simulation, use a fast update rate
        self.config['hardware']['update_rate'] = 30  # Hz
        self.last_print_time = 0
        self.print_interval = 2.0  # Only print updates every 2 seconds
        self.verbose = False  # Set to False to reduce console output
        self._updating = False  # Flag to prevent recursion
        
        # Terminal display integration
        self.use_terminal_display = TERMINAL_DISPLAY_AVAILABLE
        self.terminal_display = None
        if self.use_terminal_display:
            self.terminal_display = get_terminal_display(rows, columns)
    
    def connect(self) -> bool:
        """Connect to the simulated hardware."""
        if self.use_terminal_display:
            self.terminal_display.start()
            self.terminal_display.set_status("Connected to simulated hardware", "info")
            self.terminal_display.add_debug_message("Initialized simulated hardware controller", "info")
        else:
            print("Connected to simulated hardware")
        
        self.is_connected = True
        return True
    
    def disconnect(self) -> None:
        """Disconnect from the simulated hardware."""
        if self.use_terminal_display:
            self.terminal_display.set_status("Disconnecting from simulated hardware", "info")
            self.terminal_display.add_debug_message("Disconnected from simulated hardware", "info")
            # Wait a moment for the message to be displayed
            time.sleep(0.5)
            self.terminal_display.stop()
        
        self.stop()
        self.is_connected = False
    
    def _update_hardware(self) -> None:
        """Update the simulated hardware (display in terminal UI or print to console)."""
        if not self.is_connected or self._updating:
            return
            
        self._updating = True
        
        try:
            # Get current LED states
            led_states = self.led_manager.get_grid()
            
            if self.use_terminal_display:
                # Update the terminal display with the current LED states
                self.terminal_display.update_led_grid(led_states)
            elif self.verbose:
                # Only print updates occasionally to avoid console spam
                current_time = time.time()
                if current_time - self.last_print_time < self.print_interval:
                    return
                    
                self.last_print_time = current_time
                
                # Print a small section of the grid to avoid console spam
                print("\nSimulated Hardware State (8x8 section):")
                for row in range(min(8, self.rows)):
                    row_str = ""
                    for col in range(min(8, self.columns)):
                        row_str += "█" if led_states[row][col] else "·"
                    print(row_str)
                print()  # Extra newline
        finally:
            self._updating = False

    def _on_led_state_changed(self, row: int, column: int, state: bool) -> None:
        """
        Custom handler for LED state changes.
        
        For simulation, we'll just do minimal work to avoid performance issues.
        """
        # Do nothing if we're already updating to prevent recursion
        if self._updating:
            return
            
        self._updating = True
        
        try:
            # When simulating, we'll just handle specific LED changes
            if row >= 0 and column >= 0:
                # Individual LED update
                if self.use_terminal_display:
                    self.terminal_display.update_led(row, column, state)
                    if self.verbose:
                        self.terminal_display.add_debug_message(f"LED [{row},{column}] set to {state}", "info")
            elif row == -1 and column == -1:
                # Full grid update - handle in _update_hardware
                pass
            elif row == -1:
                # Column update - handle in _update_hardware
                if self.use_terminal_display and self.verbose:
                    self.terminal_display.add_debug_message(f"Column {column} updated", "info")
            elif column == -1:
                # Row update - handle in _update_hardware
                if self.use_terminal_display and self.verbose:
                    self.terminal_display.add_debug_message(f"Row {row} updated", "info")
        finally:
            self._updating = False


# Factory function to create the appropriate hardware controller
def create_hardware_controller(config_path: Optional[str] = None) -> HardwareController:
    """
    Create a hardware controller based on configuration.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        HardwareController: The appropriate hardware controller instance
    """
    # Load config to determine hardware type
    default_config = {
        'hardware': {
            'type': 'simulated'
        }
    }
    
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                if config_path.endswith('.json'):
                    loaded_config = json.load(f)
                elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    try:
                        import yaml
                        loaded_config = yaml.safe_load(f)
                    except ImportError:
                        return SimulatedHardwareController(config_path=config_path)
                else:
                    return SimulatedHardwareController(config_path=config_path)
            
            if 'hardware' in loaded_config and 'type' in loaded_config['hardware']:
                hardware_type = loaded_config['hardware']['type'].lower()
            else:
                hardware_type = 'simulated'
        except Exception:
            return SimulatedHardwareController(config_path=config_path)
    else:
        hardware_type = 'simulated'
    
    # Create the appropriate controller
    if hardware_type == 'rpi':
        return RPiHardwareController(config_path=config_path)
    else:  # Default to simulated
        return SimulatedHardwareController(config_path=config_path)


if __name__ == "__main__":
    # Example usage
    controller = create_hardware_controller()
    
    # Connect to hardware
    if controller.connect():
        print("Connected to hardware")
        
        # Start the controller
        controller.start()
        
        # Get the LED state manager
        led_manager = get_led_manager()
        
        # Test setting some LEDs
        print("Setting LED patterns...")
        
        # Set a pattern
        for i in range(min(8, controller.rows)):
            led_manager.set_led(i, i, True)
        
        # Wait for the hardware to update
        time.sleep(2)
        
        # Set another pattern
        for i in range(min(8, controller.rows)):
            for j in range(min(8, controller.columns)):
                led_manager.set_led(i, j, (i + j) % 2 == 0)
        
        # Wait for the hardware to update
        time.sleep(2)
        
        # Clean up
        print("Cleaning up...")
        controller.disconnect()
    else:
        print("Failed to connect to hardware") 