"""
Message Bus for Punch Card Application.

This module provides a simple message bus implementation for component communication.
Components can subscribe to specific event types and publish events to trigger handlers.
"""

from typing import Dict, List, Callable, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MessageBus")

class MessageBus:
    """
    A simple message bus for component communication.
    
    This allows different parts of the application to communicate without
    direct dependencies between them. Components can subscribe to specific
    event types and publish events to trigger handlers.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton implementation to ensure a single message bus instance."""
        if cls._instance is None:
            cls._instance = super(MessageBus, cls).__new__(cls)
            cls._instance._subscribers = {}
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the message bus."""
        self._subscribers = {}
        logger.info("MessageBus initialized")
    
    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """
        Subscribe to an event type with a callback function.
        
        Args:
            event_type: The event type to subscribe to
            callback: The function to call when the event occurs
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to event type '{event_type}'")
    
    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: The event type to unsubscribe from
            callback: The callback function to remove
        """
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
            logger.debug(f"Unsubscribed from event type '{event_type}'")
    
    def publish(self, event_type: str, data: Any = None) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event_type: The type of event to publish
            data: The data to pass to subscriber callbacks
        """
        if event_type not in self._subscribers:
            logger.debug(f"No subscribers for event type '{event_type}'")
            return
            
        subscribers = self._subscribers[event_type]
        logger.debug(f"Publishing event '{event_type}' to {len(subscribers)} subscribers")
        
        for callback in subscribers:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in subscriber callback for event '{event_type}': {str(e)}")


# Event types
EVENT_NEW_MESSAGE = "new_message"  
EVENT_DISPLAY_COMPLETE = "display_complete"
EVENT_API_STATUS_CHANGED = "api_status_changed"
EVENT_PUNCH_CARD_UPDATED = "punch_card_updated"


# Singleton instance getter
def get_message_bus() -> MessageBus:
    """Get the global message bus instance."""
    return MessageBus() 