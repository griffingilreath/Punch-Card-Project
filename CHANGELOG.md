# Changelog

All notable changes to the Punch Card Project will be documented in this file.

## [v0.6.0] - 2024-03-24

### Major Project Reorganization

#### Added
- New directory structure with dedicated modules:
  - `src/display/`: All display-related code
  - `src/api/`: API integration functionality
  - `src/core/`: Core application logic
  - `src/animation/`: Animation modules
  - `src/console/`: Console interface modules
  - `src/models/`: Data models
  - `src/utils/`: Utility functions
- New main entry point script (`punch_card.py`) for easier execution
- Dedicated `secrets/` directory with template for API keys
- Comprehensive security documentation in `SECURITY.md`

#### Changed
- Moved all configuration files to `config/` directory
- Consolidated all documentation in `docs/` directory
- Moved all backup files to `backups/` directory
- Relocated legacy code to `src/legacy/` directory
- Centralized resources in `resources/` directory
- Updated `.gitignore` to explicitly exclude backup files and secrets directory

#### Technical Details
- Import paths have been updated to reflect the new directory structure
- The main entry point script now properly imports from the module structure
- Python path handling has been improved to make imports more reliable

## [v0.5.9-security] - 2024-03-24

### Security Enhancement

#### Added
- Comprehensive `SECURITY.md` with API key management guidelines
- Enhanced documentation of API key handling practices

#### Changed
- Updated security-related documentation throughout the project
- Improved guidance on API key management

## [v0.5.9] - 2024-03-24

### Security & Bug Fixes

#### Added
- New patterns in `.gitignore` to exclude backup files that might contain API keys

#### Fixed
- Fixed issue with punch card holes not properly clearing from the display
- Resolved visual artifacts in the punch card display

## [v0.5.8] - 2024-03-24

### Enhanced Message Display

#### Added
- Improved message display timing functionality for better user experience

#### Changed
- Switched from `update()` to `repaint()` for complete widget refresh
- Enhanced code organization and readability

#### Fixed
- Fixed issue with punch card holes display - holes now properly clear after display
- Technical change: The `clear_grid` method now uses `repaint()` instead of `update()` to ensure all visual artifacts are cleared

## [v0.5.7] - 2024-03-23

### Non-Functional Save Point

#### Added
- Command-line interface with options for various display modes and test functions
- Testing functions for validating encoding accuracy
- Visual representation of character-to-punch mapping

#### Changed
- Simplified the main display module with a functional standalone version
- Streamlined implementation by removing problematic code sections
- Reduced dependencies to essential PyQt6 components

#### Fixed
- Fixed IBM 026 encoding for properly encoding text into punch card format
- Improved visualization of the punch card's LED matrix

## [v0.5.5] - 2024-03-24

### API Client Improvement

#### Added
- Complete custom OpenAI client implementation to bypass proxy issues

#### Changed
- Enhanced API communication reliability

## [v0.5.3] - 2024-03-24

### UI Improvements & Bug Fixes

#### Changed
- Enhanced OpenAI menu user interface layout

#### Fixed
- Fixed NoneType errors in the application
- Improved OpenAI client patching to fix proxies issues

## [v0.5.2] - 2024-03-??

### Early Integration

#### Added
- Initial OpenAI API integration
- Basic UI framework
- Punch card visualization implementation
- IBM 026 character encoding logic

## [v0.5.0] - 2024-03-??

### Initial Framework

#### Added
- Foundational project structure
- Qt-based GUI framework
- Core punch card representation
- Initial display architecture 