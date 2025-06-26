"""
Observable Mixin - Entity change tracking and notifications
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from typing import Dict, List, Callable, Any, Optional
from enum import Enum


class ChangeType(Enum):
    """Types of entity changes"""
    COMPONENT_ADDED = "component_added"
    COMPONENT_REMOVED = "component_removed"
    COMPONENT_MODIFIED = "component_modified"
    TAG_ADDED = "tag_added"
    TAG_REMOVED = "tag_removed"
    STATE_CHANGED = "state_changed"


class ObservableMixin:
    """
    Adds observation capabilities to entities
    
    Allows external observers to track entity changes.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize observable"""
        super().__init__(*args, **kwargs)
        self._observers: Dict[str, List[Callable]] = {
            change_type.value: [] for change_type in ChangeType
        }
        self._change_history: List[Dict[str, Any]] = []
        self._recording_changes = True
        self._max_history_size = 100
        
    def add_observer(self, change_type: ChangeType, callback: Callable):
        """
        Add observer for specific change type
        
        Args:
            change_type: Type of change to observe
            callback: Function to call on change
        """
        self._observers[change_type.value].append(callback)
        
    def remove_observer(self, change_type: ChangeType, callback: Callable):
        """
        Remove observer
        
        Args:
            change_type: Type of change
            callback: Callback to remove
        """
        if callback in self._observers[change_type.value]:
            self._observers[change_type.value].remove(callback)
            
    def notify_observers(self, change_type: ChangeType, **kwargs):
        """
        Notify all observers of a change
        
        Args:
            change_type: Type of change
            **kwargs: Additional change data
        """
        for callback in self._observers[change_type.value]:
            try:
                callback(self, change_type, **kwargs)
            except Exception as e:
                print(f"Observer error: {e}")
                
        # Record change
        if self._recording_changes:
            self._record_change(change_type, kwargs)
            
    def _record_change(self, change_type: ChangeType, data: Dict[str, Any]):
        """Record change in history"""
        import time
        
        change = {
            'timestamp': time.time(),
            'type': change_type.value,
            'data': data
        }
        
        self._change_history.append(change)
        
        # Limit history size
        if len(self._change_history) > self._max_history_size:
            self._change_history.pop(0)
            
    # Override Entity methods to add notifications
    def add_component(self, component):
        """Add component with notification"""
        result = super().add_component(component)
        self.notify_observers(
            ChangeType.COMPONENT_ADDED,
            component_type=type(component),
            component=component
        )
        return result
        
    def remove_component(self, component_type):
        """Remove component with notification"""
        component = super().remove_component(component_type)
        if component:
            self.notify_observers(
                ChangeType.COMPONENT_REMOVED,
                component_type=component_type,
                component=component
            )
        return component
        
    def add_tag(self, tag: str):
        """Add tag with notification"""
        super().add_tag(tag)
        self.notify_observers(
            ChangeType.TAG_ADDED,
            tag=tag
        )
        
    def remove_tag(self, tag: str):
        """Remove tag with notification"""
        super().remove_tag(tag)
        self.notify_observers(
            ChangeType.TAG_REMOVED,
            tag=tag
        )
        
    def get_change_history(self, change_type: Optional[ChangeType] = None) -> List[Dict[str, Any]]:
        """
        Get change history
        
        Args:
            change_type: Filter by specific change type
            
        Returns:
            List of changes
        """
        if change_type:
            return [
                change for change in self._change_history
                if change['type'] == change_type.value
            ]
        return self._change_history.copy()
        
    def clear_change_history(self):
        """Clear all change history"""
        self._change_history.clear()
        
    def set_recording_changes(self, enabled: bool):
        """Enable/disable change recording"""
        self._recording_changes = enabled