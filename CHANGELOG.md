# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [0.7.0] - 2024-03-24

### Added
- Component-based architecture for better code organization
- Dedicated component directory structure
- Energy usage tracking for M4 Mac Mini
- Improved message bus system
- New display settings panel
- Enhanced OpenAI settings interface

### Changed
- Extracted all major UI components into separate modules
- Reduced main window module size by over 70%
- Improved code organization and maintainability
- Renamed `gui_display.py` to `main_window.py`
- Enhanced menu bar organization

### Fixed
- Various UI rendering issues
- Menu bar duplication problems
- Window resizing bugs

## [0.6.9] - 2024-03-23

### Added
- Enhanced statistics panel with improved layout
- Real-time analytics with automatic refresh
- Support for saving and loading statistics

### Changed
- Improved text field sizing and alignment
- Enhanced error handling for statistics tracking
- Better performance for real-time updates

## [0.6.8] - 2024-03-22

### Added
- Sound control system with volume slider
- Mute functionality
- Enhanced menu bar organization

### Fixed
- Menu bar duplication issues
- Text alignment problems
- Window resizing bugs
- Sound manager integration issues

## [0.6.7] - 2024-03-21

### Added
- Comprehensive Settings Manager
- Animation Manager (Beta)
- Enhanced Menu Bar integration
- Text positioning system (Alpha)
- Documentation for new features

### Known Issues
- Text positioning remains unstable

## [0.6.6] - 2024-03-20

### Added
- Keychain integration for secure API key storage
- Centralized settings management
- Tabbed settings interface
- Usage statistics tracking

### Changed
- Improved API integration and error handling
- Enhanced settings organization

## [0.6.5] - 2024-03-19

### Added
- Expanded OpenAI model selection
- Service status monitoring
- Enhanced console output

### Changed
- Improved API error handling
- Better connection management

## [0.6.4] - 2024-03-18

### Changed
- Improved UI spacing and alignment
- Enhanced card animation performance
- Optimized memory usage

### Fixed
- Various UI rendering bugs

## [0.6.3] - 2024-03-17

### Changed
- Made GUI the default interface
- Updated command-line options
- Improved documentation
- Enhanced error handling

## [0.6.2] - 2024-03-16

### Changed
- Improved documentation formatting
- Updated hardware integration docs
- Enhanced code examples
- Standardized documentation structure

## [0.6.1] - 2024-03-15

### Added
- Comprehensive test suite
- Pytest integration
- Test coverage reporting

### Changed
- Improved test organization
- Enhanced documentation

## [0.6.0] - 2024-03-14

### Added
- Modern directory structure
- Module-based architecture
- Secure API key storage
- Comprehensive documentation

### Changed
- Complete project reorganization
- Enhanced code maintainability
- Improved configuration management

## [0.5.9] - 2024-03-13

### Added
- Security documentation
- Enhanced API key handling

### Fixed
- Punch card hole display issues
- Git security improvements

## [0.5.8] - 2024-03-12

### Changed
- Improved message display timing
- Enhanced code organization
- Switched to `repaint()` for better performance

### Fixed
- Punch card holes display issues

## [0.1.0] - 2024-03-01

### Added
- Initial project structure
- Basic punch card encoding functionality
- Command-line interface 