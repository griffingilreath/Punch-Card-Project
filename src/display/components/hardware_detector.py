#!/usr/bin/env python3
"""
Hardware Detector Module

Detects and monitors hardware components like Raspberry Pi and LED controller.
"""

import socket
import threading

class HardwareDetector:
    """Detects and monitors hardware components like Raspberry Pi and LED controller."""
    
    def __init__(self, console_logger=None):
        self.console_logger = console_logger
        self.raspberry_pi_status = "Detecting..."
        self.led_controller_status = "Detecting..."
        self.is_hardware_ready = False
        self.using_virtual_mode = False
        self.raspberry_pi_ip = "192.168.1.10"  # Default IP - can be configured
        self.raspberry_pi_port = 5555          # Default port - can be configured
        self.detection_complete = False
        
    def log(self, message, level="INFO"):
        """Log a message if console logger is available."""
        if self.console_logger:
            self.console_logger.log(message, level)
        else:
            print(f"[{level}] {message}")
    
    def detect_hardware(self):
        """Start hardware detection in a background thread."""
        self.log("Starting hardware detection process", "INFO")
        threading.Thread(target=self._run_detection, daemon=True).start()
    
    def _run_detection(self):
        """Run the detection process for Raspberry Pi and LED controller."""
        # Check for Raspberry Pi connection
        self.raspberry_pi_status = "Detecting..."
        self.log(f"Attempting to connect to Raspberry Pi at {self.raspberry_pi_ip}:{self.raspberry_pi_port}", "INFO")
        
        try:
            # Try to establish a socket connection to the Pi
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)  # 3 second timeout
            s.connect((self.raspberry_pi_ip, self.raspberry_pi_port))
            
            # If connection successful, check LED controller
            self.raspberry_pi_status = "Connected"
            self.log("Successfully connected to Raspberry Pi", "SUCCESS")
            
            # Send a command to query LED controller status
            s.sendall(b"CHECK_LED_CONTROLLER")
            response = s.recv(1024).decode('utf-8')
            
            if "READY" in response:
                self.led_controller_status = "Ready"
                self.log("LED controller is ready", "SUCCESS")
                self.is_hardware_ready = True
            else:
                self.led_controller_status = "Error: " + response
                self.log(f"LED controller error: {response}", "ERROR")
            
            s.close()
            
        except (socket.timeout, socket.error) as e:
            self.raspberry_pi_status = "Not Found"
            self.led_controller_status = "Not Available"
            self.log(f"Failed to connect to Raspberry Pi: {str(e)}", "ERROR")
            self.log("Will use virtual mode for testing", "WARNING")
            self.using_virtual_mode = True
        
        # Mark detection as complete
        self.detection_complete = True
        self.log("Hardware detection complete", "INFO")
    
    def enable_virtual_mode(self):
        """Explicitly enable virtual mode for testing."""
        self.log("Virtual mode enabled for testing", "WARNING")
        self.raspberry_pi_status = "Virtual Mode"
        self.led_controller_status = "Virtual Mode"
        self.using_virtual_mode = True
        self.is_hardware_ready = True
        self.detection_complete = True 