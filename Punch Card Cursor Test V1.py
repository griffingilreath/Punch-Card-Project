import board
import neopixel
import sqlite3
from typing import List, Dict, Optional
import serial
import time
import argparse

# Constants for LED grid configuration
ROWS = 12
COLUMNS = 80
LED_COUNT = ROWS * COLUMNS
LED_PIN = board.D18  # Raspberry Pi GPIO pin
DEFAULT_BRIGHTNESS = 0.5
DEFAULT_MESSAGE = "SYSTEM READY"

# Hollerith/EBCDIC encoding mapping (simplified example)
CHAR_MAPPING = {
    # A=12,1
    'A': [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    # B=12,2
    'B': [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    # C=12,3
    'C': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    # D=12,4
    'D': [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    # E=12,5
    'E': [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    # F=11,1
    'F': [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    # G=11,2
    'G': [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    # H=11,3
    'H': [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    # I=11,4
    'I': [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    # J=11,5
    'J': [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    # K=0,1
    'K': [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    # L=0,2
    'L': [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    # M=0,3
    'M': [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    # N=0,4
    'N': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    # O=0,5
    'O': [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    # P=12,1,2
    'P': [1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    # Q=12,1,3
    'Q': [1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
    # R=12,1,4
    'R': [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    # S=12,1,5
    'S': [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    # T=12,2,3
    'T': [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
    # U=11,1,2
    'U': [0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    # V=11,1,3
    'V': [0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
    # W=11,1,4
    'W': [0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    # X=11,1,5
    'X': [0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    # Y=11,2,3
    'Y': [0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
    # Z=11,2,4
    'Z': [0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],

 # Digits (0-9)
    '0': [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    '1': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    '2': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    '3': [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    '3': [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    '4': [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    '5': [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    '5': [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    '6': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    '7': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    '7': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    '8': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    '9': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

    # Special characters commonly used in punch cards
    '-': [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    '/': [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    '.': [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    '&': [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    '-': [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    '@': [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    '*': [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    '&': [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    ' ': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Space (no punch)
}
# Each sub-array represents a vertical column of punch positions from top (Row 12) to bottom (Row 9).
# '1' indicates punched (LED on), and '0' indicates no punch (LED off).

# Ensure additional required characters are mapped appropriately based on IBM punch card standards (EBCDIC/Hollerith).
# The full set can be expanded to include lowercase letters and additional symbols according to the project's needs.

# Mapping of punch patterns to human-readable descriptions
PUNCH_DESCRIPTIONS = {
    'A': '12,1',
    'B': '12,2',
    'C': '12,3',
    'D': '12,4',
    'E': '12,5',
    'F': '11,1',
    'G': '11,2',
    'H': '11,3',
    'I': '11,4',
    'J': '11,5',
    'K': '0,1',
    'L': '0,2',
    'M': '0,3',
    'N': '0,4',
    'O': '0,5',
    'P': '12,1,2',
    'Q': '12,1,3',
    'R': '12,1,4',
    'S': '12,1,5',
    'T': '12,2,3',
    'U': '11,1,2',
    'V': '11,1,3',
    'W': '11,1,4',
    'X': '11,1,5',
    'Y': '11,2,3',
    'Z': '11,2,4',
    '0': '0',
    '1': '1',
    '2': '2',
    '3': '3',
    '4': '4',
    '5': '5',
    '6': '6',
    '7': '7',
    '8': '8',
    '9': '9',
    '-': '11,1',
    '/': '11,2',
    '.': '11,3',
    '&': '11,4',
    '@': '11,5',
    '*': '11,5',
    ' ': 'no punch',
}

class PunchCardDisplay:
    def __init__(self, debug_mode=False, simulate_serial=False, test_message=None):
        self.debug_mode = debug_mode
        self.simulate_serial = simulate_serial
        self.test_message = test_message
        
        # Initialize NeoPixel strip (only if not in debug-only mode)
        if not self.debug_mode or self.debug_mode == "both":
            try:
                self.pixels = neopixel.NeoPixel(
                    LED_PIN, 
                    LED_COUNT,
                    brightness=DEFAULT_BRIGHTNESS,
                    auto_write=False
                )
                self.log("NeoPixel LED strip initialized successfully")
            except Exception as e:
                self.log(f"Warning: Could not initialize NeoPixel strip: {e}")
                self.pixels = None
        else:
            self.pixels = None
            self.log("Running in debug-only mode, LED hardware not initialized")
        
        # Initialize database connection
        self.db_conn = None
        self.setup_database()
        
        # Initialize serial connection
        self.serial = None
        if not self.simulate_serial:
            self.setup_serial()
        else:
            self.log("Serial communication simulation enabled")
        
    def log(self, message):
        """Log messages to terminal"""
        print(f"[PunchCardDisplay] {message}")
            
    def setup_database(self) -> None:
        """Initialize SQLite database with required table structure"""
        try:
            self.db_conn = sqlite3.connect('punchcard_messages.db')
            cursor = self.db_conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    serial_number TEXT PRIMARY KEY,
                    message TEXT NOT NULL CHECK(length(message) <= 80)
                )
            ''')
            self.db_conn.commit()
            self.log("Database initialized successfully")
            
            # Add test message if in debug mode
            if self.debug_mode and self.test_message:
                self.save_message_to_db("TEST123", self.test_message)
                self.log(f"Added test message to database: '{self.test_message}'")
                
        except sqlite3.Error as e:
            self.log(f"Database initialization error: {e}")
            
    def setup_serial(self) -> None:
        """Initialize serial communication"""
        try:
            self.serial = serial.Serial('/dev/ttyUSB0', 9600)
            self.log("Serial communication initialized successfully")
        except serial.SerialException as e:
            self.log(f"Serial initialization error: {e}")
            
    def set_brightness(self, brightness: float) -> None:
        """Adjust global LED brightness"""
        if self.pixels and 0.0 <= brightness <= 1.0:
            self.pixels.brightness = brightness
            self.pixels.show()
            self.log(f"LED brightness set to {brightness}")
            
    def get_message_from_db(self, serial_number: str) -> Optional[str]:
        """Retrieve message from database by serial number"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('SELECT message FROM messages WHERE serial_number = ?', 
                         (serial_number,))
            result = cursor.fetchone()
            message = result[0] if result else None
            
            if message:
                self.log(f"Retrieved message for serial {serial_number}: '{message}'")
            else:
                self.log(f"No message found for serial {serial_number}, using default")
                
            return message
        except sqlite3.Error as e:
            self.log(f"Database error when retrieving message: {e}")
            return DEFAULT_MESSAGE
            
    def save_message_to_db(self, serial_number: str, message: str) -> bool:
        """Save or update message in database"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO messages (serial_number, message) 
                VALUES (?, ?)
            ''', (serial_number, message[:80]))
            self.db_conn.commit()
            self.log(f"Saved message for serial {serial_number}: '{message[:80]}'")
            return True
        except sqlite3.Error as e:
            self.log(f"Database error when saving message: {e}")
            return False
            
    def char_to_led_pattern(self, char: str) -> List[bool]:
        """Convert character to LED pattern using Hollerith/EBCDIC encoding"""
        pattern = CHAR_MAPPING.get(char.upper(), [0] * ROWS)
        if self.debug_mode:
            punch_desc = PUNCH_DESCRIPTIONS.get(char.upper(), "unknown")
            self.log(f"Character '{char}' encoded as {punch_desc}")
        return pattern
    
    def get_punch_encoding_description(self, message: str) -> str:
        """Generate a human-readable description of the punch encoding for a message"""
        encoding_desc = "Encoding Message: "
        for char in message:
            punch_desc = PUNCH_DESCRIPTIONS.get(char.upper(), "unknown")
            encoding_desc += f"# {char}={punch_desc} "
        return encoding_desc
            
    def display_message(self, message: str) -> None:
        """Display message on LED grid"""
        self.log(f"Message Received: {message}")
        self.log(self.get_punch_encoding_description(message))
        
        # Only update physical LEDs if not in debug-only mode
        if self.pixels:
            # Clear display
            self.pixels.fill((0, 0, 0))
            self.log("Clearing LED display")
            
            # Convert message to LED patterns
            for col, char in enumerate(message[:COLUMNS]):
                pattern = self.char_to_led_pattern(char)
                for row, is_punched in enumerate(pattern):
                    led_index = row * COLUMNS + col
                    self.pixels[led_index] = (255, 255, 255) if is_punched else (0, 0, 0)
            
            self.pixels.show()
            self.log("LED display updated with new message")
        else:
            self.log("LED display update skipped (hardware not initialized)")
        
    def simulate_serial_input(self):
        """Simulate serial input for testing purposes"""
        if self.test_message:
            self.log("Simulating serial input: DISPLAY:TEST123")
            return "DISPLAY:TEST123"
        else:
            self.log("Simulating serial input: DISPLAY:DEMO123")
            return "DISPLAY:DEMO123"
        
    def run(self):
        """Main operation loop"""
        self.log("Starting main operation loop")
        
        # If test message provided, display it immediately
        if self.debug_mode and self.test_message and not self.simulate_serial:
            self.log("Debug mode: displaying test message immediately")
            self.display_message(self.test_message)
        
        while True:
            try:
                command = None
                
                # Get command from serial or simulation
                if self.simulate_serial:
                    command = self.simulate_serial_input()
                    time.sleep(5)  # Wait between simulated commands
                elif self.serial and self.serial.in_waiting:
                    # Read serial command
                    command = self.serial.readline().decode().strip()
                    self.log(f"Received serial command: {command}")
                
                # Process command if we have one
                if command:
                    # Parse command (example format: "DISPLAY:SERIAL123")
                    if command.startswith("DISPLAY:"):
                        serial_number = command.split(":")[1]
                        self.log(f"Processing display command for serial: {serial_number}")
                        message = self.get_message_from_db(serial_number)
                        if message:
                            self.display_message(message)
                        else:
                            self.log(f"No message found for {serial_number}, displaying default")
                            self.display_message(DEFAULT_MESSAGE)
                            
                time.sleep(0.1)  # Prevent CPU overload
                
            except Exception as e:
                self.log(f"Operation error: {e}")
                if self.pixels:
                    self.display_message(DEFAULT_MESSAGE)
                time.sleep(1)

if __name__ == "__main__":
    # Set up command line arguments for testing
    parser = argparse.ArgumentParser(description='Punch Card LED Display Controller')
    parser.add_argument('--debug', choices=['terminal', 'both', 'false'], default='false',
                        help='Debug mode: terminal-only, both terminal and LEDs, or disabled')
    parser.add_argument('--simulate-serial', action='store_true',
                        help='Simulate serial input for testing')
    parser.add_argument('--test-message', type=str,
                        help='Test message to display')
    
    args = parser.parse_args()
    
    # Convert args to appropriate types
    debug_mode = False if args.debug == 'false' else args.debug
    
    # Create and run the display
    display = PunchCardDisplay(
        debug_mode=debug_mode,
        simulate_serial=args.simulate_serial,
        test_message=args.test_message
    )
    
    display.run()
