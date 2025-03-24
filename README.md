# Punch Card Project v0.6.0 - Major Project Reorganization

[![Wiki](https://img.shields.io/badge/wiki-documentation-informational)](https://github.com/griffingilreath/Punch-Card-Project/wiki)

## Security Note

**Important**: Any API keys that might appear in the repository history are no longer valid and have been rotated. This project uses a secure approach for handling API keys:

1. API keys are stored in a `secrets` directory that is excluded from Git
2. The `.gitignore` file explicitly excludes backup files that might contain sensitive information
3. We use environment variables as the preferred method for storing API keys
4. The dedicated `update_api_key.py` utility helps securely manage API keys

To set up your API key:
1. Run `python update_api_key.py` and follow the prompts
2. Or set the `OPENAI_API_KEY` environment variable

Never commit API keys or other secrets directly to the repository.

## Version History

A summary of version changes is provided below. For more detailed information, see:
- [CHANGELOG.md](CHANGELOG.md) - Technical changelog with detailed changes
- [UPDATE_NOTES.md](UPDATE_NOTES.md) - User-focused update notes

### v0.6.0 (March 24, 2024) - Major Project Reorganization
- **Complete Directory Structure Reorganization**: Implemented a modern, well-organized directory structure
- **Module-Based Architecture**: Separated code into logical modules (display, api, core, animation, console)
- **Enhanced Maintainability**: Improved code organization for better maintainability and collaboration
- **Dedicated Module Directories**: Created specialized directories for each component
- **API Key Protection**: Implemented secure API key storage in the git-ignored `secrets/` directory
- **Backup File Management**: Added explicit patterns in `.gitignore` to prevent committing backup files
- **Documentation**: Added comprehensive security documentation in `SECURITY.md`
- **Clean Repository History**: Removed sensitive information from repository history
- **Centralized Configuration**: Moved all configuration files to the `config/` directory
- **Organized Documentation**: Consolidated documentation in the `docs/` directory
- **Legacy Code Management**: Preserved legacy code in a dedicated `src/legacy/` directory
- **Resource Organization**: Centralized resources in the `resources/` directory
- **Simplified Entry Point**: Created a clean main entry point at the project root (`punch_card.py`)
- **Organized Backups**: Moved all backup files to the `backups/` directory
- **Clean Project Root**: Significantly reduced clutter in the project root directory
- **Preserved Development History**: Maintained development history in an organized structure

### v0.5.9-security (March 24, 2024) - Security Enhancement
- **Security Documentation**: Added comprehensive `SECURITY.md` with API key management guidelines
- **Enhanced API Key Handling**: Improved documentation and practices for API key management

### v0.5.9 (March 24, 2024) - Security & Bug Fixes
- **Enhanced Git Security**: Updated `.gitignore` to exclude backup files that might contain API keys
- **Security Documentation**: Added comprehensive `SECURITY.md` with API key management guidelines
- **Visual Bug Fix**: Fixed issue with punch card holes not properly clearing

### v0.5.8 (March 24, 2024) - Enhanced Message Display
- **Message Display Enhancement**: Improved message display timing functionality
- **Visual Bug Fix**: Fixed issue with punch card holes display - holes now properly clear after display
- **Code Structure Improvements**: Enhanced code organization and readability
- **Switched to `repaint()`**: Changed from `update()` to `repaint()` for complete widget refresh

### v0.5.7 (March 23, 2024) - Non-Functional Save Point
- **Replaced Complex Implementation**: Simplified the main display module with a functional standalone version
- **Working Punch Card Visualization**: Successfully displays IBM 026 punch card patterns 
- **Command-Line Interface**: Preserved all command-line options from the original implementation
- **Preserved Original Functionality**: Maintains the core functionality of displaying text on punch cards
- **Fixed IBM 026 Encoding**: Properly encodes text into IBM 026 punch card format
- **Fixed LED Grid**: Proper visualization of the punch card's LED matrix
- **Streamlined Implementation**: Removed problematic code sections that caused syntax errors
- **Minimized Dependencies**: Reduced to essential PyQt6 components
- **Command Line Options**: Support for various display modes and test functions
- **Testing Functions**: Built-in tests for validating encoding accuracy
- **Character Encoding Display**: Visual representation of character-to-punch mapping 