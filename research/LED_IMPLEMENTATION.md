# LED-Based IBM Punch Card Display Implementation

This document provides detailed technical specifications and implementation guidelines for creating a physical LED grid that accurately represents an IBM 80-column punch card.

## 12×80 LED Grid Design

### Grid Specifications

| Feature | Specification |
|---------|---------------|
| Grid Dimensions | 12 rows × 80 columns (960 LEDs total) |
| LED Type | Individually addressable RGB LEDs (WS2812B/NeoPixels) |
| Horizontal Spacing | ~0.087 inches (~2.21 mm) between columns |
| Vertical Spacing | ~0.25 inches between rows |
| Physical Dimensions | ~7⅜ × 3¼ inches (to match IBM punch card) |
| LED Control Protocol | Serial data (one-wire interface for WS2812B) |

### LED Layout Options

#### Option 1: LED Strip Implementation

Using WS2812B LED strips (typically 144 LEDs/meter or 60 LEDs/meter):

```
 ┌──────────────────────────────────────────────────┐
 │ → → → → → → → → → → → → → → → → → → → → → → → → → → │ Row 12
 │ ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← │ Row 11
 │ → → → → → → → → → → → → → → → → → → → → → → → → → → │ Row 0
 │ ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← │ Row 1
 │ → → → → → → → → → → → → → → → → → → → → → → → → → → │ Row 2
 │ ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← │ Row 3
 │ → → → → → → → → → → → → → → → → → → → → → → → → → → │ Row 4
 │ ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← │ Row 5
 │ → → → → → → → → → → → → → → → → → → → → → → → → → → │ Row 6
 │ ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← │ Row 7
 │ → → → → → → → → → → → → → → → → → → → → → → → → → → │ Row 8
 │ ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← │ Row 9
 └──────────────────────────────────────────────────┘
        (Arrows indicate strip routing direction)
```

Considerations:
- Serpentine pattern requires translating between physical and logical positions
- Standard LED strip spacing may not exactly match card hole spacing
- Requires cutting and soldering strips between rows
- Reduces wiring complexity compared to individual LEDs

#### Option 2: Individual LED Implementation

Using discrete WS2812B LEDs mounted on a PCB or perf board:

```
 ┌──────────────────────────────────────────────────┐
 │ ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● │ Row 12
 │ ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● │ Row 11
 │ ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● │ Row 0
 │ ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● │ Row 1
 │ ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● │ Row 2
 │ ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● │ Row 3
 │ ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● │ Row 4
 │ ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● │ Row 5
 │ ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● │ Row 6
 │ ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● │ Row 7
 │ ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● │ Row 8
 │ ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● │ Row 9
 └──────────────────────────────────────────────────┘
               (Each ● represents one LED)
```

Considerations:
- Enables precise spacing to match original punch card
- Significantly more soldering and assembly time
- Direct mapping between physical and logical positions
- Better aesthetic result due to proper spacing

## Power Consumption and Electrical Requirements

### Power Calculation

| Component | Specification |
|-----------|--------------|
| LED Count | 960 LEDs |
| Maximum Current per LED | ~60 mA at full white (all RGB channels at max) |
| Working Current per LED | ~20 mA on average (typical usage) |
| Total Maximum Current | 960 × 60 mA = 57.6 A (theoretical maximum) |
| Total Working Current | 960 × 20 mA = 19.2 A (typical usage) |
| Voltage | 5V DC |
| Maximum Power | 5V × 57.6A = 288W (theoretical maximum) |
| Working Power | 5V × 19.2A = 96W (typical usage) |

### Power Supply Recommendations

For reliable operation, the power supply should provide:
- 5V DC output
- 20-30A capacity (30A recommended for headroom)
- Clean, regulated output with low ripple
- Protection features: overcurrent, overvoltage, thermal

Recommended power supply types:
- Mean Well LRS-150-5 (5V, 30A, 150W)
- Mean Well RSP-200-5 (5V, 40A, 200W)

### Power Distribution

To prevent voltage drop and ensure all LEDs receive adequate power:

#### Power Injection Points

Divide the 960 LEDs into 4 sections of 240 LEDs each:

```
Section 1   Section 2   Section 3   Section 4
┌─────────┬─────────┬─────────┬─────────┐
│ Row 12  │ Row 12  │ Row 12  │ Row 12  │
│   :     │   :     │   :     │   :     │
│ Row 9   │ Row 9   │ Row 9   │ Row 9   │
└─────────┴─────────┴─────────┴─────────┘
   5V+       5V+       5V+       5V+
   GND       GND       GND       GND
```

### Wiring Diagram

```
┌──── 5V Power Supply (5V, 30A) ────┐
│                                   │
│  +5V            GND               │
└─┬─┬─┬─┬─────────┬─┬─┬─┬───────────┘
  │ │ │ │         │ │ │ │
  │ │ │ │         │ │ │ │
  │ │ │ │         │ │ │ │
┌─┴─┴─┴─┴─────────┴─┴─┴─┴───────────┐
│ Power Distribution Board           │
│ (with 10A fuses for each section)  │
└─┬─────┬─────┬─────┬─┬─────┬─────┬─┘
  │     │     │     │ │     │     │
  │     │     │     │ │     │     │
┌─┴─┐ ┌─┴─┐ ┌─┴─┐ ┌─┴─┴─┐ ┌─┴─┐ ┌─┴─┐
│S1 │ │S2 │ │S3 │ │S4   │ │MCU│ │Logic│
│5V+│ │5V+│ │5V+│ │5V+  │ │5V+│ │5V+  │
│GND│ │GND│ │GND│ │GND  │ │GND│ │GND  │
└───┘ └───┘ └───┘ └─────┘ └───┘ └─────┘
```

### Wiring Recommendations

- Use 14 AWG wire for main power distribution
- Use 16-18 AWG for section power feeds
- Keep GND connections common across all sections
- Add decoupling capacitors (1000μF, 6.3V or higher) at each power injection point
- Use blade fuses (10A) for each section
- Include a master fuse (25A) at the power supply output

## Microcontroller Selection and LED Control

### Recommended Controllers

| Controller | Specifications | Advantages |
|------------|---------------|------------|
| Teensy 4.0 | 600 MHz ARM Cortex-M7, 1024KB RAM | High performance, excellent libraries, dedicated purpose |
| Teensy 4.1 | 600 MHz ARM Cortex-M7, 1024KB RAM, Ethernet | More I/O pins, network capability |
| Raspberry Pi 4 | 1.5 GHz quad-core ARM Cortex-A72, 2-8GB RAM | Full OS, network, UI capabilities |

### Controller Comparison

**Teensy Advantages:**
- Real-time performance
- Lower power consumption
- Precise timing control
- OctoWS2811 library supports high-speed LED control
- Dedicated for LED control

**Raspberry Pi Advantages:**
- Full Linux OS
- Network capabilities
- User interface options
- Can run other applications simultaneously
- Better for complex processing and data management

### Hybrid Approach

For optimal performance, consider a hybrid approach:

```
┌─────────────────┐      ┌─────────────────┐      ┌──────────────────┐
│                 │      │                 │ Data │                  │
│ Raspberry Pi 4  ├──────┤ Teensy 4.0/4.1  ├──────┤ 12×80 LED Matrix │
│                 │ USB  │                 │      │                  │
└─────────────────┘      └─────────────────┘      └──────────────────┘
       UI, Web            LED Control              Display Hardware
     Application          and Timing
```

### Software Implementation

#### Teensy Code Example (using OctoWS2811 library)

```cpp
#include <OctoWS2811.h>

#define NUM_ROWS 12
#define NUM_COLS 80
#define NUM_LEDS (NUM_ROWS * NUM_COLS)

// LED memory
const int ledsPerPin = NUM_LEDS / 8;
DMAMEM int displayMemory[ledsPerPin * 6];
int drawingMemory[ledsPerPin * 6];

// OctoWS2811 configuration
const int config = WS2811_GRB | WS2811_800kHz;
OctoWS2811 leds(ledsPerPin, displayMemory, drawingMemory, config);

// Card data (12×80 grid, each bit represents a hole)
bool cardData[NUM_ROWS][NUM_COLS] = {0};

void setup() {
  Serial.begin(115200);
  leds.begin();
  leds.show();  // Initialize all LEDs to off
}

void loop() {
  // Check if data is available from Raspberry Pi
  if (Serial.available()) {
    processSerialData();
    updateLEDs();
  }
}

// Process serial data from Raspberry Pi
void processSerialData() {
  // Format: row,col,state;row,col,state;...
  String data = Serial.readStringUntil('\n');
  int startIdx = 0;
  int endIdx = data.indexOf(';', startIdx);
  
  while (endIdx != -1) {
    String chunk = data.substring(startIdx, endIdx);
    
    int firstComma = chunk.indexOf(',');
    int secondComma = chunk.indexOf(',', firstComma + 1);
    
    if (firstComma != -1 && secondComma != -1) {
      int row = chunk.substring(0, firstComma).toInt();
      int col = chunk.substring(firstComma + 1, secondComma).toInt();
      int state = chunk.substring(secondComma + 1).toInt();
      
      if (row >= 0 && row < NUM_ROWS && col >= 0 && col < NUM_COLS) {
        cardData[row][col] = state;
      }
    }
    
    startIdx = endIdx + 1;
    endIdx = data.indexOf(';', startIdx);
  }
}

// Update LED display to match card data
void updateLEDs() {
  for (int row = 0; row < NUM_ROWS; row++) {
    for (int col = 0; col < NUM_COLS; col++) {
      // Calculate LED index (based on serpentine pattern)
      int index;
      if (row % 2 == 0) {
        // Even rows go left to right
        index = row * NUM_COLS + col;
      } else {
        // Odd rows go right to left
        index = row * NUM_COLS + (NUM_COLS - 1 - col);
      }
      
      // Set LED color based on card data
      if (cardData[row][col]) {
        leds.setPixel(index, 0xFFFFFF);  // White for punched hole
      } else {
        leds.setPixel(index, 0x000000);  // Off for no hole
      }
    }
  }
  
  leds.show();  // Update the LED display
}
```

#### Raspberry Pi Code Example (Python)

```python
#!/usr/bin/env python3
import serial
import time

class LEDController:
    def __init__(self, port="/dev/ttyACM0", baud_rate=115200):
        """Initialize the LED controller with serial connection to Teensy."""
        self.serial = serial.Serial(port, baud_rate)
        time.sleep(2)  # Wait for Teensy to initialize
        self.rows = 12
        self.cols = 80
        # Initialize empty card (no holes)
        self.card_data = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
    def clear_card(self):
        """Clear all holes from the card."""
        self.card_data = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
    def set_hole(self, row, col, state):
        """Set or clear a hole at the specified position."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.card_data[row][col] = 1 if state else 0
            
    def display_text(self, text, row_offset=0, col_offset=0):
        """Display text on the punch card using hole patterns."""
        self.clear_card()
        
        # Character to hole pattern mapping (simplified example)
        char_to_holes = {
            'A': [(12, 1)],
            'B': [(12, 2)],
            # ... add all character mappings
            '0': [(0,)],
            '1': [(1,)],
            # ... add more characters
            ' ': []
        }
        
        col = col_offset
        for char in text:
            if char.upper() in char_to_holes and col < self.cols:
                for hole in char_to_holes[char.upper()]:
                    for row in hole:
                        row_idx = row if row < 10 else row - 10 + 0  # Adjust for rows 10-12
                        self.set_hole(row_idx + row_offset, col, 1)
                col += 1
                
    def update_display(self):
        """Send the current card data to the Teensy controller."""
        update_data = []
        
        for row in range(self.rows):
            for col in range(self.cols):
                if self.card_data[row][col]:
                    update_data.append(f"{row},{col},1")
                    
        # Send data as a semicolon-separated list of row,col,state
        command = ";".join(update_data) + "\n"
        self.serial.write(command.encode())
        
    def close(self):
        """Close the serial connection."""
        self.serial.close()

# Example usage
if __name__ == "__main__":
    controller = LEDController()
    
    try:
        # Display "HELLO WORLD" on the punch card
        controller.display_text("HELLO WORLD", row_offset=0, col_offset=10)
        controller.update_display()
        
        time.sleep(5)
        
        # Clear and display a different message
        controller.clear_card()
        controller.display_text("PUNCH CARD DISPLAY", row_offset=0, col_offset=5)
        controller.update_display()
        
        time.sleep(5)
        
    finally:
        controller.close()
```

## Heat Dissipation and Long-Term Operation

### Thermal Considerations

LED displays can generate significant heat during operation:

| Condition | Heat Generation |
|-----------|----------------|
| All LEDs on at max brightness | ~288W (comparable to small space heater) |
| Typical usage (punch cards) | ~30-50W (only punch holes lit, reduced brightness) |

### Heat Management Strategies

1. **Brightness Limitation**
   - Limit global brightness to 30-50% of maximum
   - Reduces power consumption and heat generation by 50-70%
   - Still provides excellent visibility

2. **Ventilation**
   - Mount LEDs on an aluminum plate for heat sinking
   - Provide ventilation slots or holes in enclosure
   - For enclosed displays, add small 40mm fans (USB or 5V powered)

3. **Power Distribution**
   - Use proper gauge wires to minimize resistive heating
   - Multiple power injection points reduce current through any single wire
   - High-quality connectors reduce resistance at junction points

### Enclosure Design Considerations

```
┌─────────────────────────────────────────┐
│                                         │
│  ┌─────────────────────────────────┐    │ ← Top ventilation slots
│  │                                 │    │
│  │       LED Matrix Display        │    │
│  │                                 │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────┐           ┌─────┐             │
│  │Power│           │Teensy│             │
│  │Supply│          │ MCU  │             │
│  └─────┘           └─────┘             │
│                                         │
└─────────────────────────────────────────┘
            ↑
    Bottom ventilation slots
```

### Long-Term Operation Tips

1. Run a burn-in test (24-48 hours at typical usage pattern) to identify any thermal issues
2. Monitor temperatures during initial operation periods
3. Ensure proper cooling for both LEDs and power supply
4. Consider using thermal sensors to monitor temperature and adjust brightness automatically
5. Use a thermal imaging camera (if available) to identify hot spots in the display

## Integration with Main Project

The LED display should be seamlessly integrated with the main punch card software:

1. **Physical Mounting**
   - Create a card-shaped enclosure with appropriate dimensions
   - Add interpretive printing above the LED matrix
   - Include appropriate labels and indices as per original IBM cards

2. **Software Integration**
   - Ensure character encoding in software matches physical display
   - Synchronize terminal display with LED update timing
   - Add configuration options for LED brightness, timing, and animations

3. **Serial Protocol**
   - Define a simple, efficient protocol for terminal-to-LED communication
   - Include error checking and handling
   - Support bidirectional communication for status updates

## References

- Adafruit NeoPixel Überguide
- PJRC OctoWS2811 Library Documentation
- IBM Punch Card Design Specifications
- "Driving Large LED Displays with Teensy 4.0" (BlinkyLights Blog)
- Mean Well Power Supply Technical Documentation 