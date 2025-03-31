# Animation Manager (Beta)

This document explains the technical implementation of the Animation Manager component in the Punch Card Project. **Note that this feature is currently in beta with some known issues.**

## Overview

The Animation Manager provides a centralized system for coordinating animations across both the GUI and hardware components. It replaces the previous approach of scattered animation logic with a consistent API and synchronization mechanism.

## Key Features

- **Centralized Animation Logic**: Single point of control for all animations
- **Consistent API**: Unified interface for creating and managing animations
- **Synchronized Animations**: Coordinate GUI and hardware animations
- **Complex Animation Sequences**: Support for multi-stage animation sequences
- **Event-Driven Architecture**: React to animation events and state changes

## Current Limitations (Beta Status)

The Animation Manager is currently in beta with several known limitations:

- Occasional timing issues with complex animation sequences
- Memory usage increases with animation complexity
- Some animations fail to complete properly when interrupted
- Performance overhead for simple animations
- API may change as we gather more feedback

## Implementation

### Core Components

The Animation Manager is built around these key components:

1. **AnimationManager Class**: Central class that coordinates all animations
2. **Animation Class**: Base class for different animation types
3. **AnimationSequence Class**: Container for multi-stage animations
4. **AnimationEvent System**: Event handling for animation states

### AnimationManager Class

The AnimationManager class provides a simple interface for creating and controlling animations:

```python
class AnimationManager:
    def __init__(self):
        self.animations = {}
        self.active_animations = set()
        self.event_handlers = {}
        
    def create_animation(self, animation_type, **kwargs):
        """Create a new animation of the specified type"""
        animation = animation_type(**kwargs)
        self.animations[animation.id] = animation
        return animation
        
    def start_animation(self, animation_id):
        """Start an animation by ID"""
        if animation_id in self.animations:
            animation = self.animations[animation_id]
            animation.start()
            self.active_animations.add(animation_id)
            self.trigger_event(AnimationEvent.STARTED, animation)
            
    def stop_animation(self, animation_id):
        """Stop an animation by ID"""
        if animation_id in self.active_animations:
            animation = self.animations[animation_id]
            animation.stop()
            self.active_animations.remove(animation_id)
            self.trigger_event(AnimationEvent.STOPPED, animation)
            
    def on_event(self, event_type, handler):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = set()
        self.event_handlers[event_type].add(handler)
        
    def trigger_event(self, event_type, animation):
        """Trigger animation event handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                handler(animation)
```

### Animation Types

The Animation Manager supports various animation types:

- **FadeAnimation**: Gradual opacity changes
- **MoveAnimation**: Movement from one position to another
- **SequenceAnimation**: Series of animation frames
- **ParallelAnimation**: Multiple animations running simultaneously
- **TypewriterAnimation**: Character-by-character typing effect
- **PunchCardAnimation**: Specialized animation for punch card holes

### Creating and Using Animations

To create and manage animations:

```python
# Get the singleton instance
animation_manager = AnimationManager.instance()

# Create an animation
fade_anim = animation_manager.create_animation(
    FadeAnimation,
    target=self.message_label,
    start_opacity=0.0,
    end_opacity=1.0,
    duration=500  # ms
)

# Create a sequence of animations
sequence = animation_manager.create_animation(
    SequenceAnimation,
    animations=[fade_anim, move_anim, type_anim],
    loop=False
)

# Start the animation
animation_manager.start_animation(sequence.id)

# Handle animation events
animation_manager.on_event(AnimationEvent.COMPLETED, self.on_animation_complete)
```

### Animation Synchronization

A key feature of the Animation Manager is synchronization between the GUI and hardware:

```python
def create_synchronized_animation(self, gui_target, hardware_target):
    """Create animations that are synchronized between GUI and hardware"""
    # Create GUI animation
    gui_anim = self.create_animation(
        FadeAnimation,
        target=gui_target,
        start_opacity=0.0,
        end_opacity=1.0,
        duration=500
    )
    
    # Create hardware animation
    hw_anim = self.create_animation(
        LEDAnimation,
        target=hardware_target,
        frames=self.generate_led_frames(),
        duration=500
    )
    
    # Synchronize them with a parallel animation
    sync_anim = self.create_animation(
        ParallelAnimation,
        animations=[gui_anim, hw_anim]
    )
    
    return sync_anim
```

## Best Practices

When using the Animation Manager:

1. **Reuse Animations**: Create animations once and reuse them
2. **Use Sequences**: Combine animations into sequences for complex behaviors
3. **Keep Durations Reasonable**: Very short animations may not render properly
4. **Clean Up**: Make sure to stop animations when components are destroyed
5. **Handle Events**: Always handle animation completion events

## Performance Considerations

The Animation Manager has some performance implications:

- **Memory Usage**: Each animation object uses memory, so limit the number created
- **CPU Usage**: Complex animations may use significant CPU time
- **Event Handling**: Many event handlers can slow down the system
- **Hardware Synchronization**: Coordinating with hardware has overhead

## Future Improvements

Planned enhancements to move the Animation Manager out of beta:

1. **Performance Optimization**: Reduce CPU and memory usage
2. **More Animation Types**: Additional animation options
3. **Better Interrupt Handling**: Properly handle animation interruptions
4. **Timeline Support**: More sophisticated animation sequencing
5. **Enhanced Hardware Sync**: Better synchronization with physical hardware

## Integration Examples

### Splash Screen Animation

```python
def create_splash_animation(self):
    # Create fade-in animation for the logo
    logo_fade = self.create_animation(
        FadeAnimation,
        target=self.logo_label,
        start_opacity=0.0,
        end_opacity=1.0,
        duration=1000
    )
    
    # Create typing animation for the message
    message_type = self.create_animation(
        TypewriterAnimation,
        target=self.message_label,
        text="SYSTEM INITIALIZING...",
        duration=2000
    )
    
    # Create sequence
    splash_sequence = self.create_animation(
        SequenceAnimation,
        animations=[logo_fade, message_type]
    )
    
    return splash_sequence
```

### Punch Card Animation

```python
def create_punch_animation(self, message):
    # Create animation for punching card holes
    punch_anim = self.create_animation(
        PunchCardAnimation,
        target=self.punch_card,
        message=message,
        duration=len(message) * 200  # 200ms per character
    )
    
    # Create hardware LED animation
    led_anim = self.create_animation(
        LEDAnimation,
        target=self.hardware_controller,
        message=message,
        duration=len(message) * 200
    )
    
    # Synchronize them
    sync_anim = self.create_animation(
        ParallelAnimation,
        animations=[punch_anim, led_anim]
    )
    
    return sync_anim
``` 