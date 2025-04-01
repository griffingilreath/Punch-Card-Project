"""
Graphical User Interface for the Punch Card Project.
"""

import os
import sys
import time
import random
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QPalette, QColor

from src.display.widgets.punch_card_widget import PunchCardWidget
from src.display.widgets.console_widget import ConsoleWidget
from src.display.widgets.stats_panel import StatsPanel
from src.display.widgets.api_console import APIConsoleWindow
from src.display.animation_manager import AnimationManager, AnimationType, AnimationState
from src.display.message_generator import MessageGenerator
from src.utils.message_bus import get_message_bus, EVENT_NEW_MESSAGE
from src.utils.hardware_detector import HardwareDetector
from src.utils.sound_manager import SoundManager
from src.utils.colors import *

def run_gui_app():
    """Run the GUI application."""
    try:
        app = QApplication(sys.argv)
        window = PunchCardWidget()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Error running GUI application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_gui_app() 