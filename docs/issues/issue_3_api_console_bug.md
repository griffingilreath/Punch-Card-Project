# Bug: API Console Display Issues Persist

## Bug Description
The API console messages are sometimes showing in the terminal instead of the GUI as intended. This issue has persisted through recent updates.

## Reproduction Steps
1. Launch the application with `python3 simple_display.py --black-bg --debug`
2. Observe API-related messages appearing in the terminal instead of the dedicated console area

## Console Output Example
```
[14:00:47] [system] OpenAI Status: none - All Systems Operational
[14:00:48] [system] Fly.io Status: none - All Systems Operational
```

## Expected Behavior
All system messages should appear in the GUI console rather than the terminal.

## Potential Causes
- Improper console redirection
- Multiple output streams not being properly managed
- Console styling issues affecting visibility

## Implementation Details
The issue likely occurs in the following files:
- `simple_display.py` - Particularly the `update_api_console` function
- `src/display/gui_display.py` - The `APIConsoleWindow` class

Proposed solution approach:
1. Examine how console messages are routed
2. Ensure all API-related logs use the GUI console rather than terminal output
3. Add proper redirection for console.log calls
4. Consider implementing a unified logging system that routes all messages appropriately

## Priority
High

## Labels
bug, console, user-experience 