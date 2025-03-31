#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Punch Card Project Runner
This script serves as the main entry point for the Punch Card application.
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'punch_card_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_path():
    """
    Add the src directory to the Python path.
    """
    # Get the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add src directory to path
    src_path = os.path.join(current_dir, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Also add the project root to path
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

def parse_arguments():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description='Punch Card Project Runner')
    parser.add_argument('--version', action='store_true', help='Show version information')
    parser.add_argument('--terminal', action='store_true', help='Run in terminal mode')
    parser.add_argument('--gui', action='store_true', help='Run in GUI mode (default)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    return parser.parse_args()

def show_version():
    """
    Display version information.
    """
    try:
        from src.utils.version_info import get_version
        version = get_version()
        print(f"Punch Card Project v{version}")
        print("Copyright © 2023-2024")
        return True
    except ImportError:
        try:
            # Try to get version from tag
            import subprocess
            result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], 
                                    capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"Punch Card Project {version}")
                print("Copyright © 2023-2024")
                return True
            else:
                version = "0.6.2"  # Fallback version
                print(f"Punch Card Project v{version}")
                print("Copyright © 2023-2024")
                return True
        except:
            logger.error("Could not determine version information")
            return False

def main():
    """
    Main entry point for the application.
    """
    # Set up the Python path
    setup_path()
    
    # Parse command-line arguments
    args = parse_arguments()
    
    # Set debug mode if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Show version information if requested
    if args.version:
        if show_version():
            return 0
        else:
            return 1
    
    # Import the main module and start the application
    try:
        if args.terminal:
            # Terminal mode
            from src.display.terminal_display import run_terminal_app
            run_terminal_app()
        else:
            # GUI mode (default)
            from src.display.gui_display import run_gui_app
            run_gui_app()
        return 0
    except ImportError as e:
        logger.error(f"Failed to import main module: {e}")
        print("\nError: Could not start application. Please ensure all dependencies are installed.")
        print("Try running: pip install -r requirements.txt")
        return 1
    except Exception as e:
        logger.exception(f"Error starting application: {e}")
        print(f"\nError: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 