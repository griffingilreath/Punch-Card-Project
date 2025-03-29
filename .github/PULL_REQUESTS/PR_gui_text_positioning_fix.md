# PR: Fix GUI Text Positioning

## Description
This PR fixes the message and status text positioning in the GUI interface, ensuring proper alignment with the punch card and maintaining position during window resize.

## Changes Made
- Replaced absolute positioning with layout-based positioning
- Added container widgets with QHBoxLayout for text elements
- Implemented dynamic margin calculation based on punch card position
- Added proper event handling for window resize and text updates
- Enhanced error handling to prevent crashes during layout adjustments
- Fixed z-ordering to maintain text visibility
- Added proper spacing above and below the punch card

## Technical Implementation
The key technical changes include:

1. Created container widgets for text elements:
```python
message_container = QWidget()
message_layout = QHBoxLayout(message_container)
message_layout.setContentsMargins(35, 10, 0, 0)
message_layout.addWidget(self.message_label)
content_layout.addWidget(message_container)
```

2. Added dynamic margin calculation:
```python
def update_label_margins(self):
    # Calculate left offset based on punch card position
    card_width = getattr(self.punch_card, 'card_width', 562)
    container_width = self.punch_card.width()
    side_margin = getattr(self.punch_card, 'side_margin', 14)
    left_offset = max(35, ((container_width - card_width) // 2) + side_margin - 5)
    
    # Update container margins
    message_layout.setContentsMargins(left_offset, 10, 0, 0)
    status_layout.setContentsMargins(left_offset, 0, 0, 10)
```

3. Added proper event handling:
```python
def resizeEvent(self, event):
    super().resizeEvent(event)
    QTimer.singleShot(100, self.update_label_margins)

def showEvent(self, event):
    super().showEvent(event)
    QTimer.singleShot(200, self.update_label_margins)
```

## Testing Performed
- Tested on macOS 14.4 with Python 3.11
- Verified text alignment at different window sizes
- Tested behavior during window resize
- Confirmed text visibility during message display
- Verified no crashes occur during normal operation
- Verified text positioning during animations

## Screenshots
[Insert before/after screenshots showing the positioning fix]

## Issue Reference
Fixes #187 - Fix message and status text positioning in GUI display

## Documentation
Added technical documentation in `docs/technical/GUI_TEXT_POSITIONING.md` explaining the implementation approach and troubleshooting information. 