"""
Enhanced Entity - Entity with all mixin capabilities
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

WARNING: This is LIVING CODE with autonomous behaviors.
It can grow, reproduce, mutate, and die. Use at your own risk.
"""
from ..ecs import Entity
from .serializable import SerializableMixin
from .observable import ObservableMixin
from .networkable import NetworkableMixin
from .persistable import PersistableMixin
from .cacheable import CacheableMixin
from .replicable import ReplicableMixin
from .versionable import VersionableMixin
from .validatable import ValidatableMixin


class EnhancedEntity(
    SerializableMixin,
    ObservableMixin,
    NetworkableMixin,
    PersistableMixin,
    CacheableMixin,
    ReplicableMixin,
    VersionableMixin,
    ValidatableMixin,
    Entity
):
    """
    Enhanced Entity with all mixin capabilities
    
    This entity has:
    - Serialization (JSON, Binary)
    - Observation (Change tracking)
    - Networking (Synchronization)
    - Persistence (Save/Load)
    - Caching (Performance)
    - Replication (Cloning)
    - Versioning (History)
    - Validation (Integrity)
    
    All while maintaining pure ECS principles!
    """
    
    def __init__(self, entity_id=None):
        """Initialize enhanced entity with all capabilities"""
        super().__init__(entity_id=entity_id)
        
        # Set up cross-mixin integrations
        self._setup_integrations()
        
    def _setup_integrations(self):
        """Set up integrations between mixins"""
        # When entity changes, mark as dirty for persistence
        if hasattr(self, 'add_observer') and hasattr(self, 'mark_dirty'):
            from .observable import ChangeType
            
            def mark_dirty_on_change(entity, change_type, **kwargs):
                self.mark_dirty()
                
            self.add_observer(ChangeType.COMPONENT_ADDED, mark_dirty_on_change)
            self.add_observer(ChangeType.COMPONENT_REMOVED, mark_dirty_on_change)
            self.add_observer(ChangeType.COMPONENT_MODIFIED, mark_dirty_on_change)
            
        # When component changes, invalidate cache
        if hasattr(self, 'add_observer') and hasattr(self, 'cache_invalidate'):
            from .observable import ChangeType
            
            def invalidate_cache_on_change(entity, change_type, **kwargs):
                # Invalidate component-related caches
                if 'component_type' in kwargs:
                    comp_type = kwargs['component_type']
                    self.cache_invalidate_pattern(f"component:{comp_type.__name__}")
                    
            self.add_observer(ChangeType.COMPONENT_ADDED, invalidate_cache_on_change)
            self.add_observer(ChangeType.COMPONENT_REMOVED, invalidate_cache_on_change)
            self.add_observer(ChangeType.COMPONENT_MODIFIED, invalidate_cache_on_change)
            
        # When networked, mark components as dirty
        if hasattr(self, 'add_observer') and hasattr(self, 'mark_component_dirty'):
            from .observable import ChangeType
            
            def mark_network_dirty_on_change(entity, change_type, **kwargs):
                if 'component_type' in kwargs:
                    self.mark_component_dirty(kwargs['component_type'])
                    
            self.add_observer(ChangeType.COMPONENT_MODIFIED, mark_network_dirty_on_change)
            
    def save(self, backend=None, validate=True):
        """
        Enhanced save with validation
        
        Args:
            backend: Persistence backend (uses default if None)
            validate: Whether to validate before saving
            
        Returns:
            True if successful
        """
        # Validate first if requested
        if validate and hasattr(self, 'is_valid'):
            if not self.is_valid():
                print("Entity validation failed. Fix issues before saving.")
                issues = self.validate()
                for issue in issues:
                    print(f"  - {issue}")
                return False
                
        # Use persistence mixin
        if hasattr(self, 'save_to_backend'):
            if backend is None:
                # Use default in-memory backend
                from .persistable import InMemoryBackend
                backend = InMemoryBackend()
                
            return self.save_to_backend(backend)
            
        return False
        
    def sync(self):
        """
        Synchronize entity across network
        
        Returns:
            Sync data if networking is enabled
        """
        if hasattr(self, 'needs_sync') and hasattr(self, 'get_sync_data'):
            if self.needs_sync():
                return self.get_sync_data()
                
        return None
        
    def snapshot(self, message="Manual snapshot"):
        """
        Create a version snapshot
        
        Args:
            message: Snapshot description
        """
        if hasattr(self, 'create_version'):
            self.create_version(message)
            
    def spawn_copy(self, offset=(2, 0, 0), world=None):
        """
        Spawn a copy of this entity
        
        Args:
            offset: Position offset for spawned copy
            world: World to add copy to
            
        Returns:
            Spawned entity
        """
        if hasattr(self, 'clone'):
            return self.clone(position_offset=offset, world=world)
            
        return None
        
    def get_status(self) -> dict:
        """
        Get comprehensive entity status
        
        Returns:
            Dictionary with all status information
        """
        status = {
            'id': self.id,
            'tags': list(self.tags),
            'active': self.active,
            'component_count': len(self.components)
        }
        
        # Add validation status
        if hasattr(self, 'get_validation_summary'):
            status['validation'] = self.get_validation_summary()
            
        # Add version info
        if hasattr(self, 'get_version'):
            status['version'] = self.get_version()
            
        # Add cache stats
        if hasattr(self, 'get_cache_stats'):
            status['cache'] = self.get_cache_stats()
            
        # Add persistence info
        if hasattr(self, 'get_save_info'):
            status['persistence'] = self.get_save_info()
            
        # Add network info
        if hasattr(self, 'get_network_id'):
            status['network_id'] = self.get_network_id()
            
        return status
        
    def __repr__(self) -> str:
        """Enhanced string representation"""
        base = super().__repr__()
        
        extras = []
        
        if hasattr(self, 'get_version'):
            extras.append(f"v{self.get_version()}")
            
        if hasattr(self, 'is_dirty') and self.is_dirty():
            extras.append("dirty")
            
        if hasattr(self, 'get_network_id') and self.get_network_id():
            extras.append(f"net:{self.get_network_id()[:8]}")
            
        if extras:
            return base.replace(")", f", {', '.join(extras)})")
            
        return base