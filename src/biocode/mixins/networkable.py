"""
Networkable Mixin - Network synchronization capabilities
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import time
from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum


class SyncMode(Enum):
    """Network synchronization modes"""
    RELIABLE = "reliable"      # TCP-like, guaranteed delivery
    UNRELIABLE = "unreliable"  # UDP-like, fast but lossy
    BROADCAST = "broadcast"    # Send to all clients
    UNICAST = "unicast"        # Send to specific client


@dataclass
class NetworkState:
    """Network synchronization state"""
    last_sync_time: float = 0.0
    sync_frequency: float = 0.1  # 10Hz default
    dirty_components: Set[type] = field(default_factory=set)
    owner_id: Optional[str] = None
    authority: bool = False  # Has authority to modify
    interpolation_buffer: List[Dict[str, Any]] = field(default_factory=list)


class NetworkableMixin:
    """
    Adds network synchronization to entities
    
    Enables entities to be synchronized across network boundaries.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize networkable"""
        super().__init__(*args, **kwargs)
        self._network_state = NetworkState()
        self._sync_callbacks = []
        self._network_id = None  # Unique network identifier
        
    def set_network_id(self, network_id: str):
        """Set unique network identifier"""
        self._network_id = network_id
        
    def get_network_id(self) -> Optional[str]:
        """Get network identifier"""
        return self._network_id
        
    def set_network_authority(self, has_authority: bool):
        """
        Set whether this instance has authority over the entity
        
        Args:
            has_authority: True if this instance can modify the entity
        """
        self._network_state.authority = has_authority
        
    def set_network_owner(self, owner_id: str):
        """
        Set the network owner of this entity
        
        Args:
            owner_id: ID of the owning client/player
        """
        self._network_state.owner_id = owner_id
        
    def mark_component_dirty(self, component_type: type):
        """
        Mark component as needing synchronization
        
        Args:
            component_type: Type of component that changed
        """
        self._network_state.dirty_components.add(component_type)
        
    def needs_sync(self) -> bool:
        """Check if entity needs network synchronization"""
        current_time = time.time()
        time_since_sync = current_time - self._network_state.last_sync_time
        
        return (
            len(self._network_state.dirty_components) > 0 and
            time_since_sync >= self._network_state.sync_frequency
        )
        
    def get_sync_data(self, mode: SyncMode = SyncMode.RELIABLE) -> Dict[str, Any]:
        """
        Get data for network synchronization
        
        Args:
            mode: Synchronization mode
            
        Returns:
            Dictionary with sync data
        """
        sync_data = {
            'network_id': self._network_id,
            'entity_id': self.id,
            'timestamp': time.time(),
            'mode': mode.value,
            'components': {}
        }
        
        # Include only dirty components
        for comp_type in self._network_state.dirty_components:
            if comp_type in self.components:
                component = self.components[comp_type]
                
                # Serialize component data
                if hasattr(component, '__dict__'):
                    comp_data = {}
                    
                    # For unreliable mode, only send essential data
                    if mode == SyncMode.UNRELIABLE:
                        # Define essential fields per component type
                        essential_fields = self._get_essential_fields(comp_type)
                        for field in essential_fields:
                            if hasattr(component, field):
                                comp_data[field] = getattr(component, field)
                    else:
                        # Send all data for reliable mode
                        comp_data = dict(component.__dict__)
                        
                    sync_data['components'][comp_type.__name__] = comp_data
                    
        # Clear dirty flags after sync
        self._network_state.dirty_components.clear()
        self._network_state.last_sync_time = time.time()
        
        return sync_data
        
    def apply_sync_data(self, sync_data: Dict[str, Any]):
        """
        Apply received synchronization data
        
        Args:
            sync_data: Synchronization data from network
        """
        # Don't apply if we have authority
        if self._network_state.authority:
            return
            
        timestamp = sync_data.get('timestamp', 0)
        
        # Add to interpolation buffer for smooth updates
        self._network_state.interpolation_buffer.append({
            'timestamp': timestamp,
            'data': sync_data
        })
        
        # Keep buffer size limited
        if len(self._network_state.interpolation_buffer) > 10:
            self._network_state.interpolation_buffer.pop(0)
            
        # Apply component updates
        for comp_name, comp_data in sync_data.get('components', {}).items():
            # Find component by name
            for comp_type, component in self.components.items():
                if comp_type.__name__ == comp_name:
                    # Update component fields
                    for field, value in comp_data.items():
                        if hasattr(component, field):
                            setattr(component, field, value)
                    break
                    
        # Notify sync callbacks
        for callback in self._sync_callbacks:
            callback(self, sync_data)
            
    def add_sync_callback(self, callback: Callable):
        """Add callback for sync events"""
        self._sync_callbacks.append(callback)
        
    def remove_sync_callback(self, callback: Callable):
        """Remove sync callback"""
        if callback in self._sync_callbacks:
            self._sync_callbacks.remove(callback)
            
    def interpolate_state(self, current_time: float):
        """
        Interpolate entity state for smooth networking
        
        Args:
            current_time: Current time for interpolation
        """
        if len(self._network_state.interpolation_buffer) < 2:
            return
            
        # Find two states to interpolate between
        prev_state = None
        next_state = None
        
        for state in self._network_state.interpolation_buffer:
            if state['timestamp'] <= current_time:
                prev_state = state
            else:
                next_state = state
                break
                
        if prev_state and next_state:
            # Calculate interpolation factor
            time_diff = next_state['timestamp'] - prev_state['timestamp']
            if time_diff > 0:
                alpha = (current_time - prev_state['timestamp']) / time_diff
                alpha = max(0, min(1, alpha))
                
                # Interpolate position if available
                self._interpolate_position(prev_state, next_state, alpha)
                
    def _interpolate_position(self, prev_state: Dict, next_state: Dict, alpha: float):
        """Interpolate position component between states"""
        from ..ecs.components.movement import PositionComponent
        
        if not self.has_component(PositionComponent):
            return
            
        prev_pos = prev_state['data'].get('components', {}).get('PositionComponent', {})
        next_pos = next_state['data'].get('components', {}).get('PositionComponent', {})
        
        if prev_pos and next_pos:
            pos = self.get_component(PositionComponent)
            
            # Linear interpolation
            if 'x' in prev_pos and 'x' in next_pos:
                pos.x = prev_pos['x'] + (next_pos['x'] - prev_pos['x']) * alpha
            if 'y' in prev_pos and 'y' in next_pos:
                pos.y = prev_pos['y'] + (next_pos['y'] - prev_pos['y']) * alpha
            if 'z' in prev_pos and 'z' in next_pos:
                pos.z = prev_pos['z'] + (next_pos['z'] - prev_pos['z']) * alpha
                
    def _get_essential_fields(self, component_type: type) -> List[str]:
        """Get essential fields for unreliable sync"""
        # Define essential fields per component type
        essential_fields_map = {
            'PositionComponent': ['x', 'y', 'z'],
            'VelocityComponent': ['dx', 'dy', 'dz'],
            'HealthComponent': ['current'],
            'EnergyComponent': ['current'],
            'StateComponent': ['state']
        }
        
        return essential_fields_map.get(component_type.__name__, [])