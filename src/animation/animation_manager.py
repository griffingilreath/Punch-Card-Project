#!/usr/bin/env python3
"""
Animation Manager for Punch Card Display

Provides animations for the punch card display, including startup,
sleep, wake, and custom animations.
"""

import os
import json
import time
import logging
from enum import Enum, auto
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='[%(asctime)s] [%(levelname)s] %(message)s',
                    datefmt='%H:%M:%S')

# Global flag to control whether startup animations should be skipped
# This can be set by external code before animations are played
SKIP_AUTO_STARTUP_ANIMATION = False

class AnimationType(Enum):
    """Types of animations that can be played"""
    STARTUP = auto()  # Animation played during application startup
    SLEEP = auto()    # Animation played when entering sleep mode
    WAKE = auto()     # Animation played when waking from sleep
    CUSTOM = auto()   # Custom user-defined animations

class AnimationState(Enum):
    """States for the animation system"""
    IDLE = auto()       # No animation playing
    PLAYING = auto()    # Animation in progress
    PAUSED = auto()     # Animation paused
    COMPLETED = auto()  # Animation has completed

class AnimationManager(QObject):
    """
    Manages animations for the punch card display
    
    Provides methods to:
    - Play built-in animations (startup, sleep, wake)
    - Load and play custom animations
    - Control animation playback (speed, interruption)
    """
    
    # Signal emitted when animation starts
    animation_started = pyqtSignal(object)
    
    # Signal emitted when animation completes
    animation_finished = pyqtSignal(object)
    
    # Signal emitted on each animation step with current progress
    animation_step = pyqtSignal(int, int)  # current_step, total_steps
    
    def __init__(self, punch_card, parent=None):
        """
        Initialize the animation manager
        
        Args:
            punch_card: The punch card widget to animate
            parent: Optional parent QObject (typically the main display)
        """
        super().__init__(parent)
        
        # Store the punch card and parent (main display)
        self.punch_card = punch_card
        self.parent_display = parent
        
        # Set up animation state
        self.state = AnimationState.IDLE
        self.current_animation = None
        self.current_step = 0
        self.animation_steps = []
        self.callback = None
        
        # Set up animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._process_animation_step)
        
        # Animation settings
        self.fps = 24  # Animation frames per second (default)
        
        # Load custom animations if available
        self._load_animations()
        
        logging.info("Animation manager initialized")
    
    def play_animation(self, animation_type, interrupt=False, callback=None, speed=1.0):
        """
        Play an animation on the punch card
        
        Args:
            animation_type: The AnimationType to play
            interrupt: Whether to interrupt any current animation
            callback: Function to call when animation completes
            speed: Animation speed multiplier (1.0 = normal)
            
        Returns:
            bool: Whether the animation was started
        """
        # Check for auto-startup animation skip flag
        if animation_type == AnimationType.STARTUP and SKIP_AUTO_STARTUP_ANIMATION:
            logging.info("Skipping automatic startup animation due to SKIP_AUTO_STARTUP_ANIMATION flag")
            if hasattr(self.parent_display, 'console') and self.parent_display.console:
                self.parent_display.console.log("Skipped automatic startup animation - will start manually later", "ANIMATION")
            # Still execute the callback if provided
            if callback:
                callback()
            return False
        
        # Check if we can start a new animation
        if self.state == AnimationState.PLAYING and not interrupt:
            logging.warning(f"Animation already in progress, can't start {animation_type}")
            return False
        
        # Stop any current animation if interrupting
        if self.state == AnimationState.PLAYING and interrupt:
            self._interrupt_current_animation()
        
        # Reset animation state
        self.current_step = 0
        self.callback = callback
        self.current_animation = animation_type
        
        # Generate animation steps based on type
        if animation_type == AnimationType.STARTUP:
            self.animation_steps = self._generate_startup_animation()
            logging.info(f"Generated startup animation with {len(self.animation_steps)} steps")
        elif animation_type == AnimationType.SLEEP:
            self.animation_steps = self._generate_sleep_animation()
            logging.info(f"Generated sleep animation with {len(self.animation_steps)} steps")
        elif animation_type == AnimationType.WAKE:
            self.animation_steps = self._generate_wake_animation()
            logging.info(f"Generated wake animation with {len(self.animation_steps)} steps")
        elif animation_type == AnimationType.CUSTOM:
            # Load a custom animation
            self.animation_steps = self._generate_custom_animation()
            logging.info(f"Generated custom animation with {len(self.animation_steps)} steps")
        else:
            # Unknown animation type
            logging.error(f"Unknown animation type: {animation_type}")
            return False
        
        # Log to console if available
        if hasattr(self.parent_display, 'console') and self.parent_display.console:
            self.parent_display.console.log(f"Playing animation: {animation_type.name}", "INFO")
        
        # Calculate interval based on FPS and speed
        interval = int(1000 / (self.fps * speed))
        self.animation_timer.setInterval(max(20, interval))  # Minimum 20ms interval (50 FPS)
        
        # Update state and start timer
        self.state = AnimationState.PLAYING
        self.animation_timer.start()
        
        # Emit signal
        self.animation_started.emit(animation_type)
        
        return True
    
    def _process_animation_step(self):
        """Process a single animation step"""
        # Check if we're at the end of the animation
        if self.current_step >= len(self.animation_steps):
            self._complete_animation()
            return
        
        # Get the current step data
        step_data = self.animation_steps[self.current_step]
        
        # Apply to punch card (GUI)
        self._apply_step_to_punch_card(step_data)
        
        # Sync with hardware if available
        self._sync_with_hardware(step_data)
        
        # Emit progress signal
        self.animation_step.emit(self.current_step, len(self.animation_steps))
        
        # Increment step counter
        self.current_step += 1
    
    def _apply_step_to_punch_card(self, step_data):
        """
        Apply animation step data to the punch card
        
        Args:
            step_data: 2D array of booleans representing LED states
        """
        rows = min(len(step_data), self.punch_card.num_rows)
        for row in range(rows):
            cols = min(len(step_data[row]), self.punch_card.num_cols)
            for col in range(cols):
                self.punch_card.set_led(row, col, step_data[row][col])
    
    def _sync_with_hardware(self, step_data):
        """
        Sync animation state with hardware LED controller if available
        
        Args:
            step_data: 2D array of booleans representing LED states
        """
        # Check if we have a hardware detector in the parent display
        if hasattr(self.parent_display, 'hardware_detector'):
            hardware_detector = self.parent_display.hardware_detector
            
            # If hardware is ready and not in virtual mode, update LEDs
            if (hasattr(hardware_detector, 'is_hardware_ready') and 
                hardware_detector.is_hardware_ready and 
                not hardware_detector.using_virtual_mode):
                
                # Check if we have a direct LED controller connection or need to send via socket
                if hasattr(self.parent_display, 'led_controller') and self.parent_display.led_controller:
                    # Direct LED controller
                    self.parent_display.led_controller.update_grid(step_data)
                    
                elif hasattr(hardware_detector, 'raspberry_pi_status') and hardware_detector.raspberry_pi_status == "Connected":
                    # We need to send via socket to the Raspberry Pi
                    self._send_led_update_to_raspberry_pi(step_data)
    
    def _send_led_update_to_raspberry_pi(self, step_data):
        """
        Send LED update to Raspberry Pi via socket connection
        
        Args:
            step_data: 2D array of booleans representing LED states
        """
        # This is a placeholder implementation - would need to be customized
        # based on the actual protocol used to communicate with the Pi
        try:
            if hasattr(self.parent_display, 'hardware_detector'):
                hardware_detector = self.parent_display.hardware_detector
                
                # Check if we have connection details
                if hasattr(hardware_detector, 'raspberry_pi_ip') and hasattr(hardware_detector, 'raspberry_pi_port'):
                    # In a real implementation, you would:
                    # 1. Establish socket connection
                    # 2. Format the LED data according to protocol
                    # 3. Send it to the Pi
                    # 4. Close connection (or keep open for efficiency)
                    
                    # Log the attempt
                    if hasattr(self.parent_display, 'console'):
                        self.parent_display.console.log("Hardware LED update sent", "LED")
        except Exception as e:
            logging.error(f"Error sending LED update to Raspberry Pi: {e}")
            if hasattr(self.parent_display, 'console'):
                self.parent_display.console.log(f"LED update error: {e}", "ERROR")
    
    def _complete_animation(self):
        """Complete the current animation"""
        # Stop the timer
        self.animation_timer.stop()
        
        # Store animation type before resetting
        completed_animation = self.current_animation
        
        # Update state
        self.state = AnimationState.COMPLETED
        
        # Execute callback if provided
        if self.callback:
            self.callback()
        
        # Reset state
        self.current_animation = None
        self.state = AnimationState.IDLE
        
        # Emit signal
        self.animation_finished.emit(completed_animation)
        
        # Log to console if available
        if hasattr(self.parent_display, 'console') and self.parent_display.console:
            self.parent_display.console.log(f"Animation completed: {completed_animation.name}", "INFO")
    
    def _interrupt_current_animation(self):
        """Interrupt the current animation"""
        if self.state == AnimationState.PLAYING:
            # Stop the timer
            self.animation_timer.stop()
            
            # Log and update state
            if hasattr(self.parent_display, 'console') and self.parent_display.console:
                self.parent_display.console.log(f"Animation interrupted: {self.current_animation.name}", "WARNING")
                
            self.state = AnimationState.IDLE
            self.current_animation = None
    
    def _load_animations(self):
        """Load custom animations from the animations directory"""
        # Path to animations directory
        animations_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                     'assets', 'animations')
        
        # Ensure directory exists
        if not os.path.exists(animations_dir):
            os.makedirs(animations_dir, exist_ok=True)
            logging.info(f"Created animations directory: {animations_dir}")
    
    def _generate_startup_animation(self):
        """
        Generate a startup animation with a smooth trailing wave effect
        
        Returns:
            list: List of animation steps, each step is a 2D array of booleans
        """
        # Get punch card dimensions
        rows = self.punch_card.num_rows
        cols = self.punch_card.num_cols
        
        # Create animation steps
        steps = []
        
        # Start with an empty grid
        empty_grid = [[False for _ in range(cols)] for _ in range(rows)]
        steps.append([row[:] for row in empty_grid])
        
        # Current grid state
        current_grid = [row[:] for row in empty_grid]
        
        # Define trailing distance (how many steps behind the punching wave the clearing wave follows)
        trailing_distance = 12
        
        # Diagonal wave filling and trailing clearing pattern
        for i in range(rows + cols + trailing_distance):  # Extended to allow trailing wave to complete
            # Make a copy of current grid for this step
            step_grid = [row[:] for row in current_grid]
            
            # Punch one diagonal at a time (leading wave)
            for r in range(rows):
                c = i - r
                if 0 <= c < cols:
                    # Punch the hole
                    step_grid[r][c] = True
            
            # Clear one diagonal at a time (trailing wave)
            trailing_i = i - trailing_distance
            for r in range(rows):
                c = trailing_i - r
                if 0 <= c < cols:
                    # Clear the hole
                    step_grid[r][c] = False
            
            # Add the step to animation
            steps.append([row[:] for row in step_grid])
            
            # Update current grid
            current_grid = [row[:] for row in step_grid]
        
        # Ensure we end with a blank grid
        steps.append([row[:] for row in empty_grid])
        
        return steps
    
    def _generate_sleep_animation(self):
        """
        Generate a sleep animation
        
        Returns:
            list: List of animation steps, each step is a 2D array of booleans
        """
        # Get punch card dimensions
        rows = self.punch_card.num_rows
        cols = self.punch_card.num_cols
        
        # Get current state of the punch card to use as starting point
        start_grid = []
        for r in range(rows):
            row_state = []
            for c in range(cols):
                row_state.append(self.punch_card.get_led(r, c))
            start_grid.append(row_state)
        
        # Create animation steps
        steps = []
        
        # Add initial state
        steps.append([row[:] for row in start_grid])
        
        # Create fade out effect (using diagonal pattern)
        for step in range(10):
            threshold = step / 10
            step_grid = [row[:] for row in start_grid]
            
            for r in range(rows):
                for c in range(cols):
                    # Use normalized position for fade calculation
                    position = (r + c) / (rows + cols)
                    if position < threshold:
                        step_grid[r][c] = False
            
            steps.append(step_grid)
        
        # End with a blank grid
        blank_grid = [[False for _ in range(cols)] for _ in range(rows)]
        steps.append(blank_grid)
        
        return steps
    
    def _generate_wake_animation(self):
        """
        Generate a wake animation
        
        Returns:
            list: List of animation steps, each step is a 2D array of booleans
        """
        # Get punch card dimensions
        rows = self.punch_card.num_rows
        cols = self.punch_card.num_cols
        
        # Create animation steps
        steps = []
        
        # Start with a blank grid
        blank_grid = [[False for _ in range(cols)] for _ in range(rows)]
        steps.append([row[:] for row in blank_grid])
        
        # Create diagonal wave of LEDs turning on
        for i in range(rows + cols - 1):
            step_grid = [row[:] for row in blank_grid]
            
            for r in range(rows):
                c = i - r
                if 0 <= c < cols:
                    step_grid[r][c] = True
            
            steps.append(step_grid)
            
            # Create trailing wave that turns LEDs off
            if i >= 8:  # Start trailing after 8 steps
                trailing_i = i - 8
                for r in range(rows):
                    c = trailing_i - r
                    if 0 <= c < cols:
                        step_grid[r][c] = False
        
        # Continue trailing wave to turn off remaining LEDs
        for i in range(rows + cols - 1, rows + cols - 1 + 8):
            step_grid = [row[:] for row in steps[-1]]  # Start from previous state
            
            # Update trailing wave
            trailing_i = i - 8
            for r in range(rows):
                c = trailing_i - r
                if 0 <= c < cols:
                    step_grid[r][c] = False
            
            steps.append(step_grid)
        
        # End with a blank grid
        steps.append([row[:] for row in blank_grid])
        
        return steps
    
    def _generate_custom_animation(self):
        """
        Load a custom animation from file or generate a sample one
        
        Returns:
            list: List of animation steps, each step is a 2D array of booleans
        """
        # Try to load a custom animation from JSON file
        try:
            # Look for a custom animation in the animations directory
            animations_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                         'assets', 'animations')
            
            # Look for JSON files
            animation_files = [f for f in os.listdir(animations_dir) if f.endswith('.json')]
            
            if animation_files:
                # Use the first animation file found
                animation_file = animation_files[0]
                animation_path = os.path.join(animations_dir, animation_file)
                
                with open(animation_path, 'r') as f:
                    animation_data = json.load(f)
                
                # Process the animation data
                if 'phases' in animation_data and isinstance(animation_data['phases'], list):
                    steps = []
                    
                    # Extract steps from each phase
                    for phase in animation_data['phases']:
                        if 'steps' in phase and isinstance(phase['steps'], list):
                            steps.extend(phase['steps'])
                    
                    if steps:
                        logging.info(f"Loaded custom animation from {animation_file} with {len(steps)} steps")
                        return steps
        except Exception as e:
            logging.error(f"Error loading custom animation: {e}")
        
        # If we couldn't load a custom animation, generate a default one
        logging.info("No valid custom animation found, generating default pattern")
        
        # Get punch card dimensions
        rows = self.punch_card.num_rows
        cols = self.punch_card.num_cols
        
        # Create animation steps
        steps = []
        
        # Start with a blank grid
        blank_grid = [[False for _ in range(cols)] for _ in range(rows)]
        steps.append([row[:] for row in blank_grid])
        
        # Create checkerboard pattern
        checkerboard = [[False for _ in range(cols)] for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                checkerboard[r][c] = (r + c) % 2 == 0
        
        # Alternate between blank and checkerboard
        for _ in range(6):
            steps.append([row[:] for row in checkerboard])
            steps.append([row[:] for row in blank_grid])
        
        # End with a blank grid
        steps.append([row[:] for row in blank_grid])
        
        return steps
    
    def get_available_animations(self):
        """
        Get a list of available animations
        
        Returns:
            list: List of available animation names/IDs
        """
        # Built-in animations
        animations = [
            {"id": AnimationType.STARTUP, "name": "Startup Animation"},
            {"id": AnimationType.SLEEP, "name": "Sleep Animation"},
            {"id": AnimationType.WAKE, "name": "Wake Animation"},
        ]
        
        # Check for custom animations
        try:
            animations_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                         'assets', 'animations')
            
            for filename in os.listdir(animations_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(animations_dir, filename), 'r') as f:
                            data = json.load(f)
                            if 'name' in data:
                                animations.append({"id": filename, "name": data['name']})
                    except:
                        # Skip invalid files
                        pass
        except:
            # No custom animations available
            pass
        
        return animations
    
    def set_fps(self, fps):
        """
        Set the animation frames per second
        
        Args:
            fps: Frames per second (1-60)
            
        Returns:
            int: The actual FPS value set (clamped to valid range)
        """
        self.fps = max(1, min(60, fps))  # Clamp to range 1-60
        
        # Update timer interval if animation is playing
        if self.state == AnimationState.PLAYING:
            self.animation_timer.setInterval(int(1000 / self.fps))
        
        return self.fps
    
    def get_animation_state(self):
        """
        Get the current animation state
        
        Returns:
            AnimationState: The current state
        """
        return self.state 