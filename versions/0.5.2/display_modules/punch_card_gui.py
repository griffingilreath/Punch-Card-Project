#!/usr/bin/env python3
"""
Punch Card GUI Launcher

A simple script to launch the minimalist punch card GUI.
"""

import sys
import argparse
from src.display.gui_display import main as gui_main

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Minimalist Punch Card GUI")
    parser.add_argument('--message', type=str, default="HELLO WORLD",
                        help='Message to display on the punch card')
    parser.add_argument('--delay', type=int, default=100,
                        help='Delay between character displays (milliseconds)')
    parser.add_argument('--wait', action='store_true',
                        help='Wait for user to press button before displaying message')
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    
    # Start the GUI
    display, app = gui_main()
    
    # Display the message if not in wait mode
    if not args.wait:
        display.display_message(args.message, source="Manual Entry", delay=args.delay)
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

# ========================================================
# If you get "command not found: python", try these instead:
# 
# 1. Use python3 explicitly:
#    python3 punch_card_gui.py --message "HELLO WORLD"
#
# 2. Run with executable permission:
#    chmod +x punch_card_gui.py
#    ./punch_card_gui.py --message "HELLO WORLD"
#
# 3. Find your Python executable and use it directly:
#    /usr/bin/env python3 punch_card_gui.py
# ======================================================== 