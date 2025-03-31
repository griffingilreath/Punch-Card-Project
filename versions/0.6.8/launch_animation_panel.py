#!/usr/bin/env python3
"""
Launch Animation Panel
A script to run the punch card display with standalone animation controls
"""

import os
import sys
import time
from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtCore import QTimer

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Set a global flag to prevent automatic startup animations
import src.animation.animation_manager
src.animation.animation_manager.SKIP_AUTO_STARTUP_ANIMATION = True

# Import the required modules
from src.core.punch_card import PunchCard
from src.display.gui_display import PunchCardDisplay, RetroButton
from animation_control_panel import StandaloneAnimationPanel
from simple_console import SimpleConsole

def run():
    """Run the punch card display with animation controls"""
    print("Starting Punch Card GUI with Animation Panel...")
    
    # Create the application
    app = QApplication(sys.argv)
    
    # Create punch card data model
    punch_card = PunchCard()
    
    # Create our own console window first
    console = SimpleConsole()
    console.show()
    console.log("Punch Card Display initializing...", "SYSTEM")
    console.log("Auto-start animations disabled - will start manually", "ANIMATION")
    
    # Create the main display
    gui = PunchCardDisplay(punch_card)
    
    # IMMEDIATELY hide or clear all virtual mode indicators BEFORE showing anything
    # Find and clear ALL status indicators that might show "Virtual Mode"
    console.log("AGGRESSIVELY clearing all 'Virtual Mode' indicators...", "SYSTEM")
    
    # First approach: Find the most common status labels directly
    for attr_name in ['status_label', 'mode_label', 'virtual_mode_label', 'hardware_status_label', 
                     'status_display', 'status_value_label', 'hardware_indicator']:
        if hasattr(gui, attr_name):
            try:
                widget = getattr(gui, attr_name)
                if hasattr(widget, 'setText'):
                    # Save the original text for debugging
                    original_text = ""
                    if hasattr(widget, 'text'):
                        original_text = widget.text()
                    # Clear it
                    widget.setText("")
                    console.log(f"Cleared {attr_name}: '{original_text}'", "SYSTEM")
            except Exception as e:
                console.log(f"Error clearing {attr_name}: {e}", "ERROR")
    
    # Second approach: Recursively search ALL child widgets for any text containing "virtual" or "mode"
    all_labels = gui.findChildren(QLabel)
    for label in all_labels:
        try:
            if hasattr(label, 'text') and label.text():
                text = label.text().lower()
                if "virtual" in text or "mode" in text or "status" in text:
                    console.log(f"Found and cleared label: '{label.text()}'", "SYSTEM")
                    label.setText("")
        except Exception as e:
            console.log(f"Error checking label text: {e}", "ERROR")
    
    # Share our console with the GUI - more thoroughly replace the existing console
    gui.simple_console = console
    
    # Replace the original console object to avoid conflicts
    if hasattr(gui, 'console'):
        # Save a reference to the original console if needed
        original_console = gui.console
        
        # Hide the original console window if it's visible
        if hasattr(original_console, 'hide'):
            try:
                original_console.hide()
                console.log("Hidden original console window", "SYSTEM")
            except Exception as e:
                console.log(f"Error hiding original console: {e}", "ERROR")
                
        # Hide the original console window if it's a widget
        if hasattr(original_console, 'isVisible') and original_console.isVisible():
            try:
                original_console.hide()
                console.log("Hidden original console widget", "SYSTEM")
            except Exception as e:
                console.log(f"Error hiding original console widget: {e}", "ERROR")
        
        # Important: Store the original log method to avoid recursion    
        original_console_log = None
        if hasattr(original_console, 'log'):
            original_console_log = original_console.log
                
        # Replace with our console (be careful not to create recursion)
        gui.console = console
        console.log("Replaced original console object", "SYSTEM")
    
    # Important: Override the original console method to use our console
    if hasattr(gui, 'show_console'):
        original_show_console = gui.show_console
        gui.show_console = lambda: console.show()
        console.log("Console method overridden", "SYSTEM")
        
    # Override the log method if it exists - BUT BE CAREFUL WITH RECURSION
    if hasattr(gui, 'log') and gui.log is not console.log:  # Prevent recursion
        original_log = gui.log
        # Create a safe wrapper
        def safe_log_wrapper(msg, level="INFO"):
            # Use our console directly, not through gui
            return console.log(msg, level)
        # Replace the method
        gui.log = safe_log_wrapper
        console.log("Log method overridden", "SYSTEM")
    
    # Also connect console menu action if it exists
    if hasattr(gui, 'menu_bar') and hasattr(gui.menu_bar, 'console_menu_popup'):
        # Try to find and override the console action
        try:
            for action in gui.menu_bar.console_menu_popup.actions():
                if action.text() == "Show Console" or "Console" in action.text():
                    # Disconnect old connections if possible
                    try:
                        action.triggered.disconnect()
                    except:
                        pass
                    # Connect to showing our console
                    action.triggered.connect(lambda: console.show())
                    console.log("Console menu action connected", "SYSTEM")
        except Exception as e:
            console.log(f"Warning: Could not connect console menu: {e}", "WARNING")
    
    # Put in virtual mode for testing
    if hasattr(gui, 'hardware_detector'):
        gui.hardware_detector.enable_virtual_mode()
        console.log("Running in virtual mode (no hardware detection)", "HARDWARE")
        print("Running in virtual mode (no hardware detection)")
        
        # Intercept the status updates to prevent "Virtual Mode" text from appearing
        if hasattr(gui.hardware_detector, 'update_status_display'):
            original_update_status = gui.hardware_detector.update_status_display
            
            # Create a wrapper that does nothing
            def silent_update_status():
                # Don't update any status displays
                console.log("Blocked hardware status update (prevents 'Virtual Mode' text)", "SYSTEM")
                return
            
            # Replace with our silent version
            gui.hardware_detector.update_status_display = silent_update_status
            console.log("✅ Blocked hardware status updates to prevent 'Virtual Mode' text", "SYSTEM")
    
    # Skip splash screen
    if hasattr(gui, 'showing_splash') and gui.showing_splash:
        if hasattr(gui, 'complete_splash_screen'):
            gui.complete_splash_screen()
            console.log("Splash screen skipped", "SYSTEM")
            print("Skipped splash screen")
    
    # Create animation panel with access to our console
    animation_panel = StandaloneAnimationPanel(gui)
    animation_panel.simple_console = console
    gui.animation_panel = animation_panel
    
    # Log messages for LED initialization
    console.log("LED grid initialized with 12 rows x 80 columns", "LED")
    
    # Modify the animation manager to use our console - IMPORTANT PART
    if hasattr(gui, 'animation_manager') and gui.animation_manager:
        # Store original method reference
        console.log("Connecting animation manager to console...", "ANIMATION")
        
        # We need to create a proper closure to avoid reference issues
        def create_logging_step_handler(original_method, console_ref):
            # Store previous grid state for comparison
            previous_state = None
            
            def logged_step_handler(step_data):
                nonlocal previous_state
                
                # Call original implementation
                original_method(step_data)
                
                # First time setup if needed
                if previous_state is None:
                    rows = len(step_data)
                    cols = len(step_data[0]) if rows > 0 else 0
                    previous_state = [[False for _ in range(cols)] for _ in range(rows)]
                
                # Count active LEDs and track changes
                active_leds = 0
                total_leds = 0
                changes = []
                
                # Compare with previous state to find changes
                for r in range(len(step_data)):
                    for c in range(len(step_data[r])):
                        total_leds += 1
                        if step_data[r][c]:
                            active_leds += 1
                        
                        # Check if this LED changed state
                        if step_data[r][c] != previous_state[r][c]:
                            new_state = "ON" if step_data[r][c] else "OFF"
                            changes.append((r, c, new_state))
                
                # Log overall summary
                led_message = f"LEDs: {active_leds} on, {total_leds-active_leds} off"
                console_ref.log(led_message, "LED")
                
                # Group and log all changes
                if changes:
                    # Group changes by ON/OFF status for cleaner output
                    on_changes = [(r, c) for r, c, state in changes if state == "ON"]
                    off_changes = [(r, c) for r, c, state in changes if state == "OFF"]
                    
                    # Log ON changes (up to 80 per line to avoid very long lines)
                    if on_changes:
                        for i in range(0, len(on_changes), 80):
                            batch = on_changes[i:i+80]
                            positions = ', '.join([f"({r},{c})" for r, c in batch])
                            console_ref.log(f"LED ON: {positions}", "LED_green")
                    
                    # Log OFF changes (up to 80 per line to avoid very long lines)
                    if off_changes:
                        for i in range(0, len(off_changes), 80):
                            batch = off_changes[i:i+80]
                            positions = ', '.join([f"({r},{c})" for r, c in batch])
                            console_ref.log(f"LED OFF: {positions}", "LED_gray")
                
                # Update previous state for next comparison
                previous_state = [row[:] for row in step_data]
                
            return logged_step_handler
        
        # Create and apply the handler with proper references
        original_apply_step = gui.animation_manager._apply_step_to_punch_card
        gui.animation_manager._apply_step_to_punch_card = create_logging_step_handler(
            original_apply_step, console
        )
        
        # Also connect the animation_step signal to log progress
        # Only log every 5th step to avoid too many messages
        step_counter = [0]  # Use a list for nonlocal state in closure
        def on_animation_step(current, total):
            step_counter[0] += 1
            if current == 0 or current == total-1 or step_counter[0] % 5 == 0:
                # Calculate percentage
                percentage = int((current / total) * 100)
                # Create a visual progress bar
                bar_width = 20
                filled = int(bar_width * current / total)
                progress_bar = '[' + '■' * filled + '□' * (bar_width - filled) + ']'
                # Log both numeric and visual progress
                console.log(f"Animation: {progress_bar} {percentage}% ({current}/{total})", "ANIMATION")
        
        gui.animation_manager.animation_step.connect(on_animation_step)
        
        # Log success
        console.log("Animation manager connected to console logging", "ANIMATION")
    
    # Fix virtual mode status indicators - ULTRA AGGRESSIVE APPROACH
    console.log("Ultra-aggressively clearing all status indicators...", "SYSTEM")
    
    # First attempt - search by text content in ALL labels and widgets
    try:
        # Check all labels in the entire application
        all_labels = gui.findChildren(QLabel)
        console.log(f"Found {len(all_labels)} QLabel objects to check", "SYSTEM")
        
        for label in all_labels:
            try:
                if not hasattr(label, 'text'):
                    continue
                
                # Clear ANY label with status-like text
                text = label.text()
                keywords = ["virtual", "mode", "status", "raspberry", "pi", "led", "hardware", 
                           "message", "controller", "idle", "displaying"]
                
                # Check if any keyword is in the text (case insensitive)
                if any(keyword in text.lower() for keyword in keywords):
                    old_text = text
                    label.setText("")
                    console.log(f"Cleared label: '{old_text}'", "SYSTEM")
            except Exception as e:
                console.log(f"Error checking label: {e}", "ERROR")
    except Exception as e:
        console.log(f"Error processing labels: {e}", "ERROR")
    
    # Special handling for message area and status display widgets
    for attr_name in ['message_area', 'status_area', 'message_display', 'status_display',
                     'message_label', 'status_label', 'source_label', 'status_value_label']:
        if hasattr(gui, attr_name):
            try:
                obj = getattr(gui, attr_name)
                # If it's a QLabel or has setText, clear it
                if hasattr(obj, 'setText'):
                    obj.setText("")
                    console.log(f"Cleared {attr_name}", "SYSTEM")
                # If it's a container, find and clear all labels within it
                elif hasattr(obj, 'findChildren'):
                    for child in obj.findChildren(QLabel):
                        if hasattr(child, 'setText'):
                            child.setText("")
                    console.log(f"Cleared all labels in {attr_name}", "SYSTEM")
            except Exception as e:
                console.log(f"Error clearing {attr_name}: {e}", "ERROR")
    
    # PAUSE ANIMATION - Make punch card stay empty for 3 seconds first
    console.log("Keeping punch card empty for 3 seconds before animations...", "SYSTEM")
    
    # Explicitly clear the card first
    if hasattr(gui, 'punch_card') and hasattr(gui.punch_card, 'clear_grid'):
        gui.punch_card.clear_grid()
        gui.punch_card.update()  # Force visual update
    
    # PAUSE MESSAGE DISPLAY SYSTEM DURING ANIMATIONS
    # Hook into animation signals to pause/resume message display
    if hasattr(gui, 'animation_manager'):
        try:
            # Store original message generation state
            original_message_interval = None
            if hasattr(gui, 'message_timer') and hasattr(gui.message_timer, 'interval'):
                original_message_interval = gui.message_timer.interval()
            
            # Store original message display time
            original_display_time = None
            if hasattr(gui, 'message_display_time'):
                original_display_time = gui.message_display_time
            
            # Pause message system when animations start
            def pause_message_system(animation_type):
                # Stop any active timers
                if hasattr(gui, 'message_timer') and hasattr(gui.message_timer, 'stop'):
                    gui.message_timer.stop()
                    console.log("Paused message timer during animation", "SYSTEM")
                
                # Also stop message display timer if active
                if hasattr(gui, 'message_display_timer') and hasattr(gui.message_display_timer, 'stop'):
                    gui.message_display_timer.stop()
                    console.log("Paused message display timer during animation", "SYSTEM")
            
            # Resume message system when animations complete
            def resume_message_system(animation_type):
                # Only restart if we had a valid interval
                if original_message_interval and hasattr(gui, 'message_timer') and hasattr(gui.message_timer, 'start'):
                    # Restore original interval
                    gui.message_timer.setInterval(original_message_interval)
                    gui.message_timer.start()
                    console.log(f"Resumed message timer with interval {original_message_interval}ms", "SYSTEM")
                
                # Restore display time if needed
                if original_display_time and hasattr(gui, 'message_display_time'):
                    gui.message_display_time = original_display_time
                    console.log(f"Restored message display time to {original_display_time}ms", "SYSTEM")
            
            # Connect signals
            gui.animation_manager.animation_started.connect(pause_message_system)
            gui.animation_manager.animation_finished.connect(resume_message_system)
            console.log("Connected animation signals to pause/resume message system", "SYSTEM")
        except Exception as e:
            console.log(f"Error setting up animation/message integration: {e}", "ERROR")
            
    # Update main window to reflect changes
    gui.update()
    
    # ONE FINAL PASS: Directly target virtual mode text IMMEDIATELY before showing GUI
    console.log("FINAL PASS: Removing any remaining 'Virtual Mode' text", "SYSTEM")
    all_widgets = gui.findChildren(QLabel)
    for widget in all_widgets:
        try:
            if hasattr(widget, 'text') and widget.text():
                text = widget.text()
                if "Virtual Mode" in text or "VIRTUAL MODE" in text:
                    widget.setText("")  # Clear it completely
                    console.log(f"✅ Cleared exact match 'Virtual Mode' text", "SYSTEM")
                elif "Virtual" in text and "Mode" in text:
                    widget.setText("")  # Clear it completely
                    console.log(f"✅ Cleared split 'Virtual...Mode' text", "SYSTEM")
        except Exception as e:
            console.log(f"Error in final text clearing: {e}", "ERROR")
    
    # Show the main GUI
    gui.show()
    console.log("GUI window shown", "SYSTEM")
    
    # Schedule our first animation to play after a delay
    # The delay gives time for the GUI to fully initialize
    QTimer.singleShot(3000, lambda: start_first_animation(gui, console))
    console.log("Initial animation scheduled to start in 3 seconds", "ANIMATION")
    
    # Add a button to open animation panel
    try:
        button_added = False
        if hasattr(gui, 'menu_bar') and hasattr(gui.menu_bar, 'card_menu_popup'):
            # Add to menu
            gui.menu_bar.card_menu_popup.addSeparator()
            action = gui.menu_bar.card_menu_popup.addAction("Animation Controls")
            action.triggered.connect(lambda: gui.animation_panel.show())
            console.log("Animation controls added to Card menu", "SYSTEM")
            button_added = True
            
        # Fallback - add a button somewhere
        if not button_added and hasattr(gui, 'toolbar'):
            from PyQt6.QtWidgets import QPushButton
            animation_button = QPushButton("Animations")
            animation_button.clicked.connect(lambda: gui.animation_panel.show())
            gui.toolbar.addWidget(animation_button)
            console.log("Animation button added to toolbar", "SYSTEM")
            button_added = True
            
        # Last resort - add a button to the main window
        if not button_added and hasattr(gui, 'button_layout'):
            animation_button = RetroButton("Animations")
            animation_button.clicked.connect(lambda: gui.animation_panel.show()) 
            gui.button_layout.addWidget(animation_button)
            console.log("Animation button added to main window", "SYSTEM")
            button_added = True
            
        # Finally, just show the animation panel directly if no button was added
        if not button_added:
            # Show animation panel after a short delay
            QTimer.singleShot(1500, lambda: gui.animation_panel.show())
            console.log("Automatic animation panel display scheduled", "SYSTEM")
            
    except Exception as e:
        console.log(f"Error setting up animation panel access: {e}", "ERROR")
        # Show directly as a fallback
        QTimer.singleShot(1500, lambda: gui.animation_panel.show())
    
    # Intercept direct LED control for consistent logging
    if hasattr(gui, 'punch_card') and hasattr(gui.punch_card, 'set_led'):
        # Store the original method
        original_set_led = gui.punch_card.set_led
        
        # Create a wrapper that logs through our console
        def logged_set_led(row, col, state):
            # Call the original method
            result = original_set_led(row, col, state)
            # Log the action
            status = "ON" if state else "OFF"
            console.log(f"Direct LED ({row},{col}) set {status}", f"LED_{'green' if state else 'gray'}")
            return result
        
        # Replace the original method
        gui.punch_card.set_led = logged_set_led
        console.log("Punch card set_led method wrapped for logging", "SYSTEM")
    
    # Also intercept any clear_grid method
    if hasattr(gui, 'punch_card') and hasattr(gui.punch_card, 'clear_grid'):
        original_clear_grid = gui.punch_card.clear_grid
        
        def logged_clear_grid():
            result = original_clear_grid()
            console.log("Punch card grid cleared", "LED")
            return result
        
        gui.punch_card.clear_grid = logged_clear_grid
        console.log("Punch card clear_grid method wrapped for logging", "SYSTEM")
    
    # Run the application
    return app.exec()

def start_first_animation(gui, console):
    """Start the first animation after initial delay"""
    if hasattr(gui, 'animation_manager'):
        try:
            from src.animation.animation_manager import AnimationType
            console.log("Starting initial startup animation...", "ANIMATION")
            
            # Disable the skip flag to allow our manual animation to play
            import src.animation.animation_manager
            src.animation.animation_manager.SKIP_AUTO_STARTUP_ANIMATION = False
            console.log("✅ FIXED: Auto-startup animation block disabled for manual play", "ANIMATION")
            
            # Ensure clean state
            if hasattr(gui, 'punch_card') and hasattr(gui.punch_card, 'clear_grid'):
                gui.punch_card.clear_grid()
                gui.punch_card.update()
            
            # Play the startup animation
            gui.animation_manager.play_animation(
                AnimationType.STARTUP,
                interrupt=True,
                speed=1.0  # Normal speed
            )
        except Exception as e:
            console.log(f"Error starting initial animation: {e}", "ERROR")
    else:
        console.log("Could not start initial animation - no animation manager found", "ERROR")

if __name__ == "__main__":
    # Run the application
    sys.exit(run()) 