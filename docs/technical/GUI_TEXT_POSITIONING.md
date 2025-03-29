# GUI Text Positioning (Alpha)

This document explains the technical implementation of text positioning in the Punch Card Project GUI interface. **Note that this feature is currently in an alpha state with known issues.**

## Overview

The GUI interface needs to display text elements (message title and status message) that are properly aligned with the punch card visualization. In version 0.6.7, we've begun experimenting with layout-based approaches to improve text positioning, but this work is still in early stages.

## Current Limitations

The current text positioning implementation has several known issues:
- Text elements frequently misalign with the punch card
- Message title sometimes overlaps with the menu bar
- Status text positioning is inconsistent during animations
- Text disappears during certain message display phases
- Significant visual glitches occur during window resizing
- Layout calculations can cause application crashes in some scenarios

## Experimental Implementation Approach

### Previous Implementation (pre-0.6.7)

Previously, we used an absolute positioning approach:

```python
self.message_label.move(x_position, y_position)
self.status_label.move(x_position, y_position)
```

This had several problems:
- Text elements would lose alignment when the window was resized
- Coordinate calculations were complex and error-prone
- Z-ordering issues caused text to be hidden
- Different coordinate systems between widgets created mapping problems

### Experimental Implementation (0.6.7 Alpha)

The experimental layout-based approach uses nested layouts:

1. **Container-Based Organization**
   - Each text element (message/status) is placed in its own container widget
   - Containers use QHBoxLayout with configurable margins
   - Text alignment is handled by the layout manager

2. **Dynamic Margin Calculation**
   - Container margins are calculated based on the punch card's position
   - The `update_label_margins()` method adjusts margins in real-time

3. **Event-Driven Updates**
   - Window resize events trigger margin recalculation
   - Text updates also trigger margin adjustments

## Key Components

### Text Container Structure

```
content_layout (QVBoxLayout)
├── message_container (QWidget)
│   └── message_layout (QHBoxLayout with left margin)
│       └── message_label (QLabel)
├── punch_card (PunchCardWidget)
└── status_container (QWidget)
    └── status_layout (QHBoxLayout with left margin)
        └── status_label (QLabel)
```

### Margin Calculation

The experimental `update_label_margins()` method calculates margins:

```python
def update_label_margins(self):
    """Update container margins to align with punch card."""
    # Get punch card position and dimensions
    card_width = self.punch_card.card_width
    container_width = self.punch_card.width()
    
    # Calculate left offset based on punch card position
    side_margin = getattr(self.punch_card, 'side_margin', 14)
    left_offset = ((container_width - card_width) // 2) + side_margin - 5
    
    # Update container margins
    message_layout.setContentsMargins(left_offset, 10, 0, 0)
    status_layout.setContentsMargins(left_offset, 0, 0, 10)
```

### Event Handling

The system responds to various events to maintain proper positioning:

```python
def resizeEvent(self, event):
    """Handle window resize events."""
    super().resizeEvent(event)
    # Update margins after resize with slight delay
    QTimer.singleShot(100, self.update_label_margins)

def showEvent(self, event):
    """Handle window show events."""
    super().showEvent(event)
    # Update margins when window is first shown
    QTimer.singleShot(200, self.update_label_margins)
```

## Error Handling

Robust error handling is necessary to prevent crashes during layout adjustments:

```python
try:
    # Update container margins...
except Exception as e:
    if hasattr(self, 'console'):
        self.console.log(f"Error updating label margins: {str(e)}", "ERROR")
```

## Testing Considerations

When testing the text positioning:

1. Verify behavior during different window states and sizes
2. Check for crashes when rapidly resizing the window
3. Monitor text visibility during all animation phases
4. Test on different operating systems and display resolutions
5. Verify error handling with deliberate error conditions

## Future Development

Planned improvements to move this feature out of alpha status:

1. Complete reimplementation of the layout system with more stable widget hierarchies
2. Better coordinate system mapping between different widgets
3. More sophisticated layout management for responsive designs
4. Improve animation integration with text positioning
5. Enhanced error recovery to prevent application crashes

## Troubleshooting

Common issues and temporary workarounds:

| Issue | Workaround |
|-------|----------|
| Text completely disappears | Restart the application |
| Menu bar overlap | Resize window to be taller |
| Text misalignment | Try different window sizes |
| Application crashes | Run with --safe-mode flag to disable dynamic text positioning |
| Flickering text | Disable animations in settings | 