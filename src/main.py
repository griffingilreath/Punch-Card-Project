#!/usr/bin/env python3
"""
██████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗     ██████╗ █████╗ ██████╗ ██████╗ 
██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║    ██╔════╝██╔══██╗██╔══██╗██╔══██╗
██████╔╝██║   ██║██╔██╗ ██║██║     ███████║    ██║     ███████║██████╔╝██║  ██║
██╔═══╝ ██║   ██║██║╚██╗██║██║     ██╔══██║    ██║     ██╔══██║██╔══██╗██║  ██║
██║     ╚██████╔╝██║ ╚████║╚██████╗██║  ██║    ╚██████╗██║  ██║██║  ██║██████╔╝
╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
                                                                               
██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████████╗                    
██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔════╝╚══██╔══╝                    
██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║        ██║                       
██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║        ██║                       
██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╗   ██║                       
╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝                       

                       A project by Griffin Gilreath | Main Application Entry Point
       
  "Do not fold, spindle, or mutilate" - IBM Punch Card warning, circa 1950s
  
  This module serves as the main entry point for the Punch Card Project.
  It orchestrates the various components: database, message generation, and display rendering.
  
  Version: 0.1.0
  Last Updated: 2024-06-15
"""
import os
import sys
import time
import argparse
import yaml
import random
from typing import Optional, Dict
from database import Database
from message_generator import MessageGenerator
from punch_card import PunchCardDisplay
import datetime

class PunchCardApplication:
    def __init__(self, config_path: str = "/Users/griffingilreath/Documents/Coding/Cursor/Punch Card V3/config/config.yaml"):
        """Initialize the punch card application"""
        self.config = self._load_config(config_path)
        self.db = Database(config_path)
        self.message_generator = MessageGenerator(config_path)
        self.display = PunchCardDisplay(
            led_delay=self.config['display']['led_delay'],
            message_delay=self.config['display']['message_delay'],
            random_delay=True,
            skip_splash=False,
            debug_mode=False
        )
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
            
    def _generate_serial_number(self) -> str:
        """Generate a unique serial number for a message"""
        return f"MSG{int(time.time())}{os.getpid()}"
        
    def _process_message(self, message: str, serial_number: Optional[str] = None) -> None:
        """Process and display a message"""
        if serial_number is None:
            serial_number = self._generate_serial_number()
            
        # Save message to database
        self.db.save_message(serial_number, message)
        
        # Calculate the delay to next message
        if self.config['display'].get('random_delay', False):
            next_message_delay = random.uniform(
                self.config['display'].get('random_delay_min', 5),
                self.config['display'].get('random_delay_max', 15)
            )
        else:
            # Use the generation_delay from the display settings
            next_message_delay = self.display.generation_delay
            
        # Display message on LED grid
        self.display.show_message(message, source=f"Serial: {serial_number}")
        
        # Wait for the next message with the appropriate delay
        time.sleep(next_message_delay)
        
        # Get current statistics
        current_stats = self.db.get_statistics() or {
            'total_messages': 0,
            'total_characters': 0,
            'total_holes': 0,
            'average_message_length': 0,
            'time_operating': 0
        }
        
        # Update statistics
        self.db.update_statistics({
            'total_messages': current_stats['total_messages'] + 1,
            'total_characters': current_stats['total_characters'] + len(message),
            'total_holes': current_stats['total_holes'] + len(message),  # Each character is one hole
            'average_message_length': (current_stats['total_characters'] + len(message)) / (current_stats['total_messages'] + 1),
            'time_operating': int(time.time() - self.display.stats.stats['start_time'])
        })
        
    def _run_test_messages(self) -> None:
        """Run through test messages if enabled"""
        if not self.config['test_messages']['enabled']:
            return
            
        test_file = self.config['test_messages']['file']
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                messages = f.readlines()
        else:
            messages = self.config['test_messages']['default_messages']
            
        for message in messages:
            message = message.strip().upper()
            if message:
                self._process_message(message)
                
    def _run_diagnostics(self) -> None:
        """Run system diagnostics if enabled"""
        if not self.config['diagnostics']['enabled']:
            return
            
        # Initialize diagnostics dictionary with basic information
        diagnostics = {
            'system': {
                'hostname': os.uname().nodename if hasattr(os, 'uname') else 'Unknown',
                'python_version': sys.version,
                'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        # Try to import psutil for system resources - gracefully handle if not available
        try:
            import psutil
            diagnostics['system'].update({
                'memory_usage': f"{psutil.virtual_memory().percent}%",
                'cpu_usage': f"{psutil.cpu_percent()}%"
            })
        except ImportError:
            diagnostics['system']['resources'] = "Module 'psutil' not installed - run 'pip install psutil'"
            
        # Try to import platform module for better platform info
        try:
            import platform
            diagnostics['system']['platform'] = platform.platform()
        except ImportError:
            diagnostics['system']['platform'] = sys.platform
            
        # Try to get network information if configured - gracefully handle if not available
        if self.config['diagnostics'].get('include_ip', False):
            try:
                import netifaces
                ip_addresses = []
                for interface in netifaces.interfaces():
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        ip_addresses.extend(addr['addr'] for addr in addrs[netifaces.AF_INET])
                diagnostics['network'] = {'ip_addresses': ip_addresses}
            except ImportError:
                diagnostics['network'] = {'status': "Module 'netifaces' not installed - run 'pip install netifaces'"}
            except Exception as e:
                diagnostics['network'] = {'error': str(e)}
            
        # Process each piece of diagnostic information
        for category, data in diagnostics.items():
            for key, value in data.items():
                message = self.message_generator.generate_diagnostic_message(category, key, value)
                self._process_message(message)
                
    def _generate_random_messages(self) -> None:
        """Generate and display random messages"""
        while True:
            # Try OpenAI first if available
            message = self.message_generator.generate_openai_message()
            if not message:
                message = self.message_generator.generate_random_sentence()
                
            self._process_message(message)
            
            # No need for additional delay here since _process_message now handles this
            
    def run(self) -> None:
        """Run the punch card application"""
        try:
            # Display splash screen
            self.display.show_splash_screen()
            time.sleep(2)
            
            # Run test messages only if not in debug mode or show_debug_messages is enabled
            if not self.display.debug_mode or self.display.show_debug_messages:
                self._run_test_messages()
            
            # Run diagnostics only if not in debug mode or show_debug_messages is enabled
            if not self.display.debug_mode or self.display.show_debug_messages:
                self._run_diagnostics()
            
            # Generate random messages
            self._generate_random_messages()
            
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.db.close()
            self.display.clear()

def main():
    parser = argparse.ArgumentParser(description="IBM 80 Column Punch Card Simulator")
    parser.add_argument("--config", default="/Users/griffingilreath/Documents/Coding/Cursor/Punch Card V3/config/config.yaml",
                      help="Path to configuration file")
    parser.add_argument("--test-message", help="Display a specific test message")
    parser.add_argument("--led-delay", type=float,
                      help="Delay between LED updates (seconds)")
    parser.add_argument("--message-delay", type=float,
                      help="Delay between messages (seconds)")
    parser.add_argument("--random-delay", type=float,
                      help="Random delay between messages (seconds)")
    
    args = parser.parse_args()
    
    app = PunchCardApplication(args.config)
    
    # Override config with command line arguments
    if args.led_delay:
        app.config['display']['led_delay'] = args.led_delay
    if args.message_delay:
        app.config['display']['message_delay'] = args.message_delay
    if args.random_delay:
        app.config['display']['random_delay_min'] = args.random_delay
        app.config['display']['random_delay_max'] = args.random_delay
        
    if args.test_message:
        app._process_message(args.test_message.upper())
    else:
        app.run()

if __name__ == "__main__":
    main() 