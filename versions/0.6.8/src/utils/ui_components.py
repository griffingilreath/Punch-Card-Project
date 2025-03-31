"""
Common UI components for the Punch Card Project.
Provides reusable UI elements with consistent styling.
"""
from PyQt6.QtWidgets import QPushButton, QWidget, QLabel
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen

from src.utils.colors import COLORS
from src.utils.fonts import get_font, get_font_css

class RetroButton(QPushButton):
    """
    Minimalist styled button with a retro look.
    
    Provides a consistent appearance for buttons throughout the application.
    """
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['button_bg'].name()};
                color: {COLORS['button_text'].name()};
                border: 1px solid {COLORS['hole_outline'].name()};
                padding: 6px 12px;
                {get_font_css(size=12)}
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover'].name()};
            }}
        """)
        # Set proper font
        self.setFont(get_font(size=12))

class ClassicTitleBar(QWidget):
    """
    Classic Macintosh-style title bar.
    
    Creates a retro title bar with decorative elements.
    """
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.setFixedHeight(20)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['title_bar'].name()};
                color: {COLORS['title_text'].name()};
                {get_font_css(bold=True, size=12)}
            }}
        """)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set font for title
        painter.setFont(get_font(bold=True, size=12))
        
        # Draw title
        painter.setPen(COLORS['title_text'])
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.title)
        
        # Draw decorative lines
        line_y = self.height() // 2
        line_width = 20
        spacing = 40
        
        # Left lines
        for i in range(3):
            x = 10 + (i * spacing)
            painter.setPen(QPen(COLORS['title_line'], 1))
            painter.drawLine(x, line_y - 1, x + line_width, line_y - 1)
            painter.drawLine(x, line_y + 1, x + line_width, line_y + 1)
        
        # Right lines
        for i in range(3):
            x = self.width() - 10 - line_width - (i * spacing)
            painter.setPen(QPen(COLORS['title_line'], 1))
            painter.drawLine(x, line_y - 1, x + line_width, line_y - 1)
            painter.drawLine(x, line_y + 1, x + line_width, line_y + 1) 