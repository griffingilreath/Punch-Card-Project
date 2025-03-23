# Punch Card Display System v0.5.0 - The GUI Update

```
  _____   _    _   _____    _    _   _____    _____           _______ _______ 
 / ____| | |  | | |_   _|  | |  | | |_   _|  / ____|         |__   __|  ____|
| |  __  | |  | |   | |    | |  | |   | |   | |  __  _   _      | |  | |__   
| | |_ | | |  | |   | |    | |  | |   | |   | | |_ || | | |     | |  |  __|  
| |__| | | |__| |  _| |_   | |__| |  _| |_  | |__| || |_| |     | |  | |____ 
 \_____|  \____/  |_____|   \____/  |_____|  \_____| \__,_|     |_|  |______|
```

## Release Date: March 23, 2024

This version represents a significant visual overhaul of the Punch Card Display System, focusing on improved GUI elements, better visibility with a black background theme, and enhanced service monitoring for both OpenAI and fly.io connections.

## Major Changes

### 1. Visual Interface Improvements

- **Black Background Theme**: Complete overhaul of the color scheme to use a black background with white text for better visibility and a more authentic punch card aesthetic.
- **Space Mono Font**: Standardized use of Space Mono throughout the interface for a consistent terminal-like appearance.
- **Classic Mac-Style Menu Bar**: Implemented a menu bar at the top of the application (where supported) or an enhanced button toolbar with properly sized buttons.
- **Enhanced Button Layout**: Fixed issues with buttons being cut off in the main interface.
- **Improved Widget Visibility**: Enhanced contrast for all UI elements.

### 2. Functionality Enhancements

- **OpenAI Integration**: Full integration with model selection and API key management.
- **Service Status Monitoring**: Real-time status monitoring for OpenAI and fly.io services.
- **API Console**: Detailed connection and response information panel that can be toggled with the 'C' key.
- **Keyboard Shortcuts**: Added hotkeys for common functions.
- **Error Handling**: Improved error handling for service connectivity issues.

### 3. Security Improvements

- **API Key Management**: Implemented secure handling of API keys with environment variable support.
- **Settings File Security**: Updated settings file structure to prevent accidental API key exposure.
- **Git Security**: Enhanced .gitignore and documentation to prevent sensitive information from being pushed to repositories.

## Technical Details

### Updated Files

- **simple_display.py**: Major overhaul with enhanced GUI components, black background theme, and API console.
- **punch_card_settings.json**: Added support for environment variable-based API key management.
- **README.md**: Comprehensive update with new features, security guidelines, and known issues.
- **.gitignore**: Enhanced to prevent sensitive information from being committed.

### Added Features

- `--black-bg` command-line flag for enabling the black background theme.
- 'C' keypress event to toggle console visibility.
- Service status indicators for OpenAI and fly.io.
- Improved error messages for connection issues.

## Version Management & File Organization

This project implements a comprehensive versioning strategy to preserve the development history and ensure all past versions remain accessible:

### Repository Structure
```
punch_card_project/
├── src/                    # Current source code
├── versions/               # Archive of previous versions
│   ├── 0.1.0/              # Initial version snapshot
│   └── 0.5.0/              # Current GUI Update snapshot
├── scripts/                # Utility scripts including version_manager.py
└── data/                   # Data files and resources
```

### Version Preservation
Each major version is:
1. Tagged in Git using `git tag -a v0.5.0 -m "The GUI Update"`
2. Archived in the versions directory with complete source code and documentation
3. Documented with a manifest.md (this file) and version_info.txt

### Version Management Tools
The `scripts/version_manager.py` utility handles:
- Creating new version snapshots
- Documenting changes between versions
- Maintaining the version history
- Ensuring consistent versioning across the project

This approach ensures that the project maintains a clear history of development and that users can access any previous version if needed.

## Known Issues

1. **API Console Visibility**: In some configurations, API console messages may appear in the terminal instead of the GUI.
2. **Visual Inconsistencies**: Different console types may have inconsistent styling.
3. **Menu Bar Compatibility**: The menu bar may not appear in some PyQt configurations.
4. **Style Application Issues**: Occasional failures with certain PyQt versions.
5. **Font Availability**: The Space Mono font may not be available on all systems, causing fallback to system fonts.

## Future Plans

- Add a dedicated database viewer for browsing saved messages.
- Standardize all console types to follow the same design language.
- Improve color scheme with potential for additional colors.
- Implement a proper settings dialog for all configuration options.
- Move all sensitive configuration to environment variables.

## Upgrading from v0.1.0

To upgrade from v0.1.0:

1. Update your requirements.txt file and install new dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your OpenAI API key as an environment variable (recommended):
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

3. Run the application with the new black background theme:
   ```bash
   python simple_display.py --black-bg --openai --debug
   ```

## Contributors

- Griffin Gilreath - Lead Developer 