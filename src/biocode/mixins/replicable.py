"""
Replicable Mixin - Entity replication and cloning
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import copy
from typing import Optional, Dict, Any, List, Set, Callable
from enum import Enum


class ReplicationMode(Enum):
    """Replication modes"""
    SHALLOW = "shallow"  # Copy references
    DEEP = "deep"       # Deep copy all data
    SELECTIVE = "selective"  # Copy only specified components
    TEMPLATE = "template"    # Create from template


class ReplicableMixin:
    """
    Adds replication capabilities to entities
    
    Enables cloning, templating, and entity duplication.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize replicable"""
        super().__init__(*args, **kwargs)
        self._replication_template: Optional[Dict[str, Any]] = None
        self._replication_excludes: Set[type] = set()
        self._replication_callbacks = []
        
    def replicate(self, mode: ReplicationMode = ReplicationMode.DEEP,
                 world=None, **kwargs) -> 'Entity':
        """
        Create a replica of this entity
        
        Args:
            mode: Replication mode
            world: Optional world to add replica to
            **kwargs: Additional parameters for replication
            
        Returns:
            Replicated entity
        """
        if mode == ReplicationMode.SHALLOW:
            replica = self._shallow_replicate()
        elif mode == ReplicationMode.DEEP:
            replica = self._deep_replicate()
        elif mode == ReplicationMode.SELECTIVE:
            components = kwargs.get('components', [])
            replica = self._selective_replicate(components)
        elif mode == ReplicationMode.TEMPLATE:
            replica = self._template_replicate()
        else:
            raise ValueError(f"Unknown replication mode: {mode}")
            
        # Post-process replica
        self._post_process_replica(replica, **kwargs)
        
        # Add to world if provided
        if world:
            world.add_entity(replica)
            
        # Notify callbacks
        for callback in self._replication_callbacks:
            callback(self, replica, mode)
            
        return replica
        
    def _shallow_replicate(self) -> 'Entity':
        """Create shallow copy"""
        from ..ecs import Entity
        
        replica = Entity()
        
        # Copy basic attributes
        replica.active = self.active
        replica.tags = self.tags.copy()
        
        # Shallow copy components (references)
        for comp_type, component in self.components.items():
            if comp_type not in self._replication_excludes:
                replica.components[comp_type] = component
                
        return replica
        
    def _deep_replicate(self) -> 'Entity':
        """Create deep copy"""
        from ..ecs import Entity
        
        replica = Entity()
        
        # Copy basic attributes
        replica.active = self.active
        replica.tags = self.tags.copy()
        
        # Deep copy components
        for comp_type, component in self.components.items():
            if comp_type not in self._replication_excludes:
                try:
                    # Try deep copy
                    replica.components[comp_type] = copy.deepcopy(component)
                except:
                    # Fallback to reference if deep copy fails
                    replica.components[comp_type] = component
                    
        return replica
        
    def _selective_replicate(self, component_types: List[type]) -> 'Entity':
        """Create selective copy"""
        from ..ecs import Entity
        
        replica = Entity()
        
        # Copy basic attributes
        replica.active = self.active
        replica.tags = self.tags.copy()
        
        # Copy only selected components
        for comp_type in component_types:
            if comp_type in self.components and comp_type not in self._replication_excludes:
                try:
                    replica.components[comp_type] = copy.deepcopy(self.components[comp_type])
                except:
                    replica.components[comp_type] = self.components[comp_type]
                    
        return replica
        
    def _template_replicate(self) -> 'Entity':
        """Create from template"""
        from ..ecs import Entity
        
        if not self._replication_template:
            # Use self as template
            return self._deep_replicate()
            
        # Create from template data
        replica = Entity()
        
        # Apply template
        template = self._replication_template
        
        replica.active = template.get('active', True)
        
        for tag in template.get('tags', []):
            replica.add_tag(tag)
            
        # Note: Component reconstruction would need registry
        # This is simplified
        
        return replica
        
    def _post_process_replica(self, replica: 'Entity', **kwargs):
        """Post-process replica after creation"""
        # Reset certain components
        if hasattr(replica, 'get_component'):
            # Reset life component if exists
            life_comp_type = type(self).__module__.replace('mixins', 'ecs.components.biological') + '.LifeComponent'
            if life_comp_type in replica.components:
                life = replica.components[life_comp_type]
                if hasattr(life, 'birth_time'):
                    import time
                    life.birth_time = time.time()
                    life.age = 0.0
                    
            # Reset health/energy to maximum
            health_comp_type = type(self).__module__.replace('mixins', 'ecs.components.biological') + '.HealthComponent'
            if health_comp_type in replica.components:
                health = replica.components[health_comp_type]
                if hasattr(health, 'current') and hasattr(health, 'maximum'):
                    health.current = health.maximum
                    
        # Apply custom modifications
        if 'position_offset' in kwargs:
            self._apply_position_offset(replica, kwargs['position_offset'])
            
        # Add replication tag
        replica.add_tag('replicated')
        
        # Clear certain tags
        tags_to_clear = kwargs.get('clear_tags', ['dead', 'dying', 'infected'])
        for tag in tags_to_clear:
            replica.remove_tag(tag)
            
    def _apply_position_offset(self, replica: 'Entity', offset: tuple):
        """Apply position offset to replica"""
        pos_comp_type = type(self).__module__.replace('mixins', 'ecs.components.movement') + '.PositionComponent'
        
        if pos_comp_type in replica.components:
            pos = replica.components[pos_comp_type]
            if hasattr(pos, 'x') and hasattr(pos, 'y') and hasattr(pos, 'z'):
                pos.x += offset[0] if len(offset) > 0 else 0
                pos.y += offset[1] if len(offset) > 1 else 0
                pos.z += offset[2] if len(offset) > 2 else 0
                
    def set_replication_template(self, template: Dict[str, Any]):
        """
        Set template for replication
        
        Args:
            template: Template data
        """
        self._replication_template = template
        
    def exclude_component_from_replication(self, component_type: type):
        """
        Exclude component type from replication
        
        Args:
            component_type: Component type to exclude
        """
        self._replication_excludes.add(component_type)
        
    def include_component_in_replication(self, component_type: type):
        """
        Include component type in replication
        
        Args:
            component_type: Component type to include
        """
        self._replication_excludes.discard(component_type)
        
    def add_replication_callback(self, callback: Callable):
        """Add callback for replication events"""
        self._replication_callbacks.append(callback)
        
    def remove_replication_callback(self, callback: Callable):
        """Remove replication callback"""
        if callback in self._replication_callbacks:
            self._replication_callbacks.remove(callback)
            
    def clone(self, **kwargs) -> 'Entity':
        """
        Convenience method for deep replication
        
        Args:
            **kwargs: Parameters for replication
            
        Returns:
            Cloned entity
        """
        return self.replicate(ReplicationMode.DEEP, **kwargs)
        
    def spawn(self, count: int = 1, **kwargs) -> List['Entity']:
        """
        Spawn multiple replicas
        
        Args:
            count: Number of replicas to create
            **kwargs: Parameters for replication
            
        Returns:
            List of spawned entities
        """
        replicas = []
        
        for i in range(count):
            # Add spawn index for unique positioning
            spawn_kwargs = kwargs.copy()
            if 'position_offset' in spawn_kwargs:
                # Modify offset for each spawn
                base_offset = spawn_kwargs['position_offset']
                spawn_kwargs['position_offset'] = (
                    base_offset[0] + i * 2,
                    base_offset[1],
                    base_offset[2]
                )
                
            replica = self.replicate(**spawn_kwargs)
            replica.add_tag(f'spawn_{i}')
            replicas.append(replica)
            
        return replicas