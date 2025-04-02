#!/usr/bin/env python3
"""
API Console Window Module

A specialized console window for API activity, requests, and error logging.
"""

import datetime
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt

from src.utils.colors import COLORS
from src.utils.fonts import get_font_css
from src.utils.ui_components import RetroButton

class APIConsoleWindow(QDialog):
    """Console window specifically for API activity, requests, and error logging."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Console")
        self.setMinimumSize(600, 400)
        
        # Set dark theme with accent color for API
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['console_bg'].name()};
                color: {COLORS['console_text'].name()};
            }}
            QTextEdit {{
                background-color: {COLORS['console_bg'].name()};
                color: {COLORS['console_text'].name()};
                {get_font_css(size=12)}
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # Add header with status
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("API Status: Unknown")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text'].name()};
                {get_font_css(bold=True, size=12)}
            }}
        """)
        status_layout.addWidget(self.status_label)
        
        self.endpoint_label = QLabel("")
        self.endpoint_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text'].name()};
                {get_font_css(size=11)}
            }}
        """)
        status_layout.addWidget(self.endpoint_label, 1)
        
        layout.addLayout(status_layout)
        
        # Create console text area
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)
        
        # Add filter options
        filter_layout = QHBoxLayout()
        
        self.show_requests = QCheckBox("Requests")
        self.show_requests.setChecked(True)
        self.show_requests.setStyleSheet(f"color: {COLORS['text'].name()}")
        
        self.show_responses = QCheckBox("Responses")
        self.show_responses.setChecked(True)
        self.show_responses.setStyleSheet(f"color: {COLORS['text'].name()}")
        
        self.show_errors = QCheckBox("Errors")
        self.show_errors.setChecked(True)
        self.show_errors.setStyleSheet(f"color: {COLORS['text'].name()}")
        
        self.show_status = QCheckBox("Status Changes")
        self.show_status.setChecked(True)
        self.show_status.setStyleSheet(f"color: {COLORS['text'].name()}")
        
        filter_layout.addWidget(QLabel("Show:"))
        filter_layout.addWidget(self.show_requests)
        filter_layout.addWidget(self.show_responses) 
        filter_layout.addWidget(self.show_errors)
        filter_layout.addWidget(self.show_status)
        filter_layout.addStretch(1)
        
        layout.addLayout(filter_layout)
        
        # Add buttons layout
        button_layout = QHBoxLayout()
        
        # Add save button
        save_button = RetroButton("Save Log")
        save_button.clicked.connect(self.save_log)
        button_layout.addWidget(save_button)
        
        # Add clear button
        clear_button = RetroButton("Clear")
        clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(clear_button)
        
        # Add test API button
        test_button = RetroButton("Test API")
        test_button.clicked.connect(self.test_api_connection)
        button_layout.addWidget(test_button)
        
        # Add close button
        close_button = RetroButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Initialize with endpoint info
        self.set_endpoint("https://punch-card-api-v3.fly.dev")
    
    def set_endpoint(self, endpoint):
        """Set the API endpoint information."""
        self.endpoint_label.setText(f"Endpoint: {endpoint}")
        self.api_endpoint = endpoint
    
    def update_status(self, status):
        """Update the API status display."""
        self.status_label.setText(f"API Status: {status}")
        
        # Set color based on status
        color = COLORS['text'].name()
        if status == "Connected":
            color = COLORS['success'].name()
        elif status == "Fallback Mode":
            color = COLORS['warning'].name()
        elif status in ["Error", "Unavailable", "No API Key", "Timeout"]:
            color = COLORS['error'].name()
            
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                {get_font_css(bold=True, size=12)}
            }}
        """)
        
        # Log status change if filter enabled
        if self.show_status.isChecked():
            self.log(f"API Status changed to: {status}", "STATUS")
    
    def log(self, message, level="INFO"):
        """Add a message to the console with timestamp and level."""
        # Apply filtering based on level and checkbox settings
        if (level == "REQUEST" and not self.show_requests.isChecked() or
            level == "RESPONSE" and not self.show_responses.isChecked() or
            level == "ERROR" and not self.show_errors.isChecked() or
            level == "STATUS" and not self.show_status.isChecked()):
            return
            
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        level_color = {
            "INFO": "white",
            "REQUEST": "cyan",
            "RESPONSE": "lightgreen",
            "ERROR": "red",
            "STATUS": "yellow"
        }.get(level, "white")
        
        self.console.append(f'<span style="color: gray">[{timestamp}]</span> '
                          f'<span style="color: {level_color}">[{level}]</span> '
                          f'<span style="color: white">{message}</span>')
        self.console.verticalScrollBar().setValue(
            self.console.verticalScrollBar().maximum()
        )

    def log_request(self, endpoint, params=None):
        """Log an API request."""
        request_details = f"Request to {endpoint}"
        if params:
            request_details += f" with params: {params}"
        self.log(request_details, "REQUEST")
    
    def log_response(self, response_data, status_code=200):
        """Log an API response."""
        try:
            # Format JSON for better readability
            formatted_data = json.dumps(response_data, indent=2)
            self.log(f"Response (Status {status_code}):\n{formatted_data}", "RESPONSE")
        except:
            # Fallback for non-JSON responses
            self.log(f"Response (Status {status_code}): {response_data}", "RESPONSE")
    
    def log_error(self, error_message, exception=None):
        """Log an API error."""
        error_text = f"Error: {error_message}"
        if exception:
            error_text += f"\nException: {str(exception)}"
        self.log(error_text, "ERROR")

    def save_log(self):
        """Save the console log to a file."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_log_{timestamp}.txt"
        try:
            with open(filename, 'w') as f:
                f.write(self.console.toPlainText())
            self.log(f"Log saved to {filename}", "INFO")
        except Exception as e:
            self.log(f"Error saving log: {str(e)}", "ERROR")
    
    def clear_log(self):
        """Clear the console log."""
        self.console.clear()
        self.log("Console cleared", "INFO")
    
    def test_api_connection(self):
        """Test the API connection and log results."""
        self.log("Testing API connection...", "INFO")
        
        try:
            import requests
            self.log_request(f"{self.api_endpoint}/health")
            
            response = requests.get(f"{self.api_endpoint}/health", timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                self.log_response(data, response.status_code)
                
                if data.get('api', {}).get('api_key_exists', False):
                    self.update_status("Connected")
                else:
                    self.update_status("No API Key")
            else:
                self.log_response(f"Non-200 status code: {response.status_code}", response.status_code)
                self.update_status("Error")
                
        except requests.exceptions.Timeout:
            self.log_error("Request timed out after 3 seconds")
            self.update_status("Timeout")
        except Exception as e:
            self.log_error("Failed to connect to API", e)
            self.update_status("Unavailable") 