# Enhancement: Sliding Animation for Message Transitions

## Description
Implement an animation that moves the existing punch card message off the display, sliding from right to left, one row of LEDs at a time, until the message has been cleared.

## Technical Details
1. Create a new animation function that:
   - Takes the current display state as input
   - Shifts each row of the display one position to the left on each frame
   - Continues until all content has been moved off-screen
2. Integrate this animation into the message display cycle:
   - Display message
   - Message persists on screen for designated time
   - Run sliding animation to clear the message
   - Begin displaying the next message

## Implementation Notes
- The animation should be smooth and consistent with the project's vintage aesthetic
- Consider variable speed options for the animation
- Add a configuration option to enable/disable this animation

## Implementation Details
The key files to modify:
- `src/display/gui_display.py` - Add a new method `slide_message_off_screen` to the `PunchCardDisplay` class
- Add animation timers and state management similar to existing animation methods

Proposed approach:
1. Create a new method for the sliding animation
2. Use timers to control the animation speed
3. Add configuration options to settings
4. Update the message display cycle to incorporate this animation

## Priority
Low (enhancement for future implementation)

## Labels
enhancement, animation, future-feature 