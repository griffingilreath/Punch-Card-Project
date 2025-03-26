#!/usr/bin/env python3
"""
Test Script for Punch Card GUI with API Status Integration

This script tests the GUI with API status display features and connects
to the deployed Punch Card API.
"""

import sys
import time
import random
import os
import requests
from PyQt6.QtWidgets import QApplication

# Import the GUI components and main application
from display.gui_display import PunchCardDisplay
from database import Database
from message_generator import MessageGenerator

class APIPunchCardTester:
    """Test class for the Punch Card GUI with API integration."""
    
    def __init__(self, offline_mode=False):
        """Initialize the tester with GUI display."""
        # Create the QApplication instance
        self.app = QApplication.instance() if QApplication.instance() else QApplication(sys.argv)
        
        # Create the display
        self.display = PunchCardDisplay()
        
        # Get reference to the API console
        self.api_console = self.display.api_console
        
        # API configuration
        self.api_endpoint = "https://punch-card-api-v3.fly.dev"
        self.api_status = "Unknown"
        self.offline_mode = offline_mode
        
        # Configure API console with endpoint
        self.api_console.set_endpoint(self.api_endpoint)
        
        # Show the API console by default for this test
        self.api_console.show()
        
        # Set offline mode or check API status
        if self.offline_mode:
            self.api_status = "Offline"
            self.api_console.log("Running in offline mode - no API calls will be made", "INFO")
            self.api_console.update_status("Offline")
            print("Running in offline mode - no API calls will be made")
        else:
            self._check_api_status()
    
    def _check_api_status(self):
        """Check the status of the OpenAI API."""
        try:
            endpoint = f"{self.api_endpoint}/health"
            self.api_console.log_request(endpoint)
            
            response = requests.get(endpoint, timeout=3)
            if response.status_code == 200:
                data = response.json()
                self.api_console.log_response(data, response.status_code)
                
                if data.get('api', {}).get('api_key_exists', False):
                    self.api_status = "Connected"
                else:
                    self.api_status = "No API Key"
            else:
                self.api_console.log_response(f"Non-200 status code: {response.status_code}", response.status_code)
                self.api_status = "Error"
        except requests.exceptions.Timeout:
            self.api_console.log_error("API health check timed out after 3 seconds")
            print("API health check timed out")
            self.api_status = "Timeout"
        except Exception as e:
            self.api_console.log_error("Error checking API status", e)
            print(f"Error checking API status: {e}")
            self.api_status = "Unavailable"
        
        # Update the API console and display status
        self.api_console.update_status(self.api_status)
        self.display.update_api_status(self.api_status)
    
    def _generate_api_message(self):
        """Generate a message using the API."""
        # Skip API calls in offline mode
        if self.offline_mode:
            return None
            
        try:
            prompt = "Generate a vintage computing message about punch cards"
            endpoint = f"{self.api_endpoint}/generate"
            params = {"prompt": prompt, "force_api": True}
            
            self.api_console.log_request(endpoint, params)
            
            response = requests.post(endpoint, json=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.api_console.log_response(data, response.status_code)
                
                if data.get('source') == 'external_api':
                    self.api_status = "Connected"
                    self.api_console.update_status(self.api_status)
                    self.display.update_api_status(self.api_status)
                    return data.get('text')
                else:
                    self.api_status = "Fallback Mode"
                    self.api_console.update_status(self.api_status)
                    self.display.update_api_status(self.api_status)
                    # Log reason for fallback
                    self.api_console.log("API call failed, using local model instead", "STATUS")
                    return None
            else:
                self.api_console.log_response(f"Error response", response.status_code)
                self.api_status = "Error"
                self.api_console.update_status(self.api_status)
                self.display.update_api_status(self.api_status)
                return None
        except requests.exceptions.Timeout:
            self.api_console.log_error("API request timed out after 5 seconds")
            print("API message generation timed out")
            self.api_status = "Timeout"
            self.api_console.update_status(self.api_status)
            self.display.update_api_status(self.api_status)
            return None
        except Exception as e:
            self.api_console.log_error("Error calling API", e)
            print(f"Error calling API: {e}")
            self.api_status = "Unavailable"
            self.api_console.update_status(self.api_status)
            self.display.update_api_status(self.api_status)
            return None
    
    def _generate_local_message(self):
        """Generate a message locally as fallback."""
        messages = [
            "HELLO WORLD",
            "IBM PUNCH CARD SYSTEM READY",
            "DO NOT FOLD SPINDLE OR MUTILATE",
            "CODE IS LIKE HUMOR. WHEN YOU HAVE TO EXPLAIN IT, IT'S BAD",
            "FIRST SOLVE THE PROBLEM THEN WRITE THE CODE"
        ]
        return random.choice(messages)
    
    def run(self, num_messages=10):
        """Run the test displaying multiple messages with API status."""
        # Show the display
        self.display.show()
        
        # Display splash with API status
        self.display.display_message(f"API STATUS TEST", f"API: {self.api_status}")
        
        # Allow time for GUI to update and be visible
        for _ in range(20):
            self.app.processEvents()
            time.sleep(0.1)
        
        # Process each message
        for i in range(num_messages):
            # Generate a message using API first
            api_message = self._generate_api_message()
            
            if api_message:
                message = api_message
                source = f"API: {self.api_status} | MSG-{i+1}"
            else:
                # Fallback to local generation
                message = self._generate_local_message()
                source = f"API: {self.api_status} | LOCAL-{i+1}"
            
            # Process and display the message
            self.display.display_message(message, source)
            
            # Wait for GUI to fully process
            for _ in range(20):
                self.app.processEvents()
                time.sleep(0.1)
            
            # Add delay between messages
            time.sleep(3)
        
        # Keep the application running
        sys.exit(self.app.exec())

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Punch Card GUI with API Integration")
    parser.add_argument('--messages', type=int, default=10,
                        help='Number of messages to display')
    parser.add_argument('--offline', action='store_true',
                        help='Run in offline mode without API calls')
    args = parser.parse_args()
    
    # Create and run the tester
    tester = APIPunchCardTester(offline_mode=args.offline)
    tester.run(num_messages=args.messages)

if __name__ == "__main__":
    main() 