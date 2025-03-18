"""
 ___________________________________________________________________
/\::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: \
\_|                                                                 |
  |  +-----------+  IBM PUNCH CARD VISUALIZATION SYSTEM             |
  |  |▓▓▓▓▓▓▓  ▓▓|                                                  |
  |  |▓▓▓▓▓▓▓  ▓▓|  This module renders an authentic IBM 80-column  |
  |  |▓▓    ▓▓ ▓▓|  punch card on the terminal screen or LED grid.  |
  |  |▓▓▓▓▓▓▓  ▓▓|                                                  |
  |  |▓▓       ▓▓|  It simulates the character-by-character         |
  |  |▓▓       ▓▓|  display process using historically accurate     |
  |  +-----------+  Hollerith encoding with EBCDIC compatibility.   |
  |                                                                 |
  |  * 80 columns x 12 rows (960 possible punches)                  |
  |  * Authentic IBM 026/029 keypunch behavior                      |
  |  * Character-by-character LED visualization                     |
  |  * Support for multiple character sets                          |
  |                                                                 |
  |  Author: Griffin Gilreath                                       |
  |  Updated: 2024-06-15                                            |
  |_________________________________________________________________|

Each card consists of 80 columns with the following rows:
    ┌─────────────────────────────────────────────────┐
12  │ Y     ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ │ Zone punch
11  │ X     ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ │ Zone punch
0   │ 0     ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ │ Zone punch
1   │ 1     ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ │ Digit punch
2   │ 2     ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ │ Digit punch
3   │ 3     ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ │ Digit punch
4   │ 4     ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ │ Digit punch
5   │ 5     ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ │ Digit punch
6   │ 6     ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ │ Digit punch
7   │ 7     ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ │ Digit punch
8   │ 8     ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ │ Digit punch
9   │ 9     ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ │ Digit punch
    │       1 2 3 4 5 6 7 8 9101112131415...        80│
    └─────────────────────────────────────────────────┘
"""
import os
import time
import random
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import shutil
from message_database import MessageDatabase
from pathlib import Path

def get_version_info() -> Dict[str, str]:
    """Read version information from version_info.txt"""
    try:
        # Get the project root directory (parent of src)
        project_root = Path(__file__).parent.parent
        version_dir = project_root / "versions" / "0.1.0"
        info_file = version_dir / "version_info.txt"
        
        if not info_file.exists():
            return {
                "version": "0.1.0",
                "date": "2024-03-18",
                "description": "Terminal Based IBM 80 Column Punch Card Simulator"
            }
        
        with open(info_file, 'r') as f:
            lines = f.readlines()
        
        # Parse the file content
        version = lines[0].split(': ')[1].strip()
        date = lines[1].split(': ')[1].strip()
        description = lines[2].split(': ')[1].strip()
        
        return {
            "version": version,
            "date": date,
            "description": description
        }
    except Exception as e:
        # Fallback to default values if there's any error
        return {
            "version": "0.1.0",
            "date": "2024-03-18",
            "description": "Terminal Based IBM 80 Column Punch Card Simulator"
        }

# Get version information
version_info = get_version_info()

# Constants for LED grid configuration
ROWS = 12
COLUMNS = 80
LED_COUNT = ROWS * COLUMNS
DEFAULT_BRIGHTNESS = 0.5
DEFAULT_MESSAGE = "SYSTEM READY"
DEFAULT_LED_DELAY = 0.5  # Default delay between LED updates in seconds
DEFAULT_MESSAGE_DELAY = 5  # Default delay between messages in seconds
MIN_RANDOM_DELAY = 5  # Minimum random delay (5 seconds)
MAX_RANDOM_DELAY = 15  # Maximum random delay (15 seconds)
DEFAULT_PREVIEW_DELAY = 2.0  # Default delay before starting to type the message
DEFAULT_COMPLETION_DELAY = 2.0  # Default delay after message completion in seconds
DEFAULT_TRANSITION_DELAY = 0.025  # Default delay for transition animation steps

# New constants for finer transition control
DEFAULT_RECEIVE_DURATION = 0.5  # Default duration for receiving message animation in seconds
DEFAULT_RECEIVE_STEPS = 10  # Default number of steps for receiving message progress bar
DEFAULT_TRANSITION_STEPS = 5  # Default number of steps for transition animation
DEFAULT_POST_SAVE_DELAY = 0.1  # Default delay after saving animation completes
DEFAULT_THINKING_DELAY = 0.5  # Default delay for "thinking" state before typing a new message
DEFAULT_GENERATION_DELAY = 5.0  # Default delay between messages for "generating next message" state

# Simplified constants - fixed number of steps
FIXED_PROGRESS_STEPS = 20  # Fixed number of steps for progress bar

# Constants for idle time settings
DEFAULT_MIN_IDLE_TIME = 5.0  # Default minimum idle time in seconds
DEFAULT_MAX_IDLE_TIME = 15.0  # Default maximum idle time in seconds
DEFAULT_IDLE_RANDOM = True  # Default to random idle time

# Constants for debug settings
DEFAULT_SHOW_DEBUG_MESSAGES = True  # Default to showing debug messages

# Constants for terminal size
MIN_TERMINAL_WIDTH = 101  # Changed from 100 to 101 as requested
MIN_TERMINAL_HEIGHT = 30  # Maintained at 30

# Program information
PROGRAM_NAME = "Punch Card Display System"
VERSION = version_info["version"]
LAST_REVISION = version_info["date"]
DESCRIPTION = version_info["description"]

# Settings file path
SETTINGS_FILE = 'punch_card_settings.json'

# Hollerith/EBCDIC encoding mapping
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

class PunchCardStats:
    def __init__(self):
        self.cards_processed = 0
        self.total_holes = 0
        self.character_stats = {}
        self.message_length_stats = {}  # Track count of messages by length
        self.start_time = time.time()
        self.last_update = time.time()
        self.stats_file = 'punch_card_stats.json'
        self.stats = self.load_stats()
        
    def load_stats(self):
        """Load statistics from file or create new if not exists"""
        try:
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)
                # Convert message_length_stats keys to integers and remove duplicates
                if 'message_length_stats' in stats:
                    message_length_stats = {}
                    for length, count in stats['message_length_stats'].items():
                        length = int(length)
                        message_length_stats[length] = message_length_stats.get(length, 0) + count
                    stats['message_length_stats'] = message_length_stats
                return stats
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'cards_processed': 0,
                'total_holes': 0,
                'character_stats': {},
                'message_length_stats': {},
                'start_time': time.time(),
                'last_update': time.time()
            }
    
    def save_stats(self):
        """Save current statistics to file"""
        try:
            # Ensure message_length_stats keys are strings for JSON serialization
            stats_to_save = self.stats.copy()
            stats_to_save['message_length_stats'] = {
                str(length): count 
                for length, count in self.stats['message_length_stats'].items()
            }
            with open(self.stats_file, 'w') as f:
                json.dump(stats_to_save, f)
        except Exception as e:
            print(f"Warning: Could not save stats to file: {e}")
    
    def update_message_stats(self, message: str):
        """Update statistics for a processed message"""
        self.stats['cards_processed'] += 1
        self.stats['last_update'] = time.time()
        
        # Strip trailing spaces to not count padding
        message = message.rstrip()
        
        # Update character statistics
        for char in message.upper():
            if char in self.stats['character_stats']:
                self.stats['character_stats'][char] += 1
            else:
                self.stats['character_stats'][char] = 1
        
        # Update message length statistics (using actual message length)
        msg_length = len(message)
        if msg_length in self.stats['message_length_stats']:
            self.stats['message_length_stats'][msg_length] += 1
        else:
            self.stats['message_length_stats'][msg_length] = 1
        
        # Count total holes (1 for each actual character)
        self.stats['total_holes'] += len(message)
        
        # Save updated statistics
        self.save_stats()
    
    def get_stats(self):
        """Get current statistics"""
        # Update time operating
        self.stats['time_operating'] = time.time() - self.stats['start_time']
        
        # Ensure message_length_stats exists
        if 'message_length_stats' not in self.stats:
            self.stats['message_length_stats'] = {}
            
        return self.stats

class PunchCardDisplay:
    def __init__(self, led_delay: float = DEFAULT_LED_DELAY,
                 message_delay: float = DEFAULT_MESSAGE_DELAY,
                 random_delay: bool = True,
                 skip_splash: bool = False,
                 debug_mode: bool = False):
        """Initialize the punch card display"""
        # Try to set terminal size using ANSI escape sequences
        # This won't work on all terminals but is worth trying
        print("\033[8;{0};{1}t".format(MIN_TERMINAL_HEIGHT, MIN_TERMINAL_WIDTH), end='')
        
        # Load settings from file or use defaults
        self.settings = self._load_settings()
        
        # Apply loaded settings or use defaults
        self.led_delay = self.settings.get('led_delay', led_delay)
        self.message_delay = self.settings.get('message_delay', message_delay)
        self.random_delay = self.settings.get('random_delay', random_delay)
        self.debug_mode = self.settings.get('debug_mode', debug_mode)
        self.brightness = self.settings.get('brightness', DEFAULT_BRIGHTNESS)
        self.sound_effects = self.settings.get('sound_effects', True)
        self.preview_delay = self.settings.get('preview_delay', DEFAULT_PREVIEW_DELAY)
        self.completion_delay = self.settings.get('completion_delay', DEFAULT_COMPLETION_DELAY)
        self.transition_delay = self.settings.get('transition_delay', DEFAULT_TRANSITION_DELAY)
        
        # Rest of the initialization code remains unchanged
        # Add new transition control settings
        self.receive_duration = self.settings.get('receive_duration', DEFAULT_RECEIVE_DURATION)
        self.transition_steps = self.settings.get('transition_steps', DEFAULT_TRANSITION_STEPS)
        self.post_save_delay = self.settings.get('post_save_delay', DEFAULT_POST_SAVE_DELAY)
        self.thinking_delay = self.settings.get('thinking_delay', DEFAULT_THINKING_DELAY)
        self.generation_delay = self.settings.get('generation_delay', DEFAULT_GENERATION_DELAY)
        
        # Add new idle time settings
        self.min_idle_time = self.settings.get('min_idle_time', DEFAULT_MIN_IDLE_TIME)
        self.max_idle_time = self.settings.get('max_idle_time', DEFAULT_MAX_IDLE_TIME)
        self.idle_random = self.settings.get('idle_random', DEFAULT_IDLE_RANDOM)
        
        # Add debug message display setting
        self.show_debug_messages = self.settings.get('show_debug_messages', DEFAULT_SHOW_DEBUG_MESSAGES)
        
        # Set dimensions
        self.rows = ROWS
        self.columns = COLUMNS
        
        # Get terminal dimensions
        try:
            terminal_size = shutil.get_terminal_size()
            self.terminal_width = terminal_size.columns
            self.terminal_height = terminal_size.lines
        except:
            self.terminal_width = MIN_TERMINAL_WIDTH
            self.terminal_height = MIN_TERMINAL_HEIGHT
            
        # Ensure minimum terminal size
        if self.terminal_width < MIN_TERMINAL_WIDTH:
            self.terminal_width = MIN_TERMINAL_WIDTH
        if self.terminal_height < MIN_TERMINAL_HEIGHT:
            self.terminal_height = MIN_TERMINAL_HEIGHT
        
        # Initialize display grid
        self.grid = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
        self.current_message = ""
        self.current_column = 0
        self.message_number = 0
        self.stats = PunchCardStats()
        self.wifi_status = False
        self.ip_address = "192.168.1.1"
        
        # Initialize message database
        self.message_db = MessageDatabase()
        self.message_number = self.message_db.current_message_number
        
        # Clear screen
        self._clear_screen()
        
        if self.debug_mode and self.show_debug_messages:
            print(f"Debug: Terminal size is {self.terminal_width}x{self.terminal_height}")
            print(f"Debug: Minimum required size is {MIN_TERMINAL_WIDTH}x{MIN_TERMINAL_HEIGHT}")
        
        # Adjust display dimensions if needed
        if self.terminal_width < MIN_TERMINAL_WIDTH or self.terminal_height < MIN_TERMINAL_HEIGHT:
            if not self.debug_mode:
                print(f"Note: Terminal size is {self.terminal_width}x{self.terminal_height}")
                print(f"Recommended size is {MIN_TERMINAL_WIDTH}x{MIN_TERMINAL_HEIGHT} or larger")
                print("Display will be adjusted to fit current terminal size")
                print("Press Enter to continue...")
                input()
                self._clear_screen()
            
            # Adjust dimensions to fit available space
            self.columns = min(self.columns, self.terminal_width - 4)  # Leave space for borders
            self.rows = min(self.rows, self.terminal_height - 6)  # Leave space for status and borders
            self.grid = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
            if self.debug_mode and self.show_debug_messages:
                print(f"Debug: Adjusted display size to {self.rows}x{self.columns}")
        else:
            # If terminal is large enough, use default size
            self.columns = COLUMNS
            self.rows = ROWS
            self.grid = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
            if self.debug_mode and self.show_debug_messages:
                print(f"Debug: Using default display size {self.rows}x{self.columns}")
        
        # Display empty card initially
        self._display_static_card()
        
    def _load_settings(self) -> dict:
        """Load settings from file or return defaults"""
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'led_delay': DEFAULT_LED_DELAY,
                'message_delay': DEFAULT_MESSAGE_DELAY,
                'random_delay': True,
                'debug_mode': False,
                'brightness': DEFAULT_BRIGHTNESS,
                'sound_effects': True,
                'preview_delay': DEFAULT_PREVIEW_DELAY,
                'completion_delay': DEFAULT_COMPLETION_DELAY,
                'transition_delay': DEFAULT_TRANSITION_DELAY,
                'min_idle_time': DEFAULT_MIN_IDLE_TIME,
                'max_idle_time': DEFAULT_MAX_IDLE_TIME,
                'idle_random': DEFAULT_IDLE_RANDOM,
                'show_debug_messages': DEFAULT_SHOW_DEBUG_MESSAGES
            }
    
    def _save_settings(self):
        """Save current settings to file"""
        settings = {
            'led_delay': self.led_delay,
            'message_delay': self.message_delay,
            'random_delay': self.random_delay,
            'debug_mode': self.debug_mode,
            'brightness': self.brightness,
            'sound_effects': self.sound_effects,
            'preview_delay': self.preview_delay,
            'completion_delay': self.completion_delay,
            'transition_delay': self.transition_delay,
            'min_idle_time': self.min_idle_time,
            'max_idle_time': self.max_idle_time,
            'idle_random': self.idle_random,
            'show_debug_messages': self.show_debug_messages,
            # Add new transition settings
            'receive_duration': self.receive_duration,
            'transition_steps': self.transition_steps,
            'post_save_delay': self.post_save_delay,
            'thinking_delay': self.thinking_delay,
            'generation_delay': self.generation_delay
        }
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            if self.debug_mode:
                print(f"Warning: Could not save settings to file: {e}")
    
    def _restore_default_settings(self):
        """Restore all settings to their default values"""
        self.led_delay = DEFAULT_LED_DELAY
        self.message_delay = DEFAULT_MESSAGE_DELAY
        self.random_delay = True
        self.debug_mode = False
        self.brightness = DEFAULT_BRIGHTNESS
        self.sound_effects = True
        self.preview_delay = DEFAULT_PREVIEW_DELAY
        self.completion_delay = DEFAULT_COMPLETION_DELAY
        self.transition_delay = DEFAULT_TRANSITION_DELAY
        self.min_idle_time = DEFAULT_MIN_IDLE_TIME
        self.max_idle_time = DEFAULT_MAX_IDLE_TIME
        self.idle_random = DEFAULT_IDLE_RANDOM
        # Reset new transition settings
        self.receive_duration = DEFAULT_RECEIVE_DURATION
        self.transition_steps = DEFAULT_TRANSITION_STEPS
        self.post_save_delay = DEFAULT_POST_SAVE_DELAY
        self.thinking_delay = DEFAULT_THINKING_DELAY
        self.generation_delay = DEFAULT_GENERATION_DELAY
        # Reset debug message display setting
        self.show_debug_messages = DEFAULT_SHOW_DEBUG_MESSAGES
        self._save_settings()

    def _ensure_terminal_size(self):
        """Update terminal size information"""
        self.terminal_width = shutil.get_terminal_size().columns
        self.terminal_height = shutil.get_terminal_size().lines
        return self.terminal_width, self.terminal_height
        
    def _clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
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
        return reordered_pattern
        
    def _get_character_description(self, char: str) -> str:
        """Get the description of a character's punch pattern"""
        return PUNCH_DESCRIPTIONS.get(char.upper(), "unknown")
            
    def _display_grid(self, status: str = None, show_message: bool = True, show_progress_bar: bool = False, progress: int = 0, total_steps: int = 0, is_transition: bool = False, show_row_numbers: bool = True):
        """Display the current state of the LED grid"""
        self._clear_screen()
        
        # Use the helper method to calculate offsets consistently, with additional offset for main display
        x_offset, y_offset = self._calculate_offsets(header_height=4, footer_height=1, apply_additional_offset=True)
        y_offset -= 3  # Move the display up by 3 rows (changed from -2 to -3)
        
        # Add vertical spacing to center the content
        print("\n" * max(0, y_offset))
        
        # Display message number and content (static position)
        if is_transition:
            message_text = "Saving to Database. . ."
        else:
            message_text = f"Message #{self.message_number:07d}: {self.current_message}"
            
        # Calculate the width of the message and status to align with rectangle edges
        if status:
            status_text = f"Status: {status}"
        elif show_progress_bar:
            if is_transition:
                status_text = "Status: SAVING. . ."
            else:
                status_text = "Status: LISTENING. . ."
        else:
            if self.current_column < len(self.current_message):
                status_text = "Status: TYPING"
            else:
                status_text = "Status: IDLE"
                
        # Get message source from database
        message_record = self.message_db.get_message(self.message_number)
        source_text = f"Source: {message_record.source if message_record else 'Unknown'}"
        
        # Always print message headers to maintain consistent spacing
        # If show_message is False, print blank lines instead of actual content
        if show_message:
            print(" " * x_offset + message_text)
            print(" " * x_offset + source_text)
            print(" " * x_offset + status_text)
            print()
        else:
            # Print empty header lines to maintain consistent spacing
            print(" " * x_offset + "Message #0000000: ")
            print(" " * x_offset + "Source: ")
            print(" " * x_offset + "Status: ")
            print()
        
        # Print top border with corner cutout
        print(" " * x_offset + "   ┌" + "─" * (self.columns - 1) + "─┐")
        
        # Define the correct row order for punch cards: 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
        row_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        row_labels = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        
        # Print grid with correct row order and consistent spacing
        for i, row_idx in enumerate(row_order):
            row_num = row_labels[i] if show_row_numbers else "  "  # Use the correct row label
            # Create row content with empty boxes for all holes
            row_content = ""
            for col in range(self.columns):
                if self.grid[row_idx][col]:
                    row_content += "█"  # Filled box for punched hole
                else:
                    row_content += "□"  # Empty box for unpunched hole
            print(" " * x_offset + f"{row_num:2s} │{row_content}│")
        
        # Print bottom border
        print(" " * x_offset + "   └" + "─" * (self.columns - 1) + "─┘")
        
        # Add empty line before decrypting status
        print()
        
        # Only print progress bar or decryption status if needed
        if show_progress_bar:
            # Calculate percentage
            percentage = int((progress / total_steps) * 100)
            progress_bar = "█" * progress + "░" * (total_steps - progress)
            
            # Create more lively bouncing dashes animation
            dash_position = int((time.time() * 3) % 8)  # Bounce between 0-7 positions
            dashes = " " * dash_position + "-" * 5 + " " * (7 - dash_position)
            
            # Show progress bar with left-justified text
            print(" " * x_offset + f"Receiving Message {dashes} [{progress_bar}] {percentage}%")
        else:
            # Show decrypting message during message display
            if show_message and self.current_column < len(self.current_message):
                current_char = self.current_message[self.current_column]
                print(" " * x_offset + f"Decrypting: {current_char}({self._get_character_description(current_char)})")
            else:
                # Print empty line to maintain consistent spacing
                print()
        
        # Add remaining vertical spacing to complete centering
        # Adjust total_content_height to account for the extra empty line
        total_content_height = (self.rows + 2) + 4 + 2  # card height + header height + footer height + extra line
        remaining_lines = max(0, self.terminal_height - y_offset - total_content_height)
        if remaining_lines > 0:
            print("\n" * remaining_lines)
        
    def show_message(self, message: str, source: str = "Generated"):
        """Display a message on the LED grid"""
        # Store the previous message grid state before clearing for the new message
        previous_grid = [row[:] for row in self.grid]  # Deep copy of current grid
        
        # Add message to database and get message number
        self.message_number = self.message_db.add_message(message, source)
        self.current_message = message
        message = message.ljust(self.columns)[:self.columns]
        
        # Update statistics
        self.stats.update_message_stats(message)
        
        # ===== TYPING STATE =====
        # Display each character with original delays
        for col, char in enumerate(message):
            self.current_column = col
            pattern = self.char_to_led_pattern(char)
            for row, is_punched in enumerate(pattern):
                self.grid[row][col] = is_punched
            self._display_grid(show_progress_bar=False)
            time.sleep(self.led_delay)
        
        # Update display time in database
        self.message_db.update_display_time(self.message_number)
        
        # ===== IDLE STATE =====
        # Wait after message completion using the configurable delay
        time.sleep(0.2 if self.debug_mode else self.completion_delay)
        
        # ===== RECEIVING/LISTENING STATE =====
        # Show "Receiving Message" progress bar until 100% using configurable parameters
        for i in range(FIXED_PROGRESS_STEPS):
            self._display_grid(show_progress_bar=True, progress=i, total_steps=FIXED_PROGRESS_STEPS, is_transition=False)
            time.sleep(self.receive_duration / FIXED_PROGRESS_STEPS)
        
        # Store the current message's grid for transition
        current_message_grid = [row[:] for row in self.grid]  # Deep copy of current grid
        
        # ===== SAVING/CLEARING STATE =====
        # Animate the sliding transition (saving animation)
        for step in range(self.transition_steps):
            # Create a temporary grid for the transition
            temp_grid = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
            
            # Calculate current transition progress (0.0 to 1.0)
            progress = step / self.transition_steps
            
            # Simple slide effect - move content left
            offset = int(progress * self.columns)
            for row in range(self.rows):
                for col in range(self.columns):
                    if col + offset < self.columns:
                        temp_grid[row][col] = current_message_grid[row][col + offset]
            
            # Update the main grid with the temporary grid
            self.grid = temp_grid
            
            # Update the display showing transition status
            self._display_grid(show_progress_bar=True, progress=FIXED_PROGRESS_STEPS, total_steps=FIXED_PROGRESS_STEPS, is_transition=True)
            
            # Use the configured transition delay
            time.sleep(self.transition_delay)
        
        # Optional post-save delay
        if self.post_save_delay > 0:
            time.sleep(self.post_save_delay)
        
        # ===== THINKING STATE =====
        # Clear the grid completely for the "thinking" state
        self.grid = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
        self.current_message = ""
        self.current_column = 0
        
        # Display empty card with "THINKING" status if delay is set
        if self.thinking_delay > 0:
            # Create custom display method for thinking state to avoid recycling _display_static_card
            self._display_thinking_state()
            time.sleep(self.thinking_delay)
            # Note: The actual generation delay happens in the main.py file, not here
        
    def _display_thinking_state(self):
        """Display an empty card with THINKING status"""
        # Clear screen first to ensure no previous content
        self._clear_screen()
        
        # Calculate centering offsets using the helper method with consistent header height
        x_offset, y_offset = self._calculate_offsets(header_height=4, footer_height=1)
        
        # Add vertical spacing to center the content
        print("\n" * max(0, y_offset))
        
        # Print message headers in the consistent position
        print(" " * x_offset + "Message #0000000: ")
        print(" " * x_offset + "Source: Neural Engine")
        print(" " * x_offset + "Status: GENERATING NEXT MESSAGE...")
        print()
        
        # Print top border with corner cutout
        print(" " * x_offset + "   ┌" + "─" * (self.columns - 1) + "─┐")
        
        # Define the correct row order for punch cards
        row_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        row_labels = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        
        # Print grid with empty boxes
        for i, row_idx in enumerate(row_order):
            row_num = row_labels[i]
            row_content = "□" * self.columns
            print(" " * x_offset + f"{row_num:2s} │{row_content}│")
        
        # Print bottom border
        print(" " * x_offset + "   └" + "─" * (self.columns - 1) + "─┘")
        
        # Add remaining vertical spacing with consistent calculations
        total_content_height = (self.rows + 2) + 4 + 1  # card height + header height + footer height
        remaining_lines = max(0, self.terminal_height - y_offset - total_content_height)
        if remaining_lines > 0:
            print("\n" * remaining_lines)
            
    def _display_static_card(self):
        """Display the static punch card rectangle without any delays"""
        # Clear screen first to ensure no previous content
        self._clear_screen()
        
        # Calculate centering offsets using the helper method with consistent header height
        x_offset, y_offset = self._calculate_offsets(header_height=4, footer_height=1)
        
        # Add vertical spacing to center the card
        print("\n" * max(0, y_offset))
        
        # Print message headers in the consistent position
        print(" " * x_offset + "Message #0000000: ")
        print(" " * x_offset + "Source: ")
        print(" " * x_offset + "Status: IDLE")
        print()
        
        # Print top border with corner cutout
        print(" " * x_offset + "   ┌" + "─" * (self.columns - 1) + "─┐")
        
        # Define the correct row order for punch cards: 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
        row_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        row_labels = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        
        # Print grid with empty boxes
        for i, row_idx in enumerate(row_order):
            row_num = row_labels[i]
            row_content = "□" * self.columns
            print(" " * x_offset + f"{row_num:2s} │{row_content}│")
        
        # Print bottom border
        print(" " * x_offset + "   └" + "─" * (self.columns - 1) + "─┘")
        
        # Add remaining vertical spacing with consistent calculations
        total_content_height = (self.rows + 2) + 4 + 1  # card height + header height + footer height
        remaining_lines = max(0, self.terminal_height - y_offset - total_content_height)
        if remaining_lines > 0:
            print("\n" * remaining_lines)
            
    def _display_loading_screen(self, message: str, progress: int = 0):
        """Display a loading screen message within the punch card rectangle"""
        self._clear_screen()
        
        # Calculate centering offsets using the helper method with consistent header height
        x_offset, y_offset = self._calculate_offsets(header_height=4, footer_height=1)
        
        # Add vertical spacing to center the content
        print("\n" * max(0, y_offset))
        
        # Print message headers in the consistent position
        print(" " * x_offset + "Message #0000000: ")
        print(" " * x_offset + "Source: Loading")
        print(" " * x_offset + "Status: INITIALIZING")
        print()
        
        # Display the card frame
        print(" " * x_offset + "   ┌" + "─" * (self.columns - 1) + "─┐")
        
        # Define row order and labels
        row_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        row_labels = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        
        # Calculate text positioning for message in the center
        message_row = self.rows // 2
        
        # Print grid with message in the center
        for i, row_idx in enumerate(row_order):
            row_num = row_labels[i] if i < len(row_labels) else "  "
            
            if i == message_row:
                # Center the message
                padding = (self.columns - len(message)) // 2
                row_content = " " * padding + message + " " * (self.columns - padding - len(message))
            elif i == message_row + 2 and progress > 0:  # Progress bar 2 rows below message
                progress_bar = "█" * progress + "░" * (20 - progress)
                progress_text = f"[{progress_bar}] {progress * 5}%"
                padding = (self.columns - len(progress_text)) // 2
                row_content = " " * padding + progress_text + " " * (self.columns - padding - len(progress_text))
            else:
                row_content = " " * self.columns
                
            print(" " * x_offset + f"{row_num:2s} │{row_content}│")
        
        # Print bottom border
        print(" " * x_offset + "   └" + "─" * (self.columns - 1) + "─┘")
        
        # Add remaining vertical spacing with consistent calculations
        total_content_height = (self.rows + 2) + 4 + 1  # card height + header height + footer height
        remaining_lines = max(0, self.terminal_height - y_offset - total_content_height)
        if remaining_lines > 0:
            print("\n" * remaining_lines)
        
    def _display_text_in_card(self, text_lines: List[str], show_row_numbers: bool = False):
        """Display text within the punch card rectangle"""
        self._clear_screen()

        # Calculate offsets using helper method with consistent header height
        x_offset, y_offset = self._calculate_offsets(header_height=4, footer_height=1)

        # Add vertical spacing to center the content
        print("\n" * max(0, y_offset))

        # Print message headers in the consistent position
        print(" " * x_offset + "Message #0000000: ")
        print(" " * x_offset + "Source: Information Display")
        print(" " * x_offset + "Status: System")
        print()

        # Print top border with corner cutout
        print(" " * x_offset + "   ┌" + "─" * (self.columns - 1) + "─┐")

        # Define the correct row order for punch cards
        row_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        row_labels = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

        # Calculate text positioning
        total_lines = len(text_lines)
        start_row = (self.rows - total_lines) // 2

        # Print grid with text
        for i, row_idx in enumerate(row_order):
            row_num = row_labels[i] if show_row_numbers else "  "
            if start_row <= i < start_row + total_lines:
                text_line = text_lines[i - start_row]
                padding = (self.columns - len(text_line)) // 2
                row_content = " " * padding + text_line + " " * (self.columns - padding - len(text_line))
            else:
                row_content = " " * self.columns
            print(" " * x_offset + f"{row_num:2s} │{row_content}│")

        # Print bottom border
        print(" " * x_offset + "   └" + "─" * (self.columns - 1) + "─┘")

        # Add remaining vertical spacing with consistent calculations
        total_content_height = (self.rows + 2) + 4 + 1  # card height + header height + footer height
        remaining_lines = max(0, self.terminal_height - y_offset - total_content_height)
        if remaining_lines > 0:
            print("\n" * remaining_lines)

    def _animate_holes_filling(self):
        """Animate holes filling with a wave pattern that moves diagonally"""
        # Calculate offsets for consistent positioning - use same as other methods
        x_offset, y_offset = self._calculate_offsets(header_height=4, footer_height=1)
        
        # Add additional vertical offset to move wave down
        y_offset += 4  # Move wave down by 3 rows
        
        # Define row order and labels
        row_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        row_labels = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        
        # Create a temporary grid for the animation
        temp_grid = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
        
        # Display empty card for 0.2 seconds before starting
        self._clear_screen()
        
        # Add vertical spacing to center the content
        print("\n" * max(0, y_offset))
        
        # Print the initial empty card frame - no headers
        print(" " * x_offset + "   ┌" + "─" * (self.columns - 1) + "─┐")
        for i, row_idx in enumerate(row_order):
            row_num = "  "  # Hide row numbers during animation
            row_content = " " * self.columns
            print(" " * x_offset + f"{row_num:2s} │{row_content}│")
        print(" " * x_offset + "   └" + "─" * (self.columns - 1) + "─┘")
        
        # Add remaining vertical spacing
        total_content_height = (self.rows + 2) + 1  # card height + footer height (no headers)
        remaining_lines = max(0, self.terminal_height - y_offset - total_content_height)
        if remaining_lines > 0:
            print("\n" * remaining_lines)
            
        time.sleep(0.2)
        
        # Calculate total number of diagonals
        total_diagonals = 12 + self.columns - 1  # Fixed to use 12 rows
        
        # Animate holes filling
        for diagonal in range(total_diagonals + 24):  # Add 24 to allow trailing waves to complete
            # Calculate start position for leading empty holes
            if diagonal < 12:  # Fixed to use 12 rows
                row = diagonal
                col = 0
            else:
                row = 11  # Fixed to use 11 (last row index)
                col = diagonal - 12 + 1
            
            # Fill leading empty holes
            empty_row, empty_col = row, col
            while empty_row >= 0 and empty_col < self.columns:
                if empty_col < self.columns:  # Check column bounds
                    temp_grid[empty_row][empty_col] = 2  # Use 2 to indicate empty hole
                empty_row -= 1
                empty_col += 1
            
            # Fill punched holes 12 diagonals behind
            punched_diagonal = diagonal - 12
            if punched_diagonal >= 0:
                if punched_diagonal < 12:  # Fixed to use 12 rows
                    punched_row = punched_diagonal
                    punched_col = 0
                else:
                    punched_row = 11  # Fixed to use 11 (last row index)
                    punched_col = punched_diagonal - 12 + 1
                
                while punched_row >= 0 and punched_col < self.columns:
                    if punched_col < self.columns:  # Check column bounds
                        temp_grid[punched_row][punched_col] = 1  # Use 1 to indicate punched hole
                    punched_row -= 1
                    punched_col += 1
            
            # Fill trailing empty holes 12 diagonals behind punched holes
            trailing_diagonal = diagonal - 24
            if trailing_diagonal >= 0:
                if trailing_diagonal < 12:  # Fixed to use 12 rows
                    trailing_row = trailing_diagonal
                    trailing_col = 0
                else:
                    trailing_row = 11  # Fixed to use 11 (last row index)
                    trailing_col = trailing_diagonal - 12 + 1
                
                while trailing_row >= 0 and trailing_col < self.columns:
                    if trailing_col < self.columns:  # Check column bounds
                        temp_grid[trailing_row][trailing_col] = 2  # Use 2 to indicate empty hole
                    trailing_row -= 1
                    trailing_col += 1
            
            # Print current state
            self._clear_screen()
            
            # Add vertical spacing to center the content
            print("\n" * max(0, y_offset))
            
            # Print the card frame with current animation state - no headers
            print(" " * x_offset + "   ┌" + "─" * (self.columns - 1) + "─┐")
            for i, row_idx in enumerate(row_order):
                row_num = "  "  # Hide row numbers during animation
                row_content = ""
                for j in range(self.columns):
                    if temp_grid[row_idx][j] == 1:
                        row_content += "█"
                    elif temp_grid[row_idx][j] == 2:
                        row_content += "□"
                    else:
                        row_content += " "
                print(" " * x_offset + f"{row_num:2s} │{row_content}│")
            print(" " * x_offset + "   └" + "─" * (self.columns - 1) + "─┘")
            
            # Add remaining vertical spacing
            remaining_lines = max(0, self.terminal_height - y_offset - total_content_height)
            if remaining_lines > 0:
                print("\n" * remaining_lines)
                
            time.sleep(0.05)  # Adjust speed of animation
        
        # Animate row numbers counting up starting from 0
        for i in range(13):  # Fixed to use 13 (12 rows + 1 for final state)
            self._clear_screen()
            
            # Add vertical spacing to center the content
            print("\n" * max(0, y_offset))
            
            print(" " * x_offset + "   ┌" + "─" * (self.columns - 1) + "─┐")
            for j, row_idx in enumerate(row_order):
                # Show row numbers in order: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12
                if j < i:
                    row_num = row_labels[j]
                else:
                    row_num = "  "  # Hide row number if we haven't reached it yet
                row_content = ""
                for k in range(self.columns):
                    if temp_grid[row_idx][k] == 1:
                        row_content += "█"
                    elif temp_grid[row_idx][k] == 2:
                        row_content += "□"
                    else:
                        row_content += " "
                print(" " * x_offset + f"{row_num:2s} │{row_content}│")
            print(" " * x_offset + "   └" + "─" * (self.columns - 1) + "─┘")
            
            # Add remaining vertical spacing
            remaining_lines = max(0, self.terminal_height - y_offset - total_content_height)
            if remaining_lines > 0:
                print("\n" * remaining_lines)
                
            time.sleep(0.1)  # Adjust speed of row number animation
        
        # Keep the final state visible for 0.2 seconds with all row numbers
        self._clear_screen()
        
        # Add vertical spacing to center the content
        print("\n" * max(0, y_offset))
        
        print(" " * x_offset + "   ┌" + "─" * (self.columns - 1) + "─┐")
        for i, row_idx in enumerate(row_order):
            row_num = row_labels[i]  # Show all row numbers in final state
            row_content = ""
            for j in range(self.columns):
                if temp_grid[row_idx][j] == 1:
                    row_content += "█"
                elif temp_grid[row_idx][j] == 2:
                    row_content += "□"
                else:
                    row_content += " "
            print(" " * x_offset + f"{row_num:2s} │{row_content}│")
        print(" " * x_offset + "   └" + "─" * (self.columns - 1) + "─┘")
        
        # Add remaining vertical spacing
        remaining_lines = max(0, self.terminal_height - y_offset - total_content_height)
        if remaining_lines > 0:
            print("\n" * remaining_lines)
            
        time.sleep(1.0)

    def _show_settings_menu(self):
        """Display and handle the settings menu"""
        # Define settings with their descriptions
        settings = [
            {
                'name': 'Sound Effects',
                'value': lambda: "ON" if self.sound_effects else "OFF",
                'adjust': lambda key: setattr(self, 'sound_effects', not self.sound_effects),
                'description': "Enable/disable sound effects for card operations"
            },
            {
                'name': 'LED Delay',
                'value': lambda: f"{self.led_delay:.2f}s",
                'adjust': lambda key: setattr(self, 'led_delay', 
                    min(1.0, self.led_delay + 0.1) if key == 'right' else max(0.1, self.led_delay - 0.1)),
                'description': "Time between each LED update (0.1-1.0s)"
            },
            {
                'name': 'Message Delay',
                'value': lambda: f"{self.message_delay:.2f}s",
                'adjust': lambda key: setattr(self, 'message_delay',
                    min(10.0, self.message_delay + 1.0) if key == 'right' else max(1.0, self.message_delay - 1.0)),
                'description': "Time between messages (1.0-10.0s)"
            },
            {
                'name': 'Preview Delay',
                'value': lambda: f"{self.preview_delay:.2f}s",
                'adjust': lambda key: setattr(self, 'preview_delay',
                    min(5.0, self.preview_delay + 0.5) if key == 'right' else max(0.5, self.preview_delay - 0.5)),
                'description': "Time message shows before typing (0.5-5.0s)"
            },
            {
                'name': 'Completion Delay',
                'value': lambda: f"{self.completion_delay:.2f}s",
                'adjust': lambda key: setattr(self, 'completion_delay',
                    min(5.0, self.completion_delay + 0.5) if key == 'right' else max(0.5, self.completion_delay - 0.5)),
                'description': "Time to pause after message is complete (0.5-5.0s)"
            },
            {
                'name': 'Transition Delay',
                'value': lambda: f"{self.transition_delay:.2f}s",
                'adjust': lambda key: setattr(self, 'transition_delay',
                    min(0.2, self.transition_delay + 0.025) if key == 'right' else max(0.01, self.transition_delay - 0.025)),
                'description': "Speed of transition animation (0.01-0.2s)"
            },
            # New transition settings
            {
                'name': 'Receive Duration',
                'value': lambda: f"{self.receive_duration:.2f}s",
                'adjust': lambda key: setattr(self, 'receive_duration',
                    min(2.0, self.receive_duration + 0.1) if key == 'right' else max(0.1, self.receive_duration - 0.1)),
                'description': "Time showing progress bar before saving (0.1-2.0s)"
            },
            {
                'name': 'Transition Steps',
                'value': lambda: f"{self.transition_steps}",
                'adjust': lambda key: setattr(self, 'transition_steps',
                    min(15, self.transition_steps + 1) if key == 'right' else max(2, self.transition_steps - 1)),
                'description': "Number of steps in the saving animation (2-15)"
            },
            {
                'name': 'Post Save Delay',
                'value': lambda: f"{self.post_save_delay:.2f}s",
                'adjust': lambda key: setattr(self, 'post_save_delay',
                    min(1.0, self.post_save_delay + 0.1) if key == 'right' else max(0.0, self.post_save_delay - 0.1)),
                'description': "Extra time to show SAVING status (0.0-1.0s)"
            },
            {
                'name': 'Thinking Delay',
                'value': lambda: f"{self.thinking_delay:.2f}s",
                'adjust': lambda key: setattr(self, 'thinking_delay',
                    min(2.0, self.thinking_delay + 0.1) if key == 'right' else max(0.0, self.thinking_delay - 0.1)),
                'description': "Time showing THINKING status before new message (0.0-2.0s)"
            },
            {
                'name': 'Generation Delay',
                'value': lambda: f"{self.generation_delay:.2f}s",
                'adjust': lambda key: setattr(self, 'generation_delay',
                    min(30.0, self.generation_delay + 1.0) if key == 'right' else max(1.0, self.generation_delay - 1.0)),
                'description': "Time between messages for GENERATING NEXT MESSAGE (1.0-30.0s)"
            },
            {
                'name': 'Random Delay',
                'value': lambda: "ON" if self.random_delay else "OFF",
                'adjust': lambda key: setattr(self, 'random_delay', not self.random_delay),
                'description': "Use random delays between messages (5-15s)"
            },
            {
                'name': 'Min Idle Time',
                'value': lambda: f"{self.min_idle_time:.2f}s",
                'adjust': lambda key: setattr(self, 'min_idle_time',
                    min(30.0, self.min_idle_time + 1.0) if key == 'right' else max(1.0, self.min_idle_time - 1.0)),
                'description': "Minimum time to wait when idle (1.0-30.0s)"
            },
            {
                'name': 'Max Idle Time',
                'value': lambda: f"{self.max_idle_time:.2f}s",
                'adjust': lambda key: setattr(self, 'max_idle_time',
                    min(60.0, self.max_idle_time + 1.0) if key == 'right' else max(self.min_idle_time, self.max_idle_time - 1.0)),
                'description': "Maximum time to wait when idle (min-60.0s)"
            },
            {
                'name': 'Random Idle Time',
                'value': lambda: "ON" if self.idle_random else "OFF",
                'adjust': lambda key: setattr(self, 'idle_random', not self.idle_random),
                'description': "Use random idle time between min and max"
            },
            {
                'name': 'Debug Mode',
                'value': lambda: "ON" if self.debug_mode else "OFF",
                'adjust': lambda key: setattr(self, 'debug_mode', not self.debug_mode),
                'description': "Show debug information and use faster timings"
            },
            {
                'name': 'Show Debug Messages',
                'value': lambda: "ON" if self.show_debug_messages else "OFF",
                'adjust': lambda key: setattr(self, 'show_debug_messages', not self.show_debug_messages),
                'description': "Show debug messages at startup"
            },
            {
                'name': 'Brightness',
                'value': lambda: f"{self.brightness:.2f}",
                'adjust': lambda key: setattr(self, 'brightness',
                    min(1.0, self.brightness + 0.1) if key == 'right' else max(0.1, self.brightness - 0.1)),
                'description': "LED brightness level (0.1-1.0)"
            },
            {
                'name': 'Restore Defaults',
                'value': lambda: "Press Enter",
                'adjust': lambda key: self._restore_default_settings() if key == 'enter' else None,
                'description': "Reset all settings to default values"
            }
        ]
        
        current_setting = 0
        
        while True:
            # Clear screen completely
            self._clear_screen()
            
            # Create the content for the menu
            menu_content = []
            
            # Add title at the top with empty line after
            menu_content.append("SETTINGS")
            menu_content.append("")
            menu_content.append("")
            
            # Add current setting with arrow
            setting = settings[current_setting]
            menu_content.append(f"→ {setting['name']}: {setting['value']()}")
            menu_content.append("")
            
            # Add description with empty line after
            menu_content.append(setting['description'])
            menu_content.append("")
            
            # Add empty lines for centering
            menu_content.append("")
            menu_content.append("")
            
            # Add controls with improved formatting
            menu_content.append("Navigation: ↑/↓  Adjust: ←/→  Enter: Save & Exit  Esc: Cancel")
            
            # Display the menu within the card frame with headers hidden
            self._display_card_frame(menu_content, show_row_numbers=False, is_settings=True, hide_headers=True)
            
            # Handle user input
            key = self._get_key()
            
            if key == 'esc':
                return
            elif key == 'enter':
                if setting['name'] == 'Restore Defaults':
                    setting['adjust'](key)
                else:
                    self._save_settings()  # Save settings before exiting
                    # Play the punch card animation after saving settings
                    self._animate_holes_filling()
                    return
            elif key == 'up':
                current_setting = (current_setting - 1) % len(settings)
            elif key == 'down':
                current_setting = (current_setting + 1) % len(settings)
            elif key == 'left' or key == 'right':
                setting['adjust'](key)

    def _show_confirmation(self, message: str) -> bool:
        """Show a confirmation dialog and return True if confirmed"""
        while True:
            self._clear_screen()
            menu_lines = [
                "CONFIRMATION",
                "",
                message,
                "",
                "Controls:",
                "Y: Yes",
                "N: No"
            ]
            # Show headers for consistent spacing
            self._display_card_frame(menu_lines, show_row_numbers=False, is_settings=True, hide_headers=False)
            
            if os.name == 'nt':
                key = msvcrt.getch().decode().upper()
            else:
                key = sys.stdin.read(1).upper()
            
            if key == 'Y':
                return True
            elif key == 'N':
                return False

    def show_splash_screen(self):
        """Display the splash screen with loading messages and statistics"""
        self._clear_screen()
        
        # Show initial loading messages within the card
        loading_messages = [
            "IBM PUNCH CARD SYSTEM",
            "Terminal Based IBM 80 Column Punch Card Simulator",
            f"Version {version_info['version']}",
            "",
            "Initializing System...",
            "Loading Character Mappings...",
            "Configuring Display Settings...",
            "Preparing Punch Card Interface..."
        ]
        
        # Display each loading message with a longer delay
        for i, message in enumerate(loading_messages):
            content = [message]
            self._display_card_frame(content, show_row_numbers=False, is_settings=False, hide_headers=True)
            # Longer delay for title pages, shorter for loading messages
            if i < 4:  # First 4 messages (title pages)
                time.sleep(1.2)  # 1.2 seconds for title pages
            else:
                time.sleep(0.7)  # 0.7 seconds for loading messages
        
        # Get current statistics
        stats = self.stats.get_stats()
        time_operating = stats['time_operating']
        days = int(time_operating // (24 * 3600))
        hours = int((time_operating % (24 * 3600)) // 3600)
        minutes = int((time_operating % 3600) // 60)
        seconds = int(time_operating % 60)
        
        # Page 1: Display Configuration
        config_stats = [
            "Display Configuration",
            f"Grid Size: {self.rows}x{self.columns}",
            f"Total LEDs: {self.rows * self.columns}",
            f"LED Delay: {self.led_delay:.2f}s",
            f"Message Delay: {self.message_delay:.2f}s",
            f"LED Brightness: {self.brightness:.2f}"
        ]
        self._display_card_frame(config_stats, show_row_numbers=False, is_settings=False, hide_headers=True)
        time.sleep(2.5)  # Increased from 2 to 2.5 seconds
        
        # Page 2: System Status
        system_stats = [
            "System Status",
            f"Debug Mode: {'Enabled' if self.debug_mode else 'Disabled'}",
            f"Random Delay: {'Enabled' if self.random_delay else 'Disabled'}",
            f"WiFi Status: {'Connected' if self.wifi_status else 'Disconnected'}",
            f"IP Address: {self.ip_address}",
            f"Time Operating: {days}d {hours}h {minutes}m {seconds}s",
            f"Last Update: {datetime.fromtimestamp(stats['last_update']).strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        self._display_card_frame(system_stats, show_row_numbers=False, is_settings=False, hide_headers=True)
        time.sleep(2.5)  # Increased from 2 to 2.5 seconds
        
        # Page 3: Statistics Overview
        overview_stats = [
            "System Statistics",
            f"Total Cards Processed: {stats['cards_processed']}",
            f"Test Messages: {stats.get('test_messages', 0)}",
            f"Current Index Size: {stats.get('index_size', 0)}",
            f"Version: {VERSION}"
        ]
        self._display_card_frame(overview_stats, show_row_numbers=False, is_settings=False, hide_headers=True)
        time.sleep(2.5)  # Increased from 2 to 2.5 seconds
        
        # Page 4: Character Statistics - Numbers and Letters
        char_stats = ["Character Statistics"]
        # Numbers in one row
        number_line = ""
        for char in "0123456789":
            count = stats['character_stats'].get(char, 0)
            number_line += f"{char}:{count} "
        char_stats.append(number_line)
        char_stats.append("")  # Empty line for spacing
        
        # Letters in three groups
        # A-J
        letter_line = ""
        for char in "ABCDEFGHIJ":
            count = stats['character_stats'].get(char, 0)
            letter_line += f"{char}:{count} "
        char_stats.append(letter_line)
        
        # K-T
        letter_line = ""
        for char in "KLMNOPQRST":
            count = stats['character_stats'].get(char, 0)
            letter_line += f"{char}:{count} "
        char_stats.append(letter_line)
        
        # U-Z
        letter_line = ""
        for char in "UVWXYZ":
            count = stats['character_stats'].get(char, 0)
            letter_line += f"{char}:{count} "
        char_stats.append(letter_line)
        
        # Space count
        char_stats.append("")  # Empty line for spacing
        space_count = stats['character_stats'].get(' ', 0)
        char_stats.append(f'"Space":{space_count}')
        
        self._display_card_frame(char_stats, show_row_numbers=False, is_settings=False, hide_headers=True)
        time.sleep(2.5)  # Increased from 2 to 2.5 seconds
        
        # Page 5: Symbol Statistics - Reorganized for better visuals
        symbol_stats = ["Symbol Statistics"]
        
        # Group symbols by type with better spacing
        punctuation = ".,-+*/=()$@#%&!\"':;?"
        brackets = "[]{}|\\<>~`^_"
        
        # Add punctuation symbols with better spacing
        symbol_line = ""
        for i, char in enumerate(punctuation):
            count = stats['character_stats'].get(char, 0)
            if count > 0:  # Only show symbols that have been used
                symbol_line += f"{char}:{count} "
                if (i + 1) % 8 == 0:  # New line after every 8 symbols
                    symbol_stats.append(symbol_line)
                    symbol_line = ""
        if symbol_line:  # Add any remaining symbols
            symbol_stats.append(symbol_line)
            
        # Add more empty lines for better visual separation
        symbol_stats.append("")
        symbol_stats.append("")
        
        # Add bracket symbols
        symbol_line = ""
        for i, char in enumerate(brackets):
            count = stats['character_stats'].get(char, 0)
            if count > 0:  # Only show symbols that have been used
                symbol_line += f"{char}:{count} "
                if (i + 1) % 8 == 0:  # New line after every 8 symbols
                    symbol_stats.append(symbol_line)
                    symbol_line = ""
        if symbol_line:  # Add any remaining symbols
            symbol_stats.append(symbol_line)
        
        self._display_card_frame(symbol_stats, show_row_numbers=False, is_settings=False, hide_headers=True)
        time.sleep(2.5)  # Increased from 2 to 2.5 seconds
        
        # Page 6: Message Length Statistics (sorted by length, longest first)
        msg_stats = ["Message Length Statistics"]
        # Get sorted message lengths and limit to top 8 (to fit under title)
        sorted_lengths = sorted(stats['message_length_stats'].items(), reverse=True)[:8]
        for length, count in sorted_lengths:
            msg_stats.append(f"{length} Characters: {count} Instances")
        self._display_card_frame(msg_stats, show_row_numbers=False, is_settings=False, hide_headers=True)
        time.sleep(2.5)  # Increased from 2 to 2.5 seconds
        
        # Show settings prompt
        if self._prompt_for_settings():
            return True
        
        # Animate holes filling
        self._animate_holes_filling()
        
        # Final pause before starting
        time.sleep(1)  # Keep at 1 second
        
        # Clear the screen and display empty card for the final state
        self._clear_screen()
        self._display_static_card()
        
        return False

    def clear(self):
        """Clear the display"""
        self.current_message = ""
        self.current_column = 0
        for row in range(self.rows):
            for col in range(self.columns):
                self.grid[row][col] = 0
        self._display_grid() 

    def _display_status(self, status_text: str, status_value: str = "") -> None:
        """Display a status message below the punch card display"""
        print("\n" + " " * 12 + status_text + " " * (self.terminal_width - len(status_text) - 12) + status_value)

    def _display_receiving(self, message: str) -> None:
        """Display receiving message status"""
        print("\n" + " " * 12 + "Receiving Message: " + message)

    def _display_decrypting(self) -> None:
        """Display decrypting status"""
        print("\n" + " " * 12 + "Decrypting. . .") 

    def _prompt_for_settings(self, settings_timeout: int = 5) -> bool:
        """Prompt user to adjust settings with countdown"""
        # Clear screen first
        self._clear_screen()
        
        # Create the content for the settings prompt
        prompt_content = [
            "Would you like to adjust settings?",
            "",
            "[Y]es / [N]o",
            "",
            f"Auto-continue in {settings_timeout} seconds..."
        ]
        
        # We want to hide headers on the settings prompt screen
        # so we pass hide_headers=True to ensure Message# and Status are hidden
        self._display_card_frame(prompt_content, show_row_numbers=False, is_settings=True, hide_headers=True)
        
        # Start the countdown timer
        start_time = time.time()
        while time.time() - start_time < settings_timeout:
            # Calculate remaining time
            remaining = int(settings_timeout - (time.time() - start_time))
            
            # Only update the display if the remaining time has changed
            if int(time.time()) != int(time.time() - 0.1):  # Check if second has changed
                # Update the countdown line
                prompt_content[-1] = f"Auto-continue in {remaining} seconds..."
                self._display_card_frame(prompt_content, show_row_numbers=False, is_settings=True, hide_headers=True)
            
            # Check for input (with short timeout to allow updates)
            if os.name == 'nt':  # Windows
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode().upper()
                    if key == 'Y':
                        self._show_settings_menu()
                        return True
                    elif key == 'N' or key == '\r':  # N or Enter
                        return False
            else:  # Unix-like
                import sys, tty, termios, select
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    if select.select([sys.stdin], [], [], 0.1)[0]:  # 0.1 second timeout
                        key = sys.stdin.read(1).upper()
                        if key == 'Y':
                            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                            self._show_settings_menu()
                            return True
                        elif key == 'N' or key == '\r':
                            return False
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
            # Small delay to prevent CPU hogging
            time.sleep(0.1)
        
        return False

    def _display_card_frame(self, content_lines: List[str], show_row_numbers: bool = False, is_settings: bool = False, hide_headers: bool = False):
        """Display content within the punch card rectangle"""
        # Clear screen first to ensure no previous content
        self._clear_screen()
        
        # Calculate centering offsets - always use 4 for header height to maintain consistent positioning
        x_offset, y_offset = self._calculate_offsets(header_height=4, footer_height=1)
        
        # Add vertical spacing to center the card
        print("\n" * max(0, y_offset))
        
        # Add message header lines or equivalent blank lines to maintain consistent spacing
        if not hide_headers:
            print(" " * x_offset + "Message #0000000: ")
            print(" " * x_offset + "Source: Information Display")
            print(" " * x_offset + "Status: System")
            print()
        else:
            # When headers are hidden, we need to adjust the vertical spacing to maintain the same card position
            print("\n" * 4)  # Keep the same spacing as with headers
        
        # Print top border
        print(" " * x_offset + "   ┌" + "─" * (self.columns - 1) + "─┐")
        
        # Define row order and labels
        row_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        row_labels = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        
        # Calculate text positioning
        total_lines = len(content_lines)
        start_row = (self.rows - total_lines) // 2
        
        # Print grid with text
        for i, row_idx in enumerate(row_order):
            row_num = row_labels[i] if show_row_numbers else "  "
            if start_row <= i < start_row + total_lines:
                text_line = content_lines[i - start_row]
                # Center the text within the card
                padding = (self.columns - len(text_line)) // 2
                row_content = " " * padding + text_line + " " * (self.columns - padding - len(text_line))
            else:
                row_content = " " * self.columns
            print(" " * x_offset + f"{row_num:2s} │{row_content}│")
        
        # Print bottom border
        print(" " * x_offset + "   └" + "─" * (self.columns - 1) + "─┘")
        
        # Add remaining vertical spacing to complete centering
        # Always use consistent total_content_height to ensure proper positioning
        total_content_height = (self.rows + 2) + 4 + 1  # card height + header height + footer height
        remaining_lines = max(0, self.terminal_height - y_offset - total_content_height)
        if remaining_lines > 0:
            print("\n" * remaining_lines)

    def _get_key(self):
        """Get a single keypress from the user"""
        if os.name == 'nt':  # Windows
            import msvcrt
            key = msvcrt.getch().decode()
            if key == '\x00':  # Special key
                key = msvcrt.getch().decode()
                if key == 'H':  # Up arrow
                    return 'up'
                elif key == 'P':  # Down arrow
                    return 'down'
                elif key == 'K':  # Left arrow
                    return 'left'
                elif key == 'M':  # Right arrow
                    return 'right'
            elif key == '\r':  # Enter
                return 'enter'
            elif key == '\x1b':  # Escape
                return 'esc'
            return key.lower()
        else:  # Unix-like
            import sys, tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)
                if key == '\x1b':  # Escape sequence
                    key = sys.stdin.read(2)
                    if key == '[A':  # Up
                        return 'up'
                    elif key == '[B':  # Down
                        return 'down'
                    elif key == '[D':  # Left
                        return 'left'
                    elif key == '[C':  # Right
                        return 'right'
                elif key == '\r':  # Enter
                    return 'enter'
                elif key == '\x1b':  # Escape
                    return 'esc'
                return key.lower()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings) 

    def _render(self):
        """Render the current grid state with consistent header spacing"""
        # For consistency with the animation phases, apply the same header formatting
        self._display_grid()

    def _calculate_offsets(self, header_height: int = 4, footer_height: int = 1, apply_additional_offset: bool = False):
        """Calculate horizontal and vertical offsets for centering content."""
        card_width = self.columns + 4  # 80 columns + 2 borders + 2 spaces for row numbers
        card_height = self.rows + 2  # 12 rows + top and bottom borders
        
        # Always account for header space even if headers are hidden
        # This ensures the rectangle is always positioned at the same location
        total_content_height = card_height + header_height + footer_height

        x_offset = (self.terminal_width - card_width) // 2
        y_offset = (self.terminal_height - total_content_height) // 2
        if apply_additional_offset:
            y_offset += 4  # Changed back from 3 to 4 to restore previous positioning

        return x_offset, y_offset