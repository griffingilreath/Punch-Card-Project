# Punch Card Display System - Development Roadmap

## Current Status - Version 0.1.0

The current version (0.1.0) represents the first stable implementation of the terminal-based IBM 80 Column Punch Card Simulator. The system currently supports:

- Terminal-based display of 80-column punch cards
- Hollerith/EBCDIC character encoding
- Message database and history
- Animated transitions between states
- Basic statistics tracking
- Configuration settings menu

## Known Issues & Bugs

### High Priority

1. **Display Positioning Inconsistency**
   - Issue: Punch card rectangle position varies when skipping splash screens (using `--test-message` flag)
   - Investigation needed: Does this issue persist when other screens are skipped?
   - Potential solution: Refactor rendering to use absolute positioning rather than relative offsets
   - Goal: Ensure consistent rectangle positioning across all display states

2. **Statistics Management**
   - Issue: Possible duplicate statistics files in use
   - Action: Verify that all statistics are being properly saved to a single source
   - Review the `PunchCardStats` class implementation to ensure proper file handling

3. **Terminal Rendering Optimization**
   - Issue: Content is never rendered at the top of the terminal window
   - Question: Is there a strategic reason for current rendering approach?
   - Goal: Simplify rendering to ensure screens are positioned consistently and efficiently

### Medium Priority

1. **Splash Screen Improvements**
   - Issue: Symbol statistics and message length statistics screens need cleaner formatting
   - Action: Redesign these screens for better readability
   - Timing: Adjust timing between splash screens for better readability

2. **Transition Animation Quality**
   - Issue: Some transition animations could be smoother
   - Action: Explore other ASCII animation techniques in terminal applications
   - Goal: Implement more engaging transitions between states

### Low Priority

1. **Documentation Improvements**
   - Issue: Code comments could be more comprehensive in some modules
   - Action: Improve in-code documentation, especially around the display positioning logic

## Feature Development Roadmap

### Version 0.2.0 - Hardware Integration

#### Primary Goals
1. **Neopixel LED Grid Integration**
   - Implement hardware interface for controlling physical LED grid
   - Ensure synchronized state between terminal display and physical LEDs
   - Follow phased implementation approach:
     - **Phase 0:** Initial prototype with 8x8 NeoPixel matrix and Arduino
     - **Phase 1:** Expanded 16x16 test grid with improved control framework
     - **Phase 2:** Communication protocol and synchronization implementation
     - **Phase 3:** Performance optimization and power management
     - **Phase 4:** Scale to full 12x80 production grid
   - Detailed steps in NEOPIXEL_INTEGRATION.md document

2. **Hardware Architecture Planning**
   - Determine optimal communication between Mac Mini (controller) and Raspberry Pi/Arduino/Teensy
   - Implement communication protocol (likely using serial or network connections)
   - Create fail-safe mechanisms for hardware disconnection

### Version 0.3.0 - Enhanced Visualization & Web Integration

1. **Terminal Output Capture**
   - Feature: Save terminal view as PDF/PNG/JPEG after punch card completion
   - Implementation: Investigate terminal screenshot capabilities or rendering alternatives
   - Database: Create simple image database for saved punch card images

2. **Website Integration**
   - Feature: Share statistics and system status via web interface
   - Implementation phases:
     - Basic API backend for statistics export
     - Authentication and secure access
     - Interactive dashboard with historical data
     - Real-time status monitoring

3. **Improved Animation System**
   - Research and implement more advanced ASCII animation techniques
   - Add "breathing space" between animations for better visual flow
   - Create pause and resume functionality for animations

### Version 1.0.0 - Production Ready

1. **Energy Monitoring**
   - Track power consumption of LED grid and microcontrollers
   - Create energy usage statistics screen
   - Implement power-saving modes

2. **Complete Database Integration**
   - Finalize local database schema for message and image storage
   - Implement database backup and restoration utilities
   - Create administration interface for database management

3. **Robust Error Handling**
   - Implement comprehensive error handling for all hardware and software components
   - Create automated recovery mechanisms
   - Add diagnostic tools

4. **Final Testing and Documentation**
   - Complete user manual
   - Document hardware specifications and assembly instructions
   - Create maintenance protocols

## Implementation Priorities

### Immediate Focus (Next 2-4 Weeks)
1. Fix display positioning inconsistency
2. Resolve statistics management issues
3. Begin NeoPixel integration Phase 0 (8x8 prototype)

### Short-term Goals (1-2 Months)
1. Complete NeoPixel Phase 1 (16x16 test grid)
2. Establish hardware communication protocols
3. Implement basic terminal output capture
4. Create initial web API endpoints for statistics

### Medium-term Goals (2-4 Months)
1. NeoPixel Phase 2-3 implementation
2. Enhanced animations and visual improvements
3. Expand web integration capabilities
4. Complete energy monitoring integration
5. Finalize database structure

### Long-term Vision (4+ Months)
1. Scale to full 12x80 NeoPixel grid (Phase 4)
2. Full 1.0.0 release with all planned features
3. Complete website integration with dashboard
4. Begin planning for expansion features (network support, multiple devices, etc.)

## Technical Implementation Notes

### Display Rendering Simplification
To address the display positioning inconsistency, we should consider:
1. Creating a single rendering function that handles all screen states
2. Using absolute positioning rather than relative positioning
3. Implementing a more robust terminal size detection system
4. Creating a layout system that can adapt to different terminal sizes

### Hardware Integration Approach
For NeoPixel integration:
1. Start with small 8x8 matrix prototype to establish core functionality
2. Create a `LEDController` class that abstracts the hardware interaction
3. Implement a fallback mode for when hardware is not available
4. Use a configuration file to specify hardware setup details
5. Consider using ZeroMQ or a similar library for inter-device communication
6. Choose between serpentine vs. row-by-row wiring layout based on prototype testing

### Website Integration Architecture
For web integration:
1. Develop Flask/FastAPI backend for serving statistics and system status
2. Implement secure authentication for administrative access
3. Create RESTful API endpoints for data access
4. Design responsive frontend dashboard using React or Vue.js
5. Implement WebSocket for real-time updates (optional)
6. Create historical data visualization components

### Statistics System Refactoring
1. Consolidate statistics storage into a single file format
2. Implement versioning for statistics files
3. Create data migration utilities for legacy statistics files
4. Prepare statistics format for web integration

## Conclusion

The primary goal is to achieve a functional Version 1.0.0 that includes proper LED grid functionality, a stable software foundation, and web integration capabilities. This roadmap outlines the path forward, focusing first on resolving critical issues before implementing new features.

Progress will be tracked through GitHub issues and project milestones, with regular updates to this roadmap document as development evolves. 

The phased approach to hardware integration will help manage the complexity of the project while allowing for continuous progress and testing. The web integration features will expand the project's capabilities and allow for remote monitoring and sharing of punch card statistics. 