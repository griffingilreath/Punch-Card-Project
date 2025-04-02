#!/usr/bin/env python3
"""
Message Generator Module

Generates random messages for display on the punch card interface.
"""

import random

class MessageGenerator:
    """Generates random messages for display."""
    def __init__(self):
        self.messages = [
            "HELLO WORLD",
            "WELCOME TO THE PUNCH CARD DISPLAY",
            "IBM PUNCH CARD SYSTEM",
            "DO NOT FOLD SPINDLE OR MUTILATE",
            "COMPUTING THE FUTURE",
            "BINARY DREAMS",
            "PAPER TAPES AND PUNCH CARDS",
            "FROM MECHANICAL TO DIGITAL",
            "HISTORY IN HOLES",
            "DATA PUNCHED IN TIME"
        ]
    
    def generate_message(self) -> str:
        """Generate a random message."""
        return random.choice(self.messages) 