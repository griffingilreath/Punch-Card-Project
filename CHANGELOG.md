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

## [0.7.1] - 2024-03-26

### Changed
- Improved OpenAI settings panel UI layout and spacing
  - Reduced font sizes to 10px for better compactness
  - Optimized padding and margins throughout the interface
  - Improved button layout and alignment
  - Enhanced status field visibility and placement
  - Adjusted panel height to prevent overflow

### Fixed
- Fixed layout issues in OpenAI settings panel where elements could overlap
- Improved vertical spacing to prevent GUI overflow
- Better alignment of test connection status and action buttons 