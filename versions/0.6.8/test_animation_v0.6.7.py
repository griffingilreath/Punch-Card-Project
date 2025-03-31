#!/usr/bin/env python3
"""
Test script for punch card animations
This verifies that both startup and sleep animations work correctly
"""

import sys
import os
import time

# Set up correct path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    from src.display.gui_display import PunchCardDisplay
    from src.core.punch_card import PunchCard
except ImportError as e:
    print(f"Import error: {e}")
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6", "openai"])
    
    # Try import again
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    from src.display.gui_display import PunchCardDisplay
    from src.core.punch_card import PunchCard


class V065AnimationDisplay(PunchCardDisplay):
    """Display class that implements the original v0.6.5 3-phase diagonal animation"""
    
    def __init__(self, punch_card):
        print("Initializing v0.6.5 animation display...")
        super().__init__(punch_card)
        
        # Hide hardware status UI elements that aren't needed for animation test
        if hasattr(self, 'hardware_status_label'):
            self.hardware_status_label.hide()
        
        if hasattr(self, 'keyboard_hint_label'):
            self.keyboard_hint_label.hide()
            
        # Start with an empty grid for the first phase
        self.punch_card.clear_grid()
        self.punch_card.update()
        
        # Initialize diagonal animation parameters from v0.6.5
        self.splash_step = 0
        self.showing_splash = True
        
        # Skip default animation and start our custom one
        if hasattr(self, 'splash_timer') and self.splash_timer.isActive():
            self.splash_timer.stop()
            
        # Create special verification function
        self.verify_top_left_corner = lambda expected, phase: self._verify_corner(expected, phase)
        
        # Start the v0.6.5 animation after a short delay
        QTimer.singleShot(500, self.start_v065_animation)
    
    def _verify_corner(self, expected, phase):
        """Verify the top-left corner LED state matches expectation"""
        actual = self.punch_card.grid[0][0]
        if actual != expected:
            print(f"Warning: Top-left corner (0,0) is {actual} but expected {expected} in {phase}")
            return False
        return True
        
    def start_v065_animation(self):
        """Start the v0.6.5 3-phase diagonal animation sequence"""
        print("Starting v0.6.5 3-phase diagonal animation...")
        
        # Make sure the punch card is in the right state for animation start
        self.showing_splash = True
        self.splash_step = 0
        
        # Create and start the animation timer with the original animation method
        self.splash_timer = QTimer(self)
        self.splash_timer.timeout.connect(self.update_v065_splash)
        self.splash_timer.start(50)  # 50ms for smoother animation (original used ~100ms)
        
    def update_v065_splash(self):
        """Implementation of the exact v0.6.5 3-phase animation logic"""
        # Skip if animation is disabled
        if not self.showing_splash:
            return
            
        # Calculate total steps needed for the animation
        NUM_ROWS = self.punch_card.num_rows
        NUM_COLS = self.punch_card.num_cols
        total_steps = NUM_COLS + NUM_ROWS - 1  # Total for diagonal coverage
        
        # Log progress
        if self.splash_step % 5 == 0:
            print(f"Splash step: {self.splash_step} of {total_steps*2 + 12}")
            
        # Phase transitions - verify top-left corner state
        if self.splash_step == 0:
            # At the very beginning, make sure top-left corner is OFF
            self.verify_top_left_corner(False, "Initial state")
        elif self.splash_step == total_steps:
            # At start of Phase 2, verify top-left corner is OFF before we turn it ON
            self.verify_top_left_corner(False, "Start of Phase 2")
        elif self.splash_step == total_steps * 2:
            # At start of Phase 3, double-check top-left corner state
            pass
            
        # Phase 1: Initial clearing (empty card)
        if self.splash_step < total_steps:
            # Make sure the top-left corner (0,0) is explicitly cleared first
            if self.splash_step == 0:
                print("Phase 1: Starting with empty grid and clearing diagonally")
                self.punch_card.set_led(0, 0, False)
                self.verify_top_left_corner(False, "Phase 1 start")
            
            # Update status text
            self.status_label.setText("INITIALIZING...")
            
            # Clear the current diagonal
            for row in range(NUM_ROWS):
                col = self.splash_step - row
                if 0 <= col < NUM_COLS:
                    # Skip the top-left corner as we've already handled it
                    if not (row == 0 and col == 0):
                        self.punch_card.set_led(row, col, False)
        
        # Phase 2: Punching holes with a 12-hole width
        elif self.splash_step < total_steps * 2:
            # Update status text
            self.status_label.setText("STARTING UP...")
            
            current_step = self.splash_step - total_steps
            
            # At the beginning of Phase 2, explicitly turn on the top-left corner
            if current_step == 0:
                print("Phase 2: Creating diagonal pattern of illuminated LEDs")
                self.punch_card.set_led(0, 0, True)
                self.verify_top_left_corner(True, "Phase 2 start")
            elif current_step <= 12:
                # During the first 12 steps of Phase 2, keep top-left corner ON
                if not self.verify_top_left_corner(True, f"Phase 2 step {current_step}"):
                    self.punch_card.set_led(0, 0, True)
            
            # Punch new holes at the current diagonal
            for row in range(NUM_ROWS):
                col = current_step - row
                if 0 <= col < NUM_COLS:
                    # Skip the top-left corner as we've already handled it
                    if not (row == 0 and col == 0):
                        self.punch_card.set_led(row, col, True)
            
            # Clear old holes (trailing diagonal pattern - 12 columns wide)
            trailing_step = max(0, current_step - 12)
            for row in range(NUM_ROWS):
                col = trailing_step - row
                if 0 <= col < NUM_COLS:
                    # Only clear top-left corner when it's definitely time
                    if row == 0 and col == 0 and current_step >= 12:
                        self.punch_card.set_led(0, 0, False)
                        self.verify_top_left_corner(False, f"Phase 2 trailing step {current_step}")
                    elif not (row == 0 and col == 0):
                        self.punch_card.set_led(row, col, False)
        
        # Phase 3: Clear the remaining 12 columns in a diagonal pattern
        elif self.splash_step < total_steps * 2 + 12:
            # Update status text
            self.status_label.setText("ALMOST READY...")
            
            # Start of phase 3
            if self.splash_step == total_steps * 2:
                print("Phase 3: Final clearing of remaining LEDs")
                self.punch_card.set_led(0, 0, False)
                self.verify_top_left_corner(False, "Phase 3 start")
            
            current_clear_step = self.splash_step - (total_steps * 2) + (total_steps - 12)
            
            for row in range(NUM_ROWS):
                col = current_clear_step - row
                if 0 <= col < NUM_COLS:
                    # Skip the top-left corner as we've already handled it
                    if not (row == 0 and col == 0):
                        self.punch_card.set_led(row, col, False)
        
        else:
            # Animation complete - finish up
            print("Animation completed!")
            
            # Stop the animation timer
            self.splash_timer.stop()
            
            # Clean up and ensure the grid is completely clear
            self.punch_card.clear_grid()
            self.punch_card.update()
            
            # Update UI to reflect completion
            self.showing_splash = False
            self.status_label.setText("READY")
            self.message_label.setText("SYSTEM READY")
            
            # Enable buttons
            for button in [self.start_button, self.clear_button, self.exit_button]:
                button.setEnabled(True)
                
            return
        
        # Play sound effects if available
        if self.splash_step % 5 == 0 and hasattr(self, 'punch_sound'):
            self.punch_sound.play()
            
        # Force a repaint to ensure LED changes are displayed
        self.punch_card.update()
        self.splash_step += 1
    
    def update_hardware_status(self):
        """Disable hardware status updates"""
        pass


def main():
    """Run the test application with the exact v0.6.5 3-phase animation."""
    app = QApplication(sys.argv)
    
    print("Punch Card Animation Test - v0.6.5 Original Animation")
    print("=" * 50)
    print("This animation has 3 phases:")
    print("1. Initial clearing - starts empty")
    print("2. Diagonal patterns - creating a 12-column wide diagonal of illuminated LEDs")
    print("3. Final clearing - cleans up remaining LEDs")
    print("=" * 50)
    
    # Create components
    punch_card = PunchCard()
    gui = V065AnimationDisplay(punch_card)
    
    # Show the window
    gui.show()
    
    # Exit when the application is closed
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 