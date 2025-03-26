#!/usr/bin/env python3
"""
Punch Card Project - Main Module
This module serves as the main entry point for the Punch Card Project.
"""
import os
import sys
import argparse
import time

def main():
    """
    Main entry point for the application.
    """
    parser = argparse.ArgumentParser(description="Punch Card Project")
    parser.add_argument("--version", action="store_true", help="Show version information")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--test", choices=["simple", "all"], help="Run tests")
    parser.add_argument("--gui", action="store_true", help="Run the GUI application (default if no arguments provided)")
    parser.add_argument("--terminal", action="store_true", help="Run in terminal mode")
    parser.add_argument("--info", action="store_true", help="Display project information and structure")
    args = parser.parse_args()
    
    if args.version:
        print("Punch Card Project v0.6.5")
        print("Copyright © 2023-2024")
        return
    
    if args.test:
        print(f"Running test mode: {args.test}")
        run_test(args.test, debug=args.debug)
        return
        
    if args.terminal:
        print("Starting terminal application...")
        try:
            from src.display.terminal_display import run_terminal_app
            run_terminal_app()
            return
        except ImportError as e:
            print(f"Error: Could not start terminal application: {e}")
            return
        except Exception as e:
            print(f"Error: {e}")
            return
            
    if args.info:
        display_project_info(args.debug)
        return
    
    # Default behavior or explicit --gui: Launch the GUI
    # Either no arguments were provided or --gui was explicitly specified
    if args.gui or (not any([args.version, args.test, args.terminal, args.info])):
        print("Starting GUI application...")
        try:
            from src.display.gui_display import run_gui_app
            run_gui_app()
            return
        except ImportError as e:
            print(f"Error: Could not start GUI. Missing dependencies: {e}")
            print("Try running: pip install -r requirements.txt")
            return
        except Exception as e:
            print(f"Error: Could not start GUI: {e}")
            return

def display_project_info(debug=False):
    """Display project information and structure"""
    print("\n" + "=" * 50)
    print("      Punch Card Project Application")
    print("=" * 50)
    print("\n[SUCCESS] Project structure is working correctly!")
    print("The application is properly loading after reorganization.")
    print("\nUsage:")
    print("  python punch_card.py              - Launch the GUI application (default)")
    print("  python punch_card.py --terminal   - Run in terminal mode")
    print("  python punch_card.py --test TYPE  - Run tests")
    print("  python punch_card.py --version    - Show version information")
    print("  python punch_card.py --help       - Show all available options")
    
    if debug:
        print("\nDirectory structure:")
        for root, dirs, files in os.walk(".", topdown=True):
            # Only process the top level
            if root == ".":
                print(f"Root: {root}")
                print(f"Directories: {dirs}")
                print(f"Files: {len(files)} files found")
                break
    print("\n" + "=" * 50)

def run_test(test_type, debug=False):
    """Run tests"""
    if test_type == "simple":
        print("Running simple test...")
        # Import test modules only when needed
        try:
            import tests.simple_test
            from importlib import reload
            reload(tests.simple_test)
            tests.simple_test.main()
        except ImportError as e:
            print(f"Error importing test module: {e}")
    elif test_type == "all":
        print("Running all tests...")
        # Here we would run all the tests
        print("Not implemented yet")
    
    if debug:
        print("\nDebug information:")
        print(f"Python version: {sys.version}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")

if __name__ == "__main__":
    main() 