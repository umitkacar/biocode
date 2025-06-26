"""
World - ECS Registry and System Manager
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

WARNING: This is LIVING CODE with autonomous behaviors.
It can grow, reproduce, mutate, and die. Use at your own risk.
"""
from typing import Dict, List, Set, Type, Optional, Callable, TypeVar, Any
from collections import defaultdict
import time
from .entity import Entity
from .system import System

T = TypeVar('T')


class World:
    """
    ECS World - Entity, System ve Component yönetimi
    
    Central registry for all ECS operations.
    Manages entity lifecycle, system execution, and component queries.
    """
    
    def __init__(self):
        """Initialize empty world"""
        # Entity storage
        self.entities: Dict[str, Entity] = {}
        self.entity_groups: Dict[str, Set[str]] = defaultdict(set)  # tag -> entity IDs
        
        # System storage
        self.systems: List[System] = []
        self.system_map: Dict[Type[System], System] = {}
        
        # Component indices for fast queries
        self.component_index: Dict[Type, Set[str]] = defaultdict(set)  # component type -> entity IDs
        
        # Event callbacks
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Statistics
        self.stats = {
            "total_entities_created": 0,
            "total_entities_destroyed": 0,
            "total_updates": 0,
            "last_update_time": 0.0,
            "average_update_time": 0.0
        }
        
        # Time tracking
        self.world_time = 0.0
        self.last_update = time.time()
        
    def create_entity(self, entity_id: Optional[str] = None) -> Entity:
        """
        Yeni entity oluştur
        
        Args:
            entity_id: Optional custom ID
            
        Returns:
            Created entity
        """
        entity = Entity(entity_id)
        self.add_entity(entity)
        return entity
        
    def add_entity(self, entity: Entity):
        """
        World'e entity ekle
        
        Args:
            entity: Entity to add
        """
        if entity.id in self.entities:
            raise ValueError(f"Entity {entity.id} already exists in world")
            
        self.entities[entity.id] = entity
        self.stats["total_entities_created"] += 1
        
        # Update indices
        for component_type in entity.components:
            self.component_index[component_type].add(entity.id)
            
        for tag in entity.tags:
            self.entity_groups[tag].add(entity.id)
            
        # Notify systems
        for system in self.systems:
            system.on_entity_added(entity)
            
        # Fire event
        self._fire_event("entity_added", entity)
        
    def remove_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Entity'yi world'den çıkar
        
        Args:
            entity_id: ID of entity to remove
            
        Returns:
            Removed entity or None
        """
        entity = self.entities.pop(entity_id, None)
        if not entity:
            return None
            
        self.stats["total_entities_destroyed"] += 1
        
        # Update indices
        for component_type in entity.components:
            self.component_index[component_type].discard(entity.id)
            
        for tag in entity.tags:
            self.entity_groups[tag].discard(entity.id)
            
        # Notify systems
        for system in self.systems:
            system.on_entity_removed(entity)
            
        # Fire event
        self._fire_event("entity_removed", entity)
        
        return entity
        
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID"""
        return self.entities.get(entity_id)
        
    def add_system(self, system: System):
        """
        System ekle
        
        Args:
            system: System to add
        """
        if type(system) in self.system_map:
            raise ValueError(f"System {type(system).__name__} already exists")
            
        self.systems.append(system)
        self.system_map[type(system)] = system
        
        # Sort by priority
        self.systems.sort(key=lambda s: s.priority)
        
        # Initialize system
        system.initialize()
        
        # Fire event
        self._fire_event("system_added", system)
        
    def remove_system(self, system_type: Type[System]) -> Optional[System]:
        """
        System kaldır
        
        Args:
            system_type: Type of system to remove
            
        Returns:
            Removed system or None
        """
        system = self.system_map.pop(system_type, None)
        if not system:
            return None
            
        self.systems.remove(system)
        
        # Cleanup system
        system.cleanup()
        
        # Fire event
        self._fire_event("system_removed", system)
        
        return system
        
    def get_system(self, system_type: Type[T]) -> Optional[T]:
        """Get system by type"""
        return self.system_map.get(system_type)
        
    def query(self, *component_types: Type) -> List[Entity]:
        """
        Component query - belirli component'lere sahip entity'leri bul
        
        Args:
            component_types: Required component types
            
        Returns:
            List of matching entities
        """
        if not component_types:
            return list(self.entities.values())
            
        # Find entities with all required components
        entity_ids = None
        
        for comp_type in component_types:
            comp_entities = self.component_index.get(comp_type, set())
            
            if entity_ids is None:
                entity_ids = comp_entities.copy()
            else:
                entity_ids &= comp_entities
                
            if not entity_ids:
                return []
                
        return [self.entities[eid] for eid in entity_ids]
        
    def query_by_tag(self, tag: str) -> List[Entity]:
        """
        Tag query - belirli tag'e sahip entity'leri bul
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of matching entities
        """
        entity_ids = self.entity_groups.get(tag, set())
        return [self.entities[eid] for eid in entity_ids]
        
    def update(self, delta_time: Optional[float] = None):
        """
        Tüm system'leri güncelle
        
        Args:
            delta_time: Time since last update (auto-calculated if None)
        """
        start_time = time.time()
        
        # Calculate delta time if not provided
        if delta_time is None:
            current_time = time.time()
            delta_time = current_time - self.last_update
            self.last_update = current_time
            
        self.world_time += delta_time
        
        # Update all systems
        for system in self.systems:
            if system.enabled:
                # Get matching entities for this system
                matching_entities = [
                    entity for entity in self.entities.values()
                    if system.matches_entity(entity)
                ]
                
                # Process batch
                system.process_batch(matching_entities, delta_time)
                
        # Update statistics
        update_duration = time.time() - start_time
        self.stats["total_updates"] += 1
        self.stats["last_update_time"] = update_duration
        
        # Running average
        alpha = 0.1
        self.stats["average_update_time"] = (
            alpha * update_duration + 
            (1 - alpha) * self.stats["average_update_time"]
        )
        
        # Fire event
        self._fire_event("world_updated", delta_time)
        
    def add_component_to_entity(self, entity_id: str, component: Any) -> bool:
        """
        Entity'ye component ekle ve index'leri güncelle
        
        Args:
            entity_id: Target entity ID
            component: Component to add
            
        Returns:
            True if successful
        """
        entity = self.get_entity(entity_id)
        if not entity:
            return False
            
        component_type = type(component)
        entity.add_component(component)
        
        # Update index
        self.component_index[component_type].add(entity_id)
        
        # Notify systems
        for system in self.systems:
            system.on_component_added(entity, component_type)
            
        return True
        
    def remove_component_from_entity(self, entity_id: str, 
                                   component_type: Type) -> bool:
        """
        Entity'den component kaldır
        
        Args:
            entity_id: Target entity ID
            component_type: Type of component to remove
            
        Returns:
            True if successful
        """
        entity = self.get_entity(entity_id)
        if not entity:
            return False
            
        if entity.remove_component(component_type):
            # Update index
            self.component_index[component_type].discard(entity_id)
            
            # Notify systems
            for system in self.systems:
                system.on_component_removed(entity, component_type)
                
            return True
            
        return False
        
    def add_tag_to_entity(self, entity_id: str, tag: str) -> bool:
        """Add tag to entity and update indices"""
        entity = self.get_entity(entity_id)
        if not entity:
            return False
            
        entity.add_tag(tag)
        self.entity_groups[tag].add(entity_id)
        return True
        
    def remove_tag_from_entity(self, entity_id: str, tag: str) -> bool:
        """Remove tag from entity and update indices"""
        entity = self.get_entity(entity_id)
        if not entity:
            return False
            
        entity.remove_tag(tag)
        self.entity_groups[tag].discard(entity_id)
        return True
        
    def register_event_handler(self, event: str, handler: Callable):
        """Register event callback"""
        self.event_handlers[event].append(handler)
        
    def unregister_event_handler(self, event: str, handler: Callable):
        """Unregister event callback"""
        if handler in self.event_handlers[event]:
            self.event_handlers[event].remove(handler)
            
    def _fire_event(self, event: str, *args, **kwargs):
        """Fire event to all registered handlers"""
        for handler in self.event_handlers[event]:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                print(f"Error in event handler for {event}: {e}")
                
    def get_stats(self) -> Dict[str, Any]:
        """Get world statistics"""
        stats = self.stats.copy()
        stats.update({
            "active_entities": len(self.entities),
            "active_systems": len(self.systems),
            "world_time": self.world_time,
            "component_types": len(self.component_index),
            "total_tags": len(self.entity_groups)
        })
        
        # Add system stats
        stats["systems"] = {}
        for system in self.systems:
            stats["systems"][type(system).__name__] = system.get_stats()
            
        return stats
        
    def clear(self):
        """Clear all entities and reset world"""
        # Remove all entities
        entity_ids = list(self.entities.keys())
        for entity_id in entity_ids:
            self.remove_entity(entity_id)
            
        # Clear indices
        self.component_index.clear()
        self.entity_groups.clear()
        
        # Reset time
        self.world_time = 0.0
        self.last_update = time.time()
        
        # Fire event
        self._fire_event("world_cleared")
        
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"World(entities={len(self.entities)}, "
            f"systems={len(self.systems)}, "
            f"time={self.world_time:.2f})"
        )