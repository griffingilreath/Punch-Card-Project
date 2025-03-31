# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.2] - 2024-03-25

### Added
- Restored OpenAI API settings tab in the Settings dialog
- Restored Statistics tab with message tracking and service status
- Added Card Dimensions settings tab for controlling punch card size
- Implemented usage and cost tracking for OpenAI API

### Fixed
- Fixed the `run_gui_app` function to properly initialize the application
- Improved error handling in the GUI application

## [0.6.1] - 2024-03-24

### Added
- Simplified branch management strategy
- Improved project structure and organization
- New documentation files (README, BRANCH_QUICK_REFERENCE, etc.)

### Changed
- Reorganized file structure to follow standard conventions
- Consolidated configuration files
- Improved error handling in GUI components

### Fixed
- Fixed segmentation fault issues in display code
- Resolved issues with message display timing

## [0.6.0] - 2024-03-22

### Added
- Working GUI with black background
- Improved display modules
- Settings configuration system

### Changed
- Refactored core punch card encoding logic
- Updated terminal display functionality

### Fixed
- Multiple display rendering bugs
- Card encoding issues

## [0.5.3] - 2024-03-17

### Added
- GUI improvements
- Better error handling

### Changed
- Updated display system

## [0.5.2] - 2024-03-15

### Added
- Initial GUI implementation
- Basic display functionality

### Changed
- Improved encoding logic

## [0.1.0] - 2024-03-10

### Added
- Initial project structure
- Basic punch card encoding functionality
- Command-line interface

## [0.6.7] - 2025-03-29

### Added
- Comprehensive Settings Manager with centralized configuration
- Animation Manager (Beta) for coordinated animation control
- Menu Bar enhancements for better feature access
- Initial prototype of layout-based text positioning (Alpha)
- Documentation for Settings Manager and Animation Manager

### Changed
- Moved from scattered settings to centralized management
- Improved configuration persistence and error handling
- Enhanced menu organization and structure
- Started transition from direct animation code to Animation Manager
- Began experiments with layout-based positioning for text elements

### Known Issues
- Text positioning is still in early alpha with significant glitches
- Animation Manager may experience timing issues with complex sequences
- Some settings aren't properly preserved between sessions
- Layout calculations can cause application crashes in certain scenarios
- Window resizing causes visual glitches with text elements

## [0.6.6] - 2025-03-27

### Added
- Keychain integration for secure API key storage
- Centralized settings management with SettingsManager class
- Improved settings dialog with tabbed interface
- Enhanced API integration with better error handling
- Usage statistics for tracking API usage

### Changed
- Updated settings organization and structure
- Improved API error handling and feedback
- Enhanced user interface for settings dialog
- Better organization of configuration options

### Fixed
- API key storage security issues
- Settings persistence problems
- UI layout issues in settings dialog
- Error handling for network timeouts

## [Earlier Versions]

See the [Version History Wiki](https://github.com/griffingilreath/Punch-Card-Project/wiki/Version-History) for details on earlier versions. 