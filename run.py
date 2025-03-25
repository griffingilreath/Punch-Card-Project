#!/usr/bin/env python3
"""
Punch Card Project Runner

This script launches the main application with proper setup.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application"""
    # Add src directory to path
    src_dir = Path(__file__).parent / 'src'
    sys.path.insert(0, str(src_dir))
    
    try:
        # Import and run the main application module
        from src.main import main as run_app
        logger.info("Starting Punch Card application")
        run_app()
    except ImportError as e:
        logger.error(f"Failed to import main module: {e}")
        print("\nError: Could not start application. Please ensure all dependencies are installed.")
        print("Try running: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 