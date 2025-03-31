#!/usr/bin/env python3
"""
Test script for Mac system sounds
"""

import os
import platform
import subprocess
import time

def main():
    """Test playing Mac system sounds using afplay"""
    print(f"Platform: {platform.system()}, Release: {platform.release()}")
    
    if platform.system() != "Darwin":
        print("This script only works on macOS")
        return
    
    # Define the sounds to test
    sounds = {
        "punch": "/System/Library/Sounds/Tink.aiff",
        "insert": "/System/Library/Sounds/Submarine.aiff",
        "eject": "/System/Library/Sounds/Purr.aiff",
        "clear": "/System/Library/Sounds/Pop.aiff"
    }
    
    # Check if the sounds exist
    for name, path in sounds.items():
        exists = os.path.exists(path)
        print(f"Sound '{name}' at path '{path}': {'Found' if exists else 'Not found'}")
        
        if not exists:
            # Try some common alternatives
            alt_paths = [
                f"/System/Library/Sounds/{name.capitalize()}.aiff",
                f"/System/Library/Sounds/{name}.aiff"
            ]
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    print(f"  Found alternative: {alt_path}")
                    sounds[name] = alt_path
                    break
    
    # List all available system sounds
    print("\nAll available system sounds:")
    sound_dir = "/System/Library/Sounds"
    if os.path.exists(sound_dir):
        for sound_file in os.listdir(sound_dir):
            if sound_file.lower().endswith(".aiff"):
                print(f"  {sound_file}")
    
    # Play each sound with a delay between them
    print("\nPlaying sounds...")
    for name, path in sounds.items():
        if os.path.exists(path):
            print(f"Playing '{name}' sound...")
            subprocess.Popen(['afplay', path])
            time.sleep(2)
        else:
            print(f"Cannot play '{name}' - file not found")
    
    print("Done!")

if __name__ == "__main__":
    main() 