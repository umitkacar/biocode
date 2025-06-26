"""
Entity - Pure ID and Component Container
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

WARNING: This is LIVING CODE with autonomous behaviors.
It can grow, reproduce, mutate, and die. Use at your own risk.
"""
import uuid
from typing import Type, TypeVar, Optional, Set, Dict

T = TypeVar('T')


class Entity:
    """
    Pure entity - sadece component container
    
    ECS mimarisinde Entity sadece bir ID ve component container'dır.
    Hiçbir davranış içermez, sadece veri tutar.
    """
    
    def __init__(self, entity_id: Optional[str] = None):
        """
        Initialize entity with unique ID
        
        Args:
            entity_id: Optional custom ID, auto-generated if not provided
        """
        self.id = entity_id or str(uuid.uuid4())
        self.components: Dict[Type, object] = {}
        self.tags: Set[str] = set()
        self.active = True
        
    def add_component(self, component: T) -> T:
        """
        Type-safe component ekleme
        
        Args:
            component: Component instance to add
            
        Returns:
            The added component for chaining
        """
        component_type = type(component)
        self.components[component_type] = component
        return component
        
    def get_component(self, component_type: Type[T]) -> Optional[T]:
        """
        Type-safe component alma
        
        Args:
            component_type: Type of component to retrieve
            
        Returns:
            Component instance or None if not found
        """
        return self.components.get(component_type)
        
    def has_component(self, component_type: Type) -> bool:
        """
        Component varlık kontrolü
        
        Args:
            component_type: Type of component to check
            
        Returns:
            True if entity has the component
        """
        return component_type in self.components
        
    def remove_component(self, component_type: Type) -> Optional[object]:
        """
        Component kaldırma
        
        Args:
            component_type: Type of component to remove
            
        Returns:
            Removed component or None if not found
        """
        return self.components.pop(component_type, None)
        
    def add_tag(self, tag: str):
        """
        Semantic tagging for entity categorization
        
        Args:
            tag: Tag string to add
        """
        self.tags.add(tag)
        
    def remove_tag(self, tag: str):
        """
        Remove a tag from entity
        
        Args:
            tag: Tag string to remove
        """
        self.tags.discard(tag)
        
    def has_tag(self, tag: str) -> bool:
        """
        Tag kontrolü
        
        Args:
            tag: Tag to check
            
        Returns:
            True if entity has the tag
        """
        return tag in self.tags
        
    def clear_tags(self):
        """Clear all tags from entity"""
        self.tags.clear()
        
    def __repr__(self) -> str:
        """String representation"""
        component_names = [c.__name__ for c in self.components.keys()]
        return (
            f"Entity(id={self.id[:8]}..., "
            f"components={component_names}, "
            f"tags={self.tags}, "
            f"active={self.active})"
        )