# Update Notes

This document contains user-focused update notes for each version of the Punch Card Project.

## v0.6.0 - Major Project Reorganization (March 24, 2024)

This update completely reorganizes the project structure to improve maintainability and security. While this reorganization doesn't change functionality, it makes the codebase much more organized and easier to work with.

### What's New
- **Simplified Usage**: Just run `./punch_card.py` to start the application
- **Better Organization**: Files are now organized in a logical structure by function
- **Enhanced Security**: API keys are now stored in a secure, git-ignored location
- **Improved Documentation**: More comprehensive documentation for all aspects of the project

### How to Update
1. Pull the latest version from GitHub
2. If you have an API key, place it in `secrets/api_key.json` (copy from the template)
3. Run the application using `./punch_card.py`

### Known Issues
- The application remains in a non-functional save point state as we continue to improve the codebase

## v0.5.9 - Security & Bug Fixes (March 24, 2024)

This update focuses on security improvements and fixes a visual bug with punch card holes.

### What's New
- **Improved Security**: Better protection for API keys
- **Visual Bug Fix**: Punch card holes now properly clear after display

### How to Update
1. Pull the latest version from GitHub
2. Update your `.gitignore` if you're contributing to the project

### Known Issues
- The application remains in a non-functional save point state

## v0.5.8 - Enhanced Message Display (March 24, 2024)

This update improves the message display functionality and fixes visual bugs.

### What's New
- **Better Message Display**: Improved message display timing
- **Visual Bug Fix**: Fixed issue with punch card holes not clearing properly
- **Performance Improvement**: Better display refresh mechanism

### How to Update
1. Pull the latest version from GitHub

### Known Issues
- The application remains in a non-functional save point state

## v0.5.7 - Non-Functional Save Point (March 23, 2024)

This version serves as a checkpoint in the development process with a simplified standalone display module that properly renders punch card patterns.

### What's New
- **Simplified Display**: Streamlined display module that works properly
- **IBM 026 Encoding**: Correct encoding of text into punch card format
- **Command-Line Options**: Support for various testing modes

### How to Update
1. Pull the latest version from GitHub
2. Note that this is a non-functional save point, intended for development purposes

### Known Issues
- This is intentionally a non-functional save point
- The UI is simplified compared to previous versions

## v0.5.5 - API Client Improvement (March 24, 2024)

This update improves the OpenAI API client to bypass proxy issues.

### What's New
- **Custom API Client**: Better handling of API requests
- **Improved Reliability**: More reliable communication with OpenAI

### How to Update
1. Pull the latest version from GitHub

### Known Issues
- The application remains in development state

## v0.5.3 - UI Improvements & Bug Fixes (March 24, 2024)

This update enhances the user interface and fixes several bugs.

### What's New
- **Better UI Layout**: Improved OpenAI menu interface
- **Bug Fixes**: Fixed NoneType errors
- **Proxy Handling**: Better handling of proxy connections

### How to Update
1. Pull the latest version from GitHub

### Known Issues
- The application remains in development state 