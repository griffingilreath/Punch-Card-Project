"""
Message Events Module

This module defines constants for message bus event names to ensure consistency
across the application.
"""

# System events
EVENT_SYSTEM_READY = "system.ready"
EVENT_SYSTEM_SHUTDOWN = "system.shutdown"
EVENT_SYSTEM_ERROR = "system.error"

# Animation events
EVENT_ANIMATION_STARTED = "animation.started"
EVENT_ANIMATION_COMPLETED = "animation.completed"

# Message events
EVENT_NEW_MESSAGE = "message.new"
EVENT_MESSAGE_DISPLAYED = "message.displayed"
EVENT_MESSAGE_CLEARED = "message.cleared"

# API events
EVENT_API_STATUS_CHANGED = "api.status_changed"
EVENT_API_REQUEST_STARTED = "api.request.started"
EVENT_API_REQUEST_COMPLETED = "api.request.completed"
EVENT_API_REQUEST_FAILED = "api.request.failed"

# Hardware events
EVENT_HARDWARE_DETECTED = "hardware.detected"
EVENT_HARDWARE_CHANGED = "hardware.changed"
EVENT_HARDWARE_ERROR = "hardware.error" 