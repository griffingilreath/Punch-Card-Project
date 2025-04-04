# Punch Card Project Release Notes

## v0.7.1 (2025-04-03) - Impact Panel Enhancements

### Overview
This release focuses on improving the Impact Panel functionality, fixing issues with statistics persistence, enhancing visual feedback for energy usage tracking, and resolving API statistics synchronization problems. The Impact Panel is now more reliable but remains in beta status as several refinements are still planned.

### New Features

#### Impact Panel Improvements
- **Enhanced API Statistics Persistence**: Fixed critical issue with API statistics resetting unexpectedly
- **Session vs. Lifetime API Stats**: Properly implemented session statistics reset upon application restart while preserving lifetime statistics
- **Improved Energy Usage Visibility**: Dramatically increased energy usage accumulation rate (600x) to make changes more visible in real-time
- **Enhanced Environmental Impact Visualization**: Increased environmental impact metrics with 5x visibility multiplier
- **Precision Improvements**: Added 6 decimal places to all energy and environmental metrics for more precise tracking
- **Statistics Verification**: Added extensive verification logging to confirm all statistics are properly saved and loaded

### Fixes

#### API Statistics
- Fixed bug where API statistics would reset unexpectedly upon application restart
- Implemented proper separation between session and lifetime statistics
- Added immediate saving of statistics after each API request to prevent data loss
- Enhanced debug logging for better troubleshooting of statistics persistence issues
- Added verification steps to confirm stats are correctly saved and loaded

#### Energy Tracking
- Fixed issues with energy usage accumulation not being visible in the UI
- Increased energy usage accumulation rate by 600x for clearer visualization
- Added detailed logging to verify energy increments are being applied
- Fixed potential race condition in environmental impact updates

#### Message Bus Integration
- Improved message bus event publishing for statistics updates
- Added more granular events for tracking energy and API usage changes
- Enhanced subscription handling for impact panel events

### Technical Improvements
- Added detailed debug logging throughout the Impact Panel
- Improved error handling for statistics loading and saving
- Enhanced message bus event handling for power usage updates
- Added specialized handling for environmental impact updates
- Optimized statistics saving to prevent excessive disk writes

### Known Issues
- **Impact Panel Beta Status**: The Impact Panel is still considered beta and has some remaining bugs
- **Energy Tracking Accuracy**: Need to confirm energy tracking is using accurate power measurements from all relevant sources
- **Environmental Impact Calculations**: Some environmental metrics use approximations that need further validation
- **Message Bus Performance**: The message bus may be contributing to lag in some scenarios
- **System Integration**: Not all systems are fully leveraging the message bus capabilities yet
- **UI Responsiveness**: Occasional lag when updating multiple statistics simultaneously

### Future Plans
- Further refinement of the message bus architecture to reduce performance overhead
- More accurate power measurement integration for better energy tracking
- Improved environmental impact calculations with more scientific metrics
- Additional visualization options for the Impact Panel
- Better integration with system power management

### Contributors
- Griffin Gilreath (Lead Developer)

### Technical Notes
- This release should be considered beta quality for the Impact Panel components
- The API statistics tracking is considered stable
- Energy tracking is functional but requires further validation for accuracy 