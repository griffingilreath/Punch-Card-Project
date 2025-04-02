#!/usr/bin/env python3
"""
Super Simple PyQt6 Application
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel

class SimpleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Super Simple App")
        self.setGeometry(100, 100, 400, 300)
        
        # Set up central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add a label
        label = QLabel("Hello, World!")
        label.setStyleSheet("font-size: 24px;")
        layout.addWidget(label)
        
        # Add a button
        button = QPushButton("Click Me")
        button.clicked.connect(self.button_clicked)
        layout.addWidget(button)
    
    def button_clicked(self):
        print("Button clicked!")
        self.statusBar().showMessage("Button was clicked!")

def main():
    app = QApplication(sys.argv)
    window = SimpleWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 