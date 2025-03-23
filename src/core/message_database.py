import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class MessageRecord:
    message_number: int
    content: str
    generated_at: str
    source: str = "Generated"  # Can be "Generated", "Database", "DEBUG", or author name
    last_displayed: Optional[str] = None
    display_count: int = 0

class MessageDatabase:
    def __init__(self, db_path: str = "message_history.json"):
        self.db_path = db_path
        self.messages: List[MessageRecord] = []
        self.current_message_number = 0
        self._load_database()
        
    def _load_database(self):
        """Load message history from file"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self.messages = [MessageRecord(**msg) for msg in data['messages']]
                    self.current_message_number = data.get('current_message_number', 0)
        except Exception as e:
            print(f"Error loading message database: {e}")
            self.messages = []
            self.current_message_number = 0
            
    def _save_database(self):
        """Save message history to file"""
        try:
            data = {
                'messages': [asdict(msg) for msg in self.messages],
                'current_message_number': self.current_message_number
            }
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving message database: {e}")
            
    def add_message(self, content: str, source: str = "Generated") -> int:
        """Add a new message to the database"""
        self.current_message_number += 1
        message = MessageRecord(
            message_number=self.current_message_number,
            content=content,
            generated_at=datetime.now().isoformat(),
            source=source
        )
        self.messages.append(message)
        self._save_database()
        return self.current_message_number
        
    def update_display_time(self, message_number: int):
        """Update the last display time for a message"""
        for message in self.messages:
            if message.message_number == message_number:
                message.last_displayed = datetime.now().isoformat()
                message.display_count += 1
                self._save_database()
                break
                
    def get_message(self, message_number: int) -> Optional[MessageRecord]:
        """Get a message by its number"""
        for message in self.messages:
            if message.message_number == message_number:
                return message
        return None
        
    def get_message_count(self) -> int:
        """Get the total number of messages in the database"""
        return len(self.messages)
        
    def get_display_count(self, message_number: int) -> int:
        """Get how many times a message has been displayed"""
        message = self.get_message(message_number)
        return message.display_count if message else 0

    def get_debug_messages(self) -> List[str]:
        """Get a list of debug messages for testing"""
        return [
            "DEBUG: Testing punch card display system",
            "DEBUG: Verifying character encoding",
            "DEBUG: Checking message alignment",
            "DEBUG: Testing special characters",
            "DEBUG: Validating row numbers",
            "DEBUG: Testing message transitions",
            "DEBUG: Checking display timing",
            "DEBUG: Verifying database storage",
            "DEBUG: Testing random delays",
            "DEBUG: System ready for production"
        ] 