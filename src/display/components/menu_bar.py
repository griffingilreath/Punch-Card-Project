#!/usr/bin/env python3
"""
Menu Bar Module

Custom in-app menu bar that simulates classic Mac menu bar appearance with wifi status widget.
"""

import random
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QMenu, QLabel, QSlider, 
    QWidgetAction, QMessageBox
)
from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QSize
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QAction
)

from src.utils.fonts import get_font_css

class WiFiStatusWidget(QWidget):
    """Custom widget for displaying WiFi status with rectangular bars."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(30)
        self.setFixedHeight(22)
        self.setProperty("status", "connected")
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # Show pointer cursor on hover
        
        # Create popup menu for WiFi settings
        self.wifi_menu = QMenu(self)
        self.wifi_menu.setStyleSheet("""
            QMenu {
                background-color: black;
                color: white;
                border: 1px solid white;
                font-family: Courier New, monospace;
                font-size: 12px;
            }
            QMenu::item {
                padding: 4px 25px;
            }
            QMenu::item:selected {
                background-color: white;
                color: black;
            }
            QMenu::separator {
                height: 1px;
                background-color: #444444;
                margin: 4px 2px;
            }
        """)
        
        # Add menu items
        self.connected_action = self.wifi_menu.addAction("Connected")
        self.connected_action.setCheckable(True)
        self.connected_action.setChecked(True)
        self.connected_action.triggered.connect(lambda: self.set_wifi_status("connected"))
        
        self.weak_action = self.wifi_menu.addAction("Weak Signal")
        self.weak_action.setCheckable(True)
        self.weak_action.triggered.connect(lambda: self.set_wifi_status("weak"))
        
        self.disconnected_action = self.wifi_menu.addAction("Disconnected")
        self.disconnected_action.setCheckable(True)
        self.disconnected_action.triggered.connect(lambda: self.set_wifi_status("disconnected"))
        
        self.wifi_menu.addSeparator()
        self.wifi_menu.addAction("WiFi Settings...").triggered.connect(self.show_wifi_settings)
    
    def set_wifi_status(self, status):
        """Set the WiFi status and update checked actions."""
        self.setProperty("status", status)
        
        # Update checked states
        self.connected_action.setChecked(status == "connected")
        self.weak_action.setChecked(status == "weak")
        self.disconnected_action.setChecked(status == "disconnected")
        
        # Repaint the widget
        self.update()
    
    def update_status(self):
        """Update the WiFi status (simulated for demo purposes)."""
        # For demo, randomly select a status with bias toward "connected"
        rand = random.random()
        if rand < 0.7:
            self.set_wifi_status("connected")
        elif rand < 0.9:
            self.set_wifi_status("weak")
        else:
            self.set_wifi_status("disconnected")
    
    def show_wifi_settings(self):
        """Show more detailed WiFi settings dialog."""
        QMessageBox.information(self, "WiFi Settings", 
                               "This would show a detailed WiFi configuration dialog.\n"
                               "Currently in simulation mode only.")
    
    def mousePressEvent(self, event):
        """Handle mouse press to show the popup menu."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Get the window and calculate its right edge
            window = self.window()
            window_right_edge = window.mapToGlobal(QPoint(window.width(), 0)).x()
            
            # Get the menu width
            menu_width = self.wifi_menu.sizeHint().width()
            
            # Get position - x from current widget, y from menu bar bottom
            x_pos = self.mapToGlobal(QPoint(0, 0)).x()
            
            # Get parent menu bar to determine its bottom edge
            parent_menubar = self.parent()
            y_pos = parent_menubar.mapToGlobal(QPoint(0, parent_menubar.height() - 1)).y()  # Moved down 1 pixel
            
            # Make sure menu doesn't go off screen
            x_position = min(x_pos, window_right_edge - menu_width)
            
            # Show popup at the adjusted position
            self.wifi_menu.popup(QPoint(x_position, y_pos))
    
    def paintEvent(self, event):
        """Paint the WiFi status icon with rectangular bars."""
        super().paintEvent(event)
        
        # Get WiFi connection status
        status = self.property("status") or "disconnected"
        
        # Create painter for this widget
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Use white color for WiFi bars in all states
        color = QColor(255, 255, 255)
        
        # Determine number of bars based on connection status
        if status == "connected":
            bars = 3
        elif status == "weak":
            bars = 2
        else:  # Disconnected
            bars = 1
        
        # Configure painter
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        
        # Calculate position centered in widget
        center_x = self.width() // 2
        y_base = self.height() - 7  # Add more space at the bottom (was 6)
        
        # Calculate total width of all bars
        bar_width = 3
        spacing = 2
        total_width = (3 * bar_width) + (2 * spacing)  # Always show 3 bars (some empty)
        start_x = center_x - (total_width // 2)
        
        # Draw all three bars (filled or empty based on status)
        for i in range(3):
            x = start_x + (i * (bar_width + spacing))
            bar_height = 4 + (i * 2)  # Slightly shorter bars (was i*3)
            y = y_base - bar_height
            
            # If this bar should be filled based on status
            if i < bars:
                painter.setBrush(QBrush(color))
            else:
                # Draw outline for inactive bars
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(QPen(color, 0.8))
            
            painter.drawRect(x, y, bar_width, bar_height)
            painter.setPen(Qt.PenStyle.NoPen)  # Reset pen for next iteration

class InAppMenuBar(QWidget):
    """Custom in-app menu bar that simulates classic Mac menu bar appearance."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(22)
        self.setStyleSheet("background-color: transparent; color: white; border: none;")
        
        # Create main layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(1)
        
        # Left side - Menu items
        self.left_container = QWidget()
        self.left_layout = QHBoxLayout(self.left_container)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(1)
        
        # Create menu buttons
        self.apple_menu = self.create_menu_button("▭", is_apple=True)
        self.card_menu = self.create_menu_button("Punch Card")
        self.settings_menu = self.create_menu_button("Settings")
        self.console_menu = self.create_menu_button("Console")
        
        # Right side - Status indicators
        self.right_container = QWidget()
        self.right_layout = QHBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(5)
        
        # Add WiFi status
        self.wifi_status = WiFiStatusWidget(self)
        self.right_layout.addWidget(self.wifi_status)
        
        # Add clock button
        self.clock_button = QPushButton()
        self.clock_button.setFlat(True)
        self.clock_button.setMinimumWidth(140)
        self.clock_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                border: none;
                padding: 2px 8px;
                text-align: center;
                {get_font_css(size=11, bold=False)}
            }}
            QPushButton:hover {{
                background-color: white;
                color: black;
            }}
            QPushButton:pressed {{
                background-color: #444444;
                color: white;
            }}
        """)
        self.right_layout.addWidget(self.clock_button)
        
        # Add containers to main layout
        self.layout.addWidget(self.left_container)
        self.layout.addStretch(1)
        self.layout.addWidget(self.right_container)
        
        # Initialize menus
        self.apple_menu_popup = QMenu(self)
        self.card_menu_popup = QMenu(self)
        self.settings_menu_popup = QMenu(self)
        self.console_menu_popup = QMenu(self)
        self.notifications_popup = QMenu(self)
        
        # Connect menu buttons
        self.apple_menu.clicked.connect(self.show_apple_menu)
        self.card_menu.clicked.connect(self.show_card_menu)
        self.settings_menu.clicked.connect(self.show_settings_menu)
        self.console_menu.clicked.connect(self.show_console_menu)
        self.clock_button.clicked.connect(self.show_notifications)
        
        # Setup timers
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()
        
        self.wifi_timer = QTimer(self)
        self.wifi_timer.timeout.connect(self.update_wifi_status)
        self.wifi_timer.start(5000)
        self.update_wifi_status()
    
    def paintEvent(self, event):
        """Custom paint event to draw the menu bar with classic Mac styling."""
        # Create painter for drawing
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)  # Turn off antialiasing for crisp lines
        
        # Step 1: Draw the black background over everything
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        
        # Step 2: Let the base class handle child widgets
        painter.end()
        super().paintEvent(event)
        
        # Step 3: Create a new painter to draw on top of everything
        painter = QPainter(self)
        
        # Set up a pen for the white bottom border
        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(1)
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        
        # Draw the line precisely at the bottom of the widget
        bottom_y = self.height() - 1
        painter.drawLine(0, bottom_y, self.width(), bottom_y)
    
    def setup_menu_actions(self, main_window):
        """Set up menu actions after the main window is fully initialized."""
        # Define common menu style
        menu_style = f"""
            QMenu {{
                background-color: black;
                color: white;
                border: 1px solid white;
                {get_font_css(size=12)}
            }}
            QMenu::item {{
                padding: 4px 25px;
            }}
            QMenu::item:selected {{
                background-color: white;
                color: black;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: #444444;
                margin: 4px 2px;
            }}
        """
        
        # Apply styles to all menus
        self.apple_menu_popup.setStyleSheet(menu_style)
        self.card_menu_popup.setStyleSheet(menu_style)
        self.settings_menu_popup.setStyleSheet(menu_style)
        self.console_menu_popup.setStyleSheet(menu_style)
        self.notifications_popup.setStyleSheet(menu_style)
        
        # ---- Apple menu items ----
        about_action = self.apple_menu_popup.addAction("About This Punch Card")
        self.apple_menu_popup.addSeparator()
        sleep_action = self.apple_menu_popup.addAction("Sleep")
        restart_action = self.apple_menu_popup.addAction("Restart")
        shutdown_action = self.apple_menu_popup.addAction("Shut Down")
        
        # Connect Apple menu signals
        about_action.triggered.connect(main_window.show_about_dialog)
        sleep_action.triggered.connect(main_window.start_sleep_mode)
        restart_action.triggered.connect(main_window.restart_app)
        shutdown_action.triggered.connect(main_window.safe_shutdown)
        
        # ---- Punch Card menu ----
        display_message_action = self.card_menu_popup.addAction("Display Message")
        clear_card_action = self.card_menu_popup.addAction("Clear Card")
        self.card_menu_popup.addSeparator()
        card_settings_action = self.card_menu_popup.addAction("Card Dimensions...")
        
        # Connect Punch Card menu signals
        display_message_action.triggered.connect(main_window.start_display)
        if hasattr(main_window, 'punch_card'):
            clear_card_action.triggered.connect(main_window.punch_card.clear_grid)
        card_settings_action.triggered.connect(main_window.show_card_settings)
        
        # ---- Settings menu ----
        display_settings_action = self.settings_menu_popup.addAction("Display Settings...")
        openai_settings_action = self.settings_menu_popup.addAction("API Settings...")
        
        # Add Sound submenu
        sound_menu = QMenu("Sound", self.settings_menu_popup)
        sound_menu.setStyleSheet(menu_style)
        
        # Add volume control
        volume_action = QWidgetAction(sound_menu)
        volume_widget = QWidget()
        volume_layout = QHBoxLayout(volume_widget)
        volume_layout.setContentsMargins(25, 5, 25, 5)
        
        volume_label = QLabel("Volume:")
        volume_label.setStyleSheet("color: white;")
        volume_layout.addWidget(volume_label)
        
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(100)
        volume_slider.setFixedWidth(100)
        volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #444444;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
        """)
        volume_layout.addWidget(volume_slider)
        
        volume_value = QLabel("100%")
        volume_value.setStyleSheet("color: white; min-width: 40px;")
        volume_layout.addWidget(volume_value)
        
        volume_action.setDefaultWidget(volume_widget)
        sound_menu.addAction(volume_action)
        
        # Add mute option
        mute_action = sound_menu.addAction("Mute")
        mute_action.setCheckable(True)
        
        # Add separator
        sound_menu.addSeparator()
        
        # Add sound settings
        sound_settings_action = sound_menu.addAction("Sound Settings...")
        
        # Add sound menu to settings menu
        self.settings_menu_popup.addMenu(sound_menu)
        
        statistics_action = self.settings_menu_popup.addAction("Statistics...")
        self.settings_menu_popup.addSeparator()
        inline_settings_action = self.settings_menu_popup.addAction("Quick Settings Panel")
        
        # Connect settings menu signals using lambda functions
        display_settings_action.triggered.connect(lambda: self.show_display_settings_debug(main_window))
        openai_settings_action.triggered.connect(lambda: self.show_api_settings_debug(main_window))
        volume_slider.valueChanged.connect(lambda v: self.on_volume_changed(v, volume_value, main_window))
        mute_action.triggered.connect(lambda checked: self.on_mute_changed(checked, main_window))
        sound_settings_action.triggered.connect(lambda: main_window.sound_settings_dialog.show())
        statistics_action.triggered.connect(main_window.show_statistics_dialog)
        inline_settings_action.triggered.connect(main_window.toggle_quick_settings)
        
        # ---- Console menu ----
        system_console_action = self.console_menu_popup.addAction("System Console")
        api_console_action = self.console_menu_popup.addAction("API Console")
        message_bus_action = self.console_menu_popup.addAction("Message Bus Viewer")
        
        # Connect Console menu signals
        system_console_action.triggered.connect(lambda: main_window.console.show())
        api_console_action.triggered.connect(lambda: main_window.api_console.show())
        message_bus_action.triggered.connect(lambda: self.show_message_bus_viewer_debug(main_window))
        
        # ---- Notifications menu (for future use) ----
        self.notifications_popup.addAction("No New Notifications")
        self.notifications_popup.addSeparator()
        notification_settings = self.notifications_popup.addAction("Notification Settings...")
        clear_all = self.notifications_popup.addAction("Clear All")
    
    def on_volume_changed(self, value, label, main_window):
        """Handle volume slider changes."""
        label.setText(f"{value}%")
        if hasattr(main_window, 'sound_manager'):
            main_window.sound_manager.set_volume(value / 100.0)
    
    def on_mute_changed(self, checked, main_window):
        """Handle mute state changes."""
        if hasattr(main_window, 'sound_manager'):
            main_window.sound_manager.set_muted(checked)
    
    def create_menu_button(self, text, is_apple=False):
        """Create a button that looks like a menu item."""
        button = QPushButton(text)
        button.setFlat(True)
        
        if is_apple:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 0px 8px;
                    text-align: center;
                    font-size: 22px;
                    font-weight: normal;
                    min-width: 24px;
                    min-height: 22px;
                    margin: 0px;
                    margin-top: -4px;
                    line-height: 15px;
                    vertical-align: top;
                    padding-top: 0px;
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: black;
                }}
                QPushButton:pressed {{
                    background-color: #444444;
                    color: white;
                }}
            """)
        else:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 2px 8px;
                    text-align: center;
                    {get_font_css(size=12)}
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: black;
                }}
                QPushButton:pressed {{
                    background-color: #444444;
                    color: white;
                }}
            """)
        
        self.left_layout.addWidget(button)
        return button
    
    def show_apple_menu(self):
        """Show the apple menu."""
        self.apple_menu_popup.exec(self.apple_menu.mapToGlobal(QPoint(0, self.height())))
    
    def show_card_menu(self):
        """Show the punch card menu."""
        self.card_menu_popup.exec(self.card_menu.mapToGlobal(QPoint(0, self.height())))
    
    def show_settings_menu(self):
        """Show the settings menu."""
        self.settings_menu_popup.exec(self.settings_menu.mapToGlobal(QPoint(0, self.height())))
    
    def show_console_menu(self):
        """Show the console menu."""
        self.console_menu_popup.exec(self.console_menu.mapToGlobal(QPoint(0, self.height())))
    
    def show_notifications(self):
        """Show the notifications menu."""
        # Get the window and calculate its right edge
        window = self.window()
        window_right_edge = window.mapToGlobal(QPoint(window.width(), 0)).x()
        
        # Get the menu width
        menu_width = self.notifications_popup.sizeHint().width()
        
        # Get position - y from menu bar bottom
        y_pos = self.mapToGlobal(QPoint(0, self.height())).y()
        
        # Calculate x position to align with window right edge
        x_pos = window_right_edge - menu_width
        
        # Show popup at the adjusted position
        self.notifications_popup.popup(QPoint(x_pos, y_pos))
    
    def update_clock(self):
        """Update the clock display."""
        from PyQt6.QtCore import QDateTime
        now = QDateTime.currentDateTime()
        self.clock_button.setText(now.toString("ddd MMM d h:mm AP"))
    
    def update_wifi_status(self):
        """Update the WiFi status indicator."""
        if hasattr(self, 'wifi_status'):
            self.wifi_status.update_status()
    
    def on_sound_volume_changed(self, value):
        """Handle volume changes from the sound control."""
        if hasattr(self.parent(), 'sound_manager'):
            self.parent().sound_manager.set_volume(value / 100.0)
    
    def on_sound_mute_changed(self, muted):
        """Handle mute state changes from the sound control."""
        if hasattr(self.parent(), 'sound_manager'):
            self.parent().sound_manager.set_muted(muted)
    
    def show_message_bus_viewer_debug(self, main_window):
        """Debug wrapper for showing message bus viewer."""
        print("DEBUG: Message bus viewer action triggered")
        try:
            from src.ui.message_bus_viewer import MessageBusViewer
            from src.utils.message_bus import get_message_bus, MessagePriority
            
            # Create the message bus viewer directly
            if not hasattr(main_window, 'message_bus_viewer'):
                print("DEBUG: Creating new MessageBusViewer instance directly")
                main_window.message_bus_viewer = MessageBusViewer(main_window)
                
            # Show the viewer
            main_window.message_bus_viewer.show()
            main_window.message_bus_viewer.raise_()
            
            # Position manually with direct calculation
            x = main_window.width() - main_window.message_bus_viewer.width() - 20
            y = 60  # Below the menu bar
            print(f"DEBUG: Positioning message bus viewer at ({x}, {y})")
            main_window.message_bus_viewer.move(x, y)
            
            # Get message bus
            message_bus = get_message_bus()
            print("DEBUG: Got message bus instance")
            
            # Test direct message publication
            print("DEBUG: Publishing test messages directly...")
            
            # Try different message formats
            message_bus.publish(
                "test_event_1", 
                {"message": "Test message 1 - dictionary format"},
                "TestSource1", 
                MessagePriority.NORMAL
            )
            
            message_bus.publish(
                "test_event_2", 
                "Test message 2 - string format",
                "TestSource2", 
                MessagePriority.HIGH
            )
            
            # Properly formatted test messages with direct data access
            for i in range(3):
                message_bus.publish(
                    f"example_event_{i}", 
                    f"Example message {i} with timestamp {i}",
                    f"ExampleSource{i}", 
                    MessagePriority.NORMAL
                )
            
            print("DEBUG: Published test messages to the message bus")
            
        except ImportError as e:
            print(f"DEBUG: Error importing MessageBusViewer: {str(e)}")
        except Exception as e:
            print(f"DEBUG: Error showing message bus viewer: {str(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            print("DEBUG: Available methods:", [method for method in dir(main_window) if not method.startswith('_')])
    
    def show_display_settings_debug(self, main_window):
        """Debug wrapper for showing display settings panel."""
        print("DEBUG: Display settings action triggered")
        try:
            # Create the display settings panel if it doesn't exist
            if not hasattr(main_window, 'display_settings_panel'):
                print("DEBUG: Creating new DisplaySettingsPanel instance")
                from src.display.components.display_settings_panel import DisplaySettingsPanel
                main_window.display_settings_panel = DisplaySettingsPanel(main_window)
                
            # Show the panel
            main_window.display_settings_panel.show()
            main_window.display_settings_panel.raise_()
            
            # Position manually with direct calculation
            x = main_window.width() - main_window.display_settings_panel.width() - 20
            y = 60  # Below the menu bar
            print(f"DEBUG: Positioning display settings panel at ({x}, {y})")
            main_window.display_settings_panel.move(x, y)
            
            # Load settings
            if hasattr(main_window.display_settings_panel, 'load_settings'):
                main_window.display_settings_panel.load_settings()
            
        except Exception as e:
            print(f"DEBUG: Error showing display settings panel: {str(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            print("DEBUG: Available methods:", [method for method in dir(main_window) if not method.startswith('_')])
    
    def show_api_settings_debug(self, main_window):
        """Debug wrapper for showing API settings panel."""
        print("DEBUG: API settings action triggered")
        try:
            # Create the API settings panel if it doesn't exist
            if not hasattr(main_window, 'openai_settings_panel'):
                print("DEBUG: Creating new OpenAISettingsPanel instance")
                from src.display.components.openai_settings_panel import OpenAISettingsPanel
                main_window.openai_settings_panel = OpenAISettingsPanel(main_window)
                
            # Show the panel
            main_window.openai_settings_panel.show()
            main_window.openai_settings_panel.raise_()
            
            # Position manually with direct calculation
            x = main_window.width() - main_window.openai_settings_panel.width() - 20
            y = 60  # Below the menu bar
            print(f"DEBUG: Positioning API settings panel at ({x}, {y})")
            main_window.openai_settings_panel.move(x, y)
            
            # Load settings
            if hasattr(main_window.openai_settings_panel, 'load_settings'):
                main_window.openai_settings_panel.load_settings()
            
        except Exception as e:
            print(f"DEBUG: Error showing API settings panel: {str(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            print("DEBUG: Available methods:", [method for method in dir(main_window) if not method.startswith('_')]) 