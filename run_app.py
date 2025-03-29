#!/usr/bin/env python3
"""
Punch Card Project Runner
This script ensures all dependencies are installed and paths are set up correctly
"""
import os
import sys
import subprocess
import argparse

def ensure_dependencies():
    """Make sure all required dependencies are installed."""
    try:
        import PyQt6
        import openai
        print("✅ Dependencies already installed")
        return True
    except ImportError:
        print("Installing required dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6", "openai"])
            print("✅ Dependencies installed successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Punch Card Application")
    
    # Animation-related flags
    animation_group = parser.add_argument_group("Animation Options")
    animation_group.add_argument("--enable-animations", action="store_true", 
                                help="Enable animations in the application")
    animation_group.add_argument("--animation-fps", type=int, default=24,
                                help="Animation frames per second (1-60)")
    
    # Hardware integration flags
    hardware_group = parser.add_argument_group("Hardware Options")
    hardware_group.add_argument("--virtual-mode", action="store_true",
                               help="Force virtual mode (no hardware detection)")
    hardware_group.add_argument("--raspberry-pi-ip", type=str, default="192.168.1.10",
                               help="IP address of the Raspberry Pi")
    hardware_group.add_argument("--raspberry-pi-port", type=int, default=5555,
                               help="Port number for Raspberry Pi connection")
    
    # Development flags
    dev_group = parser.add_argument_group("Development Options")
    dev_group.add_argument("--dev-mode", action="store_true",
                          help="Enable development mode with extra logging")
    dev_group.add_argument("--show-console", action="store_true",
                          help="Show console window at startup")
    
    return parser.parse_args()

def run_app():
    """Run the Punch Card application."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set the working directory to the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Add the project root to the Python path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Import the application module
    try:
        from src.core.punch_card import PunchCard
        from src.display.gui_display import PunchCardDisplay
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        
        # Initialize and run the application
        print("Starting application...")
        app = QApplication(sys.argv)
        
        # Create the punch card data model
        punch_card = PunchCard()
        
        # Create the main display
        gui = PunchCardDisplay(punch_card)
        
        # Configure based on command line arguments
        
        # Setup hardware detection if not in forced virtual mode
        if args.virtual_mode and hasattr(gui, 'hardware_detector'):
            print("Using virtual mode (forced by command line)")
            gui.hardware_detector.enable_virtual_mode()
        
        # Configure hardware detector with custom IP/port if provided
        if hasattr(gui, 'hardware_detector'):
            if args.raspberry_pi_ip:
                gui.hardware_detector.raspberry_pi_ip = args.raspberry_pi_ip
            if args.raspberry_pi_port:
                gui.hardware_detector.raspberry_pi_port = args.raspberry_pi_port
        
        # Enable animations if requested
        if args.enable_animations:
            print("Enabling animations...")
            try:
                # Import animation manager
                from src.animation.animation_manager import AnimationManager, AnimationType
                
                # Check if an animation manager already exists
                if not hasattr(gui, 'animation_manager') or gui.animation_manager is None:
                    # Create new animation manager
                    animation_manager = AnimationManager(punch_card, gui)
                    gui.animation_manager = animation_manager
                
                # Configure animation FPS
                if args.animation_fps:
                    gui.animation_manager.set_fps(args.animation_fps)
                
                # Make sure animation_manager is connected to handle events
                if hasattr(gui, 'animation_manager'):
                    # Only connect if not already connected
                    connected = False
                    for connection in gui.animation_manager.animation_finished.receivers():
                        if hasattr(gui, 'on_animation_finished'):
                            connected = True
                    
                    if not connected and hasattr(gui, 'on_animation_finished'):
                        gui.animation_manager.animation_finished.connect(gui.on_animation_finished)
                
                print("✅ Animations enabled")
                
            except Exception as e:
                print(f"❌ Error enabling animations: {e}")
                import traceback
                traceback.print_exc()
        
        # Show console at startup if requested
        if args.show_console and hasattr(gui, 'console'):
            QTimer.singleShot(500, gui.console.show)
        
        # Enable dev mode if requested
        if args.dev_mode and hasattr(gui, 'console'):
            gui.console.log("Development mode enabled", "INFO")
        
        # Show the GUI and run the application
        gui.show()
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Error running application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 50)
    print("Punch Card Project Runner")
    print("=" * 50)
    
    if ensure_dependencies():
        run_app()
    else:
        print("Could not run application due to missing dependencies.")
        sys.exit(1) 