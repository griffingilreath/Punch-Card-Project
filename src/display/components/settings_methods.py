"""Settings-related methods for the main window."""

def toggle_display_settings(self):
    """Toggle display settings panel visibility."""
    self.update_status("Toggling Display Settings...")
    
    if not self.display_settings_panel.isVisible():
        # Show the panel
        self.display_settings_panel.show()
        self.display_settings_panel.raise_()
        
        # Position panel correctly
        x = self.width() - self.display_settings_panel.width() - 20
        y = 60  # Below the menu bar
        self.display_settings_panel.move(x, y)
        
        # Load settings
        if hasattr(self.display_settings_panel, 'load_settings'):
            self.display_settings_panel.load_settings()
    else:
        self.display_settings_panel.hide()

def toggle_api_settings(self):
    """Toggle API settings panel visibility."""
    self.update_status("Toggling API Settings...")
    
    if not self.openai_settings_panel.isVisible():
        # Show the panel
        self.openai_settings_panel.show()
        self.openai_settings_panel.raise_()
        
        # Position panel correctly
        x = self.width() - self.openai_settings_panel.width() - 20
        y = 60  # Below the menu bar
        self.openai_settings_panel.move(x, y)
        
        # Load settings
        if hasattr(self.openai_settings_panel, 'load_settings'):
            self.openai_settings_panel.load_settings()
    else:
        self.openai_settings_panel.hide() 