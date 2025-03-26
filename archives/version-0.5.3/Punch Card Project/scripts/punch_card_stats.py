import json
import time
from datetime import datetime
from typing import Dict, Optional

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
        # Ensure message_length_stats keys are strings for JSON serialization
        stats_to_save = self.stats.copy()
        stats_to_save['message_length_stats'] = {
            str(length): count 
            for length, count in self.stats['message_length_stats'].items()
        }
        with open(self.stats_file, 'w') as f:
            json.dump(stats_to_save, f)
    
    def update_message_stats(self, message: str):
        """Update statistics for a processed message"""
        self.stats['cards_processed'] += 1
        self.stats['last_update'] = time.time()
        
        # Update character statistics
        for char in message.upper():
            if char in self.stats['character_stats']:
                self.stats['character_stats'][char] += 1
            else:
                self.stats['character_stats'][char] = 1
        
        # Update message length statistics
        msg_length = len(message)
        if msg_length in self.stats['message_length_stats']:
            self.stats['message_length_stats'][msg_length] += 1
        else:
            self.stats['message_length_stats'][msg_length] = 1
        
        # Count total holes (1 for each character)
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