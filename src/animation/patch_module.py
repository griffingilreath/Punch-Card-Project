#!/usr/bin/env python3
"""
Animation System Patch Module
Ensures all required components for the animation system are available
"""

import os
import sys
import logging
import importlib.util

# Setup simple console logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s',
                   datefmt='%H:%M:%S')

def ensure_dependencies():
    """Ensure all required dependencies for animations are present"""
    try:
        # Check for PyQt6
        import PyQt6
        logging.info("PyQt6 is available")
        
        # Check for other dependencies
        import json
        import time
        import enum
        
        return True
    except ImportError as e:
        logging.error(f"Missing dependency: {e}")
        return False

def ensure_directories():
    """Ensure all required directories exist"""
    try:
        # Get base paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        assets_dir = os.path.join(project_root, 'assets')
        
        # Create assets directory if it doesn't exist
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)
            logging.info(f"Created assets directory: {assets_dir}")
        
        # Create animations directory if it doesn't exist
        animations_dir = os.path.join(assets_dir, 'animations')
        if not os.path.exists(animations_dir):
            os.makedirs(animations_dir)
            logging.info(f"Created animations directory: {animations_dir}")
        
        return True
    except Exception as e:
        logging.error(f"Error ensuring directories: {e}")
        return False

def ensure_animation_files(default_only=False):
    """Ensure all required animation files are present"""
    try:
        # Get base paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        assets_dir = os.path.join(project_root, 'assets')
        animations_dir = os.path.join(assets_dir, 'animations')
        
        # Create custom animation if not present
        custom_anim_path = os.path.join(animations_dir, 'custom_diagonal.json')
        if not os.path.exists(custom_anim_path) and not default_only:
            sample_content = '''{
    "name": "Custom Diagonal",
    "fps": 25,
    "interruptible": true,
    "phases": [
        {
            "name": "First Wave",
            "steps": [
                [[false, false, false, false], [false, false, false, false], [false, false, false, false]],
                [[true, false, false, false], [false, false, false, false], [false, false, false, false]],
                [[true, true, false, false], [true, false, false, false], [false, false, false, false]],
                [[true, true, true, false], [true, true, false, false], [true, false, false, false]],
                [[true, true, true, true], [true, true, true, false], [true, true, false, false]],
                [[false, true, true, true], [true, true, true, true], [true, true, true, false]],
                [[false, false, true, true], [false, true, true, true], [true, true, true, true]],
                [[false, false, false, true], [false, false, true, true], [false, true, true, true]],
                [[false, false, false, false], [false, false, false, true], [false, false, true, true]],
                [[false, false, false, false], [false, false, false, false], [false, false, false, true]],
                [[false, false, false, false], [false, false, false, false], [false, false, false, false]]
            ],
            "transition_pause": 100
        },
        {
            "name": "Second Wave",
            "steps": [
                [[false, false, false, false], [false, false, false, false], [false, false, false, false]],
                [[false, false, false, false], [false, false, false, false], [true, false, false, false]],
                [[false, false, false, false], [true, false, false, false], [true, true, false, false]],
                [[true, false, false, false], [true, true, false, false], [true, true, true, false]],
                [[true, true, false, false], [true, true, true, false], [true, true, true, true]],
                [[true, true, true, false], [true, true, true, true], [false, true, true, true]],
                [[true, true, true, true], [false, true, true, true], [false, false, true, true]],
                [[false, true, true, true], [false, false, true, true], [false, false, false, true]],
                [[false, false, true, true], [false, false, false, true], [false, false, false, false]],
                [[false, false, false, true], [false, false, false, false], [false, false, false, false]],
                [[false, false, false, false], [false, false, false, false], [false, false, false, false]]
            ],
            "transition_pause": 100
        }
    ]
}'''
            with open(custom_anim_path, 'w') as f:
                f.write(sample_content)
            logging.info(f"Created sample animation: {custom_anim_path}")
        
        return True
    except Exception as e:
        logging.error(f"Error ensuring animation files: {e}")
        return False

def patch():
    """Apply all necessary patches for the animation system"""
    logging.info("Applying animation system patches...")
    
    # Check dependencies
    if not ensure_dependencies():
        logging.error("Failed to verify dependencies")
        return False
    
    # Ensure directories
    if not ensure_directories():
        logging.error("Failed to create required directories")
        return False
    
    # Ensure animation files
    if not ensure_animation_files():
        logging.warning("Failed to create sample animation files")
    
    logging.info("Animation system patched successfully")
    return True

if __name__ == "__main__":
    # Run the patch function when script is executed directly
    if patch():
        print("Patching completed successfully")
    else:
        print("Patching failed")
        sys.exit(1) 