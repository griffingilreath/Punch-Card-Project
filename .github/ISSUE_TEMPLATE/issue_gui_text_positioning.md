---
name: GUI Text Positioning Bug
about: Fix the text message & status positioning in the GUI interface
title: "[BUG] Fix message and status text positioning in GUI display"
labels: bug, ui, display, high-priority
assignees: griffingilreath

---

## Description
The message title and status text in the GUI interface are not correctly positioned relative to the punch card. Text elements often overlap with the menu bar, appear too far from the punch card, or disappear during message display.

## Current Issues
- Text elements (message title and status) don't maintain proper alignment with the punch card
- Message title sometimes overlaps with the menu bar
- Status text appears too far below the punch card
- Text elements disappear during message display
- Position is lost when window is resized

## Reproduction Steps
1. Launch the application with `python launch_animation_panel.py`
2. Observe the message title and status text positioning
3. Resize the window and note how text alignment is lost
4. Display a message and observe how text sometimes disappears

## Expected Behavior
- Message title should appear just above the punch card, aligned with its left edge
- Status text should appear just below the punch card, aligned with its left edge
- Both text elements should maintain their position during window resize
- Text should remain visible during all phases of message display

## Technical Root Cause
The current implementation uses absolute positioning which doesn't account for:
- Different coordinate systems between the window and the punch card widget
- Layout changes during window resize
- Z-ordering issues that can cause elements to be hidden

## Proposed Solution
1. Replace absolute positioning with layout-based positioning
2. Use container widgets with proper margins to position text elements
3. Implement dynamic margin calculation based on punch card position
4. Add event handlers for window resize and other relevant events
5. Ensure proper z-ordering to keep text elements visible

## Technical Details
- Modify the initialization of message_label and status_label in gui_display.py
- Update the position_text_elements method to use layout-based positioning
- Add proper error handling to prevent crashes during layout adjustments
- Update display_message method to maintain text visibility

## Acceptance Criteria
- [ ] Message title appears 10px above the punch card, aligned with its left edge
- [ ] Status text appears 10px below the punch card, aligned with its left edge
- [ ] Text elements maintain their position during window resize
- [ ] Text remains visible during all phases of message display
- [ ] No visual glitches or crashes occur during normal operation

## References
- Current implementation in gui_display.py
- PyQt layout management documentation: https://doc.qt.io/qt-6/layout.html 