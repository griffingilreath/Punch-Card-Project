"""
Message Bus Viewer

A panel for viewing live message bus activity with filtering capabilities.
"""

import time
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QComboBox, QLabel, QPushButton, QCheckBox, QGridLayout, QWidget
)
from PyQt6.QtCore import Qt, QTimer, QEvent, QPoint, QSize, QRect
from PyQt6.QtGui import QTextCursor, QPainter, QPen, QColor

from src.utils.message_bus import get_message_bus, MessagePriority
from src.utils.colors import COLORS
from src.utils.fonts import get_font_css
from src.utils.ui_components import RetroButton

class CustomComboBox(QComboBox):
    """Custom combo box that constrains its popup width to fit in the parent container."""
    
    def showPopup(self):
        """Override to position the popup correctly within the panel's bounds."""
        # Call the original implementation first
        super().showPopup()
        
        # Use a timer with a slightly longer delay to ensure the popup is fully visible
        QTimer.singleShot(50, self.position_popup)
    
    def position_popup(self):
        """Position the popup correctly within the panel bounds."""
        # Get the view
        popup = self.view()
        if not popup or not popup.isVisible():
            return
            
        # Find the message bus viewer parent
        parent = self
        while parent and not isinstance(parent, MessageBusViewer):
            parent = parent.parent()
            
        if not parent:
            return
            
        # Use a fixed width for the popup that will fit within the panel
        fixed_width = 150  # Set a reasonable fixed width for all dropdowns
        
        # Set the fixed width immediately
        popup.setFixedWidth(fixed_width)
        
        # Get the combo box position relative to the panel
        combo_global_pos = self.mapToGlobal(QPoint(0, 0))

class MessageBusViewer(QFrame):
    """Panel for viewing live message bus activity."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(450, 650)
        self.setStyleSheet("""
            QFrame {
                background-color: black;
                color: white;
                border: 1px solid #444444;
            }
            QLabel {
                color: white;
                font-family: 'Courier New';
                font-size: 11px;
                padding: 1px;
            }
            QComboBox {
                background-color: #101010;
                color: white;
                border: 1px solid #444444;
                padding: 2px 8px 2px 6px;
                font-family: 'Courier New';
                font-size: 11px;
                min-width: 100px;
                max-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
                width: 16px;
            }
            QComboBox::down-arrow {
                image: url(none);
                width: 10px;
                height: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #101010;
                color: white;
                selection-background-color: #303030;
                selection-color: white;
                border: 1px solid #444444;
                padding: 4px;
            }
            QTextEdit {
                background-color: #050505;
                color: white;
                border: 1px solid #444444;
                font-family: 'Courier New';
                font-size: 10px;
            }
            QCheckBox {
                color: white;
                font-family: 'Courier New';
                font-size: 11px;
            }
            QCheckBox::indicator {
                width: 12px;
                height: 12px;
                border: 1px solid white;
            }
            QCheckBox::indicator:checked {
                background-color: white;
            }
            QPushButton {
                font-size: 11px;
            }
        """)
        
        # Get message bus instance
        self.message_bus = get_message_bus()
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        
        # Header with filter controls
        header_container = QWidget()
        header_container.setStyleSheet("background-color: #101010; border: 1px solid #333333;")
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(8, 8, 8, 8)
        header_layout.setSpacing(6)
        
        # Title and intro
        title_layout = QHBoxLayout()
        
        header_label = QLabel("📡 Message Bus Viewer")
        header_label.setStyleSheet(f"{get_font_css(size=13, bold=True)}")
        title_layout.addWidget(header_label)
        
        title_layout.addStretch()
        
        # Auto-scroll checkbox
        self.auto_scroll = QCheckBox("Auto-scroll")
        self.auto_scroll.setChecked(True)
        self.auto_scroll.setToolTip("Automatically scroll to the newest messages")
        title_layout.addWidget(self.auto_scroll)
        
        header_layout.addLayout(title_layout)
        
        # Filter header
        filter_header = QLabel("FILTERS:")
        filter_header.setStyleSheet("color: #aaaaaa; font-size: 10px;")
        header_layout.addWidget(filter_header)
        
        # Filter controls - reorganize to use vertical layout
        filter_layout = QGridLayout()
        filter_layout.setVerticalSpacing(4)
        filter_layout.setHorizontalSpacing(10)
        
        # Priority filter
        priority_label = QLabel("Priority:")
        priority_label.setFixedWidth(55)
        self.priority_filter = CustomComboBox()
        self.priority_filter.addItems(["All", "Critical", "High", "Normal", "Low"])
        self.priority_filter.setToolTip("Filter messages by priority level")
        self.priority_filter.currentTextChanged.connect(self.apply_filters)
        self.priority_filter.setMaxVisibleItems(10)
        self.priority_filter.setFixedWidth(150)
        filter_layout.addWidget(priority_label, 0, 0)
        filter_layout.addWidget(self.priority_filter, 0, 1)
        
        # Source filter
        source_label = QLabel("Source:")
        source_label.setFixedWidth(55)
        self.source_filter = CustomComboBox()
        self.source_filter.addItem("All")
        self.source_filter.setToolTip("Filter messages by source component")
        self.source_filter.currentTextChanged.connect(self.apply_filters)
        self.source_filter.setMaxVisibleItems(10)
        self.source_filter.setFixedWidth(150)
        filter_layout.addWidget(source_label, 0, 2)
        filter_layout.addWidget(self.source_filter, 0, 3)
        
        # Event type filter
        event_label = QLabel("Event:")
        event_label.setFixedWidth(55)
        self.event_filter = CustomComboBox()
        self.event_filter.addItem("All")
        self.event_filter.setToolTip("Filter messages by event type")
        self.event_filter.currentTextChanged.connect(self.apply_filters)
        self.event_filter.setMaxVisibleItems(10)
        self.event_filter.setFixedWidth(150)
        filter_layout.addWidget(event_label, 1, 0)
        filter_layout.addWidget(self.event_filter, 1, 1)
        
        # No need for event filters with custom combo boxes
        
        # Add the complete filter layout to the header
        header_layout.addLayout(filter_layout)
        
        # Add header container to main layout
        layout.addWidget(header_container)
        
        # Create message display
        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        layout.addWidget(self.message_display)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        # Add a clear button
        self.clear_button = RetroButton("Clear")
        self.clear_button.setToolTip("Clear all messages")
        self.clear_button.clicked.connect(self.clear_messages)
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        
        # Add status info
        self.status_label = QLabel("No messages")
        self.status_label.setStyleSheet("color: #888888; font-size: 10px;")
        button_layout.addWidget(self.status_label)
        
        # Add a close button
        self.close_button = RetroButton("Close")
        self.close_button.clicked.connect(self.hide)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Initialize message history
        self.messages = []
        self.filtered_messages = []
        
        # Set up auto-scroll timer
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.scroll_to_bottom)
        self.scroll_timer.setInterval(100)  # Check every 100ms
    
    def showEvent(self, event):
        """Handle show event to update messages and subscribe to message bus."""
        super().showEvent(event)
        
        # Display initial "waiting for messages" state if no messages yet
        if not self.messages:
            self.message_display.setHtml("""
                <div style='margin: 20px; text-align: center; color: #555555; font-size: 11px;'>
                    <p>Connecting to message bus...</p>
                    <p>Messages will appear here as they are published.</p>
                </div>
            """)
        
        # Subscribe to message bus with wildcard for all events
        try:
            # Unsubscribe first to prevent duplicate subscriptions
            try:
                self.message_bus.unsubscribe("*", self.on_message)
            except:
                pass
            
            # Subscribe to all events
            self.message_bus.subscribe("*", self.on_message)
            print("DEBUG: Subscribed to message bus events")
        except Exception as e:
            print(f"DEBUG: Error subscribing to message bus: {str(e)}")
        
        # Start auto-scroll timer
        self.scroll_timer.start()
        
        # If we already have messages, update the display
        if self.messages:
            self.apply_filters()
    
    def hideEvent(self, event):
        """Handle hide event to unsubscribe from message bus."""
        super().hideEvent(event)
        
        # Unsubscribe from message bus when hidden
        try:
            self.message_bus.unsubscribe("*", self.on_message)
        except Exception as e:
            print(f"DEBUG: Error unsubscribing: {str(e)}")
        
        # Stop timers
        if self.scroll_timer.isActive():
            self.scroll_timer.stop()
    
    def on_message(self, message):
        """Handle a new message from the bus."""
        # Handle different data formats
        if isinstance(message.data, dict):
            # Extract message from dict if available
            display_data = message.data.get('message', str(message.data))
        elif isinstance(message.data, str):
            display_data = message.data
        else:
            display_data = str(message.data)
        
        # Create a copy of the message with standardized data for display
        from dataclasses import dataclass, replace
        message_copy = replace(message, data=display_data)
        
        # Add message to history
        self.messages.append(message_copy)
        
        # Update source and event type filters
        self.update_filters()
        
        # Apply current filters
        self.apply_filters()
        
        # Force scroll to bottom if auto-scroll is enabled
        if self.auto_scroll.isChecked():
            self.message_display.moveCursor(QTextCursor.MoveOperation.End)
    
    def update_filters(self):
        """Update the source and event type filter options."""
        # Get unique sources and event types
        sources = {"All"}
        event_types = {"All"}
        
        for message in self.messages:
            sources.add(message.metadata.source)
            event_types.add(message.event_type)
        
        # Update source filter
        current_source = self.source_filter.currentText()
        self.source_filter.blockSignals(True)
        self.source_filter.clear()
        
        # Sort items and limit length
        sorted_sources = sorted(sources)
        for source in sorted_sources:
            # Truncate very long source names for dropdown display
            display_text = source
            if len(display_text) > 30:
                display_text = display_text[:27] + "..."
            self.source_filter.addItem(display_text)
            if display_text != source:  # Add tooltip for truncated items
                index = self.source_filter.count() - 1
                self.source_filter.setItemData(index, source, Qt.ItemDataRole.ToolTipRole)
        
        if current_source in sources:
            self.source_filter.setCurrentText(current_source)
        self.source_filter.blockSignals(False)
        
        # Update event type filter
        current_event = self.event_filter.currentText()
        self.event_filter.blockSignals(True)
        self.event_filter.clear()
        
        # Sort items and limit length
        sorted_events = sorted(event_types)
        for event_type in sorted_events:
            # Truncate very long event names for dropdown display
            display_text = event_type
            if len(display_text) > 30:
                display_text = display_text[:27] + "..."
            self.event_filter.addItem(display_text)
            if display_text != event_type:  # Add tooltip for truncated items
                index = self.event_filter.count() - 1
                self.event_filter.setItemData(index, event_type, Qt.ItemDataRole.ToolTipRole)
        
        if current_event in event_types:
            self.event_filter.setCurrentText(current_event)
        self.event_filter.blockSignals(False)
    
    def apply_filters(self):
        """Apply current filters to messages."""
        # Get filter values
        priority_filter = self.priority_filter.currentText()
        source_filter = self.source_filter.currentText()
        event_filter = self.event_filter.currentText()
        
        # Apply filters
        self.filtered_messages = []
        for message in self.messages:
            # Check priority filter
            if priority_filter != "All" and message.metadata.priority.name != priority_filter.upper():
                continue
            
            # Check source filter
            if source_filter != "All" and message.metadata.source != source_filter:
                continue
            
            # Check event type filter
            if event_filter != "All" and message.event_type != event_filter:
                continue
            
            self.filtered_messages.append(message)
        
        # Update display
        self.update_display()
    
    def update_display(self):
        """Update the message display with filtered messages."""
        # Clear the current content
        self.message_display.clear()
        
        # Update status label with message count
        total_messages = len(self.messages)
        filtered_messages = len(self.filtered_messages)
        
        if total_messages == 0:
            self.status_label.setText("No messages")
        elif filtered_messages == total_messages:
            self.status_label.setText(f"{total_messages} messages")
        else:
            self.status_label.setText(f"{filtered_messages} of {total_messages} messages")
        
        if not self.filtered_messages:
            # Add a placeholder message if no messages
            self.message_display.setHtml("""
                <div style='margin: 20px; text-align: center; color: #555555; font-size: 11px;'>
                    <p>No messages received yet or none match current filters.</p>
                    <p>Messages will appear here as they are published to the message bus.</p>
                </div>
            """)
            return
        
        # Define priority styling
        priority_styles = {
            MessagePriority.CRITICAL: "color: #ff5555; font-weight: bold;",   # Bright red
            MessagePriority.HIGH: "color: #ffaa00;",                          # Orange
            MessagePriority.NORMAL: "color: #bbbbbb;",                        # Light gray
            MessagePriority.LOW: "color: #666666;"                            # Dark gray
        }
        
        # Define event type styling based on common categories
        event_style = {
            "new_message": "color: #88ff88;",         # Green for new messages
            "error": "color: #ff8888;",               # Red for errors
            "status": "color: #88ccff;",              # Blue for status updates
            "animation": "color: #ffccaa;",           # Orange for animations
            "default": "color: #dddd88;"              # Yellow-ish default
        }
        
        # Build HTML content with a compact table-like format
        html_content = """
        <style>
            body { background-color: #050505; color: #dddddd; font-family: 'Courier New', monospace; font-size: 10px; }
            .msg-container { border-bottom: 1px solid #222222; padding: 2px 4px; margin: 0; }
            .msg-container:hover { background-color: #101010; }
            .msg-header { display: flex; align-items: center; margin-bottom: 1px; }
            .msg-time { display: inline-block; min-width: 60px; }
            .msg-source { display: inline-block; min-width: 80px; max-width: 120px; overflow: hidden; text-overflow: ellipsis; color: #00cccc; }
            .msg-event { display: inline-block; min-width: 100px; max-width: 160px; overflow: hidden; text-overflow: ellipsis; }
            .msg-data { margin-left: 14px; margin-top: 1px; margin-bottom: 2px; color: #dddddd; word-wrap: break-word; }
        </style>
        <div>
        """
        
        # Add each message
        for message in self.filtered_messages:
            # Format timestamp
            timestamp = time.strftime("%H:%M:%S", time.localtime(message.metadata.timestamp))
            
            # Determine event style
            event_class = "default"
            if "message" in message.event_type:
                event_class = "new_message"
            elif "error" in message.event_type:
                event_class = "error"
            elif "status" in message.event_type:
                event_class = "status"
            elif "animation" in message.event_type:
                event_class = "animation"
            
            # Add message row
            html_content += f"""
            <div class="msg-container">
                <div class="msg-header">
                    <span class="msg-time" style="{priority_styles.get(message.metadata.priority, 'color: #bbbbbb;')}">{timestamp}</span>
                    <span class="msg-source" title="{message.metadata.source}">{message.metadata.source}</span>
                    <span class="msg-event" style="{event_style.get(event_class)}" title="{message.event_type}">{message.event_type}</span>
                </div>
                <div class="msg-data">{message.data}</div>
            </div>
            """
        
        # Close the container
        html_content += "</div>"
        
        # Set the HTML content
        self.message_display.setHtml(html_content)
    
    def scroll_to_bottom(self):
        """Scroll to bottom if auto-scroll is enabled."""
        if self.auto_scroll.isChecked():
            self.message_display.moveCursor(QTextCursor.MoveOperation.End)
    
    def clear_messages(self):
        """Clear all messages from the display."""
        self.messages = []
        self.filtered_messages = []
        self.message_display.clear()
        self.update_filters()
    
    def paintEvent(self, event):
        """Custom paint event to draw an angular border."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw border
        painter.setPen(QPen(QColor(COLORS['hole_outline']), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1)) 