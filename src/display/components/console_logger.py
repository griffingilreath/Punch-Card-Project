#!/usr/bin/env python3
"""
Console Logger Module

Simple logger class that acts as a placeholder when no real console is available.
"""

class ConsoleLogger:
    """Simple logger class that acts as a placeholder when no real console is available"""
    def __init__(self):
        self.logs = []
        
    def log(self, message, level="INFO"):
        """Log a message with specified level"""
        self.logs.append((level, message))
        print(f"[{level}] {message}")

    def show(self):
        """Placeholder for show method"""
        pass

    def clear(self):
        """Clear logs"""
        self.logs = [] 