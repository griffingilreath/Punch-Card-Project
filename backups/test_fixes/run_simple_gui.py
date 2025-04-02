#!/usr/bin/env python3
"""
Simple GUI Launcher for Punch Card Project

A simplified version of the test script that successfully ran the GUI
"""

import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SimpleGUI")

# Ensure src is in the path
sys.path.append('.')

def run_simple_gui():
    """Run the GUI application without message bus monitoring."""
    logger.info("Starting simple GUI...")
    
    try:
        # Import the GUI launcher
        from src.display.gui_display import run_gui_app
        
        # Start the GUI application
        logger.info("Launching GUI application...")
        run_gui_app()
        
    except ImportError as e:
        logger.error(f"Failed to import GUI application: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error running GUI application: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("SIMPLIFIED GUI LAUNCHER")
    print("=" * 60)
    print("This script launches the main GUI application")
    print("=" * 60)
    
    run_simple_gui() 