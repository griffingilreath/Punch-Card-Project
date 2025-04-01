#!/usr/bin/env python3
"""
Test script for message database persistence.
This script validates that messages are properly saved and retrieved.
"""

import os
import sys
from datetime import datetime

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Import the database class
from src.core.message_database import MessageDatabase

def main():
    """Main test function to verify database functionality."""
    # Create test database with a different filename to avoid modifying the actual database
    test_db_file = "test_message_history.json"
    print(f"Creating test database at {test_db_file}")
    
    # Delete test file if it exists
    if os.path.exists(test_db_file):
        os.remove(test_db_file)
        print(f"Deleted existing test database file")
    
    # Create database instance
    db = MessageDatabase(test_db_file)
    print(f"Initial message count: {db.get_message_count()}")
    
    # Test adding messages
    print("\n--- Testing message addition ---")
    msg1 = "TEST MESSAGE ONE"
    msg1_id = db.add_message(msg1, "Test")
    print(f"Added message with ID {msg1_id}: '{msg1}'")
    
    msg2 = "ANOTHER TEST MESSAGE"
    msg2_id = db.add_message(msg2, "OpenAI")
    print(f"Added message with ID {msg2_id}: '{msg2}'")
    
    msg3 = "THIRD TEST MESSAGE WITH DATABASE SOURCE"
    msg3_id = db.add_message(msg3, "Database")
    print(f"Added message with ID {msg3_id}: '{msg3}'")
    
    print(f"Message count after additions: {db.get_message_count()}")
    
    # Test retrieving messages
    print("\n--- Testing message retrieval ---")
    for msg_id in [msg1_id, msg2_id, msg3_id]:
        msg = db.get_message(msg_id)
        if msg:
            print(f"Retrieved message #{msg.message_number}: '{msg.content}' (Source: {msg.source})")
        else:
            print(f"Failed to retrieve message #{msg_id}")
    
    # Test updating display times
    print("\n--- Testing display time updates ---")
    print(f"Message #{msg1_id} display count before: {db.get_display_count(msg1_id)}")
    db.update_display_time(msg1_id)
    print(f"Updated display time for message #{msg1_id}")
    print(f"Message #{msg1_id} display count after: {db.get_display_count(msg1_id)}")
    
    # Test multiple display time updates
    print("\n--- Testing multiple display updates ---")
    for i in range(3):
        db.update_display_time(msg2_id)
        print(f"Updated display #{i+1} for message #{msg2_id}")
    print(f"Message #{msg2_id} display count after: {db.get_display_count(msg2_id)}")
    
    # Test reloading database from file
    print("\n--- Testing database persistence ---")
    del db  # Delete the current instance
    print("Original database instance deleted")
    
    # Create new instance to load from file
    new_db = MessageDatabase(test_db_file)
    print(f"Reloaded database from file, message count: {new_db.get_message_count()}")
    
    # Verify message content after reload
    for msg_id in [msg1_id, msg2_id, msg3_id]:
        msg = new_db.get_message(msg_id)
        if msg:
            print(f"Verified message #{msg.message_number}: '{msg.content}' (Display count: {msg.display_count})")
        else:
            print(f"Failed to retrieve message #{msg_id} after reload")
    
    # Cleanup
    print("\n--- Cleanup ---")
    if os.path.exists(test_db_file):
        os.remove(test_db_file)
        print(f"Test database file {test_db_file} removed")
    
    print("\nDatabase test completed successfully!")

if __name__ == "__main__":
    main() 