# NeoPixel Integration - Phase 0 Prototype

This document outlines the implementation details for the initial prototype phase (Phase 0) of integrating NeoPixel LEDs with the Punch Card Display System. The prototype will use an 8x8 NeoPixel matrix connected to an Arduino, controlled via serial communication from the main Python application.

## Hardware Components

For the prototype, you'll need:

1. **8x8 NeoPixel Matrix** - [Adafruit NeoPixel NeoMatrix 8x8](https://www.adafruit.com/product/1487) or similar
2. **Arduino Nano/Uno** - Any Arduino board with at least one digital output pin and USB serial
3. **Power Supply** - 5V/2A DC power supply (do not power NeoPixels from Arduino's 5V pin for more than a few LEDs)
4. **Breadboard and Jumper Wires**
5. **470 Ohm Resistor** - For data line protection
6. **1000μF Capacitor** - For power stabilization

## Wiring Diagram

```
                            1000μF
                            Capacitor
                          +--------+
5V Power Supply ----+-----| + |  - |----+
                    |     +--------+    |
                    |                   |
Arduino 5V ---------+                   |
                                        |
Arduino GND ---------------------------+------ NeoPixel GND
                                       |
                    470Ω               |
Arduino Pin 6 ------/\/\/\-------------+------ NeoPixel DIN
```

## Arduino Code (arduino_neopixel_controller.ino)

This sketch receives commands from the Python application via serial and controls the NeoPixel matrix:

```cpp
/*
 * Arduino NeoPixel Controller for Punch Card Display System - Phase 0 Prototype
 */

#include <Adafruit_NeoPixel.h>

// NeoPixel configuration
#define PIN            6     // NeoPixel data pin
#define NUMPIXELS      64    // 8x8 grid

// Grid dimensions
int rows = 8;
int cols = 8;
float brightness = 0.5;
bool is_serpentine = true;   // Zigzag wiring pattern

// Initialize the NeoPixel library
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  
  // Initialize NeoPixels
  pixels.begin();
  pixels.setBrightness(brightness * 255);
  pixels.show(); // Initialize all pixels to 'off'
  
  // Send ready message
  Serial.println("READY");
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
}

void processCommand(String command) {
  // Parse the command
  int commaIndex = command.indexOf(',');
  if (commaIndex == -1) {
    // Single word command
    if (command == "CLEAR") {
      clearGrid();
      Serial.println("OK");
    }
    else if (command == "SHUTDOWN") {
      clearGrid();
      Serial.println("OK");
    }
    else if (command == "SHOW") {
      pixels.show();
      Serial.println("OK");
    }
    else {
      Serial.println("ERROR: Unknown command");
    }
    return;
  }
  
  // Multi-part command
  String cmd = command.substring(0, commaIndex);
  String params = command.substring(commaIndex + 1);
  
  if (cmd == "PIXEL") {
    // Format: PIXEL,row,col,r,g,b
    int values[5]; // row, col, r, g, b
    int currentIndex = 0;
    int nextComma = 0;
    
    for (int i = 0; i < 5 && nextComma != -1; i++) {
      nextComma = params.indexOf(',', currentIndex);
      if (nextComma != -1) {
        values[i] = params.substring(currentIndex, nextComma).toInt();
        currentIndex = nextComma + 1;
      } else {
        values[i] = params.substring(currentIndex).toInt();
      }
    }
    
    setPixel(values[0], values[1], values[2], values[3], values[4]);
    Serial.println("OK");
  }
  else if (cmd == "BRIGHTNESS") {
    // Format: BRIGHTNESS,value
    brightness = max(0.0, min(1.0, params.toFloat()));
    pixels.setBrightness(brightness * 255);
    pixels.show();
    Serial.println("OK");
  }
  else if (cmd == "TEST") {
    // Format: TEST,pattern
    if (params == "chase") {
      testChasePattern();
    }
    else if (params == "rainbow") {
      testRainbowPattern();
    }
    else {
      Serial.println("ERROR: Unknown test pattern");
      return;
    }
    Serial.println("OK");
  }
  else {
    Serial.println("ERROR: Unknown command");
  }
}

int getPixelIndex(int row, int col) {
  if (row < 0 || row >= rows || col < 0 || col >= cols) {
    return -1; // Out of bounds
  }
  
  if (is_serpentine) {
    // Serpentine layout (zigzag)
    if (row % 2 == 0) {
      // Even rows go left to right
      return row * cols + col;
    } else {
      // Odd rows go right to left
      return row * cols + (cols - 1 - col);
    }
  } else {
    // Regular grid layout
    return row * cols + col;
  }
}

void setPixel(int row, int col, int r, int g, int b) {
  int index = getPixelIndex(row, col);
  if (index != -1) {
    pixels.setPixelColor(index, pixels.Color(r, g, b));
  }
}

void clearGrid() {
  pixels.clear();
  pixels.show();
}

void testChasePattern() {
  // Moving dot pattern
  for (int i = 0; i < rows * cols; i++) {
    pixels.clear();
    int row = i / cols;
    int col = i % cols;
    int index = getPixelIndex(row, col);
    pixels.setPixelColor(index, pixels.Color(255, 255, 255));
    pixels.show();
    delay(50);
  }
  clearGrid();
}

void testRainbowPattern() {
  // Rainbow pattern
  for (int j = 0; j < 256; j++) {
    for (int i = 0; i < rows * cols; i++) {
      int row = i / cols;
      int col = i % cols;
      int index = getPixelIndex(row, col);
      pixels.setPixelColor(index, Wheel((i + j) & 255));
    }
    pixels.show();
    delay(20);
  }
  clearGrid();
}

// Input a value 0 to 255 to get a color value.
uint32_t Wheel(byte WheelPos) {
  WheelPos = 255 - WheelPos;
  if (WheelPos < 85) {
    return pixels.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  }
  if (WheelPos < 170) {
    WheelPos -= 85;
    return pixels.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
  WheelPos -= 170;
  return pixels.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
}
```

## Python NeoPixel Controller Class

This class provides an abstraction for controlling the NeoPixel matrix from the Python application:

```python
"""
NeoPixel Controller for Punch Card Display System - Phase 0 Prototype

This module provides a simple interface for controlling a NeoPixel LED grid
to display the current state of the punch card display.
"""

import time
import serial
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Color:
    """Simple color representation with RGB values."""
    r: int
    g: int
    b: int
    
    def as_tuple(self) -> Tuple[int, int, int]:
        """Return color as an RGB tuple."""
        return (self.r, self.g, self.b)
    
    def as_hex(self) -> str:
        """Return color as a hex string."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
    
    @classmethod
    def from_hex(cls, hex_color: str) -> 'Color':
        """Create a Color from a hex string."""
        hex_color = hex_color.lstrip('#')
        return cls(
            r=int(hex_color[0:2], 16),
            g=int(hex_color[2:4], 16),
            b=int(hex_color[4:6], 16)
        )

# Default colors
COLOR_ON = Color(255, 255, 255)  # White
COLOR_OFF = Color(0, 0, 0)       # Black
COLOR_ERROR = Color(255, 0, 0)   # Red

class NeoPixelController:
    """Controller for NeoPixel LED grid, with fallback to terminal simulation."""
    
    def __init__(self, 
                 rows: int = 8, 
                 columns: int = 8, 
                 hardware_enabled: bool = False,
                 port: str = "/dev/ttyUSB0",
                 baudrate: int = 115200,
                 brightness: float = 0.5):
        """Initialize the NeoPixel controller."""
        self.rows = rows
        self.columns = columns
        self.hardware_enabled = hardware_enabled
        self.port = port
        self.baudrate = baudrate
        self.brightness = max(0.0, min(1.0, brightness))
        
        # Initialize the grid buffer
        self.grid_buffer = [[COLOR_OFF for _ in range(columns)] for _ in range(rows)]
        
        # Physical hardware connection
        self.serial = None
        
        # Connect to hardware if enabled
        if self.hardware_enabled:
            self._connect_hardware()
    
    def _connect_hardware(self) -> bool:
        """Connect to the Arduino controller."""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            
            # Wait for Arduino to reset
            time.sleep(2)
            
            # Check for READY message
            response = self.serial.readline().decode('utf-8').strip()
            if response != "READY":
                print(f"Unexpected response from Arduino: {response}")
                self.serial.close()
                self.serial = None
                return False
            
            # Set initial brightness
            self._send_command(f"BRIGHTNESS,{self.brightness}")
            
            return True
        except Exception as e:
            print(f"Error connecting to Arduino: {e}")
            if self.serial:
                self.serial.close()
                self.serial = None
            return False
    
    def _send_command(self, command: str) -> bool:
        """Send a command to the Arduino and wait for acknowledgment."""
        if not self.serial:
            return False
        
        try:
            # Send command with newline
            self.serial.write(f"{command}\n".encode('utf-8'))
            
            # Wait for response
            response = self.serial.readline().decode('utf-8').strip()
            return response == "OK"
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
    
    def set_pixel(self, row: int, col: int, color: Color) -> None:
        """Set a single pixel in the grid."""
        if 0 <= row < self.rows and 0 <= col < self.columns:
            self.grid_buffer[row][col] = color
            
            if self.hardware_enabled and self.serial:
                self._send_command(f"PIXEL,{row},{col},{color.r},{color.g},{color.b}")
    
    def update_grid(self, grid: List[List[bool]], color_on: Optional[Color] = None) -> None:
        """Update the entire grid at once from a boolean grid."""
        color_on = color_on or COLOR_ON
        
        # Update local buffer
        for row in range(min(len(grid), self.rows)):
            for col in range(min(len(grid[row]), self.columns)):
                self.grid_buffer[row][col] = color_on if grid[row][col] else COLOR_OFF
        
        # Send to hardware
        if self.hardware_enabled and self.serial:
            # Clear the grid first
            self._send_command("CLEAR")
            
            # Send each pixel
            for row in range(self.rows):
                for col in range(self.columns):
                    color = self.grid_buffer[row][col]
                    if color.r > 0 or color.g > 0 or color.b > 0:  # Only send non-black pixels
                        self._send_command(f"PIXEL,{row},{col},{color.r},{color.g},{color.b}")
            
            # Show the updated grid
            self._send_command("SHOW")
    
    def update_from_punch_card(self, punch_card, card_rows: int = 12, scale_factor: float = 1.0) -> None:
        """Update the LED grid from a punch card display.
        
        This is a specialized method that converts the punch card display 
        to an appropriate format for the LED grid.
        
        Args:
            punch_card: The PunchCardDisplay instance
            card_rows: Number of rows to capture from the punch card
            scale_factor: Scaling factor for the grid (for smaller displays)
        """
        # Create a boolean grid from the punch card
        grid = [[False for _ in range(self.columns)] for _ in range(self.rows)]
        
        # Extract the punch card state - this will need to be adapted based on
        # how the punch card state is represented in the actual implementation
        try:
            # This is an example - actual implementation will vary
            for i in range(min(card_rows, self.rows)):
                for j in range(min(80, self.columns)):
                    # Check if there's a punch hole at this position
                    # This is a placeholder - actual code will depend on PunchCardDisplay implementation
                    if hasattr(punch_card, 'card_grid') and punch_card.card_grid:
                        has_hole = bool(punch_card.card_grid[i][j])
                        row_idx = min(int(i * scale_factor), self.rows - 1)
                        col_idx = min(int(j * scale_factor), self.columns - 1)
                        grid[row_idx][col_idx] = has_hole
        except Exception as e:
            print(f"Error extracting punch card state: {e}")
        
        # Update the grid
        self.update_grid(grid)
    
    def clear(self) -> None:
        """Clear the entire grid (set all pixels to off)."""
        for row in range(self.rows):
            for col in range(self.columns):
                self.grid_buffer[row][col] = COLOR_OFF
        
        if self.hardware_enabled and self.serial:
            self._send_command("CLEAR")
    
    def test_pattern(self, pattern: str = "chase", duration: float = 5.0) -> None:
        """Display a test pattern on the LEDs.
        
        Args:
            pattern: Test pattern to display ("chase", "rainbow")
            duration: Duration to display the pattern in seconds
        """
        if self.hardware_enabled and self.serial:
            self._send_command(f"TEST,{pattern}")
        else:
            # For software simulation, implement test patterns
            print(f"Software simulation of {pattern} pattern for {duration}s")
            time.sleep(duration)
    
    def set_brightness(self, brightness: float) -> None:
        """Set the brightness of the LEDs."""
        self.brightness = max(0.0, min(1.0, brightness))
        
        if self.hardware_enabled and self.serial:
            self._send_command(f"BRIGHTNESS,{self.brightness}")
    
    def shutdown(self) -> None:
        """Safely shut down the LED controller."""
        # Turn off all LEDs
        self.clear()
        
        # Close serial connection if open
        if self.hardware_enabled and self.serial:
            self._send_command("SHUTDOWN")
            self.serial.close()
            self.serial = None
```

## Integration with Punch Card Display

To integrate the NeoPixel controller with the existing punch card display system, you'll need to:

1. Add the NeoPixelController class to the project
2. Initialize the controller in the main application
3. Update the controller whenever the punch card display changes

Here's an example of how to integrate it with the main application:

```python
# In main.py or another appropriate entry point

from punch_card import PunchCardDisplay
from neopixel_controller import NeoPixelController

def main():
    # Initialize the punch card display
    punch_card = PunchCardDisplay()
    
    # Initialize the NeoPixel controller (disabled by default)
    neopixel_enabled = False  # Set to True when hardware is connected
    neopixel_port = "/dev/ttyUSB0"  # Change to match your system
    
    if neopixel_enabled:
        led_controller = NeoPixelController(
            rows=8,
            columns=8,
            hardware_enabled=True,
            port=neopixel_port,
            brightness=0.5
        )
    else:
        led_controller = None
    
    # Add the LED controller to the punch card display
    punch_card.led_controller = led_controller
    
    # Run the application
    try:
        # ... existing application logic ...
        
        # Make sure to update the LED controller when the punch card state changes
        # This could be implemented in the PunchCardDisplay class
        
    finally:
        # Ensure proper shutdown
        if led_controller:
            led_controller.shutdown()

if __name__ == "__main__":
    main()
```

## Modifications to PunchCardDisplay Class

You'll need to modify the `PunchCardDisplay` class to update the LED controller when the display changes. Here's an example of how this could be implemented:

```python
# In punch_card.py, modify the PunchCardDisplay class

def _display_grid(self, holes, sync_leds=True):
    """Display the current punch card grid with holes punched."""
    # ... existing display code ...
    
    # Update LED controller if available
    if sync_leds and hasattr(self, 'led_controller') and self.led_controller:
        self.led_controller.update_from_punch_card(self)
```

## Next Steps

After completing the Phase 0 prototype:

1. **Test the Integration**: Verify that the LED display correctly mirrors the terminal display.

2. **Optimize Communication**: The current approach sends each pixel individually, which can be slow. Future versions could send the entire grid in a more efficient format.

3. **Scale to Larger Grid**: Plan for scaling to larger LED arrays using the lessons learned from the 8x8 prototype.

4. **Web Integration**: Begin implementing the web API to enable remote monitoring of the punch card system.

5. **Document Findings**: Document any issues encountered and lessons learned to inform the development of Phase 1.

## Resources

- [Adafruit NeoPixel Guide](https://learn.adafruit.com/adafruit-neopixel-uberguide)
- [Arduino Serial Communication](https://www.arduino.cc/reference/en/language/functions/communication/serial/)
- [PySerial Documentation](https://pyserial.readthedocs.io/en/latest/) 