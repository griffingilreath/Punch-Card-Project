# Enhancement: Persistent Message Display Until Next Message

## Description
Currently, messages appear to be displayed on the punch card but don't remain visible after typing completes. Messages should persist on the display until the next message begins, providing better readability.

## Expected Behavior
- Messages should remain fully visible on the punch card display after being typed
- Message should only be cleared when a new message begins typing

## Technical Approach
1. Modify the message display system to maintain the current message state
2. Only clear the display when a new message is about to be displayed
3. Ensure the transition between messages is smooth

## Implementation Details
The key files to modify:
- `src/display/gui_display.py` - Specifically the `display_message` and `display_next_char` methods in the `PunchCardDisplay` class

Current behavior:
1. `display_message` method is called with a message
2. It sets up a timer to display each character one at a time via `display_next_char`
3. Once all characters are displayed, it doesn't maintain the message state

Proposed changes:
- Add a state variable to track the current displayed message
- Only clear the display when a new message is explicitly requested
- Ensure the message remains fully visible until a new one begins

## Priority
Medium

## Labels
enhancement, user-experience 