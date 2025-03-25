import sqlite3
import os
from datetime import datetime
import yaml
from typing import Optional, Dict, List, Any

class Database:
    def __init__(self, config_path: str = "../config/config.yaml"):
        """Initialize database connection and create tables if they don't exist"""
        self.config = self._load_config(config_path)
        self.db_path = self.config['database']['path']
        self._ensure_db_directory()
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
            
    def _ensure_db_directory(self):
        """Ensure the database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                serial_number TEXT UNIQUE,
                message TEXT NOT NULL CHECK(length(message) <= 80),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                message_type TEXT DEFAULT 'user',
                punch_pattern TEXT,
                character_count INTEGER
            )
        ''')
        
        # Diagnostics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnostics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                category TEXT,
                key TEXT,
                value TEXT,
                UNIQUE(timestamp, category, key)
            )
        ''')
        
        # Statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_messages INTEGER DEFAULT 0,
                total_characters INTEGER DEFAULT 0,
                total_holes INTEGER DEFAULT 0,
                average_message_length REAL DEFAULT 0,
                time_operating INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
        
    def save_message(self, serial_number: str, message: str, 
                    message_type: str = 'user', punch_pattern: str = None) -> bool:
        """Save a message to the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO messages 
                (serial_number, message, message_type, punch_pattern, character_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (serial_number, message, message_type, punch_pattern, len(message)))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error when saving message: {e}")
            return False
            
    def save_diagnostic(self, category: str, key: str, value: str) -> bool:
        """Save diagnostic information"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO diagnostics (category, key, value)
                VALUES (?, ?, ?)
            ''', (category, key, value))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error when saving diagnostic: {e}")
            return False
            
    def update_statistics(self, stats: Dict[str, Any]) -> bool:
        """Update system statistics"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO statistics 
                (total_messages, total_characters, total_holes, 
                 average_message_length, time_operating)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                stats['total_messages'],
                stats['total_characters'],
                stats['total_holes'],
                stats['average_message_length'],
                stats['time_operating']
            ))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error when updating statistics: {e}")
            return False
            
    def get_message(self, serial_number: str) -> Optional[str]:
        """Retrieve a message by serial number"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT message FROM messages WHERE serial_number = ?', 
                         (serial_number,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Database error when retrieving message: {e}")
            return None
            
    def get_diagnostics(self, limit: int = 100) -> List[Dict]:
        """Retrieve recent diagnostic information"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT timestamp, category, key, value 
                FROM diagnostics 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            return [{
                'timestamp': row[0],
                'category': row[1],
                'key': row[2],
                'value': row[3]
            } for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error when retrieving diagnostics: {e}")
            return []
            
    def get_statistics(self) -> Optional[Dict]:
        """Retrieve the most recent statistics"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT total_messages, total_characters, total_holes,
                       average_message_length, time_operating
                FROM statistics
                ORDER BY timestamp DESC
                LIMIT 1
            ''')
            row = cursor.fetchone()
            if row:
                return {
                    'total_messages': row[0],
                    'total_characters': row[1],
                    'total_holes': row[2],
                    'average_message_length': row[3],
                    'time_operating': row[4]
                }
            return None
        except sqlite3.Error as e:
            print(f"Database error when retrieving statistics: {e}")
            return None
            
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close() 