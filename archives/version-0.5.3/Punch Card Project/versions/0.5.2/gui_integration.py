#!/usr/bin/env python3
"""
GUI Integration Example

Shows how to integrate the minimalist GUI display with the main punch card system.
"""

import sys
import time
import random
from typing import List, Optional

# Import the GUI display
from display.gui_display import PunchCardDisplay, QApplication

class PunchCardSystem:
    """
    Simple example of integrating the GUI display with a punch card system.
    """
    def __init__(self):
        """Initialize the punch card system with GUI display."""
        # Create the QApplication instance
        self.app = QApplication.instance() if QApplication.instance() else QApplication([])
        
        # Create the display
        self.display = PunchCardDisplay()
        
        # Sample messages
        self.sample_messages = [
            "HELLO WORLD",
            "IBM PUNCH CARD",
            "DO NOT FOLD SPINDLE OR MUTILATE",
            "PYTHON INTEGRATION EXAMPLE",
            "MINIMALIST DESIGN"
        ]
        
        # Stats tracking
        self.stats = {
            "messages_processed": 0,
            "start_time": time.time()
        }
    
    def process_message(self, message: str, delay: int = 100) -> None:
        """Process and display a message."""
        # Log the message (in a real system this might go to a database)
        print(f"Processing message: {message}")
        
        # Display the message
        self.display.display_message(message, delay)
        
        # Update stats
        self.stats["messages_processed"] += 1
    
    def generate_random_message(self) -> str:
        """Generate a random message."""
        return random.choice(self.sample_messages)
    
    def run(self, num_messages: int = 5, auto_delay: int = 3000) -> None:
        """Run the system, displaying multiple messages."""
        # Show the display
        self.display.show()
        
        # Process each message with a delay between them
        for i in range(num_messages):
            # Generate a message
            message = self.generate_random_message()
            
            # Process the message
            self.process_message(message)
            
            # Wait for the message to be fully displayed
            # In a real system, we would use signals/slots for this
            while getattr(self.display, 'running', False):
                self.app.processEvents()
                time.sleep(0.1)
            
            # Add a delay between messages
            if i < num_messages - 1:
                # Wait a bit between messages
                start_wait = time.time()
                while time.time() - start_wait < auto_delay / 1000:
                    self.app.processEvents()
                    time.sleep(0.1)
        
        # Keep the application running
        sys.exit(self.app.exec())

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GUI Integration Example")
    parser.add_argument('--messages', type=int, default=5,
                        help='Number of messages to display')
    parser.add_argument('--delay', type=int, default=3000,
                        help='Delay between messages (milliseconds)')
    args = parser.parse_args()
    
    # Create and run the system
    system = PunchCardSystem()
    system.run(num_messages=args.messages, auto_delay=args.delay)

if __name__ == "__main__":
    main() 