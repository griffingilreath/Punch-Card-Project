#!/usr/bin/env python3
"""
Stats Panel Module

A panel for viewing punch card statistics in an angular and modular design.
"""

import time
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel, 
    QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor

from src.utils.colors import COLORS
from src.utils.fonts import get_font_css
from src.utils.ui_components import RetroButton
from src.core.punch_card import PunchCardStats

class StatsPanel(QFrame):
    """Panel for viewing punch card statistics in an angular and modular design."""
    
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
                font-size: 12px;
                padding: 1px;
                min-width: 120px;
            }
            QGroupBox {
                color: white;
                border: 1px solid #444444;
                border-radius: 0px;
                margin-top: 1.5ex;
                font-family: 'Courier New';
                font-size: 12px;
                font-weight: bold;
                padding: 4px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: white;
                font-family: 'Courier New';
                font-size: 12px;
                font-weight: bold;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Header
        header_label = QLabel("📊 Punch Card Statistics")
        header_label.setStyleSheet(f"{get_font_css(size=14, bold=True)}")
        layout.addWidget(header_label)
        
        # Stats content layout
        content_layout = QVBoxLayout()
        content_layout.setSpacing(8)
        layout.addLayout(content_layout)
        
        # Add General Stats
        self.general_group = QGroupBox("General Statistics")
        general_layout = QGridLayout()
        self.general_group.setLayout(general_layout)
        general_layout.setContentsMargins(8, 15, 8, 8)
        general_layout.setSpacing(4)
        general_layout.setColumnMinimumWidth(1, 120)
        
        # We'll populate these in update_stats
        self.cards_processed_label = QLabel("0")
        self.total_holes_label = QLabel("0")
        self.avg_msg_length_label = QLabel("0.00 characters")
        self.processing_rate_label = QLabel("0.00 cards/hour")
        self.most_used_char_label = QLabel("None")
        self.least_used_char_label = QLabel("None")
        
        # Set alignment for all value labels
        for label in [self.cards_processed_label, self.total_holes_label, 
                     self.avg_msg_length_label, self.processing_rate_label,
                     self.most_used_char_label, self.least_used_char_label]:
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setMinimumWidth(120)
        
        general_layout.addWidget(QLabel("Cards Processed:"), 0, 0)
        general_layout.addWidget(self.cards_processed_label, 0, 1)
        
        general_layout.addWidget(QLabel("Total Holes:"), 1, 0)
        general_layout.addWidget(self.total_holes_label, 1, 1)
        
        general_layout.addWidget(QLabel("Avg Message Length:"), 2, 0)
        general_layout.addWidget(self.avg_msg_length_label, 2, 1)
        
        general_layout.addWidget(QLabel("Processing Rate:"), 3, 0)
        general_layout.addWidget(self.processing_rate_label, 3, 1)
        
        general_layout.addWidget(QLabel("Most Used Char:"), 4, 0)
        general_layout.addWidget(self.most_used_char_label, 4, 1)
        
        general_layout.addWidget(QLabel("Least Used Char:"), 5, 0)
        general_layout.addWidget(self.least_used_char_label, 5, 1)
        
        content_layout.addWidget(self.general_group)
        
        # Message Types
        self.types_group = QGroupBox("Message Types")
        types_layout = QGridLayout()
        self.types_group.setLayout(types_layout)
        types_layout.setContentsMargins(8, 15, 8, 8)
        types_layout.setSpacing(4)
        types_layout.setColumnMinimumWidth(1, 120)
        
        self.local_count_label = QLabel("0")
        self.ai_count_label = QLabel("0")
        self.database_count_label = QLabel("0")
        self.other_count_label = QLabel("0")
        
        # Set alignment for all value labels
        for label in [self.local_count_label, self.ai_count_label,
                     self.database_count_label, self.other_count_label]:
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setMinimumWidth(120)
        
        types_layout.addWidget(QLabel("Local:"), 0, 0)
        types_layout.addWidget(self.local_count_label, 0, 1)
        
        types_layout.addWidget(QLabel("AI:"), 1, 0)
        types_layout.addWidget(self.ai_count_label, 1, 1)
        
        types_layout.addWidget(QLabel("Database:"), 2, 0)
        types_layout.addWidget(self.database_count_label, 2, 1)
        
        types_layout.addWidget(QLabel("Other:"), 3, 0)
        types_layout.addWidget(self.other_count_label, 3, 1)
        
        content_layout.addWidget(self.types_group)
        
        # Error Statistics
        self.error_group = QGroupBox("Error Statistics")
        error_layout = QGridLayout()
        self.error_group.setLayout(error_layout)
        error_layout.setContentsMargins(8, 15, 8, 8)
        error_layout.setSpacing(4)
        error_layout.setColumnMinimumWidth(1, 120)
        
        self.encoding_errors_label = QLabel("0")
        self.invalid_chars_label = QLabel("0")
        self.msg_too_long_label = QLabel("0")
        self.other_errors_label = QLabel("0")
        
        # Set alignment for all value labels
        for label in [self.encoding_errors_label, self.invalid_chars_label,
                     self.msg_too_long_label, self.other_errors_label]:
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setMinimumWidth(120)
        
        error_layout.addWidget(QLabel("Encoding Errors:"), 0, 0)
        error_layout.addWidget(self.encoding_errors_label, 0, 1)
        
        error_layout.addWidget(QLabel("Invalid Characters:"), 1, 0)
        error_layout.addWidget(self.invalid_chars_label, 1, 1)
        
        error_layout.addWidget(QLabel("Message Too Long:"), 2, 0)
        error_layout.addWidget(self.msg_too_long_label, 2, 1)
        
        error_layout.addWidget(QLabel("Other Errors:"), 3, 0)
        error_layout.addWidget(self.other_errors_label, 3, 1)
        
        content_layout.addWidget(self.error_group)
        
        # Add Energy & Time Statistics
        self.energy_group = QGroupBox("Energy & Time Statistics")
        energy_layout = QGridLayout()
        self.energy_group.setLayout(energy_layout)
        energy_layout.setContentsMargins(8, 15, 8, 8)
        energy_layout.setSpacing(4)
        energy_layout.setColumnMinimumWidth(1, 120)
        
        # Define constants for M4 Mac Mini power usage
        self.M4_MAC_MINI_WATTS = 12.5  # Average power in watts
        self.ELECTRICITY_COST_PER_KWH = 0.15  # Default cost in dollars per kilowatt-hour
        
        # Create labels for energy statistics
        self.time_active_label = QLabel("0 minutes")
        self.energy_consumed_label = QLabel("0.00 kWh")
        self.cost_estimate_label = QLabel("$0.00")
        self.electricity_rate_label = QLabel(f"${self.ELECTRICITY_COST_PER_KWH}/kWh")
        self.power_consumption_label = QLabel(f"{self.M4_MAC_MINI_WATTS}W")
        
        # Set alignment for all value labels
        for label in [self.time_active_label, self.energy_consumed_label, 
                     self.cost_estimate_label, self.electricity_rate_label,
                     self.power_consumption_label]:
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setMinimumWidth(120)
        
        energy_layout.addWidget(QLabel("Time Active:"), 0, 0)
        energy_layout.addWidget(self.time_active_label, 0, 1)
        
        energy_layout.addWidget(QLabel("Energy Used:"), 1, 0)
        energy_layout.addWidget(self.energy_consumed_label, 1, 1)
        
        energy_layout.addWidget(QLabel("Cost Estimate:"), 2, 0)
        energy_layout.addWidget(self.cost_estimate_label, 2, 1)
        
        energy_layout.addWidget(QLabel("Electricity Rate:"), 3, 0)
        energy_layout.addWidget(self.electricity_rate_label, 3, 1)
        
        energy_layout.addWidget(QLabel("M4 Mac Mini Power:"), 4, 0)
        energy_layout.addWidget(self.power_consumption_label, 4, 1)
        
        content_layout.addWidget(self.energy_group)
        
        # Add buttons with more spacing
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.refresh_btn = RetroButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_stats)
        button_layout.addWidget(self.refresh_btn)
        
        self.reset_btn = RetroButton("Reset")
        self.reset_btn.clicked.connect(self.reset_stats)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        self.close_btn = RetroButton("Close")
        self.close_btn.clicked.connect(self.hide)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # Add a refresh timer to update stats periodically 
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_stats)
        self.refresh_timer.setInterval(5000)  # 5 seconds
        
    def showEvent(self, event):
        """Handle show event to update stats and start refresh timer."""
        super().showEvent(event)
        self.refresh_stats()
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
    
    def hideEvent(self, event):
        """Handle hide event to stop refresh timer."""
        super().hideEvent(event)
        if hasattr(self, 'refresh_timer') and self.refresh_timer.isActive():
            self.refresh_timer.stop()
    
    def refresh_stats(self):
        """Refresh the statistics display."""
        if not hasattr(self.parent(), 'stats'):
            return
            
        stats = self.parent().stats.get_stats()
        
        # Update general stats
        self.cards_processed_label.setText(f"{stats.get('cards_processed', 0):,}")
        self.total_holes_label.setText(f"{stats.get('total_holes', 0):,}")
        
        avg_msg_length = stats.get('average_message_length', 0)
        self.avg_msg_length_label.setText(f"{avg_msg_length:.2f} characters")
        
        processing_rate = stats.get('processing_rate', 0)
        self.processing_rate_label.setText(f"{processing_rate:.2f} cards/hour")
        
        most_used = stats.get('most_used_char', '')
        if most_used:
            self.most_used_char_label.setText(f"'{most_used}'")
        else:
            self.most_used_char_label.setText("None")
            
        least_used = stats.get('least_used_char', '')
        if least_used:
            self.least_used_char_label.setText(f"'{least_used}'")
        else:
            self.least_used_char_label.setText("None")
        
        # Update message types
        message_types = stats.get('message_types', {})
        self.local_count_label.setText(f"{message_types.get('Local', 0):,}")
        self.ai_count_label.setText(f"{message_types.get('AI', 0):,}")
        self.database_count_label.setText(f"{message_types.get('Database', 0):,}")
        self.other_count_label.setText(f"{message_types.get('Other', 0):,}")
        
        # Update error stats
        error_stats = stats.get('error_stats', {})
        self.encoding_errors_label.setText(f"{error_stats.get('encoding_errors', 0):,}")
        self.invalid_chars_label.setText(f"{error_stats.get('invalid_characters', 0):,}")
        self.msg_too_long_label.setText(f"{error_stats.get('message_too_long', 0):,}")
        self.other_errors_label.setText(f"{error_stats.get('other_errors', 0):,}")
        
        # Update energy & time statistics
        time_operating_seconds = stats.get('time_operating', 0)
        hours = time_operating_seconds / 3600
        minutes = (time_operating_seconds % 3600) / 60
        
        if hours >= 1:
            self.time_active_label.setText(f"{int(hours)}h {int(minutes)}m")
        else:
            self.time_active_label.setText(f"{int(minutes)} minutes")
            
        # Calculate energy consumption (kWh = power in watts * hours / 1000)
        energy_kwh = (self.M4_MAC_MINI_WATTS * hours) / 1000
        self.energy_consumed_label.setText(f"{energy_kwh:.4f} kWh")
        
        # Calculate cost (cost = kWh * rate)
        cost = energy_kwh * self.ELECTRICITY_COST_PER_KWH
        self.cost_estimate_label.setText(f"${cost:.4f}")
    
    def reset_stats(self):
        """Reset the statistics."""
        confirm = QMessageBox.question(
            self, 
            "Reset Statistics",
            "Are you sure you want to reset all punch card statistics?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            if hasattr(self.parent(), 'stats'):
                # Create a new PunchCardStats instance with default values
                self.parent().stats = PunchCardStats()
                # Initialize with default values
                self.parent().stats.stats = {
                    'cards_processed': 0,
                    'total_holes': 0,
                    'character_stats': {},
                    'message_length_stats': {},
                    'message_types': {
                        'Local': 0,
                        'AI': 0,
                        'Database': 0,
                        'Other': 0
                    },
                    'error_stats': {
                        'encoding_errors': 0,
                        'invalid_characters': 0,
                        'message_too_long': 0,
                        'other_errors': 0
                    },
                    'start_time': time.time(),
                    'last_update': time.time()
                }
                # Save the reset statistics
                self.parent().stats.save_stats()
                QMessageBox.information(
                    self, 
                    "Statistics Reset",
                    "Punch card statistics have been reset."
                )
                self.refresh_stats()
    
    def paintEvent(self, event):
        """Custom paint event to draw an angular border."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw border
        painter.setPen(QPen(QColor(COLORS['hole_outline']), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1)) 