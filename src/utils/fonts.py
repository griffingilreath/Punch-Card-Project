"""
Font utilities for the Punch Card Project.
Provides consistent font styling across the application.
"""
from PyQt6.QtGui import QFont

# Font configuration
FONT_FAMILY = "Courier New"
FONT_SIZE = 12  # Default font size

def get_font(bold=False, italic=False, size=FONT_SIZE) -> QFont:
    """
    Get a font with the specified style.
    
    Args:
        bold: Whether the font should be bold
        italic: Whether the font should be italic
        size: The font size in points
        
    Returns:
        QFont: A configured font object
    """
    font = QFont()
    font.setFamily(FONT_FAMILY)
    font.setPointSize(size)
    font.setBold(bold)
    font.setItalic(italic)
    font.setStyleHint(QFont.StyleHint.Monospace)  # Fallback to any monospace font
    return font

def get_font_css(bold=False, italic=False, size=FONT_SIZE) -> str:
    """
    Get CSS font styling with the specified style.
    
    Args:
        bold: Whether the font should be bold
        italic: Whether the font should be italic
        size: The font size in points
        
    Returns:
        str: CSS string for the font styling
    """
    weight = "bold" if bold else "normal"
    style = "italic" if italic else "normal"
    return f"font-family: {FONT_FAMILY}; font-size: {size}px; font-weight: {weight}; font-style: {style};" 