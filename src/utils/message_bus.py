"""
Message Bus for Punch Card Application.

This module provides a message bus implementation for component communication.
Components can subscribe to specific event types and publish events to trigger handlers.
"""

from typing import Dict, List, Callable, Any, Optional, Set
import logging
import time
import threading
from dataclasses import dataclass
from enum import Enum, auto

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MessageBus")

class MessagePriority(Enum):
    """Priority levels for messages."""
    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    CRITICAL = auto()

@dataclass
class MessageMetadata:
    """Metadata for a message."""
    timestamp: float
    source: str
    priority: MessagePriority
    transaction_id: Optional[str] = None

@dataclass
class Message:
    """A message with its data and metadata."""
    event_type: str
    data: Any
    metadata: MessageMetadata

class MessageBus:
    """
    A message bus for component communication.
    
    This allows different parts of the application to communicate without
    direct dependencies between them. Components can subscribe to specific
    event types and publish events to trigger handlers.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton implementation to ensure a single message bus instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MessageBus, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the message bus."""
        self._subscribers = {}
        self._message_history = []
        self._current_transaction = None
        self._transaction_messages = []
        self._filters = {}
        logger.info("MessageBus initialized")
    
    def subscribe(self, event_type: str, callback: Callable[[Message], None], 
                 priority: int = 0, filter_func: Optional[Callable[[Message], bool]] = None) -> None:
        """
        Subscribe to an event type with a callback function.
        
        Args:
            event_type: The event type to subscribe to
            callback: The function to call when the event occurs
            priority: Higher priority subscribers are called first
            filter_func: Optional function to filter messages
        """
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            
            # Store subscriber info
            subscriber_info = {
                'callback': callback,
                'priority': priority,
                'filter': filter_func
            }
            
            self._subscribers[event_type].append(subscriber_info)
            # Sort subscribers by priority
            self._subscribers[event_type].sort(key=lambda x: x['priority'], reverse=True)
            
            logger.debug(f"Subscribed to event type '{event_type}' with priority {priority}")
    
    def unsubscribe(self, event_type: str, callback: Callable[[Message], None]) -> None:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: The event type to unsubscribe from
            callback: The callback function to remove
        """
        with self._lock:
            if event_type in self._subscribers:
                self._subscribers[event_type] = [
                    sub for sub in self._subscribers[event_type] 
                    if sub['callback'] != callback
                ]
                logger.debug(f"Unsubscribed from event type '{event_type}'")
    
    def start_transaction(self) -> str:
        """
        Start a new transaction.
        
        Returns:
            str: The transaction ID
        """
        with self._lock:
            if self._current_transaction is not None:
                raise RuntimeError("Transaction already in progress")
            
            self._current_transaction = str(time.time())
            self._transaction_messages = []
            logger.debug(f"Started transaction {self._current_transaction}")
            return self._current_transaction
    
    def commit_transaction(self) -> None:
        """Commit the current transaction."""
        with self._lock:
            if self._current_transaction is None:
                raise RuntimeError("No transaction in progress")
            
            # Publish all messages in the transaction
            for message in self._transaction_messages:
                self._publish_internal(message)
            
            self._current_transaction = None
            self._transaction_messages = []
            logger.debug("Transaction committed")
    
    def rollback_transaction(self) -> None:
        """Roll back the current transaction."""
        with self._lock:
            if self._current_transaction is None:
                raise RuntimeError("No transaction in progress")
            
            self._current_transaction = None
            self._transaction_messages = []
            logger.debug("Transaction rolled back")
    
    def publish(self, event_type: str, data: Any = None, 
                source: str = "unknown", priority: MessagePriority = MessagePriority.NORMAL) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event_type: The type of event to publish
            data: The data to pass to subscriber callbacks
            source: The source of the message
            priority: The priority of the message
        """
        metadata = MessageMetadata(
            timestamp=time.time(),
            source=source,
            priority=priority,
            transaction_id=self._current_transaction
        )
        
        message = Message(event_type=event_type, data=data, metadata=metadata)
        
        if self._current_transaction is not None:
            # Store message for later if in a transaction
            self._transaction_messages.append(message)
        else:
            # Publish immediately if not in a transaction
            self._publish_internal(message)
    
    def _publish_internal(self, message: Message) -> None:
        """Internal method to publish a message to subscribers."""
        # Debug logging for all messages
        print(f"\nDEBUG: MESSAGE BUS: Publishing message of type '{message.event_type}' from source '{message.metadata.source}'")
        print(f"DEBUG: MESSAGE BUS: Message priority: {message.metadata.priority}")
        print(f"DEBUG: MESSAGE BUS: Message data type: {type(message.data)}")
        if isinstance(message.data, dict):
            print(f"DEBUG: MESSAGE BUS: Message data (dict): {message.data}")
        elif isinstance(message.data, str):
            print(f"DEBUG: MESSAGE BUS: Message data (str): {message.data}")
        else:
            print(f"DEBUG: MESSAGE BUS: Message data: {str(message.data)}")
        
        # Count subscribers that will receive this message
        matching_subscribers = 0
        if message.event_type in self._subscribers:
            matching_subscribers = len(self._subscribers[message.event_type])
        
        # Check for wildcard subscribers
        if "*" in self._subscribers:
            matching_subscribers += len(self._subscribers["*"])
            
        print(f"DEBUG: MESSAGE BUS: Number of subscribers for this message: {matching_subscribers}")
        
        if message.event_type not in self._subscribers and "*" not in self._subscribers:
            logger.debug(f"No subscribers for event type '{message.event_type}'")
            return
        
        # Store message in history
        self._message_history.append(message)
        
        # Call subscribers for this specific event type
        if message.event_type in self._subscribers:
            subscribers = self._subscribers[message.event_type]
            logger.debug(f"Publishing event '{message.event_type}' to {len(subscribers)} subscribers")
            
            # Call subscribers in priority order
            for subscriber in subscribers:
                try:
                    # Apply filter if present
                    if subscriber['filter'] is not None and not subscriber['filter'](message):
                        continue
                    
                    print(f"DEBUG: MESSAGE BUS: Calling subscriber for '{message.event_type}'")
                    subscriber['callback'](message)
                except Exception as e:
                    logger.error(f"Error in subscriber callback for event '{message.event_type}': {str(e)}")
                    import traceback
                    print(f"DEBUG: MESSAGE BUS: Error in subscriber: {traceback.format_exc()}")
        
        # Call wildcard subscribers
        if "*" in self._subscribers:
            wildcard_subscribers = self._subscribers["*"]
            logger.debug(f"Publishing event '{message.event_type}' to {len(wildcard_subscribers)} wildcard subscribers")
            
            # Call subscribers in priority order
            for subscriber in wildcard_subscribers:
                try:
                    # Apply filter if present
                    if subscriber['filter'] is not None and not subscriber['filter'](message):
                        continue
                    
                    print(f"DEBUG: MESSAGE BUS: Calling wildcard subscriber for '{message.event_type}'")
                    subscriber['callback'](message)
                except Exception as e:
                    logger.error(f"Error in wildcard subscriber callback for event '{message.event_type}': {str(e)}")
                    import traceback
                    print(f"DEBUG: MESSAGE BUS: Error in wildcard subscriber: {traceback.format_exc()}")
    
    def replay_events(self, event_types: Optional[Set[str]] = None, 
                     target_callback: Optional[Callable[[Message], None]] = None) -> None:
        """
        Replay events from history.
        
        Args:
            event_types: Optional set of event types to replay
            target_callback: Optional specific callback to receive replayed messages
        """
        with self._lock:
            for message in self._message_history:
                if event_types is not None and message.event_type not in event_types:
                    continue
                
                if target_callback is not None:
                    try:
                        target_callback(message)
                    except Exception as e:
                        logger.error(f"Error in replay callback: {str(e)}")
                else:
                    self._publish_internal(message)


# Event types
EVENT_NEW_MESSAGE = "new_message"  
EVENT_DISPLAY_COMPLETE = "display_complete"
EVENT_API_STATUS_CHANGED = "api_status_changed"
EVENT_PUNCH_CARD_UPDATED = "punch_card_updated"
EVENT_SYSTEM_ERROR = "system_error"
EVENT_HARDWARE_STATUS = "hardware_status"
EVENT_ANIMATION_STARTED = "animation_started"
EVENT_ANIMATION_COMPLETED = "animation_completed"
EVENT_SOUND_PLAYED = "sound_played"
EVENT_SETTINGS_CHANGED = "settings_changed"


# Singleton instance getter
def get_message_bus() -> MessageBus:
    """Get the global message bus instance."""
    return MessageBus() 