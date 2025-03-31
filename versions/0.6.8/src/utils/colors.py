"""
Color definitions for the Punch Card Project.
Centralizes all color definitions to ensure consistency across the application.
"""
from PyQt6.QtGui import QColor

# Application color scheme
COLORS = {
    'background': QColor(0, 0, 0),        # Black background
    'card_bg': QColor(0, 0, 0),           # Black card background
    'card_outline': QColor(255, 255, 255), # White card outline
    'hole_outline': QColor(255, 255, 255), # White hole outline
    'hole_fill': QColor(0, 0, 0),         # Black for unpunched holes
    'hole_punched': QColor(255, 255, 255), # White for punched holes
    'text': QColor(255, 255, 255),        # White text
    'button_bg': QColor(30, 30, 30),      # Dark button background
    'button_hover': QColor(50, 50, 50),   # Slightly lighter on hover
    'button_text': QColor(255, 255, 255), # White button text
    'console_bg': QColor(20, 20, 20),     # Darker background for console
    'console_text': QColor(200, 200, 200), # Light gray for console text
    'title_bar': QColor(40, 40, 40),      # Dark gray for title bar
    'title_text': QColor(200, 200, 200),  # Light gray for title text
    'title_line': QColor(100, 100, 100),  # Medium gray for title lines
    'error': QColor(150, 50, 50),         # Dark red for errors
    'success': QColor(50, 150, 50),       # Dark green for success
    'warning': QColor(150, 150, 50),      # Dark yellow for warnings
} 