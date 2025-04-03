# Message Bus Architecture for Punch Card Project

## Overview

This document outlines the message bus architecture for the Punch Card Project, providing a comprehensive plan for implementing and migrating to a decoupled component communication system. The message bus will serve as the central communication mechanism between components, replacing direct method calls and creating a more maintainable, testable, and extensible system.

## Table of Contents

1. [Current Architecture](#current-architecture)
2. [Message Bus Design Principles](#message-bus-design-principles)
3. [Implementation Strategy](#implementation-strategy)
4. [Event Types & Message Schema](#event-types--message-schema)
5. [Component Migration Strategy](#component-migration-strategy)
6. [Integration with PyQt Signals](#integration-with-pyqt-signals)
7. [Testing Approach](#testing-approach)
8. [Documentation Standards](#documentation-standards)
9. [References](#references)

## Current Architecture

The current architecture, after our component refactoring in v0.7.0, consists of:

- **MainWindow**: Main orchestrator that coordinates other components
- **Component modules**: Extracted from the original monolithic design
  - PunchCardWidget
  - ConsoleWindow
  - MenuBar components
  - Settings and dialog components
  - Hardware and animation subsystems

Current communication patterns:
- Direct method calls between components
- Some use of PyQt signals/slots for specific events
- Parent-child relationships for component hierarchy
- Some global state shared between components

Limitations:
- Tight coupling between components
- Difficulty in testing components in isolation
- Challenges in extending the system with new components
- Complex dependency graph making changes risky

## Message Bus Design Principles

Our message bus architecture will follow these key principles:

1. **Decoupling**: Components should not directly reference or call methods on each other
2. **Standardization**: All component communication should follow a consistent pattern
3. **Discoverability**: Event types should be well-defined and documented
4. **Testability**: Components should be easily testable in isolation
5. **Maintainability**: Message patterns should be clear and traceable
6. **Backward Compatibility**: Migration should support gradual adoption
7. **Performance**: Message delivery should be efficient
8. **Extensibility**: Easy to add new events and handlers

## Implementation Strategy

We already have a basic message bus implementation in `src/utils/message_bus.py`, which follows the Singleton pattern. We'll expand this implementation to:

1. **Standard Message Format**: Define a consistent message structure with:
   - Event type (string identifier)
   - Data payload (any serializable data)
   - Metadata (timestamp, source component, priority)

2. **Enhanced Message Bus Class**:
   - Add support for prioritized message handling
   - Implement message filtering capabilities
   - Add transaction support for related messages
   - Provide message replay capability for new subscribers
   - Add validation of message format

3. **Diagnostic Tools**:
   - Message bus monitoring/logging
   - Visualization of message flow
   - Performance metrics

### Code Structure

The enhanced message bus will maintain its current API while adding new capabilities:

```python
# Core message bus class
class MessageBus:
    def subscribe(self, event_type, callback, priority=0)
    def unsubscribe(self, event_type, callback)
    def publish(self, event_type, data=None, metadata=None)
    def get_subscribers(self, event_type)
    
    # New methods
    def filter_events(self, filter_func)
    def start_transaction()
    def commit_transaction()
    def rollback_transaction()
    def replay_events(self, event_types, target_callback)
```

## Event Types & Message Schema

We'll define a comprehensive set of event types organized by domain:

### UI Events
- `ui:display_updated`: Punch card display has been updated
- `ui:message_displayed`: New message has been displayed
- `ui:settings_changed`: User settings have been updated
- `ui:menu_action`: User has triggered a menu action
- `ui:animation_started`: An animation sequence has started
- `ui:animation_completed`: An animation sequence has completed

### Data Events
- `data:message_loaded`: A message has been loaded from storage
- `data:message_saved`: A message has been saved to storage
- `data:settings_loaded`: Settings loaded from storage
- `data:settings_saved`: Settings saved to storage

### System Events
- `system:startup_begin`: System startup has begun
- `system:startup_complete`: System startup has completed
- `system:shutdown_begin`: System shutdown has begun
- `system:shutdown_complete`: System shutdown has completed
- `system:error`: A system error has occurred
- `system:hardware_detected`: Hardware detection completed
- `system:sleep_mode`: System entering sleep mode
- `system:wake_mode`: System waking from sleep mode

### Hardware Events
- `hardware:connected`: Hardware device connected
- `hardware:disconnected`: Hardware device disconnected
- `hardware:data_received`: Data received from hardware

### API Events
- `api:request_sent`: API request has been sent
- `api:response_received`: API response has been received
- `api:error`: API error has occurred

### Message Schemas

Each event type will have a defined schema for its data payload. For example:

```python
# UI:DISPLAY_UPDATED schema
{
    "row": int,  # The row that was updated, or null if multiple rows
    "col": int,  # The column that was updated, or null if multiple columns
    "state": bool,  # The new state of the LED
    "full_refresh": bool,  # Whether this was a full display refresh
    "timestamp": float  # When the update occurred
}

# SYSTEM:ERROR schema
{
    "error_code": str,  # Error code
    "message": str,  # Human-readable error message
    "source": str,  # Component or module that generated the error
    "severity": str,  # "info", "warning", "error", "critical"
    "timestamp": float,  # When the error occurred
    "stacktrace": str  # Optional stack trace for debugging
}
```

## Component Migration Strategy

We'll migrate components in phases, starting with the most isolated components:

### Phase 1: Core Infrastructure
1. Enhance message bus implementation
2. Create event type constants and documentation
3. Implement message schema validation
4. Create testing utilities for message bus

### Phase 2: Output Components
1. Migrate ConsoleWindow to use message bus for logging
2. Update PunchCardWidget to publish display update events
3. Modify StatusPanel to subscribe to relevant events

### Phase 3: Input Components
1. Update MenuBar to publish menu action events
2. Migrate settings dialogs to publish setting change events
3. Convert hardware detection to publish hardware events

### Phase 4: Core Orchestration
1. Update MainWindow to subscribe to events instead of receiving direct calls
2. Migrate animation system to be message-driven
3. Convert sound system to respond to message bus events

### Phase 5: Cleanup
1. Remove direct component references
2. Eliminate remaining direct method calls
3. Update documentation to reflect the new architecture

## Integration with PyQt Signals

PyQt's signal-slot mechanism is a core part of Qt applications. We'll integrate it with our message bus:

1. **Signal-to-Message Bridge**: Create adapters to convert PyQt signals to message bus events
2. **Message-to-Signal Bridge**: Create adapters to convert message bus events to PyQt signals
3. **Component Wrappers**: Wrap Qt components with message bus awareness

Example:

```python
# Signal to Message Bridge
class SignalMessageBridge(QObject):
    def __init__(self, message_bus):
        super().__init__()
        self.message_bus = message_bus
        
    def connect_signal(self, qt_signal, event_type, transform_func=None):
        qt_signal.connect(
            lambda *args: self.message_bus.publish(
                event_type, 
                transform_func(*args) if transform_func else args[0] if args else None
            )
        )

# Usage
bridge = SignalMessageBridge(get_message_bus())
bridge.connect_signal(
    self.punch_card.animation_finished,
    "ui:animation_completed",
    lambda anim_type: {"animation_type": anim_type}
)
```

## Testing Approach

The message bus architecture enables easier testing:

### Unit Testing Components
- Mock the message bus to isolate components
- Verify published events from components
- Simulate incoming events to test component behavior

### Integration Testing
- Use spy components to monitor message flow
- Create test scenarios that exercise event chains
- Validate end-to-end behavior through message sequences

### Test Utilities
- Message bus recorder for capturing event sequences
- Event simulator for replaying sequences
- Validation utilities for checking message schemas

## Documentation Standards

For all message bus related code, we'll follow these documentation standards:

1. **Event Types**: All event types must be documented with:
   - Event name and constant
   - Description of when it's fired
   - Expected data schema
   - Example usage code

2. **Publishers**: Components that publish events must document:
   - Which events they publish
   - Under what conditions
   - What data is included

3. **Subscribers**: Components that subscribe to events must document:
   - Which events they subscribe to
   - How they respond to each event
   - Any side effects of handling events

## References

1. [Component Architecture Document](COMPONENT_ARCHITECTURE.md)
2. [Existing Message Bus Implementation](../../src/utils/message_bus.py)
3. [GUI Refactoring Issue](../../gui_refactor_issue.md)
4. [Release Notes v0.7.0](../../release_notes/v0.7.0.md)
5. [Observer Pattern](https://en.wikipedia.org/wiki/Observer_pattern)
6. [Publish-Subscribe Pattern](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern)
7. [Event-driven Architecture](https://en.wikipedia.org/wiki/Event-driven_architecture) 