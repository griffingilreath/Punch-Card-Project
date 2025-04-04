#!/usr/bin/env python3
"""
Impact Panel Module

A panel for tracking and displaying electric usage, API request costs, and environmental impact.
"""

import logging
import psutil
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QFormLayout,
    QPushButton, QMessageBox, QTabWidget, QWidget, QProgressBar, QSpacerItem, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor

from src.utils.colors import COLORS
from src.utils.fonts import get_font_css
from src.utils.ui_components import RetroButton
from src.utils.settings_manager import get_settings
from src.utils.message_bus import get_message_bus
from src.utils.message_events import (
    EVENT_API_REQUEST_STARTED,
    EVENT_API_REQUEST_COMPLETED,
    EVENT_API_REQUEST_FAILED,
    EVENT_SYSTEM_READY,
    EVENT_SYSTEM_SHUTDOWN,
    EVENT_POWER_USAGE_UPDATED,
    EVENT_ENVIRONMENTAL_IMPACT_UPDATED
)

# Configure logging
logger = logging.getLogger('ImpactPanel')

# Constants for environmental impact calculations
CARBON_INTENSITY = 0.4  # kg CO2 per kWh (US average)
COST_PER_KWH = 0.12    # $ per kWh (US average)
CAR_EMISSIONS = 0.404   # kg CO2 per mile (average car)
TREE_ABSORPTION = 21.77 # kg CO2 per tree per year

# Component power usage estimates (in watts)
COMPONENT_POWER = {
    'mac_mini': {
        'idle': 6.8,
        'active': 15.0,
        'max': 30.0
    },
    'punch_card': {
        'idle': 5.0,
        'active': 20.0,
        'max': 30.0
    }
}

class ImpactPanel(QFrame):
    """Panel for tracking and displaying electric usage, API request costs, and environmental impact."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize session statistics to zero
        self.total_electric_usage = 0.0
        self.total_cost = 0.0
        self.total_co2 = 0.0
        self.peak_usage = 0.0
        self.average_usage = 0.0
        self.daily_usage = {}
        self.weekly_usage = {}
        self.monthly_usage = {}
        self.total_api_requests = 0
        self.total_tokens = 0
        self.api_cost = 0.0
        
        # Initialize API time-based statistics
        self.api_daily_requests = {}
        self.api_weekly_requests = {}
        self.api_monthly_requests = {}
        
        # Initialize master (lifetime) statistics
        self.master_electric_usage = 0.0
        self.master_cost = 0.0
        self.master_co2 = 0.0
        self.master_api_requests = 0
        self.master_tokens = 0
        self.master_api_cost = 0.0
        
        # Initialize tracking variables
        self._last_power_reading = 0.0
        self._last_api_request_time = None
        self._is_initialized = False
        
        # Get console for logging if available
        self.console = getattr(parent, 'console', None)
        
        # Initialize settings manager and message bus
        self.settings_manager = get_settings()
        self.message_bus = get_message_bus()
        
        # Subscribe to message bus events with high priority
        self.message_bus.subscribe(EVENT_API_REQUEST_STARTED, self.on_api_request_started, priority=1)
        self.message_bus.subscribe(EVENT_API_REQUEST_COMPLETED, self.on_api_request_completed, priority=1)
        self.message_bus.subscribe(EVENT_API_REQUEST_FAILED, self.on_api_request_failed, priority=1)
        self.message_bus.subscribe(EVENT_SYSTEM_READY, self.on_system_ready, priority=2)
        self.message_bus.subscribe(EVENT_SYSTEM_SHUTDOWN, self.on_system_shutdown, priority=2)
        self.message_bus.subscribe(EVENT_POWER_USAGE_UPDATED, self.on_power_updated, priority=1)
        self.message_bus.subscribe(EVENT_ENVIRONMENTAL_IMPACT_UPDATED, self.on_environmental_impact_updated, priority=1)
        
        # Log subscriptions
        if self.console:
            self.console.log("Impact Panel subscribed to message bus events", "INFO")
        else:
            logger.info("Impact Panel subscribed to message bus events")
        
        # Force an initial power data fetch
        self.fetch_power_data()
        
        # Set up UI
        self.setMinimumSize(450, 600)
        self.setMaximumHeight(600)
        self.setStyleSheet("""
            QFrame {
                background-color: black;
                color: white;
                border: 1px solid #333333;
            }
            QLabel {
                color: white;
                font-family: 'Courier New';
                font-size: 12px;
                padding: 2px;
            }
            QGroupBox {
                color: white;
                border: 1px solid #333333;
                border-radius: 0px;
                margin-top: 1.5ex;
                font-family: 'Courier New';
                font-size: 12px;
                font-weight: bold;
                padding: 6px;
                background-color: #0a0a0a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 4px;
                color: white;
                font-family: 'Courier New';
                font-size: 12px;
                font-weight: bold;
                background-color: black;
            }
            QTabWidget::pane {
                border: 1px solid #333333;
                background-color: black;
            }
            QTabBar::tab {
                background-color: #0a0a0a;
                color: white;
                border: 1px solid #333333;
                padding: 8px 12px;
                font-family: 'Courier New';
                font-size: 12px;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #1a1a1a;
            }
            QProgressBar {
                border: 1px solid #333333;
                background-color: #0a0a0a;
                text-align: center;
                color: white;
                height: 14px;
            }
            QProgressBar::chunk {
                background-color: #00aa00;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header_label = QLabel("🌍 Environmental Impact")
        header_label.setStyleSheet(f"{get_font_css(size=14, bold=True)}")
        layout.addWidget(header_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #333333;
                background-color: black;
                padding: 8px;
            }
            QTabBar::tab {
                background-color: #0a0a0a;
                color: white;
                border: 1px solid #333333;
                padding: 8px 12px;
                font-family: 'Courier New';
                font-size: 12px;
                min-width: 80px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1a1a1a;
            }
            QTabBar::tab:hover {
                background-color: #2a2a2a;
            }
        """)
        
        # Energy Usage Tab
        energy_tab = QWidget()
        energy_layout = QVBoxLayout(energy_tab)
        energy_layout.setSpacing(12)  # Increased vertical spacing
        energy_layout.setContentsMargins(8, 8, 8, 8)  # Increased margins
        
        # Component Usage Group - Make more compact
        component_group = QGroupBox("Component Usage")
        component_layout = QGridLayout()
        component_layout.setSpacing(6)  # Increased spacing
        component_layout.setContentsMargins(8, 16, 8, 8)  # Increased margins
        
        # Mac Mini section - Combine labels to save space
        mac_header = QLabel("Mac Mini M4")
        mac_header.setStyleSheet("font-weight: bold;")
        mac_header.setMinimumHeight(24)  # Increased height
        component_layout.addWidget(mac_header, 0, 0, 1, 2)
        
        # Create combined label for CPU, Memory and Power
        self.mac_stats_label = QLabel("CPU: 0% | Memory: 0% | Power: 0.0W")
        self.mac_stats_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.mac_stats_label.setMinimumHeight(24)  # Increased height
        component_layout.addWidget(self.mac_stats_label, 1, 0, 1, 2)
        
        # Punch Card section - Make more compact
        card_header = QLabel("Punch Card Display")
        card_header.setStyleSheet("font-weight: bold;")
        card_header.setMinimumHeight(24)  # Increased height
        component_layout.addWidget(card_header, 2, 0, 1, 2)
        
        self.card_power_label = QLabel("Power Usage: 0.0 W")
        self.card_power_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.card_power_label.setMinimumHeight(24)  # Increased height
        component_layout.addWidget(self.card_power_label, 3, 0, 1, 2)
        
        component_group.setLayout(component_layout)
        
        # Current Usage Group - More compact layout
        current_group = QGroupBox("Current Usage")
        current_layout = QGridLayout()
        current_layout.setSpacing(6)  # Increased spacing
        current_layout.setContentsMargins(8, 16, 8, 8)  # Increased margins
        
        # Total Power - Make more compact
        power_label = QLabel("Total Power:")
        power_label.setFixedWidth(80)  # Fixed width to save space
        power_label.setMinimumHeight(24)  # Increased height
        current_layout.addWidget(power_label, 0, 0)
        
        self.current_power_label = QLabel("0.0 W")
        self.current_power_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.current_power_label.setMinimumHeight(24)  # Increased height
        self.current_power_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        current_layout.addWidget(self.current_power_label, 0, 1)
        
        # CPU Usage with progress bar - Make smaller
        cpu_label = QLabel("CPU Usage:")
        cpu_label.setFixedWidth(80)
        cpu_label.setMinimumHeight(24)  # Increased height
        current_layout.addWidget(cpu_label, 1, 0)
        
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMinimum(0)
        self.cpu_progress.setMaximum(100)
        self.cpu_progress.setValue(0)
        self.cpu_progress.setFixedHeight(24)  # Increased height
        self.cpu_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #333333;
                background-color: #0a0a0a;
                text-align: center;
                color: white;
                font-family: 'Courier New';
                font-size: 10px;
                padding: 2px;
            }
            QProgressBar::chunk {
                background-color: #00aa00;
            }
        """)
        current_layout.addWidget(self.cpu_progress, 1, 1)
        
        # Memory Usage with progress bar - Make smaller
        mem_label = QLabel("Memory:")
        mem_label.setFixedWidth(80)
        mem_label.setMinimumHeight(24)  # Increased height
        current_layout.addWidget(mem_label, 2, 0)
        
        self.memory_progress = QProgressBar()
        self.memory_progress.setMinimum(0)
        self.memory_progress.setMaximum(100)
        self.memory_progress.setValue(0)
        self.memory_progress.setFixedHeight(24)  # Increased height
        self.memory_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #333333;
                background-color: #0a0a0a;
                text-align: center;
                color: white;
                font-family: 'Courier New';
                font-size: 10px;
                padding: 2px;
            }
            QProgressBar::chunk {
                background-color: #00aa00;
            }
        """)
        current_layout.addWidget(self.memory_progress, 2, 1)
        
        current_group.setLayout(current_layout)
        
        # Combine Total Usage and Time Breakdown into one group to save space
        usage_group = QGroupBox("Energy Statistics")
        usage_layout = QGridLayout()
        usage_layout.setSpacing(6)  # Increased spacing
        usage_layout.setContentsMargins(8, 16, 8, 8)  # Increased margins
        
        # Column labels with increased height
        period_label = QLabel("Time Period")
        period_label.setMinimumHeight(24)
        usage_layout.addWidget(period_label, 0, 0)
        
        energy_label = QLabel("Energy")
        energy_label.setMinimumHeight(24)
        usage_layout.addWidget(energy_label, 0, 1)
        
        cost_label = QLabel("Cost")
        cost_label.setMinimumHeight(24)
        usage_layout.addWidget(cost_label, 0, 2)
        
        # Set fixed column widths
        usage_layout.setColumnMinimumWidth(0, 80)
        usage_layout.setColumnMinimumWidth(1, 70)
        usage_layout.setColumnMinimumWidth(2, 70)
        
        # Daily usage row
        daily_label = QLabel("Daily:")
        daily_label.setMinimumHeight(24)
        usage_layout.addWidget(daily_label, 1, 0)
        
        self.daily_usage_label = QLabel("0.01 kWh")
        self.daily_usage_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.daily_usage_label.setMinimumHeight(24)
        usage_layout.addWidget(self.daily_usage_label, 1, 1)
        
        self.daily_cost_label = QLabel("$0.00")
        self.daily_cost_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.daily_cost_label.setMinimumHeight(24)
        usage_layout.addWidget(self.daily_cost_label, 1, 2)
        
        # Weekly usage row
        weekly_label = QLabel("Weekly:")
        weekly_label.setMinimumHeight(24)
        usage_layout.addWidget(weekly_label, 2, 0)
        
        self.weekly_usage_label = QLabel("0.01 kWh")
        self.weekly_usage_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.weekly_usage_label.setMinimumHeight(24)
        usage_layout.addWidget(self.weekly_usage_label, 2, 1)
        
        weekly_cost_label = QLabel("$0.00")
        weekly_cost_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        weekly_cost_label.setMinimumHeight(24)
        usage_layout.addWidget(weekly_cost_label, 2, 2)
        
        # Monthly usage row
        monthly_label = QLabel("Monthly:")
        monthly_label.setMinimumHeight(24)
        usage_layout.addWidget(monthly_label, 3, 0)
        
        self.monthly_usage_label = QLabel("0.01 kWh")
        self.monthly_usage_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.monthly_usage_label.setMinimumHeight(24)
        usage_layout.addWidget(self.monthly_usage_label, 3, 1)
        
        monthly_cost_label = QLabel("$0.00")
        monthly_cost_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        monthly_cost_label.setMinimumHeight(24)
        usage_layout.addWidget(monthly_cost_label, 3, 2)
        
        # Session usage row
        session_label = QLabel("Session:")
        session_label.setMinimumHeight(24)
        usage_layout.addWidget(session_label, 4, 0)
        
        self.session_energy_label = QLabel("0.01 kWh")
        self.session_energy_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.session_energy_label.setMinimumHeight(24)
        usage_layout.addWidget(self.session_energy_label, 4, 1)
        
        self.session_cost_label = QLabel("$0.00")
        self.session_cost_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.session_cost_label.setMinimumHeight(24)
        usage_layout.addWidget(self.session_cost_label, 4, 2)
        
        # Lifetime usage row
        lifetime_label = QLabel("Lifetime:")
        lifetime_label.setMinimumHeight(24)
        lifetime_label.setStyleSheet("font-weight: bold;")
        usage_layout.addWidget(lifetime_label, 5, 0)
        
        self.lifetime_energy_label = QLabel("0.01 kWh")
        self.lifetime_energy_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lifetime_energy_label.setMinimumHeight(24)
        self.lifetime_energy_label.setStyleSheet("font-weight: bold;")
        usage_layout.addWidget(self.lifetime_energy_label, 5, 1)
        
        self.lifetime_cost_label = QLabel("$0.00")
        self.lifetime_cost_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lifetime_cost_label.setMinimumHeight(24)
        self.lifetime_cost_label.setStyleSheet("font-weight: bold;")
        usage_layout.addWidget(self.lifetime_cost_label, 5, 2)
        
        usage_group.setLayout(usage_layout)
        energy_layout.addWidget(usage_group)
        energy_layout.addStretch(1)  # Add stretch to push everything up
        
        # Set the energy tab as the first tab
        self.tab_widget.addTab(energy_tab, "Energy Usage")
        
        # Environmental Impact Tab
        env_tab = QWidget()
        env_layout = QVBoxLayout(env_tab)
        env_layout.setSpacing(12)
        env_layout.setContentsMargins(8, 8, 8, 8)
        
        # Carbon Emissions Group
        carbon_group = QGroupBox("Carbon Emissions")
        carbon_layout = QFormLayout()
        carbon_layout.setSpacing(4)
        carbon_layout.setContentsMargins(8, 10, 8, 8)
        
        self.co2_label = QLabel("0.0 kg")
        self.car_miles_label = QLabel("0.0 mi")
        self.trees_label = QLabel("0")
        
        carbon_layout.addRow("CO2 Emissions:", self.co2_label)
        carbon_layout.addRow("Equivalent Car Miles:", self.car_miles_label)
        carbon_layout.addRow("Trees Needed:", self.trees_label)
        carbon_group.setLayout(carbon_layout)
        env_layout.addWidget(carbon_group)
        
        # Environmental Impact Group
        impact_group = QGroupBox("Environmental Impact")
        impact_layout = QFormLayout()
        impact_layout.setSpacing(4)
        impact_layout.setContentsMargins(8, 10, 8, 8)
        
        self.water_label = QLabel("0.0 L")
        self.land_label = QLabel("0.0 m²")
        self.air_label = QLabel("0.0 µg/m³")
        
        impact_layout.addRow("Water Usage:", self.water_label)
        impact_layout.addRow("Land Impact:", self.land_label)
        impact_layout.addRow("Air Quality Impact:", self.air_label)
        impact_group.setLayout(impact_layout)
        env_layout.addWidget(impact_group)
        
        self.tab_widget.addTab(env_tab, "Environment")
        
        # API Usage Tab
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        api_layout.setSpacing(12)
        api_layout.setContentsMargins(8, 8, 8, 8)
        
        # API Statistics Group
        api_stats_group = QGroupBox("Session Statistics")
        api_stats_layout = QFormLayout()
        api_stats_layout.setSpacing(4)
        api_stats_layout.setContentsMargins(8, 10, 8, 8)
        
        self.total_requests_label = QLabel("0")
        self.total_tokens_label = QLabel("0")
        self.api_cost_label = QLabel("$0.00")
        
        api_stats_layout.addRow("Total Requests:", self.total_requests_label)
        api_stats_layout.addRow("Total Tokens:", self.total_tokens_label)
        api_stats_layout.addRow("API Cost:", self.api_cost_label)
        api_stats_group.setLayout(api_stats_layout)
        api_layout.addWidget(api_stats_group)
        
        # Lifetime API Statistics Group
        api_lifetime_group = QGroupBox("Lifetime Statistics")
        api_lifetime_layout = QFormLayout()
        api_lifetime_layout.setSpacing(4)
        api_lifetime_layout.setContentsMargins(8, 10, 8, 8)
        
        self.master_requests_label = QLabel("0")
        self.master_tokens_label = QLabel("0")
        self.master_api_cost_label = QLabel("$0.00")
        
        # Make lifetime stats bold to match energy tab
        self.master_requests_label.setStyleSheet("font-weight: bold;")
        self.master_tokens_label.setStyleSheet("font-weight: bold;")
        self.master_api_cost_label.setStyleSheet("font-weight: bold;")
        
        api_lifetime_layout.addRow("Total Requests:", self.master_requests_label)
        api_lifetime_layout.addRow("Total Tokens:", self.master_tokens_label)
        api_lifetime_layout.addRow("API Cost:", self.master_api_cost_label)
        api_lifetime_group.setLayout(api_lifetime_layout)
        api_layout.addWidget(api_lifetime_group)
        
        # API Time Breakdown Group
        api_time_group = QGroupBox("Time Breakdown")
        api_time_layout = QFormLayout()
        api_time_layout.setSpacing(4)
        api_time_layout.setContentsMargins(8, 10, 8, 8)
        
        self.api_daily_label = QLabel("0")
        self.api_weekly_label = QLabel("0")
        self.api_monthly_label = QLabel("0")
        
        api_time_layout.addRow("Daily Requests:", self.api_daily_label)
        api_time_layout.addRow("Weekly Requests:", self.api_weekly_label)
        api_time_layout.addRow("Monthly Requests:", self.api_monthly_label)
        api_time_group.setLayout(api_time_layout)
        api_layout.addWidget(api_time_group)
        
        self.tab_widget.addTab(api_tab, "API")
        
        layout.addWidget(self.tab_widget)
        
        # Reset button
        reset_button = RetroButton("Reset Statistics")
        reset_button.clicked.connect(self.reset_statistics)
        
        # Create a button layout like in stats panel
        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)
        button_layout.addWidget(reset_button)
        button_layout.addStretch()
        
        # Add close button
        self.close_btn = RetroButton("Close")
        self.close_btn.clicked.connect(self.hide)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # Set up timer for periodic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_and_save_statistics)
        self.update_timer.start(60000)  # Update every minute
        
        # Set up timer to update current power usage more frequently
        self.power_timer = QTimer()
        self.power_timer.timeout.connect(self.fetch_power_data)
        self.power_timer.start(5000)  # Update every 5 seconds instead of every second
        
        # Add throttling variables
        self._last_power_update = datetime.now()
        self._last_env_update = datetime.now()
        self._power_update_threshold = 2.0  # Only update if power changes by 2W
        self._last_power_values = {
            'mac_power': 0,
            'card_power': 0,
            'total_power': 0,
            'cpu_percent': 0,
            'memory_percent': 0
        }
        
        # Load initial statistics
        self.load_statistics()
    
    def get_mac_power_usage(self):
        """Get current Mac Mini power usage based on CPU and memory usage."""
        try:
            # Get CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            
            # Calculate power usage based on usage levels
            if cpu_percent < 20:
                power = COMPONENT_POWER['mac_mini']['idle']
            elif cpu_percent < 80:
                power = COMPONENT_POWER['mac_mini']['active']
            else:
                power = COMPONENT_POWER['mac_mini']['max']
            
            # Adjust power based on memory usage
            power *= (1 + (memory_percent / 100))
            
            return power, cpu_percent, memory_percent
            
        except Exception as e:
            if hasattr(self, 'console') and self.console:
                self.console.log(f"Error getting Mac power usage: {str(e)}", "ERROR")
            else:
                print(f"Error getting Mac power usage: {str(e)}")
            return COMPONENT_POWER['mac_mini']['idle'], 0, 0
    
    def get_punch_card_power(self):
        """Get current punch card power usage."""
        try:
            # For now, use a simple estimate based on whether the display is active
            # In a real implementation, this would read from the actual hardware
            if hasattr(self.parent(), 'punch_card') and self.parent().punch_card.isVisible():
                return COMPONENT_POWER['punch_card']['active']
            return COMPONENT_POWER['punch_card']['idle']
        except Exception as e:
            if hasattr(self, 'console') and self.console:
                self.console.log(f"Error getting punch card power: {str(e)}", "ERROR")
            else:
                print(f"Error getting punch card power: {str(e)}")
            return COMPONENT_POWER['punch_card']['idle']
    
    def fetch_power_data(self):
        """Fetch current power data and publish to message bus."""
        try:
            # Get current date and time for timestamps
            current_time = datetime.now()
            
            # Check if we've already initialized power tracking
            if not hasattr(self, '_last_power_update'):
                self._last_power_update = current_time - timedelta(seconds=10)
                self._last_env_update = current_time - timedelta(seconds=10)
                self._last_power_reading = 0.0
                self._last_power_values = {}
            
            # Calculate time since last update
            time_since_update = (current_time - self._last_power_update).total_seconds()
            
            # Get computer power usage
            mac_power = self.get_mac_power_usage()
            
            # Get punch card power usage  
            card_power = self.get_punch_card_power()
            
            # Calculate total power
            total_power = mac_power + card_power
            
            # Get CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=None)
            memory_percent = psutil.virtual_memory().percent
            
            # Check if power changed significantly (>1W) or enough time has passed
            power_changed = not hasattr(self, '_last_power_values') or \
                            abs(total_power - self._last_power_values.get('total_power', 0)) > 1.0 or \
                            abs(cpu_percent - self._last_power_values.get('cpu_percent', 0)) > 5.0
            
            if power_changed or time_since_update >= 5:
                # Update last values
                self._last_power_values = {
                    'mac_power': mac_power,
                    'card_power': card_power,
                    'total_power': total_power,
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent
                }
                
                # Publish power usage data to message bus
                self.message_bus.publish(EVENT_POWER_USAGE_UPDATED, {
                    "mac_power": mac_power,
                    "card_power": card_power,
                    "total_power": total_power,
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "timestamp": current_time.isoformat()
                })
                
                self._last_power_update = current_time
                
                # Publish environmental impact more frequently - every 5 seconds instead of 10
                # and use a smaller threshold for power changes
                if abs(total_power - self._last_power_reading) > 1.0:  # 1W threshold instead of 2W
                    time_since_env_update = (current_time - self._last_env_update).total_seconds()
                    if time_since_env_update >= 5:  # Every 5 seconds instead of 10
                        # Calculate multipliers to make environmental impact more visible
                        visibility_multiplier = 5.0  # Make environmental impact 5x more visible
                        
                        self.message_bus.publish(EVENT_ENVIRONMENTAL_IMPACT_UPDATED, {
                            "co2": self.total_co2 * visibility_multiplier,
                            "car_miles": self.total_co2 * 2.5 * visibility_multiplier,
                            "trees_needed": max(1, int(self.total_co2 * visibility_multiplier / 22)),
                            "water_usage": self.total_electric_usage * 100 * visibility_multiplier,
                            "land_impact": self.total_electric_usage * 0.01 * visibility_multiplier,
                            "timestamp": current_time.isoformat()
                        })
                        
                        if self.console:
                            self.console.log(f"DEBUG: Published environmental impact update with visibility multiplier {visibility_multiplier}x", "DEBUG")
                        
                        self._last_env_update = current_time
                
                self._last_power_reading = total_power
                
                # Log successful update if console available
                if self.console:
                    self.console.log(f"Power data updated - Total: {total_power:.1f}W", "DEBUG")
            
        except Exception as e:
            if self.console:
                self.console.log(f"Error fetching power data: {str(e)}", "ERROR")
            else:
                print(f"Error fetching power data: {str(e)}")
    
    def on_power_updated(self, message):
        """Handle power usage update events from the message bus."""
        try:
            if message and hasattr(message, 'data'):
                self.update_current_power(message.data)
                
                # Save data to settings at regular intervals (every 10th update)
                if not hasattr(self, '_power_update_counter'):
                    self._power_update_counter = 0
                self._power_update_counter += 1
                
                # Save stats every 10 updates to avoid too many writes
                if self._power_update_counter % 10 == 0:
                    self.save_statistics()
                    if self.console:
                        self.console.log("Saving impact statistics to settings", "DEBUG")
                        
                # Log successful update
                if self.console:
                    self.console.log(f"Power update received - Total: {message.data.get('total_power', 0):.1f}W", "DEBUG")
        except Exception as e:
            if self.console:
                self.console.log(f"Error in power update handler: {str(e)}", "ERROR")
            else:
                logger.error(f"Error in power update handler: {str(e)}")
    
    def update_current_power(self, data):
        """Update the current power display and CPU/memory usage."""
        try:
            mac_power = data.get('mac_power', 0)
            card_power = data.get('card_power', 0)
            total_power = data.get('total_power', 0)
            cpu_percent = data.get('cpu_percent', 0)
            memory_percent = data.get('memory_percent', 0)
            
            # Format values to one decimal place
            mac_power_formatted = f"{mac_power:.1f}"
            card_power_formatted = f"{card_power:.1f}"
            total_power_formatted = f"{total_power:.1f}"
            cpu_percent_formatted = f"{cpu_percent:.1f}"
            memory_percent_formatted = f"{memory_percent:.1f}"
            
            # Update the combined Mac stats label
            self.mac_stats_label.setText(f"CPU: {cpu_percent_formatted}% | Mem: {memory_percent_formatted}% | Power: {mac_power_formatted}W")
            
            # Update individual labels
            self.card_power_label.setText(f"Power Usage: {card_power_formatted} W")
            self.current_power_label.setText(f"{total_power_formatted} W")
            
            # Update progress bars
            self.cpu_progress.setValue(int(cpu_percent))
            self.cpu_progress.setFormat(f"{cpu_percent_formatted}%")
            
            self.memory_progress.setValue(int(memory_percent))
            self.memory_progress.setFormat(f"{memory_percent_formatted}%")
            
            # Update peak usage if current is higher
            if total_power > self.peak_usage:
                self.peak_usage = total_power
                self.settings_manager.set_setting("peak_usage", total_power)
            
            # Update average usage
            self.average_usage = ((self.average_usage * 59) + total_power) / 60
            self.settings_manager.set_setting("average_usage", self.average_usage)
            
            # Store last power reading
            self._last_power_reading = total_power
            
            # Calculate and update power usage stats periodically
            # MODIFIED: EXTREMELY aggressive accumulation for clear visibility
            current_kwh = (total_power / 1000) * (1.0/0.1)  # 600x faster accumulation (was 1/60, now 1/0.1)
            
            if self.console:
                self.console.log(f"DEBUG: Adding {current_kwh:.8f} kWh to energy usage (600x accelerated)", "DEBUG")
            
            # Store previous values for comparison
            prev_total = self.total_electric_usage
            prev_master = self.master_electric_usage
            
            # Update energy usage statistics
            self.total_electric_usage += current_kwh
            self.total_cost = self.total_electric_usage * COST_PER_KWH
            self.total_co2 = self.total_electric_usage * CARBON_INTENSITY
            
            # Update master (lifetime) statistics
            self.master_electric_usage += current_kwh
            self.master_cost = self.master_electric_usage * COST_PER_KWH
            self.master_co2 = self.master_electric_usage * CARBON_INTENSITY
            
            # Log the change for verification
            if self.console:
                self.console.log(f"VERIFICATION: Energy before: {prev_total:.6f} kWh, after: {self.total_electric_usage:.6f} kWh", "DEBUG")
                self.console.log(f"VERIFICATION: Master energy before: {prev_master:.6f} kWh, after: {self.master_electric_usage:.6f} kWh", "DEBUG")

            # Update time-based statistics
            today = datetime.now().strftime("%Y-%m-%d")
            current_week = datetime.now().strftime("%Y-W%W")
            current_month = datetime.now().strftime("%Y-%m")
            
            self.daily_usage[today] = self.daily_usage.get(today, 0.0) + current_kwh
            self.weekly_usage[current_week] = self.weekly_usage.get(current_week, 0.0) + current_kwh
            self.monthly_usage[current_month] = self.monthly_usage.get(current_month, 0.0) + current_kwh
            
            # Update energy usage labels immediately for visual feedback with more precision
            self.session_energy_label.setText(f"{self.total_electric_usage:.6f} kWh")
            self.lifetime_energy_label.setText(f"{self.master_electric_usage:.6f} kWh")
            self.daily_usage_label.setText(f"{self.daily_usage[today]:.6f} kWh")
            
            # Save statistics immediately to prevent loss on manual reload
            self.save_statistics()
            
            # Also publish the updated energy values to the message bus for other components
            if hasattr(self, 'message_bus'):
                self.message_bus.publish('stats.energy.updated', {
                    'session_energy': self.total_electric_usage,
                    'master_energy': self.master_electric_usage,
                    'timestamp': datetime.now().isoformat()
                }, source='ImpactPanel')
            
            # If we made it here without errors, the update was successful
            if self.console:
                self.console.log(f"Updated power data: {total_power_formatted}W (CPU: {cpu_percent_formatted}%, Mem: {memory_percent_formatted}%)", "DEBUG")
                self.console.log(f"Current energy totals - Session: {self.total_electric_usage:.6f} kWh, Lifetime: {self.master_electric_usage:.6f} kWh", "DEBUG")
                
        except Exception as e:
            if self.console:
                self.console.log(f"Error updating current power: {str(e)}", "ERROR")
            else:
                logger.error(f"Error updating current power: {str(e)}")
    
    def update_statistics(self):
        """Update the UI with current statistics."""
        try:
            # Log for debugging
            if hasattr(self, 'console') and self.console:
                self.console.log("DEBUG: update_statistics called - updating UI with current statistics", "DEBUG")

            # Update electric usage statistics
            self.total_electric_usage = self.settings_manager.get_setting('total_electric_usage', 0.0)
            self.total_cost = self.settings_manager.get_setting('total_cost', 0.0)
            self.total_co2 = self.settings_manager.get_setting('total_co2', 0.0)
            self.peak_usage = self.settings_manager.get_setting('peak_usage', 0.0)
            self.average_usage = self.settings_manager.get_setting('average_usage', 0.0)
            
            # Update master statistics
            self.master_electric_usage = self.settings_manager.get_setting('master_electric_usage', 0.0)
            self.master_cost = self.settings_manager.get_setting('master_cost', 0.0)
            self.master_co2 = self.settings_manager.get_setting('master_co2', 0.0)
            self.master_api_requests = self.settings_manager.get_setting('master_api_requests', 0)
            self.master_tokens = self.settings_manager.get_setting('master_tokens', 0)
            self.master_api_cost = self.settings_manager.get_setting('master_api_cost', 0.0)
            
            # Debug master stats loaded from settings
            if hasattr(self, 'console') and self.console:
                self.console.log(f"DEBUG: update_statistics refreshed - Master electric: {self.master_electric_usage:.6f} kWh, CO2: {self.master_co2:.6f} kg", "DEBUG")
                self.console.log(f"DEBUG: update_statistics refreshed - Master API: {self.master_api_requests} requests, {self.master_tokens} tokens", "DEBUG")

            # Update time-based statistics
            self.daily_usage = self.settings_manager.get_setting('daily_usage', {})
            self.weekly_usage = self.settings_manager.get_setting('weekly_usage', {})
            self.monthly_usage = self.settings_manager.get_setting('monthly_usage', {})
            
            # Update API usage statistics
            self.total_api_requests = self.settings_manager.get_setting('total_api_requests', 0)
            self.total_tokens = self.settings_manager.get_setting('total_tokens', 0)
            self.api_cost = self.settings_manager.get_setting('api_cost', 0.0)
            
            # Debug session stats loaded from settings
            if hasattr(self, 'console') and self.console:
                self.console.log(f"DEBUG: update_statistics refreshed - Session electric: {self.total_electric_usage:.6f} kWh, CO2: {self.total_co2:.6f} kg", "DEBUG")
                self.console.log(f"DEBUG: update_statistics refreshed - Session API: {self.total_api_requests} requests, {self.total_tokens} tokens", "DEBUG")
            
            # Update Energy Statistics panel
            today = datetime.now().strftime("%Y-%m-%d")
            current_week = datetime.now().strftime("%Y-W%W")
            current_month = datetime.now().strftime("%Y-%m")
            
            # Get today's usage or default to 0
            today_usage = self.daily_usage.get(today, 0.0)
            
            # Get this week's usage or default to 0
            week_usage = self.weekly_usage.get(current_week, 0.0)
            
            # Get this month's usage or default to 0
            month_usage = self.monthly_usage.get(current_month, 0.0)
            
            # Scale power to kWh
            scaled_power = self.total_electric_usage
            
            # Update energy usage labels with increased precision
            if hasattr(self, 'console') and self.console:
                self.console.log(f"DEBUG: Setting energy usage labels - Session: {scaled_power:.6f} kWh, Lifetime: {self.master_electric_usage:.6f} kWh", "DEBUG")
                self.console.log(f"DEBUG: Setting time-based usage labels - Today: {today_usage:.6f} kWh, Week: {week_usage:.6f} kWh, Month: {month_usage:.6f} kWh", "DEBUG")
            
            self.session_energy_label.setText(f"{scaled_power:.6f} kWh")
            self.lifetime_energy_label.setText(f"{self.master_electric_usage:.6f} kWh")
            
            # Time-based usage labels with increased precision
            self.daily_usage_label.setText(f"{today_usage:.6f} kWh")
            self.weekly_usage_label.setText(f"{week_usage:.6f} kWh")
            self.monthly_usage_label.setText(f"{month_usage:.6f} kWh")
            
            # Update cost labels with increased precision
            self.session_cost_label.setText(f"${self.total_cost:.6f}")
            self.lifetime_cost_label.setText(f"${self.master_cost:.6f}")
            self.daily_cost_label.setText(f"${today_usage * COST_PER_KWH:.6f}")
            
            # Calculate environmental impact
            # These are estimated values based on power usage
            co2_per_kwh = 0.5 # kg CO2 per kWh (approximate)
            miles_per_kg_co2 = 2.5 # miles per kg CO2 (approximate)
            trees_per_kg_co2 = 0.025 # trees needed to offset 1 kg CO2 (approximate) 
            liters_per_kwh = 250 # liters of water per kWh (approximate)
            land_impact_per_kwh = 0.025 # square meters per kWh (approximate)
            air_quality_per_kwh = 5 # µg/m³ particulate matter per kWh (approximate)
            
            # Calculate impact estimates
            co2_emissions = self.total_co2 
            car_miles = co2_emissions * miles_per_kg_co2
            trees_needed = max(1, int(co2_emissions * trees_per_kg_co2))
            water_usage = self.total_electric_usage * liters_per_kwh
            land_impact = self.total_electric_usage * land_impact_per_kwh
            air_quality = self.total_electric_usage * air_quality_per_kwh
            
            # Update environmental impact labels
            self.co2_label.setText(f"{co2_emissions:.6f} kg")
            self.car_miles_label.setText(f"{car_miles:.6f} mi")
            self.trees_label.setText(f"{trees_needed}")
            self.water_label.setText(f"{water_usage:.6f} L")
            self.land_label.setText(f"{land_impact:.6f} m²")
            self.air_label.setText(f"{air_quality:.6f} µg/m³")
            
            # Update API usage labels
            self.total_requests_label.setText(f"{self.total_api_requests:,}")
            self.total_tokens_label.setText(f"{self.total_tokens:,}")
            self.api_cost_label.setText(f"${self.api_cost:.6f}")
            
            # Also update the current values
            self.current_power_label.setText(f"{self._last_power_reading:.1f} W")
            
            # Debug updated UI values
            if hasattr(self, 'console') and self.console:
                self.console.log(f"DEBUG: UI updated - Electric Usage: {self.total_electric_usage:.6f} kWh, CO2: {self.total_co2:.6f} kg", "DEBUG")
                self.console.log(f"DEBUG: UI updated - API Requests: {self.total_api_requests}, Cost: ${self.api_cost:.6f}", "DEBUG")
            
        except Exception as e:
            if hasattr(self, 'console') and self.console:
                self.console.log(f"Error updating statistics: {str(e)}", "ERROR")
            else:
                print(f"Error updating statistics: {str(e)}")
            # Don't re-raise the exception as this is a UI update
    
    def load_statistics(self):
        """Load statistics from settings."""
        try:
            # Add a log message to show this method is being called
            if self.console:
                self.console.log("Loading impact panel statistics from settings", "INFO")
                self.console.log("DEBUG: Beginning to load statistics", "DEBUG")
            
            # IMPORTANT: Load API statistics first to prevent overwriting
            loaded_api_requests = int(self.settings_manager.get_setting('total_api_requests', 0))
            loaded_tokens = int(self.settings_manager.get_setting('total_tokens', 0))
            loaded_api_cost = float(self.settings_manager.get_setting('api_cost', 0.0))
            
            # Get master statistics for API
            master_api_requests = int(self.settings_manager.get_setting('master_api_requests', 0))
            master_tokens = int(self.settings_manager.get_setting('master_tokens', 0))
            master_api_cost = float(self.settings_manager.get_setting('master_api_cost', 0.0))
            
            # Log the API stats being loaded
            if self.console:
                self.console.log(f"DEBUG: Raw loaded API stats - Requests: {loaded_api_requests}, Master: {master_api_requests}", "DEBUG")
                self.console.log(f"DEBUG: Raw loaded API tokens - Tokens: {loaded_tokens}, Master: {master_tokens}", "DEBUG")
                self.console.log(f"DEBUG: Raw loaded API cost - Cost: ${loaded_api_cost:.6f}, Master: ${master_api_cost:.6f}", "DEBUG")
            
            # Load master (lifetime) statistics for energy
            self.master_electric_usage = float(self.settings_manager.get_setting('master_electric_usage', 0.0))
            self.master_cost = float(self.settings_manager.get_setting('master_cost', 0.0))
            self.master_co2 = float(self.settings_manager.get_setting('master_co2', 0.0))
            
            # Now set API statistics, using maximum values to ensure we don't lose data
            self.master_api_requests = master_api_requests
            self.master_tokens = master_tokens  
            self.master_api_cost = master_api_cost
            
            # Ensure session values are at least equal to master values to avoid loss
            self.total_api_requests = max(loaded_api_requests, self.master_api_requests)
            self.total_tokens = max(loaded_tokens, self.master_tokens)
            self.api_cost = max(loaded_api_cost, self.master_api_cost)
            
            if self.console:
                self.console.log(f"DEBUG: Final API stats after loading - Session: {self.total_api_requests}, Master: {self.master_api_requests}", "DEBUG")
            
            # Load session statistics
            self.total_electric_usage = float(self.settings_manager.get_setting('total_electric_usage', 0.0))
            self.total_cost = float(self.settings_manager.get_setting('total_cost', 0.0))
            self.total_co2 = float(self.settings_manager.get_setting('total_co2', 0.0))
            self.peak_usage = float(self.settings_manager.get_setting('peak_usage', 0.0))
            self.average_usage = float(self.settings_manager.get_setting('average_usage', 0.0))
            
            if self.console:
                self.console.log(f"DEBUG: Loaded master stats - Electric: {self.master_electric_usage:.6f} kWh, Cost: ${self.master_cost:.6f}, CO2: {self.master_co2:.6f} kg", "DEBUG")
                self.console.log(f"DEBUG: Loaded master API stats - Requests: {self.master_api_requests}, Tokens: {self.master_tokens}, Cost: ${self.master_api_cost:.6f}", "DEBUG")
                self.console.log(f"DEBUG: Loaded session stats - Electric: {self.total_electric_usage:.6f} kWh, Cost: ${self.total_cost:.6f}, CO2: {self.total_co2:.6f} kg", "DEBUG")
                self.console.log(f"DEBUG: Loaded session API stats - Requests: {self.total_api_requests}, Tokens: {self.total_tokens}, Cost: ${self.api_cost:.6f}", "DEBUG")
            
            # Load time-based statistics - ensure dictionaries are properly loaded
            daily_usage = self.settings_manager.get_setting('daily_usage', {})
            weekly_usage = self.settings_manager.get_setting('weekly_usage', {})
            monthly_usage = self.settings_manager.get_setting('monthly_usage', {})
            
            # Convert string keys back to proper types if needed
            self.daily_usage = {k: float(v) for k, v in daily_usage.items()}
            self.weekly_usage = {k: float(v) for k, v in weekly_usage.items()}
            self.monthly_usage = {k: float(v) for k, v in monthly_usage.items()}
            
            # Load API time-based statistics
            api_daily_requests = self.settings_manager.get_setting('api_daily_requests', {})
            api_weekly_requests = self.settings_manager.get_setting('api_weekly_requests', {})
            api_monthly_requests = self.settings_manager.get_setting('api_monthly_requests', {})
            
            # Convert string keys back to proper types if needed
            self.api_daily_requests = {k: int(v) for k, v in api_daily_requests.items()}
            self.api_weekly_requests = {k: int(v) for k, v in api_weekly_requests.items()}
            self.api_monthly_requests = {k: int(v) for k, v in api_monthly_requests.items()}
            
            # Update UI with loaded statistics
            self.update_statistics()
            self.update_api_statistics()
            
            # Force an immediate save to ensure format is consistent and to verify our values are preserved
            self.save_statistics()
            
            # Verify statistics were properly saved by reading them back
            verification_api_requests = self.settings_manager.get_setting('total_api_requests', 0)
            if self.console:
                self.console.log(f"VERIFICATION: After save - API requests: {verification_api_requests}, Master: {self.master_api_requests}", "INFO")
                self.console.log(f"Statistics loaded and saved - Energy: {self.total_electric_usage:.6f} kWh, API Requests: {self.total_api_requests}", "INFO")
            
            # Mark as initialized
            self._is_initialized = True
            
            # Report on message bus about statistics loaded
            if hasattr(self, 'message_bus'):
                try:
                    self.message_bus.publish('stats.loaded', {
                        'api_requests': self.total_api_requests,
                        'master_api_requests': self.master_api_requests,
                        'electric_usage': self.total_electric_usage,
                        'timestamp': datetime.now().isoformat()
                    }, source='ImpactPanel')
                    if self.console:
                        self.console.log("Published stats.loaded event to message bus", "DEBUG")
                except Exception as bus_error:
                    if self.console:
                        self.console.log(f"Failed to publish stats.loaded event: {str(bus_error)}", "ERROR")
            
        except Exception as e:
            if self.console:
                self.console.log(f"Error loading impact panel statistics: {str(e)}", "ERROR")
            else:
                logger.error(f"Error loading statistics: {str(e)}")
            # Initialize with default values if loading fails
            self.reset_statistics()
    
    def save_statistics(self):
        """Save current statistics to settings."""
        try:
            if self.console and hasattr(self, '_is_initialized') and self._is_initialized:
                self.console.log("DEBUG: Beginning to save statistics", "DEBUG")
                self.console.log(f"DEBUG: Saving session stats - Electric: {self.total_electric_usage:.6f} kWh, Cost: ${self.total_cost:.6f}, CO2: {self.total_co2:.6f} kg", "DEBUG")
                self.console.log(f"DEBUG: Saving API stats - Requests: {self.total_api_requests}, Tokens: {self.total_tokens}, Cost: ${self.api_cost:.6f}", "DEBUG")
                self.console.log(f"DEBUG: Saving master API stats - Requests: {self.master_api_requests}, Tokens: {self.master_tokens}", "DEBUG")
            
            # CRITICAL: Ensure master stats are at least equal to session stats to prevent data loss
            self.master_api_requests = max(self.master_api_requests, self.total_api_requests)
            self.master_tokens = max(self.master_tokens, self.total_tokens)
            self.master_api_cost = max(self.master_api_cost, self.api_cost)
            
            # Save API statistics FIRST to ensure they're not lost
            self.settings_manager.set_setting('total_api_requests', self.total_api_requests)
            self.settings_manager.set_setting('total_tokens', self.total_tokens)
            self.settings_manager.set_setting('api_cost', self.api_cost)
            
            # Save master API statistics NEXT
            self.settings_manager.set_setting('master_api_requests', self.master_api_requests)
            self.settings_manager.set_setting('master_tokens', self.master_tokens)
            self.settings_manager.set_setting('master_api_cost', self.master_api_cost)
            
            # Save API time-based statistics
            self.settings_manager.set_setting('api_daily_requests', self.api_daily_requests)
            self.settings_manager.set_setting('api_weekly_requests', self.api_weekly_requests)
            self.settings_manager.set_setting('api_monthly_requests', self.api_monthly_requests)
            
            # Save session statistics
            self.settings_manager.set_setting('total_electric_usage', self.total_electric_usage)
            self.settings_manager.set_setting('total_cost', self.total_cost)
            self.settings_manager.set_setting('total_co2', self.total_co2)
            self.settings_manager.set_setting('peak_usage', self.peak_usage)
            self.settings_manager.set_setting('average_usage', self.average_usage)
            
            # Save time-based statistics
            self.settings_manager.set_setting('daily_usage', self.daily_usage)
            self.settings_manager.set_setting('weekly_usage', self.weekly_usage)
            self.settings_manager.set_setting('monthly_usage', self.monthly_usage)
            
            # Save master energy statistics
            self.settings_manager.set_setting('master_electric_usage', self.master_electric_usage)
            self.settings_manager.set_setting('master_cost', self.master_cost)
            self.settings_manager.set_setting('master_co2', self.master_co2)
            
            # Make sure the settings are immediately written to disk
            if hasattr(self.settings_manager, 'save_settings'):
                self.settings_manager.save_settings()
            
            # Verify stats were saved correctly
            verification_api_requests = self.settings_manager.get_setting('total_api_requests', 0)
            if verification_api_requests != self.total_api_requests:
                if self.console:
                    self.console.log(f"WARNING: API requests not saved correctly. Expected {self.total_api_requests}, got {verification_api_requests}", "WARNING")
            
            if self.console and hasattr(self, '_is_initialized') and self._is_initialized:
                self.console.log("Impact panel statistics saved to settings", "DEBUG")
                
            # Report on message bus about statistics saved
            if hasattr(self, 'message_bus'):
                try:
                    self.message_bus.publish('stats.saved', {
                        'api_requests': self.total_api_requests,
                        'master_api_requests': self.master_api_requests,
                        'electric_usage': self.total_electric_usage,
                        'timestamp': datetime.now().isoformat()
                    }, source='ImpactPanel')
                    if self.console:
                        self.console.log("Published stats.saved event to message bus", "DEBUG")
                except Exception as bus_error:
                    if self.console:
                        self.console.log(f"Failed to publish stats.saved event: {str(bus_error)}", "ERROR")
                
        except Exception as e:
            if self.console:
                self.console.log(f"Error saving impact panel statistics: {str(e)}", "ERROR")
            else:
                logger.error(f"Error saving statistics: {str(e)}")
    
    def reset_statistics(self):
        """Reset session statistics to zero."""
        try:
            # Reset session statistics
            self.total_electric_usage = 0.0
            self.total_cost = 0.0
            self.total_co2 = 0.0
            self.peak_usage = 0.0
            self.average_usage = 0.0
            
            # Reset time-based statistics
            self.daily_usage = {}
            self.weekly_usage = {}
            self.monthly_usage = {}
            
            # Reset API usage statistics
            self.total_api_requests = 0
            self.total_tokens = 0
            self.api_cost = 0.0
            self.api_daily_requests = {}
            self.api_weekly_requests = {}
            self.api_monthly_requests = {}
            
            # Save reset values to settings
            self.save_statistics()
            
            # Update UI
            self.update_statistics()
            self.update_api_statistics()
            
            if self.console:
                self.console.log("Statistics reset to default values", "INFO")
            
        except Exception as e:
            if self.console:
                self.console.log(f"Error resetting statistics: {str(e)}", "ERROR")
            else:
                logger.error(f"Error resetting statistics: {str(e)}")
    
    def paintEvent(self, event):
        """Custom paint event to draw an angular border."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw border
        painter.setPen(QPen(QColor(COLORS['hole_outline']), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
    
    def update_and_save_statistics(self):
        """Update and save statistics to settings."""
        try:
            # First update statistics
            self.update_statistics()
            
            # Then save to settings
            self.save_statistics()
            
            # Also update API statistics
            self.update_api_statistics()
            
            if self.console:
                self.console.log("Impact panel statistics updated and saved", "DEBUG")
            
        except Exception as e:
            if self.console:
                self.console.log(f"Error updating and saving statistics: {str(e)}", "ERROR")
            else:
                logger.error(f"Error updating and saving statistics: {str(e)}")
    
    def update_api_statistics(self):
        """Update the API statistics display with current data."""
        try:
            # Log for debugging
            if hasattr(self, 'console') and self.console:
                self.console.log(f"DEBUG: update_api_statistics called - API requests: {self.total_api_requests}, tokens: {self.total_tokens}", "DEBUG")
            
            # Get current date/time values
            today = datetime.now().strftime("%Y-%m-%d")
            current_week = datetime.now().strftime("%Y-W%W")
            current_month = datetime.now().strftime("%Y-%m")
            
            # Update API usage counts
            self.api_daily_label.setText(f"{self.api_daily_requests.get(today, 0):,}")
            self.api_weekly_label.setText(f"{self.api_weekly_requests.get(current_week, 0):,}")
            self.api_monthly_label.setText(f"{self.api_monthly_requests.get(current_month, 0):,}")
            
            # Update session API requests and cost with increased precision
            self.total_requests_label.setText(f"{self.total_api_requests:,}")
            self.total_tokens_label.setText(f"{self.total_tokens:,}")
            self.api_cost_label.setText(f"${self.api_cost:.6f}")
            
            # Update lifetime API statistics with increased precision
            if hasattr(self, 'master_requests_label'):
                self.master_requests_label.setText(f"{self.master_api_requests:,}")
            if hasattr(self, 'master_tokens_label'):
                self.master_tokens_label.setText(f"{self.master_tokens:,}")
            if hasattr(self, 'master_api_cost_label'):
                self.master_api_cost_label.setText(f"${self.master_api_cost:.6f}")
            
            # Debug updated UI values
            if hasattr(self, 'console') and self.console:
                self.console.log(f"DEBUG: API UI updated - Daily: {self.api_daily_requests.get(today, 0)}, Weekly: {self.api_weekly_requests.get(current_week, 0)}, Monthly: {self.api_monthly_requests.get(current_month, 0)}", "DEBUG")
                self.console.log(f"DEBUG: API UI updated - Session: {self.total_api_requests} requests, Lifetime: {self.master_api_requests} requests", "DEBUG")
                
            # Ensure the API stats are saved after updating the UI
            self.settings_manager.set_setting('total_api_requests', self.total_api_requests)
            self.settings_manager.set_setting('master_api_requests', self.master_api_requests)
            self.settings_manager.set_setting('total_tokens', self.total_tokens)
            self.settings_manager.set_setting('master_tokens', self.master_tokens)
            self.settings_manager.set_setting('api_cost', self.api_cost)
            self.settings_manager.set_setting('master_api_cost', self.master_api_cost)
                
        except Exception as e:
            if self.console:
                self.console.log(f"Error updating API statistics: {str(e)}", "ERROR")
            else:
                logger.error(f"Error updating API statistics: {str(e)}")

    def on_api_request_started(self, message):
        """Handle API request started event."""
        try:
            # Set last request time
            self._last_api_request_time = datetime.now()
            
            # Update request count
            self.total_api_requests += 1
            self.master_api_requests += 1
            
            # Update time-based statistics
            today = datetime.now().strftime("%Y-%m-%d")
            current_week = datetime.now().strftime("%Y-W%W")
            current_month = datetime.now().strftime("%Y-%m")
            
            # Update daily/weekly/monthly counts
            self.api_daily_requests[today] = self.api_daily_requests.get(today, 0) + 1
            self.api_weekly_requests[current_week] = self.api_weekly_requests.get(current_week, 0) + 1
            self.api_monthly_requests[current_month] = self.api_monthly_requests.get(current_month, 0) + 1
            
            # Save to settings
            self.settings_manager.set_setting('total_api_requests', self.total_api_requests)
            self.settings_manager.set_setting('master_api_requests', self.master_api_requests)
            self.settings_manager.set_setting('api_daily_requests', self.api_daily_requests)
            self.settings_manager.set_setting('api_weekly_requests', self.api_weekly_requests)
            self.settings_manager.set_setting('api_monthly_requests', self.api_monthly_requests)
            
            # Update the API statistics display
            self.update_api_statistics()
            
            if self.console:
                self.console.log(f"API request started - Total requests: {self.total_api_requests}", "INFO")
            
        except Exception as e:
            if self.console:
                self.console.log(f"Error handling API request start: {str(e)}", "ERROR")
            else:
                logger.error(f"Error handling API request start: {str(e)}")
    
    def on_api_request_completed(self, message):
        """Handle API request completed event."""
        try:
            if hasattr(message, 'data'):
                # Extract data from message
                data = message.data
                tokens = data.get('tokens', 0)
                cost = data.get('cost', 0.0)
                
                # Log the raw data
                if self.console:
                    self.console.log(f"DEBUG: API request completed with {tokens} tokens, ${cost:.6f} cost", "DEBUG")
                    self.console.log(f"DEBUG: Before update - Total requests: {self.total_api_requests}, Total tokens: {self.total_tokens}", "DEBUG")
                
                # Update session totals
                self.total_tokens += tokens
                self.api_cost += cost
                
                # Update master totals
                self.master_tokens += tokens
                self.master_api_cost += cost
                
                # Make sure master API request count matches or exceeds session count
                self.master_api_requests = max(self.master_api_requests, self.total_api_requests)
                
                if self.console:
                    self.console.log(f"DEBUG: After update - Total requests: {self.total_api_requests}, Total tokens: {self.total_tokens}", "DEBUG")
                    self.console.log(f"DEBUG: After update - Master requests: {self.master_api_requests}, Master tokens: {self.master_tokens}", "DEBUG")
                
                # CRITICAL: Save to settings immediately after each API request
                self.settings_manager.set_setting('total_tokens', self.total_tokens)
                self.settings_manager.set_setting('api_cost', self.api_cost)
                self.settings_manager.set_setting('master_tokens', self.master_tokens)
                self.settings_manager.set_setting('master_api_cost', self.master_api_cost)
                self.settings_manager.set_setting('master_api_requests', self.master_api_requests)
                self.settings_manager.set_setting('total_api_requests', self.total_api_requests)
                
                # Force settings to be written to disk immediately
                if hasattr(self.settings_manager, 'save_settings'):
                    self.settings_manager.save_settings()
                    if self.console:
                        self.console.log("DEBUG: Forced immediate save of API stats to disk", "DEBUG")
                
                # Update the UI if panel is visible
                if self.isVisible():
                    self.update_api_statistics()
                
                if self.console:
                    self.console.log(f"API request completed - Tokens: {tokens}, Cost: ${cost:.6f}", "INFO")
                
                # Share data with PunchCardStats if available
                if hasattr(self.parent(), 'stats'):
                    # Update API stats in the main stats object
                    main_stats = self.parent().stats
                    if hasattr(main_stats, 'stats'):
                        if 'api_stats' not in main_stats.stats:
                            main_stats.stats['api_stats'] = {
                                'total_requests': 0,
                                'total_tokens': 0,
                                'total_cost': 0.0
                            }
                        
                        # Update the stats
                        api_stats = main_stats.stats['api_stats']
                        api_stats['total_requests'] = self.total_api_requests
                        api_stats['total_tokens'] = self.total_tokens
                        api_stats['total_cost'] = self.api_cost
                        
                        # Save stats to disk
                        main_stats.save_stats()
                        
                        if self.console:
                            self.console.log("Synchronized API stats with PunchCardStats", "DEBUG")
                
                # Publish event to message bus
                if hasattr(self, 'message_bus'):
                    try:
                        self.message_bus.publish('stats.api.updated', {
                            'api_requests': self.total_api_requests,
                            'api_tokens': self.total_tokens,
                            'api_cost': self.api_cost,
                            'timestamp': datetime.now().isoformat()
                        }, source='ImpactPanel')
                    except Exception as e:
                        if self.console:
                            self.console.log(f"Failed to publish API stats update: {str(e)}", "ERROR")
                
        except Exception as e:
            if self.console:
                self.console.log(f"Error handling API request completion: {str(e)}", "ERROR")
            else:
                logger.error(f"Error handling API request completion: {str(e)}")
    
    def on_api_request_failed(self, message):
        """Handle API request failed event."""
        try:
            # Count the failed request
            self.total_api_requests += 1
            self.master_api_requests += 1
            
            # Update time-based statistics
            today = datetime.now().strftime("%Y-%m-%d")
            current_week = datetime.now().strftime("%Y-W%W")
            current_month = datetime.now().strftime("%Y-%m")
            
            # Update daily/weekly/monthly counts
            self.api_daily_requests[today] = self.api_daily_requests.get(today, 0) + 1
            self.api_weekly_requests[current_week] = self.api_weekly_requests.get(current_week, 0) + 1
            self.api_monthly_requests[current_month] = self.api_monthly_requests.get(current_month, 0) + 1
            
            # Save to settings
            self.settings_manager.set_setting('total_api_requests', self.total_api_requests)
            self.settings_manager.set_setting('master_api_requests', self.master_api_requests)
            self.settings_manager.set_setting('api_daily_requests', self.api_daily_requests)
            self.settings_manager.set_setting('api_weekly_requests', self.api_weekly_requests)
            self.settings_manager.set_setting('api_monthly_requests', self.api_monthly_requests)
            
            # Update the API statistics display
            self.update_api_statistics()
            
            if self.console:
                self.console.log(f"API request failed - Total requests: {self.total_api_requests}", "WARNING")
            
        except Exception as e:
            if self.console:
                self.console.log(f"Error handling API request failure: {str(e)}", "ERROR")
            else:
                logger.error(f"Error handling API request failure: {str(e)}")
    
    def on_system_ready(self, message):
        """Handle system ready event."""
        try:
            # Log the system ready event
            if self.console:
                self.console.log("System ready event received", "INFO")
            
            # Save master stats temporarily before loading
            master_api_requests = self.master_api_requests
            master_tokens = self.master_tokens
            master_api_cost = self.master_api_cost
            
            # Load statistics when system is ready
            self.load_statistics()
            
            # IMPORTANT: Reset session statistics while preserving lifetime stats
            # This ensures session stats reset on reload but lifetime stats remain
            self.total_api_requests = 0
            self.total_tokens = 0
            self.api_cost = 0.0
            
            # Restore master stats to ensure they persist
            self.master_api_requests = max(self.master_api_requests, master_api_requests)
            self.master_tokens = max(self.master_tokens, master_tokens)
            self.master_api_cost = max(self.master_api_cost, master_api_cost)
            
            # Reset daily/weekly/monthly API counts
            today = datetime.now().strftime("%Y-%m-%d")
            current_week = datetime.now().strftime("%Y-W%W")
            current_month = datetime.now().strftime("%Y-%m")
            self.api_daily_requests[today] = 0
            self.api_weekly_requests[current_week] = 0
            self.api_monthly_requests[current_month] = 0
            
            # Update UI immediately with reset session values
            self.update_api_statistics()
            
            # Force save to persist the reset
            self.save_statistics()
            
            # Verify that statistics were loaded correctly
            if self.console:
                self.console.log(f"System ready: Reset session API stats to 0. Lifetime stats: {self.master_api_requests}", "INFO")
            
            # Start update timers
            self.update_timer.start(60000)  # Update every minute
            self.power_timer.start(5000)    # Update power every 5 seconds
            
            if self.console:
                self.console.log("Impact panel initialized on system ready", "INFO")
            
        except Exception as e:
            if self.console:
                self.console.log(f"Error handling system ready: {str(e)}", "ERROR")
            else:
                logger.error(f"Error handling system ready: {str(e)}")
    
    def on_system_shutdown(self, message):
        """Handle system shutdown event."""
        try:
            # Log the system shutdown event
            if self.console:
                self.console.log("System shutdown event received", "INFO")
                self.console.log(f"Before final save - API requests: {self.total_api_requests}, master: {self.master_api_requests}", "INFO")
                
            # Save final statistics - critical to maintain data between sessions
            self.update_and_save_statistics()
            
            # Verify the save was successful
            verification_api_requests = self.settings_manager.get_setting('total_api_requests', 0)
            if self.console:
                self.console.log(f"Verification after final save - API requests saved as: {verification_api_requests}", "INFO")
            
            # Stop update timers
            self.update_timer.stop()
            self.power_timer.stop()
            
            if self.console:
                self.console.log("Impact panel saved final statistics on shutdown", "INFO")
            
        except Exception as e:
            if self.console:
                self.console.log(f"Error handling system shutdown: {str(e)}", "ERROR")
            else:
                logger.error(f"Error handling system shutdown: {str(e)}")

    def on_environmental_impact_updated(self, message):
        """Handle environmental impact updates."""
        try:
            if message and hasattr(message, 'data'):
                data = message.data
                
                # Always update the values, not just when visible
                self.co2_label.setText(f"{data.get('co2', 0.0):.6f} kg")  # More precision
                self.car_miles_label.setText(f"{data.get('car_miles', 0.0):.6f} mi")  # More precision
                self.trees_label.setText(f"{int(data.get('trees_needed', 1))}")
                self.water_label.setText(f"{data.get('water_usage', 0.0):.6f} L")  # More precision
                self.land_label.setText(f"{data.get('land_impact', 0.0):.6f} m²")  # More precision
                
                # Calculate and update the air quality impact too
                air_quality = data.get('water_usage', 0.0) * 0.01  # Simple estimation
                self.air_label.setText(f"{air_quality:.6f} µg/m³")  # More precision
                
                # Log successful update with detailed values
                if self.console:
                    self.console.log(f"Environmental impact update received", "DEBUG")
                    self.console.log(f"  CO2: {data.get('co2', 0.0):.6f} kg", "DEBUG")
                    self.console.log(f"  Car Miles: {data.get('car_miles', 0.0):.6f} mi", "DEBUG")
                    self.console.log(f"  Trees Needed: {int(data.get('trees_needed', 1))}", "DEBUG")
                    self.console.log(f"  Water Usage: {data.get('water_usage', 0.0):.6f} L", "DEBUG")
                    self.console.log(f"  Land Impact: {data.get('land_impact', 0.0):.6f} m²", "DEBUG")
                    self.console.log(f"  Air Quality: {air_quality:.6f} µg/m³", "DEBUG")
        except Exception as e:
            if self.console:
                self.console.log(f"Error handling environmental impact update: {str(e)}", "ERROR")
            else:
                logger.error(f"Error handling environmental impact update: {str(e)}")

    def showEvent(self, event):
        """Handle show event."""
        super().showEvent(event)
        # Force a power data update when shown
        self.fetch_power_data()
        # Update statistics display
        self.update_statistics()
        self.update_api_statistics()
        
    def hideEvent(self, event):
        """Handle hide event."""
        super().hideEvent(event)
        # Save statistics when hidden
        self.save_statistics()

    def __del__(self):
        """Destructor to ensure statistics are saved."""
        try:
            # Save statistics one final time before being destroyed
            if hasattr(self, 'settings_manager'):
                # Log the final save if console is available
                if hasattr(self, 'console') and self.console:
                    self.console.log("Impact panel destructor - final statistics save", "INFO")
                    
                # Make sure we don't lose API stats by reconciling them
                if hasattr(self, 'total_api_requests') and hasattr(self, 'master_api_requests'):
                    self.master_api_requests = max(self.master_api_requests, self.total_api_requests)
                    
                    # Save directly to settings
                    self.settings_manager.set_setting('total_api_requests', self.total_api_requests)
                    self.settings_manager.set_setting('master_api_requests', self.master_api_requests)
                    
                    if hasattr(self, 'console') and self.console:
                        self.console.log(f"Final API stats save - Requests: {self.total_api_requests}, Master: {self.master_api_requests}", "INFO")
        except Exception as e:
            # Can't reliably log here as console might be gone
            pass

# For testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    panel = ImpactPanel()
    panel.show()
    sys.exit(app.exec()) 