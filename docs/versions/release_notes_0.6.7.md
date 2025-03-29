# Release Notes - v0.6.7

## Settings System Overhaul and Animation Manager Beta

**Release Date:** March 29, 2025

This release focuses on improving the configuration system with a comprehensive settings manager and introducing a beta version of our new animation management system. Initial work has also begun on addressing text positioning issues.

### Key Improvements

- **Settings Manager (Stable)**: Completely overhauled settings system with centralized management
- **Enhanced Menu Bar Integration**: Improved menu structure with better organization and access to settings
- **Animation Manager (Beta)**: New system for coordinating and synchronizing animations across the application
- **Initial Text Positioning Work (Alpha)**: First steps toward improving text alignment with the punch card

### Settings Manager Improvements

- Centralized settings access through a single manager class
- Type-safe access to configuration values with proper validation
- Automatic settings persistence with change tracking
- Organized settings dialog with intuitive categorization
- Improved error handling for configuration loading and saving

### Animation Manager (Beta)

The new Animation Manager represents a significant architectural improvement:

- **Pros**:
  - Centralizes animation logic for better coordination
  - Provides a consistent API for all animation types
  - Enables synchronized animations between GUI and hardware
  - Simplifies the creation of complex, multi-stage animations
  - Reduces code duplication across the application

- **Cons**:
  - May introduce performance overhead for simple animations
  - Still needs optimization for hardware-synchronized animations
  - API may change as we gather more feedback

- **Why we moved to this approach**:
  - Previous approach scattered animation logic across multiple components
  - Animations were difficult to coordinate between GUI and hardware
  - Code duplication made maintenance challenging
  - Testing animations required significant setup work

### Text Positioning (Alpha)

Initial work has begun on improving text positioning, but this is still in an early alpha state:

- Experimenting with layout-based positioning instead of absolute coordinates
- Initial implementation of container widgets with dynamic margins
- Preliminary work on window resize handling

### Known Issues

- **Text Positioning**: 
  - Text elements still frequently misalign with the punch card
  - Message title sometimes overlaps with the menu bar
  - Status text positioning is inconsistent during animations
  - Text disappears during certain message display phases
  - Significant visual glitches occur during window resizing
  - Layout calculations can cause application crashes in some scenarios

- **Animation Manager**:
  - Occasional timing issues with complex animation sequences
  - Memory usage increases with animation complexity
  - Some animations fail to complete properly when interrupted

- **Settings Manager**:
  - Some settings aren't properly preserved between sessions
  - Large configuration files can cause loading delays

### Future Improvements

- Full implementation of text positioning with proper alignment
- Animation Manager performance optimizations
- Enhanced synchronization between GUI and hardware
- Responsive layout options for different screen sizes
- Additional animation types and transitions

## Installation

Update from previous version:

```bash
git pull
git checkout v0.6.7
```

Fresh installation:

```bash
git clone https://github.com/griffingilreath/Punch-Card-Project.git
cd Punch-Card-Project
git checkout v0.6.7
pip install -r requirements.txt
python launch_animation_panel.py
``` 