# Punch Card v0.6.7 Integration Plan

## Objective
Combine the full functionality of v0.6.7 (which includes all menu connections, message display, API features) with the improved text positioning and layout stability we developed.

## Key Methods to Integrate

### 1. Improved `align_message_with_card` Method

The v0.6.7 version positions text by finding the punch card geometry and moving the labels, but our improved version from `punch_card_fix.py` adds these enhancements:

```python
def align_message_with_card(self):
    """Align the message with the punch card display."""
    if hasattr(self, 'message_label') and hasattr(self, 'punch_card'):
        # Update the message label size based on content
        if self.message_label.text():
            self.message_label.adjustSize()
        
        # Get the card's position
        card_geometry = self.punch_card.geometry()
        message_width = self.message_label.width()
        
        # Center the message over the card
        message_x = card_geometry.x() + (card_geometry.width() - message_width) // 2
        message_y = card_geometry.y() - self.message_label.height() - 5
        
        # Ensure the message is visible
        if message_y < 10:
            message_y = 10  # Minimum top margin
        
        # Position the message
        self.message_label.move(message_x, message_y)
        self.message_label.setVisible(True)
        
        # Log the positioning
        if hasattr(self, 'console'):
            self.console.log(f"Text aligned with card at ({message_x}, {message_y})", "DEBUG")
```

### 2. Improved `resizeEvent` Method

The v0.6.7 version has a simple resizeEvent, but our improved version adds better timing for alignment:

```python
def resizeEvent(self, event):
    """Handle resize events."""
    super().resizeEvent(event)
    # Use direct alignment for more reliable positioning after resize
    QTimer.singleShot(50, self.align_message_with_card)
```

### 3. Add `showEvent` Method

Add a showEvent handler that ensures correct positioning when the window is first shown:

```python
def showEvent(self, event):
    """Handle show event."""
    super().showEvent(event)
    # Use direct alignment for more reliable positioning after window is shown
    QTimer.singleShot(100, self.align_message_with_card)
```

### 4. Enhanced `update_status` Method

Update the status method to ensure text positioning is maintained after status changes:

```python
def update_status(self, status: str):
    """Update the status display and console log with a status message."""
    # Update status label
    if hasattr(self, 'status_label'):
        self.status_label.setText(status)
        self.status_label.update()
    
    # Log to console
    if hasattr(self, 'console'):
        self.console.log(f"Status: {status}")
    
    # Ensure positioning is correct after status change
    QTimer.singleShot(10, self.align_message_with_card)
```

## Integration Steps

1. **Make a backup of the current working v0.6.7 file**
   ```
   cp src/display/gui_display.py src/display/gui_display.py.v067_original
   ```

2. **Modify the `align_message_with_card` method in the v0.6.7 file**
   - Replace with our improved version
   - This method is crucial for correctly positioning text

3. **Update resize and display handling**
   - Add or modify the `resizeEvent` method
   - Add the `showEvent` method
   - Update the `update_status` method to call alignment

4. **Test with incremental changes**
   - Verify each change maintains functionality while improving layout
   - Focus on proper text positioning during window resize

5. **Preserve all other v0.6.7 functionality**
   - Ensure all menu connections remain intact
   - Preserve all API functionality
   - Keep all working features like message display and animations

## Recommended Approach

Since the updated alignment code is relatively self-contained, we should:

1. Start with the full v0.6.7 code (which we've restored)
2. Implement the improved alignment methods directly in this file
3. Test functionality to ensure everything still works
4. Make minimal adjustments to preserve all behavior while fixing layout

## Post-Integration Testing

1. Test message display with various window sizes
2. Verify text remains aligned during animations
3. Confirm all menu items still work correctly
4. Check that API functionality is preserved
5. Ensure the settings dialog works properly

This approach maximizes our chance of success by making targeted changes to fix positioning while preserving all the functional aspects of v0.6.7. 