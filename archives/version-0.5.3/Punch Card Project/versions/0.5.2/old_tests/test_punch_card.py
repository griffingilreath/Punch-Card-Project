import sqlite3
from typing import List, Dict, Optional
import time
import argparse
import random
import shutil
import os
from datetime import datetime
from punch_card_stats import PunchCardStats

# Mock NeoPixel class for testing
class MockNeoPixel:
    def __init__(self, pin, led_count, brightness=0.5, auto_write=False):
        self.led_count = led_count
        self.brightness = brightness
        self.pixels = [(0, 0, 0)] * led_count
        
    def fill(self, color):
        self.pixels = [color] * self.led_count
        
    def show(self):
        pass
        
    def __setitem__(self, index, color):
        self.pixels[index] = color

# Constants for LED grid configuration
ROWS = 12
COLUMNS = 80
LED_COUNT = ROWS * COLUMNS
DEFAULT_BRIGHTNESS = 0.5
DEFAULT_MESSAGE = "SYSTEM READY"
DEFAULT_LED_DELAY = 0.5  # Default delay between LED updates in seconds
DEFAULT_MESSAGE_DELAY = 30  # Default delay between messages in seconds (changed to 30)
MIN_RANDOM_DELAY = 30  # Minimum random delay (30 seconds)
MAX_RANDOM_DELAY = 60  # Maximum random delay (60 seconds)

# Constants for terminal size
MIN_TERMINAL_WIDTH = 100
MIN_TERMINAL_HEIGHT = 40

# Program information
PROGRAM_NAME = "Punch Card Display System"
VERSION = "0.0.1"
LAST_REVISION = "2024-03-17"
DESCRIPTION = "Terminal Based IBM 80 Column Punch Card Simulator"

"""
IBM 026 style code mapping for uppercase letters A–Z and digits 0–9.

This particular layout sets:
 - A–I => zone punch row 12 plus digit rows 1..9
 - J–R => zone punch row 11 plus digit rows 1..9
 - S–Z => zone punch row 0 plus digit rows 2..9 (skipping digit row 1 for this section)

Row numbering and dictionary index mapping:
  Index => Row
    0   => 12
    1   => 11
    2   => 0
    3   => 1
    4   => 2
    5   => 3
    6   => 4
    7   => 5
    8   => 6
    9   => 7
    10  => 8
    11  => 9

For example, 'S' = row 0,2 => index 2 and index 4 => [0,0,1,0,1,0,0,0,0,0,0,0].

A '1' indicates a punch (LED on); '0' indicates no punch.
"""

CHAR_MAPPING = {
    # ---------------------------------------
    # A–I => zone=12 + digit=1..9
    # ---------------------------------------
    # A = 12,1
    'A': [1,0,0,1,0,0,0,0,0,0,0,0],  # index=0 => row12, index=3 => row1
    # B = 12,2
    'B': [1,0,0,0,1,0,0,0,0,0,0,0],
    # C = 12,3
    'C': [1,0,0,0,0,1,0,0,0,0,0,0],
    # D = 12,4
    'D': [1,0,0,0,0,0,1,0,0,0,0,0],
    # E = 12,5
    'E': [1,0,0,0,0,0,0,1,0,0,0,0],
    # F = 12,6
    'F': [1,0,0,0,0,0,0,0,1,0,0,0],
    # G = 12,7
    'G': [1,0,0,0,0,0,0,0,0,1,0,0],
    # H = 12,8
    'H': [1,0,0,0,0,0,0,0,0,0,1,0],
    # I = 12,9
    'I': [1,0,0,0,0,0,0,0,0,0,0,1],

    # ---------------------------------------
    # J–R => zone=11 + digit=1..9
    # ---------------------------------------
    # J = 11,1
    'J': [0,1,0,1,0,0,0,0,0,0,0,0],
    # K = 11,2
    'K': [0,1,0,0,1,0,0,0,0,0,0,0],
    # L = 11,3
    'L': [0,1,0,0,0,1,0,0,0,0,0,0],
    # M = 11,4
    'M': [0,1,0,0,0,0,1,0,0,0,0,0],
    # N = 11,5
    'N': [0,1,0,0,0,0,0,1,0,0,0,0],
    # O = 11,6
    'O': [0,1,0,0,0,0,0,0,1,0,0,0],
    # P = 11,7
    'P': [0,1,0,0,0,0,0,0,0,1,0,0],
    # Q = 11,8
    'Q': [0,1,0,0,0,0,0,0,0,0,1,0],
    # R = 11,9
    'R': [0,1,0,0,0,0,0,0,0,0,0,1],

    # ---------------------------------------
    # S–Z => zone=0 + digit=2..9 (skipping 1)
    # ---------------------------------------
    # S = 0,2
    'S': [0,0,1,0,1,0,0,0,0,0,0,0],
    # T = 0,3
    'T': [0,0,1,0,0,1,0,0,0,0,0,0],
    # U = 0,4
    'U': [0,0,1,0,0,0,1,0,0,0,0,0],
    # V = 0,5
    'V': [0,0,1,0,0,0,0,1,0,0,0,0],
    # W = 0,6
    'W': [0,0,1,0,0,0,0,0,1,0,0,0],
    # X = 0,7
    'X': [0,0,1,0,0,0,0,0,0,1,0,0],
    # Y = 0,8
    'Y': [0,0,1,0,0,0,0,0,0,0,1,0],
    # Z = 0,9
    'Z': [0,0,1,0,0,0,0,0,0,0,0,1],

    # ---------------------------------------
    # Digits 0–9 => single punch in row 0..9
    # ---------------------------------------
    '0': [0,0,1,0,0,0,0,0,0,0,0,0],  # row 0
    '1': [0,0,0,1,0,0,0,0,0,0,0,0],  # row 1
    '2': [0,0,0,0,1,0,0,0,0,0,0,0],  # row 2
    '3': [0,0,0,0,0,1,0,0,0,0,0,0],  # row 3
    '4': [0,0,0,0,0,0,1,0,0,0,0,0],  # row 4
    '5': [0,0,0,0,0,0,0,1,0,0,0,0],  # row 5
    '6': [0,0,0,0,0,0,0,0,1,0,0,0],  # row 6
    '7': [0,0,0,0,0,0,0,0,0,1,0,0],  # row 7
    '8': [0,0,0,0,0,0,0,0,0,0,1,0],  # row 8
    '9': [0,0,0,0,0,0,0,0,0,0,0,1],  # row 9

    # ---------------------------------------
    # Special Characters => combinations of punches
    # ---------------------------------------
    ' ': [0,0,0,0,0,0,0,0,0,0,0,0],  # no punch
    '.': [0,0,1,0,0,0,0,0,0,0,0,0],  # row 0
    ',': [0,0,0,1,0,0,0,0,0,0,0,0],  # row 1
    '-': [0,0,0,0,1,0,0,0,0,0,0,0],  # row 2
    '+': [0,0,0,0,0,1,0,0,0,0,0,0],  # row 3
    '*': [0,0,0,0,0,0,1,0,0,0,0,0],  # row 4
    '/': [0,0,0,0,0,0,0,1,0,0,0,0],  # row 5
    '=': [0,0,0,0,0,0,0,0,1,0,0,0],  # row 6
    '(': [0,0,0,0,0,0,0,0,0,1,0,0],  # row 7
    ')': [0,0,0,0,0,0,0,0,0,0,1,0],  # row 8
    '$': [0,0,0,0,0,0,0,0,0,0,0,1],  # row 9
    '@': [1,1,0,0,0,0,0,0,0,0,0,0],  # 12,11
    '#': [1,0,1,0,0,0,0,0,0,0,0,0],  # 12,0
    '%': [0,1,1,0,0,0,0,0,0,0,0,0],  # 11,0
    '&': [1,1,1,0,0,0,0,0,0,0,0,0],  # 12,11,0
    '!': [1,0,0,0,0,0,0,0,0,0,0,0],  # 12
    '"': [0,1,0,0,0,0,0,0,0,0,0,0],  # 11
    "'": [0,0,1,0,0,0,0,0,0,0,0,0],  # 0
    ':': [0,0,0,1,0,0,0,0,0,0,0,0],  # 1
    ';': [0,0,0,0,1,0,0,0,0,0,0,0],  # 2
    '?': [0,0,0,0,0,1,0,0,0,0,0,0],  # 3
    '[': [0,0,0,0,0,0,1,0,0,0,0,0],  # 4
    ']': [0,0,0,0,0,0,0,1,0,0,0,0],  # 5
    '{': [0,0,0,0,0,0,0,0,1,0,0,0],  # 6
    '}': [0,0,0,0,0,0,0,0,0,1,0,0],  # 7
    '|': [0,0,0,0,0,0,0,0,0,0,1,0],  # 8
    '\\': [0,0,0,0,0,0,0,0,0,0,0,1],  # 9
    '<': [1,0,0,0,0,0,0,0,0,0,0,0],  # 12
    '>': [0,1,0,0,0,0,0,0,0,0,0,0],  # 11
    '~': [0,0,1,0,0,0,0,0,0,0,0,0],  # 0
    '`': [0,0,0,1,0,0,0,0,0,0,0,0],  # 1
    '^': [0,0,0,0,1,0,0,0,0,0,0,0],  # 2
    '_': [0,0,0,0,0,1,0,0,0,0,0,0],  # 3
}

# Mapping of punch patterns to human-readable descriptions
PUNCH_DESCRIPTIONS = {
    # Letters (A-Z)
    'A': '12,1',
    'B': '12,2',
    'C': '12,3',
    'D': '12,4',
    'E': '12,5',
    'F': '12,6',
    'G': '12,7',
    'H': '12,8',
    'I': '12,9',
    'J': '11,1',
    'K': '11,2',
    'L': '11,3',
    'M': '11,4',
    'N': '11,5',
    'O': '11,6',
    'P': '11,7',
    'Q': '11,8',
    'R': '11,9',
    'S': '0,2',
    'T': '0,3',
    'U': '0,4',
    'V': '0,5',
    'W': '0,6',
    'X': '0,7',
    'Y': '0,8',
    'Z': '0,9',

    # Numbers (0-9)
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

    # Special characters
    ' ': 'no punch',
    '.': '0',
    ',': '1',
    '-': '2',
    '+': '3',
    '*': '4',
    '/': '5',
    '=': '6',
    '(': '7',
    ')': '8',
    '$': '9',
    '@': '12,11',
    '#': '12,0',
    '%': '11,0',
    '&': '12,11,0',
    '!': '12',
    '"': '11',
    "'": '0',
    ':': '1',
    ';': '2',
    '?': '3',
    '[': '4',
    ']': '5',
    '{': '6',
    '}': '7',
    '|': '8',
    '\\': '9',
    '<': '12',
    '>': '11',
    '~': '0',
    '`': '1',
    '^': '2',
    '_': '3'
}

class PunchCardDisplay:
    def __init__(self, debug_mode=True, simulate_serial=True, test_message=None, 
                 led_delay=DEFAULT_LED_DELAY, message_delay=DEFAULT_MESSAGE_DELAY,
                 random_delay=False):
        self.debug_mode = debug_mode
        self.simulate_serial = simulate_serial
        self.test_message = test_message
        self.led_delay = led_delay
        self.message_delay = message_delay
        self.random_delay = random_delay
        self.test_messages = self.load_test_messages()
        self.current_message_index = 0
        self.current_display_buffer = None  # Store the current display buffer
        
        # Initialize statistics
        self.stats = PunchCardStats()
        
        # Initialize mock NeoPixel strip
        self.pixels = MockNeoPixel(None, LED_COUNT, brightness=DEFAULT_BRIGHTNESS)
        
        # Initialize database connection
        self.db_conn = None
        
        # Set up terminal size and calculate vertical offset
        self.setup_terminal()
        self.y_offset = 3  # Reduced vertical offset for better alignment
        
        # Show splash screen and configuration
        self.show_splash_screen()
        self.show_configuration()
        
        # Setup database after splash screen
        self.setup_database()
            
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
        # Reorder the pattern to match the correct row order: 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
        reordered_pattern = [
            pattern[0],  # 12
            pattern[1],  # 11
            pattern[2],  # 0
            pattern[3],  # 1
            pattern[4],  # 2
            pattern[5],  # 3
            pattern[6],  # 4
            pattern[7],  # 5
            pattern[8],  # 6
            pattern[9],  # 7
            pattern[10], # 8
            pattern[11]  # 9
        ]
        if self.debug_mode:
            punch_desc = PUNCH_DESCRIPTIONS.get(char.upper(), "unknown")
            self.log(f"Character '{char}' encoded as {punch_desc}")
        return reordered_pattern
    
    def get_punch_encoding_description(self, message: str) -> str:
        """Generate a human-readable description of the punch encoding for a message"""
        encoding_desc = "Encoding Message: "
        for i, char in enumerate(message, 1):
            punch_desc = PUNCH_DESCRIPTIONS.get(char.upper(), "unknown")
            encoding_desc += f"#{i:02d}/80 {char}={punch_desc} "
        encoding_desc += "\n* * * End of message. * * *"
        return encoding_desc
            
    def load_test_messages(self):
        """Load test messages from file"""
        messages = []
        try:
            with open('test_messages.txt', 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        serial, message = line.strip().split('|')
                        messages.append((serial, message))
            self.log(f"Loaded {len(messages)} test messages")
            return messages
        except FileNotFoundError:
            self.log("Test messages file not found, using default messages")
            return [
                ("TEST001", "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
                ("TEST002", "HELLO WORLD THIS IS A TEST MESSAGE"),
                ("TEST003", "IBM PUNCH CARD SYSTEM READY"),
                ("TEST004", "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"),
                ("TEST005", "RANDOM MESSAGE WITH NUMBERS 12345 AND SPECIAL CHARS @#$%^&*()_+{}[]|:;\"'<>,.?/~`-=!\\")
            ]

    def setup_terminal(self):
        """Set up terminal size and clear screen"""
        # Get current terminal size
        terminal_size = shutil.get_terminal_size()
        
        # Check if terminal is too small
        if terminal_size.columns < MIN_TERMINAL_WIDTH or terminal_size.lines < MIN_TERMINAL_HEIGHT:
            # Try to resize terminal
            try:
                os.system(f'printf "\033[8;{MIN_TERMINAL_HEIGHT};{MIN_TERMINAL_WIDTH}t"')
                # Force terminal to update its size
                shutil.get_terminal_size()
            except:
                self.log("Warning: Could not resize terminal. Display may be distorted.")
        
        # Clear screen and move cursor to top
        print("\033[2J\033[H", end="", flush=True)

    def get_centered_offset(self, content_width):
        """Calculate the horizontal offset to center content"""
        terminal_width = shutil.get_terminal_size().columns
        return (terminal_width - content_width) // 2

    def display_countdown(self, remaining_time, total_delay, x_offset):
        """Display countdown with progress bar and bouncing dashes"""
        total_width = 40  # Width of the progress bar
        elapsed = total_delay - remaining_time
        progress = int((elapsed / total_delay) * total_width)
        bar = "█" * progress + "░" * (total_width - progress)
        percentage = int((elapsed / total_delay) * 100)
        
        # Create bouncing dashes pattern (5 dashes)
        dash_positions = [
            "     -----",  # All dashes on the right
            "    ----- ",
            "   -----  ",
            "  -----   ",
            " -----    ",
            "-----     ",  # All dashes on the left
            " -----    ",
            "  -----   ",
            "   -----  ",
            "    ----- ",
            "     -----"  # All dashes on the right
        ]
        # Slower animation speed (4 instead of 8) and smoother transitions
        bounce_cycle = int(elapsed * 4) % len(dash_positions)
        dashes = dash_positions[bounce_cycle]
        
        # Print countdown aligned with other text
        countdown_text = f"Receiving Message {dashes} [{bar}] {percentage}%"
        print(f"\r{' ' * x_offset}{countdown_text}", end="", flush=True)

    def animate_transition(self, display_buffer):
        """Animate the transition of the current message out"""
        transition_delay = 0.05  # Delay between each column shift
        
        # Calculate centering offset
        card_width = COLUMNS + 4  # 80 columns + 2 borders + 2 spaces for row numbers
        x_offset = self.get_centered_offset(card_width)
        
        # Get current message number
        current_stats = self.stats.get_stats()
        message_number = current_stats['cards_processed']
        
        for shift in range(COLUMNS):
            # Shift all columns one position to the left
            for col in range(COLUMNS - 1):
                for row in range(ROWS):
                    display_buffer[row][col] = display_buffer[row][col + 1]
            # Clear the rightmost column
            for row in range(ROWS):
                display_buffer[row][COLUMNS - 1] = "□"
            
            # Print current state of display
            print("\033[2J\033[H")  # Clear screen
            
            # Print empty lines for consistent vertical spacing
            print("\n" * self.y_offset)
            
            # Print header with consistent spacing
            print(" " * x_offset + f"Message #{message_number:07d}: Saving to database...")
            print()  # Single line spacing between message and card
            
            # Print top border with corner cutout
            print(" " * x_offset + "   ┌" + "─" * (COLUMNS - 1) + "─┐")
            
            # Define the correct row order for punch cards: 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
            row_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # Indices in display_buffer
            row_labels = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
            
            # Print grid with correct row order and consistent spacing
            for i, row_idx in enumerate(row_order):
                row_num = row_labels[i]  # Use the correct row label
                row_content = "".join(display_buffer[row_idx])
                print(" " * x_offset + f"{row_num:2s} │{row_content}│")
            
            # Print bottom border
            print(" " * x_offset + "   └" + "─" * (COLUMNS - 1) + "─┘")
            
            # Print processing info with consistent spacing
            print()  # Single line spacing
            print(" " * x_offset + "Saving message to database...")
            
            time.sleep(transition_delay)

    def update_statistics(self, message: str):
        """Update statistics for a processed message"""
        self.stats.update_message_stats(message)

    def display_message(self, message: str) -> None:
        """Display message on LED grid"""
        self.log(f"Message Received: {message}")
        self.log(self.get_punch_encoding_description(message))
        
        # Update statistics for this message
        self.update_statistics(message)
        
        # Get current message number
        current_stats = self.stats.get_stats()
        message_number = current_stats['cards_processed']
        
        # Simulate LED display with sequential character display
        self.log("Simulating LED display:")
        message = message[:COLUMNS]  # Ensure message doesn't exceed column limit
        
        # Initialize empty display with full 80 columns
        self.current_display_buffer = [["□" for _ in range(COLUMNS)] for _ in range(ROWS)]
        
        # Calculate centering offset
        card_width = COLUMNS + 4  # 80 columns + 2 borders + 2 spaces for row numbers
        x_offset = self.get_centered_offset(card_width)
        
        # Display each character sequentially
        for col, char in enumerate(message):
            pattern = self.char_to_led_pattern(char)
            # Update display buffer with new character
            for row in range(ROWS):
                self.current_display_buffer[row][col] = "█" if pattern[row] else "□"
            
            # Print current state of display
            print("\033[2J\033[H")  # Clear screen
            
            # Print empty lines for consistent vertical spacing
            print("\n" * self.y_offset)
            
            # Print message number and message above the card
            print(" " * x_offset + f"Message #{message_number:07d}: {message}")
            print()  # Single line spacing between message and card
            
            # Print top border with corner cutout
            print(" " * x_offset + "   ┌" + "─" * (COLUMNS - 1) + "─┐")
            
            # Define the correct row order for punch cards: 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
            row_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # Indices in display_buffer
            row_labels = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
            
            # Print grid with correct row order and consistent spacing
            for i, row_idx in enumerate(row_order):
                row_num = row_labels[i]  # Use the correct row label
                row_content = "".join(self.current_display_buffer[row_idx])
                print(" " * x_offset + f"{row_num:2s} │{row_content}│")
            
            # Print bottom border
            print(" " * x_offset + "   └" + "─" * (COLUMNS - 1) + "─┘")
            
            # Print processing info with consistent spacing
            print()  # Single line spacing
            punch_desc = PUNCH_DESCRIPTIONS.get(char.upper(), "unknown")
            print(" " * x_offset + f"{col+1}/{len(message)} - Character: '{char}' ({punch_desc})")
            
            time.sleep(self.led_delay)

    def get_next_delay(self) -> float:
        """Get the next delay time between messages"""
        if self.random_delay:
            delay = random.uniform(MIN_RANDOM_DELAY, MAX_RANDOM_DELAY)
            return delay
        return self.message_delay
            
    def generate_random_sentence(self) -> str:
        """Generate a random sentence up to 80 characters"""
        # Word lists for generating sentences
        articles = ["THE", "A", "AN"]
        adjectives = ["QUICK", "LAZY", "BROWN", "HAPPY", "SLEEPY", "BUSY", "CLEVER", "WISE", "BRAVE", "STRONG"]
        nouns = ["FOX", "DOG", "CAT", "BIRD", "FISH", "BEAR", "WOLF", "LION", "TIGER", "ELEPHANT"]
        verbs = ["JUMPS", "RUNS", "WALKS", "FLIES", "SWIMS", "CLIMBS", "DANCES", "SINGS", "PLAYS", "WORKS"]
        adverbs = ["QUICKLY", "SLOWLY", "HAPPILY", "CAREFULLY", "BRAVELY", "WISELY", "STRONGLY", "GENTLY"]
        
        # Generate sentence components
        sentence_parts = []
        current_length = 0
        
        # Always start with an article
        article = random.choice(articles)
        sentence_parts.append(article)
        current_length = len(article)
        
        # Add adjective (50% chance)
        if random.random() < 0.5:
            adj = random.choice(adjectives)
            if current_length + len(adj) + 1 <= 80:  # +1 for space
                sentence_parts.append(adj)
                current_length += len(adj) + 1
        
        # Add noun
        noun = random.choice(nouns)
        if current_length + len(noun) + 1 <= 80:
            sentence_parts.append(noun)
            current_length += len(noun) + 1
        
        # Add verb
        verb = random.choice(verbs)
        if current_length + len(verb) + 1 <= 80:
            sentence_parts.append(verb)
            current_length += len(verb) + 1
        
        # Add adverb (30% chance)
        if random.random() < 0.3:
            adv = random.choice(adverbs)
            if current_length + len(adv) + 1 <= 80:
                sentence_parts.append(adv)
                current_length += len(adv) + 1
        
        # Add prepositional phrase (40% chance)
        if random.random() < 0.4:
            prep = random.choice(["OVER", "UNDER", "THROUGH", "AROUND", "BETWEEN"])
            if current_length + len(prep) + 1 <= 80:
                sentence_parts.append(prep)
                current_length += len(prep) + 1
                
                # Add article
                article = random.choice(articles)
                if current_length + len(article) + 1 <= 80:
                    sentence_parts.append(article)
                    current_length += len(article) + 1
                    
                    # Add adjective (30% chance)
                    if random.random() < 0.3:
                        adj = random.choice(adjectives)
                        if current_length + len(adj) + 1 <= 80:
                            sentence_parts.append(adj)
                            current_length += len(adj) + 1
                    
                    # Add noun
                    noun = random.choice(nouns)
                    if current_length + len(noun) <= 80:
                        sentence_parts.append(noun)
        
        # Join parts with spaces and add period
        sentence = " ".join(sentence_parts) + "."
        
        # Ensure sentence doesn't exceed 80 characters
        return sentence[:80]
            
    def simulate_serial_input(self):
        """Simulate serial input for testing purposes"""
        if self.test_messages:
            serial, message = self.test_messages[self.current_message_index]
            self.current_message_index = (self.current_message_index + 1) % len(self.test_messages)
            self.save_message_to_db(serial, message)
            self.log(f"Simulating serial input: DISPLAY:{serial}")
            return f"DISPLAY:{serial}"
        else:
            # Generate random sentence after test messages
            message = self.generate_random_sentence()
            serial = f"RAND{random.randint(1000, 9999)}"
            self.save_message_to_db(serial, message)
            self.log(f"Generated random message: DISPLAY:{serial}")
            return f"DISPLAY:{serial}"
        
    def run(self):
        """Main operation loop"""
        self.log("Starting main operation loop")
        
        while True:
            try:
                # Process command
                command = self.simulate_serial_input()
                if command.startswith("DISPLAY:"):
                    serial_number = command.split(":")[1]
                    self.log(f"Processing display command for serial: {serial_number}")
                    message = self.get_message_from_db(serial_number)
                    if message:
                        self.display_message(message)
                    else:
                        self.log(f"No message found for {serial_number}, displaying default")
                        self.display_message(DEFAULT_MESSAGE)
                
                # Wait for 5 seconds after processing the message
                time.sleep(5)
                
                # Wait for next message with countdown
                delay = self.get_next_delay()
                start_time = time.time()
                
                # Calculate centering offset for the countdown display
                card_width = COLUMNS + 4  # 80 columns + 2 borders + 2 spaces for row numbers
                x_offset = self.get_centered_offset(card_width)
                
                # Get current message number
                current_stats = self.stats.get_stats()
                message_number = current_stats['cards_processed']
                
                while time.time() - start_time < delay:
                    remaining = delay - (time.time() - start_time)
                    # Print countdown with proper spacing
                    print("\033[2J\033[H")  # Clear screen
                    print("\n" * self.y_offset)
                    
                    # Print the current message and punch card display
                    if self.current_display_buffer:
                        print(" " * x_offset + f"Message #{message_number:07d}: {message}")
                        print()  # Single line spacing between message and card
                        
                        # Print top border with corner cutout
                        print(" " * x_offset + "   ┌" + "─" * (COLUMNS - 1) + "─┐")
                        
                        # Define the correct row order for punch cards: 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
                        row_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # Indices in display_buffer
                        row_labels = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
                        
                        # Print grid with correct row order and consistent spacing
                        for i, row_idx in enumerate(row_order):
                            row_num = row_labels[i]  # Use the correct row label
                            row_content = "".join(self.current_display_buffer[row_idx])
                            print(" " * x_offset + f"{row_num:2s} │{row_content}│")
                        
                        # Print bottom border
                        print(" " * x_offset + "   └" + "─" * (COLUMNS - 1) + "─┘")
                    
                    # Print processing info and countdown
                    print()  # Single line spacing
                    print(" " * x_offset + "Waiting for next message...")
                    print(" " * x_offset)  # Space for countdown
                    self.display_countdown(remaining, delay, x_offset)
                    time.sleep(0.1)
                print()  # New line after countdown
                
                # Animate the transition out after the delay
                if self.current_display_buffer:
                    self.animate_transition(self.current_display_buffer)
                    
            except Exception as e:
                self.log(f"Operation error: {e}")
                self.display_message(DEFAULT_MESSAGE)
                time.sleep(self.get_next_delay())

    def show_splash_screen(self):
        """Display a splash screen with a punch card and loading messages"""
        # Clear screen
        print("\033[2J\033[H")
        
        # Calculate centering offset
        card_width = COLUMNS + 4  # 80 columns + 2 borders + 2 spaces for row numbers
        x_offset = self.get_centered_offset(card_width)
        
        # Print loading messages on the punch card
        loading_messages = [
            "Initializing System...",
            "Loading Character Set...",
            "Configuring LED Grid...",
            "Preparing Database...",
            "System Ready"
        ]
        
        # Calculate timing for messages (15 seconds total for splash screen)
        message_delay = 3.0  # 3 seconds per message
        start_time = time.time()
        
        for i, message in enumerate(loading_messages):
            # Calculate position to center the message
            message_padding = (COLUMNS - len(message)) // 2
            
            # Print current state
            print("\033[2J\033[H")  # Clear screen
            print("\n" * self.y_offset)
            
            # Print top border
            print(" " * x_offset + "   ┌" + "─" * (COLUMNS - 1) + "─┐")
            
            # Calculate vertical centering for the message
            empty_rows = ROWS - 1
            top_padding = empty_rows // 2
            
            # Print empty rows before message
            for _ in range(top_padding):
                print(" " * x_offset + "   │" + " " * COLUMNS + "│")
            
            # Print message
            print(" " * x_offset + "   │" + " " * message_padding + message + " " * (COLUMNS - message_padding - len(message)) + "│")
            
            # Print remaining empty rows
            for _ in range(ROWS - top_padding - 1):
                print(" " * x_offset + "   │" + " " * COLUMNS + "│")
            
            print(" " * x_offset + "   └" + "─" * (COLUMNS - 1) + "─┘")
            
            # Wait for the message delay
            elapsed = time.time() - start_time
            if elapsed < (i + 1) * message_delay:
                time.sleep((i + 1) * message_delay - elapsed)
        
        # Final display of all messages
        print("\033[2J\033[H")
        print("\n" * self.y_offset)
        print(" " * x_offset + "   ┌" + "─" * (COLUMNS - 1) + "─┐")
        
        # Calculate vertical centering for all messages
        total_messages = len(loading_messages)
        empty_rows = ROWS - total_messages
        top_padding = empty_rows // 2
        
        # Print empty rows before messages
        for _ in range(top_padding):
            print(" " * x_offset + "   │" + " " * COLUMNS + "│")
        
        # Print all messages
        for message in loading_messages:
            message_padding = (COLUMNS - len(message)) // 2
            print(" " * x_offset + "   │" + " " * message_padding + message + " " * (COLUMNS - message_padding - len(message)) + "│")
        
        # Print remaining empty rows
        for _ in range(ROWS - top_padding - total_messages):
            print(" " * x_offset + "   │" + " " * COLUMNS + "│")
        
        print(" " * x_offset + "   └" + "─" * (COLUMNS - 1) + "─┘")
        
        # Wait for remaining time to complete 15 seconds
        elapsed = time.time() - start_time
        if elapsed < 15:
            time.sleep(15 - elapsed)

    def show_configuration(self):
        """Display program configuration information across multiple cards"""
        # Calculate centering offset
        card_width = COLUMNS + 4  # 80 columns + 2 borders + 2 spaces for row numbers
        x_offset = self.get_centered_offset(card_width)
        
        # Get current statistics
        current_stats = self.stats.get_stats()
        
        # Configuration messages split into smaller sections
        config_sections = [
            # Section 1: Basic Program Info
            [
                f"{PROGRAM_NAME} v{VERSION}",
                f"Last Revision: {LAST_REVISION}",
                DESCRIPTION
            ],
            # Section 2: Display Configuration
            [
                "Display Configuration",
                f"Grid Size: {ROWS}x{COLUMNS} LEDs",
                f"Total LEDs: {LED_COUNT}",
                f"LED Delay: {self.led_delay:.2f} seconds",
                f"Message Delay: {self.message_delay:.2f} seconds",
                f"LED Brightness: {DEFAULT_BRIGHTNESS * 100:.0f}%"
            ],
            # Section 3: System Status
            [
                "System Status",
                f"Debug Mode: {'Enabled' if self.debug_mode else 'Disabled'}",
                f"Random Delay: {'Enabled' if self.random_delay else 'Disabled'}",
                f"Cards Processed: {current_stats['cards_processed']}",
                f"Number of Holes Punched: {current_stats['total_holes']}",
                f"Time Operating: {int(current_stats['time_operating'] / 3600):02d}:{int((current_stats['time_operating'] % 3600) / 60):02d}:{int(current_stats['time_operating'] % 60):02d}"
            ]
        ]

        # Add debug information as a separate section if debug mode is enabled
        if self.debug_mode:
            debug_section = [
                "Debug Information",
                f"Test Messages: {len(self.test_messages)}",
                f"Current Index: {self.current_message_index}",
                f"Last Update: {datetime.fromtimestamp(current_stats['last_update']).strftime('%H:%M:%S')}"
            ]
            config_sections.append(debug_section)
            
            # Create a separate section for character usage statistics
            char_usage_section = [
                "Character Usage Statistics"
            ]
            
            # Organize character counts by category
            letters = [(char, count) for char, count in current_stats['character_stats'].items() 
                      if char.isalpha() and count > 0]
            numbers = [(char, count) for char, count in current_stats['character_stats'].items() 
                      if char.isdigit() and count > 0]
            symbols = [(char, count) for char, count in current_stats['character_stats'].items() 
                      if not char.isalnum() and count > 0]
            
            # Calculate how many characters can fit per line (with spacing)
            chars_per_line = 10  # Increased to show more characters per line
            
            # Add character counts in organized format
            if numbers:
                # Group numbers into lines
                for i in range(0, len(numbers), chars_per_line):
                    line = numbers[i:i + chars_per_line]
                    char_line = "  ".join(f"{char}:{count:3d}" for char, count in line)
                    char_usage_section.append(char_line)
                char_usage_section.append("")  # Add empty line after numbers
            
            if letters:
                # Group letters into lines
                for i in range(0, len(letters), chars_per_line):
                    line = letters[i:i + chars_per_line]
                    char_line = "  ".join(f"{char}:{count:3d}" for char, count in line)
                    char_usage_section.append(char_line)
                char_usage_section.append("")  # Add empty line after letters
            
            if symbols:
                # Group symbols into lines
                for i in range(0, len(symbols), chars_per_line):
                    line = symbols[i:i + chars_per_line]
                    # Special handling for space character
                    char_line = "  ".join(
                        '"Space":{:3d}'.format(count) if char == " " else f"{char}:{count:3d}"
                        for char, count in line
                    )
                    char_usage_section.append(char_line)
            
            if not any([letters, numbers, symbols]):
                char_usage_section.append("No characters processed yet")
            
            config_sections.append(char_usage_section)
            
            # Create a separate section for message length statistics
            message_length_section = [
                "Message Length Statistics"
            ]
            
            # Add message length statistics
            length_stats = [(length, count) for length, count in current_stats['message_length_stats'].items()]
            if length_stats:
                # Sort by length and display
                for length, count in sorted(length_stats):
                    message_length_section.append(f"{length} character messages: {count}")
            else:
                message_length_section.append("No message length statistics available")
            
            config_sections.append(message_length_section)
        
        # Display each section
        for section_num, section in enumerate(config_sections, 1):
            # Print empty lines for vertical centering
            print("\033[2J\033[H")
            print("\n" * self.y_offset)
            
            # Print top border
            print(" " * x_offset + "   ┌" + "─" * (COLUMNS - 1) + "─┐")
            
            # Calculate vertical centering for the section
            empty_rows = ROWS - len(section)
            top_padding = empty_rows // 2
            
            # Print empty rows before section
            for _ in range(top_padding):
                print(" " * x_offset + "   │" + " " * COLUMNS + "│")
            
            # Display messages for this section
            for message in section:
                # Calculate position to center the message
                message_padding = (COLUMNS - len(message)) // 2
                print(" " * x_offset + "   │" + " " * message_padding + message + " " * (COLUMNS - message_padding - len(message)) + "│")
            
            # Fill remaining rows with empty spaces
            remaining_rows = ROWS - top_padding - len(section)
            for _ in range(remaining_rows):
                print(" " * x_offset + "   │" + " " * COLUMNS + "│")
            
            # Print bottom border
            print(" " * x_offset + "   └" + "─" * (COLUMNS - 1) + "─┘")
            
            # Wait for 7 seconds before showing next section
            time.sleep(7)
        
        # After showing all sections, animate the punch card structure
        print("\033[2J\033[H")
        print("\n" * self.y_offset)
        print(" " * x_offset + "   ┌" + "─" * (COLUMNS - 1) + "─┐")
        
        # Initialize empty grid
        grid = [[" " for _ in range(COLUMNS)] for _ in range(ROWS)]
        
        # Define row order and labels
        row_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        row_labels = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        
        # Animate punch card structure diagonally with smoother transitions
        # Start from top-left and move diagonally down-right
        for diagonal in range(ROWS + COLUMNS - 1):
            # Calculate the starting row and column for this diagonal
            if diagonal < ROWS:
                row = diagonal
                col = 0
            else:
                row = ROWS - 1
                col = diagonal - ROWS + 1
            
            # Fill cells along this diagonal with smooth transitions
            while row >= 0 and col < COLUMNS:
                grid[row][col] = "□"
                # Print current state
                print("\033[2J\033[H")
                print("\n" * self.y_offset)
                print(" " * x_offset + "   ┌" + "─" * (COLUMNS - 1) + "─┐")
                
                # Print grid with correct row order and labels
                for i, row_idx in enumerate(row_order):
                    row_num = row_labels[i]
                    row_content = "".join(grid[row_idx])
                    print(" " * x_offset + f"{row_num:2s} │{row_content}│")
                
                print(" " * x_offset + "   └" + "─" * (COLUMNS - 1) + "─┘")
                
                # Smoother animation timing
                # Faster for the first part, slower for the middle, and medium for the end
                if diagonal < ROWS // 2:
                    time.sleep(0.002)  # Faster at the start
                elif diagonal < ROWS + COLUMNS // 2:
                    time.sleep(0.003)  # Medium speed in the middle
                else:
                    time.sleep(0.002)  # Faster at the end
                
                row -= 1
                col += 1
        
        # Final pause before starting the main program
        time.sleep(2)
        print("\n" * 2)  # Add space before starting the main program

if __name__ == "__main__":
    # Set up command line arguments for testing
    parser = argparse.ArgumentParser(description='Punch Card LED Display Controller')
    parser.add_argument('--test-message', type=str, default="HELLO WORLD",
                        help='Test message to display')
    parser.add_argument('--led-delay', type=float, default=DEFAULT_LED_DELAY,
                        help='Delay between LED updates in seconds')
    parser.add_argument('--message-delay', type=float, default=DEFAULT_MESSAGE_DELAY,
                        help='Delay between messages in seconds')
    parser.add_argument('--random-delay', action='store_true', default=True,
                        help='Use random delay between messages (30-60 seconds)')
    
    args = parser.parse_args()
    
    # Create and run the display
    display = PunchCardDisplay(
        debug_mode=True,
        simulate_serial=True,
        test_message=args.test_message,
        led_delay=args.led_delay,
        message_delay=args.message_delay,
        random_delay=args.random_delay
    )
    
    display.run() 