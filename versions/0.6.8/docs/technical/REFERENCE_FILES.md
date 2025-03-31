# Reference Files Guide

This document helps locate important files from the original project structure that may be needed for reference.

## GUI and Display Files

### Working GUI Files (v0.5.3)
- **Location**: `../LOOK HERE Punch Card Project 0.5.3/Punch Card Project`
- **Key Files**:
  - `src/display/gui_display.py` - Working GUI implementation
  - `simple_display.py` - Simplified display with working black background
  - `src/main.py` - Main entry point

### Latest Development Files
- **Location**: `../Cursor/Punch Card Project`
- **Key Files**:
  - `src/display/gui_display.py` - Latest GUI implementation
  - `src/core/punch_card.py` - Core punch card implementation
  - `src/utils/gui_integration.py` - GUI utilities

## Version History and Management

### Version Manager
- **Location**: `../Cursor/Punch Card Project/scripts`
- **Key Files**:
  - `version_manager.py` - Script for version management
  - `git_version_manager.py` - Git integration for version management

### Version Archives
- **Location**: `../Cursor/Punch Card Project/versions`
- Contains archived versions of the project:
  - `0.1.0/` - Initial version
  - `0.5.0/` - Mid-stage development
  - `0.5.2/` - Latest version before reorganization

## Configuration and Settings

### Settings Files
- **Location**: `../Cursor/Punch Card Project/src`
- **Key Files**:
  - `punch_card_settings.json` - Main settings file
  - `message_history.json` - Message history

### Configuration Templates
- **Location**: `../Cursor/Punch Card Project/config`
- Contains configuration templates for various environments

## Testing and Development

### Test Files
- **Location**: `../Cursor/Punch Card Project/tests`
- Contains test scripts and test data

### Working Examples
- **Location**: `../Cursor/Punch Card Project`
- **Key Files**:
  - `test_message_display_time.py` - Example of message display timing
  - `run_working_gui.py` - Example of GUI launcher

## Resources

### Fonts
- **Location**: `../Cursor/Punch Card Project/fonts`
- Contains SpaceMono font files used by the GUI

### Data Files
- **Location**: `../Cursor/Punch Card Project/data`
- Contains sample data and database files

## Backup Files

- **Location**: `../Cursor/Punch Card Project/backup_v0.1.0`
- Contains backup of version 0.1.0 for historical reference

---

## Important File Checklist

- [ ] `gui_display.py` - GUI implementation
- [ ] `punch_card.py` - Core implementation
- [ ] `main.py` - Main entry point
- [ ] `punch_card_settings.json` - Settings
- [ ] Font files
- [ ] Message database functionality
- [ ] Theme and style settings

## Migration Workflow

When migrating files from the reference structure to the clean project:

1. First check the v0.5.3 version for working implementations
2. If not found, check the latest development files in Cursor/Punch Card Project
3. Verify functionality by running tests
4. Document any changes made during migration
5. Commit to the testing branch

Use the `./check_gui_files.py` script to scan for missing essential files and automatically migrate them. 