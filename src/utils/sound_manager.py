"""
Sound Manager for the Punch Card Project

This module provides sound functionality for the application,
using macOS system sounds.
"""

import os
import platform
import subprocess
import logging
from typing import Optional

# Logger for sound manager
logger = logging.getLogger("SoundManager")

class SoundManager:
    """
    Manages sound effects for the punch card application.
    Uses macOS system sounds for a native experience.
    """
    
    def __init__(self, console_logger=None):
        """
        Initialize the sound manager.
        
        Args:
            console_logger: Optional console logger for UI feedback
        """
        self.console_logger = console_logger
        self.sounds_loaded = False
        self.volume = 1.0  # Full volume by default
        self.muted = False
        self.mac_sounds = {}
        
        # Initialize default sound mappings
        self.sound_mappings = {
            "punch": "Tink",     # Short, crisp sound for typing
            "complete": "Glass", # Pleasant sound for message complete
            "clear": "Pop",     # Quick sound for clearing
            "startup": "Hero",   # Dramatic sound for startup
            "eject": "Submarine", # Submarine sound for card ejection
            "insert": "Bottle"   # Bottle sound for card insertion
        }
        
        self.log("Initializing sound manager...", "INFO")
        
        # Load sounds based on platform
        if platform.system() == "Darwin":
            self.log("macOS detected, loading system sounds...", "INFO")
            self.load_mac_system_sounds()
        else:
            self.log("Non-macOS platform detected - sound effects may be limited", "WARNING")
        
        if self.sounds_loaded:
            self.log("Sound manager initialized successfully", "SUCCESS")
        else:
            self.log("Sound manager initialization incomplete - some sounds may not work", "WARNING")
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message to both the console logger and system logger."""
        # Log to the console logger if available
        if self.console_logger and hasattr(self.console_logger, "log"):
            self.console_logger.log(message, level)
        
        # Always log to the system logger
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)
    
    def load_mac_system_sounds(self):
        """Load macOS system sounds for punch card operations."""
        try:
            # Debug info about platform
            system_info = f"Platform: {platform.system()}, Release: {platform.release()}, Version: {platform.version()}"
            self.log(f"System info: {system_info}", "INFO")
            
            # Only use system sounds on macOS
            if platform.system() != "Darwin":
                self.log("Not running on macOS - sound effects may be limited", "WARNING")
                self.sounds_loaded = False
                return False
            
            self.log("Loading Mac system sounds...", "INFO")
            
            # Define sound files with preferred sounds in order of preference
            sound_preferences = {
                "Tink": [
                    "/System/Library/Sounds/Tink.aiff",
                    "/System/Library/Components/CoreAudio.component/Contents/SharedSupport/SystemSounds/Tink.aiff",
                ],
                "Glass": [
                    "/System/Library/Sounds/Glass.aiff",
                    "/System/Library/Components/CoreAudio.component/Contents/SharedSupport/SystemSounds/Glass.aiff",
                ],
                "Pop": [
                    "/System/Library/Sounds/Pop.aiff",
                    "/System/Library/Components/CoreAudio.component/Contents/SharedSupport/SystemSounds/Pop.aiff",
                ],
                "Hero": [
                    "/System/Library/Sounds/Hero.aiff",
                    "/System/Library/Components/CoreAudio.component/Contents/SharedSupport/SystemSounds/Hero.aiff",
                ],
                "Bottle": [
                    "/System/Library/Sounds/Bottle.aiff",
                    "/System/Library/Components/CoreAudio.component/Contents/SharedSupport/SystemSounds/Bottle.aiff",
                ],
                "Frog": [
                    "/System/Library/Sounds/Frog.aiff",
                    "/System/Library/Components/CoreAudio.component/Contents/SharedSupport/SystemSounds/Frog.aiff",
                ],
                "Funk": [
                    "/System/Library/Sounds/Funk.aiff",
                    "/System/Library/Components/CoreAudio.component/Contents/SharedSupport/SystemSounds/Funk.aiff",
                ],
                "Morse": [
                    "/System/Library/Sounds/Morse.aiff",
                    "/System/Library/Components/CoreAudio.component/Contents/SharedSupport/SystemSounds/Morse.aiff",
                ],
                "Ping": [
                    "/System/Library/Sounds/Ping.aiff",
                    "/System/Library/Components/CoreAudio.component/Contents/SharedSupport/SystemSounds/Ping.aiff",
                ],
                "Purr": [
                    "/System/Library/Sounds/Purr.aiff",
                    "/System/Library/Components/CoreAudio.component/Contents/SharedSupport/SystemSounds/Purr.aiff",
                ],
                "Sosumi": [
                    "/System/Library/Sounds/Sosumi.aiff",
                    "/System/Library/Components/CoreAudio.component/Contents/SharedSupport/SystemSounds/Sosumi.aiff",
                ],
                "Submarine": [
                    "/System/Library/Sounds/Submarine.aiff",
                    "/System/Library/Components/CoreAudio.component/Contents/SharedSupport/SystemSounds/Submarine.aiff",
                ]
            }
            
            # Try to find the best available sound for each type
            all_sounds_available = True
            for sound_name, sound_paths in sound_preferences.items():
                found_sound = False
                for path in sound_paths:
                    # Expand user path if needed
                    if path.startswith("~"):
                        path = os.path.expanduser(path)
                    
                    if os.path.exists(path):
                        self.mac_sounds[sound_name] = path
                        self.log(f"Using {sound_name} sound: {path}", "INFO")
                        found_sound = True
                        break
                
                if not found_sound:
                    self.log(f"Could not find any sound for {sound_name}", "WARNING")
                    all_sounds_available = False
            
            # Set sounds_loaded flag based on availability
            self.sounds_loaded = len(self.mac_sounds) > 0
            if self.sounds_loaded:
                self.log("Mac system sounds loaded successfully", "SUCCESS")
            else:
                self.log("No Mac system sounds were found", "WARNING")
            
            return self.sounds_loaded
            
        except Exception as e:
            self.log(f"Error loading Mac sounds: {str(e)}", "ERROR")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}", "ERROR")
            self.sounds_loaded = False
            return False
    
    def set_volume(self, volume: float):
        """Set the volume level (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        self.log(f"Volume set to {int(self.volume * 100)}%", "INFO")
    
    def set_muted(self, muted: bool):
        """Set the muted state."""
        self.muted = muted
        self.log(f"Sound {'muted' if muted else 'unmuted'}", "INFO")
    
    def update_sound_mappings(self, mappings: dict):
        """Update the sound mappings with new selections."""
        try:
            self.log("Updating sound mappings...", "INFO")
            
            # Store the new mappings
            self.sound_mappings = mappings
            
            # Log the new mappings
            for action, sound in mappings.items():
                self.log(f"Action '{action}' mapped to sound '{sound}'", "INFO")
            
            return True
            
        except Exception as e:
            self.log(f"Error updating sound mappings: {str(e)}", "ERROR")
            return False
    
    def play_sound(self, sound_name: str) -> bool:
        """Play a sound effect."""
        try:
            # Don't play sounds if muted
            if self.muted:
                return False
            
            # Only use system sounds on macOS
            if platform.system() == "Darwin":
                try:
                    # Get the mapped sound name if it exists
                    if sound_name not in self.sound_mappings:
                        self.log(f"No mapping found for sound action '{sound_name}', using default", "WARNING")
                        sound_file = sound_name
                    else:
                        sound_file = self.sound_mappings.get(sound_name)
                    
                    # Check if the sound exists in mac_sounds
                    if sound_file in self.mac_sounds:
                        sound_path = self.mac_sounds[sound_file]
                        if os.path.exists(sound_path):
                            # Use afplay with volume control, run in background
                            volume_arg = str(self.volume)
                            subprocess.Popen([
                                "afplay",
                                "-v", volume_arg,
                                sound_path
                            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            return True
                        else:
                            self.log(f"Sound file not found: {sound_path}", "ERROR")
                    else:
                        # Try to fall back to a default sound if the mapped sound is not available
                        if sound_name in self.sound_mappings and "Pop" in self.mac_sounds:
                            self.log(f"Sound '{sound_file}' not found, falling back to 'Pop'", "WARNING")
                            sound_path = self.mac_sounds["Pop"]
                            volume_arg = str(self.volume)
                            subprocess.Popen([
                                "afplay",
                                "-v", volume_arg,
                                sound_path
                            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            return True
                        else:
                            self.log(f"Sound {sound_file} not found in mac_sounds dictionary", "ERROR")
                    return False
                except Exception as e:
                    self.log(f"Error playing sound: {str(e)}", "ERROR")
                    return False
            
            return False
            
        except Exception as e:
            self.log(f"Error in play_sound: {str(e)}", "ERROR")
            return False
    
    def play_mac_sound(self, sound_name: str) -> bool:
        """Play a sound on macOS."""
        try:
            # Don't play if muted
            if self.muted:
                self.log(f"Sound {sound_name} not played (muted)", "INFO")
                return False
            
            # Get the mapped sound name if it exists
            if sound_name not in self.sound_mappings:
                self.log(f"No mapping found for sound action '{sound_name}', using default", "WARNING")
                sound_file = sound_name
            else:
                sound_file = self.sound_mappings.get(sound_name)
            
            # Check if the sound exists in mac_sounds
            if sound_file in self.mac_sounds:
                sound_path = self.mac_sounds[sound_file]
                if os.path.exists(sound_path):
                    # Use afplay with volume control, run in background
                    volume_arg = str(self.volume)
                    subprocess.Popen([
                        "afplay",
                        "-v", volume_arg,
                        sound_path
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return True
                else:
                    self.log(f"Sound file not found: {sound_path}", "ERROR")
            else:
                # Try to fall back to a default sound if the mapped sound is not available
                if sound_name in self.sound_mappings and "Pop" in self.mac_sounds:
                    self.log(f"Sound '{sound_file}' not found, falling back to 'Pop'", "WARNING")
                    sound_path = self.mac_sounds["Pop"]
                    volume_arg = str(self.volume)
                    subprocess.Popen([
                        "afplay",
                        "-v", volume_arg,
                        sound_path
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return True
                else:
                    self.log(f"Sound {sound_file} not found in mac_sounds dictionary", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"Error playing Mac sound: {str(e)}", "ERROR")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}", "ERROR")
            return False
    
    def open_sound_settings(self) -> bool:
        """Open macOS System Settings to the Sound settings."""
        try:
            # Open System Settings to Sound settings
            result = subprocess.run([
                "open",
                "x-apple.systempreferences:com.apple.preference.sound"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if result.returncode == 0:
                self.log("Opened Sound settings successfully", "INFO")
                return True
            else:
                self.log(f"Failed to open Sound settings: {result.stderr.decode()}", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Error opening Sound settings: {str(e)}", "ERROR")
            return False

# Create a singleton instance
_sound_manager = None

def get_sound_manager(console_logger=None) -> SoundManager:
    """Get the singleton SoundManager instance."""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager(console_logger)
    return _sound_manager 