"""
System Base - Pure Logic Processing
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

WARNING: This is LIVING CODE with autonomous behaviors.
It can grow, reproduce, mutate, and die. Use at your own risk.
"""
from abc import ABC, abstractmethod
from typing import Set, Type, Tuple, List, Dict, Any, Optional
from .entity import Entity


class System(ABC):
    """
    Base System - Sadece logic, veri yok
    
    ECS mimarisinde System'ler sadece logic içerir.
    Entity'leri component'lerine göre filtreler ve işler.
    """
    
    def __init__(self, priority: int = 0):
        """
        Initialize system with execution priority
        
        Args:
            priority: Execution order (lower = earlier)
        """
        self.priority = priority
        self.enabled = True
        self._required_components: Set[Type] = set()
        self._excluded_components: Set[Type] = set()
        self._required_tags: Set[str] = set()
        self._excluded_tags: Set[str] = set()
        
    @abstractmethod
    def required_components(self) -> Tuple[Type, ...]:
        """
        Bu system'in çalışması için gerekli component'ler
        
        Returns:
            Tuple of required component types
        """
        pass
        
    def excluded_components(self) -> Tuple[Type, ...]:
        """
        Bu component'lere sahip entity'ler hariç tutulur
        
        Returns:
            Tuple of excluded component types
        """
        return ()
        
    def required_tags(self) -> Tuple[str, ...]:
        """
        Entity'de bulunması gereken tag'ler
        
        Returns:
            Tuple of required tags
        """
        return ()
        
    def excluded_tags(self) -> Tuple[str, ...]:
        """
        Entity'de bulunmaması gereken tag'ler
        
        Returns:
            Tuple of excluded tags
        """
        return ()
        
    def matches_entity(self, entity: Entity) -> bool:
        """
        Entity'nin bu system tarafından işlenip işlenmeyeceğini kontrol et
        
        Args:
            entity: Entity to check
            
        Returns:
            True if entity matches all criteria
        """
        if not entity.active:
            return False
            
        # Check required components
        for comp_type in self.required_components():
            if not entity.has_component(comp_type):
                return False
                
        # Check excluded components
        for comp_type in self.excluded_components():
            if entity.has_component(comp_type):
                return False
                
        # Check required tags
        for tag in self.required_tags():
            if not entity.has_tag(tag):
                return False
                
        # Check excluded tags
        for tag in self.excluded_tags():
            if entity.has_tag(tag):
                return False
                
        return True
        
    @abstractmethod
    def process(self, entity: Entity, delta_time: float):
        """
        Process tek bir entity
        
        Args:
            entity: Entity to process
            delta_time: Time since last update in seconds
        """
        pass
        
    def process_batch(self, entities: List[Entity], delta_time: float):
        """
        Process entity batch - override for optimization
        
        Args:
            entities: List of matching entities
            delta_time: Time since last update
        """
        for entity in entities:
            if self.matches_entity(entity):
                self.process(entity, delta_time)
                
    def on_entity_added(self, entity: Entity):
        """
        Entity system'e eklendiğinde çağrılır
        
        Args:
            entity: Newly added entity
        """
        pass
        
    def on_entity_removed(self, entity: Entity):
        """
        Entity system'den çıkarıldığında çağrılır
        
        Args:
            entity: Removed entity
        """
        pass
        
    def on_component_added(self, entity: Entity, component_type: Type):
        """
        Entity'ye component eklendiğinde
        
        Args:
            entity: Entity that received component
            component_type: Type of added component
        """
        pass
        
    def on_component_removed(self, entity: Entity, component_type: Type):
        """
        Entity'den component çıkarıldığında
        
        Args:
            entity: Entity that lost component
            component_type: Type of removed component
        """
        pass
        
    def initialize(self):
        """System başlatma - override if needed"""
        pass
        
    def cleanup(self):
        """System temizleme - override if needed"""
        pass
        
    def get_stats(self) -> Dict[str, Any]:
        """
        System istatistikleri - debugging için
        
        Returns:
            Dictionary of system statistics
        """
        return {
            "enabled": self.enabled,
            "priority": self.priority,
            "required_components": [c.__name__ for c in self.required_components()],
            "excluded_components": [c.__name__ for c in self.excluded_components()],
            "required_tags": list(self.required_tags()),
            "excluded_tags": list(self.excluded_tags())
        }
        
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"{self.__class__.__name__}("
            f"priority={self.priority}, "
            f"enabled={self.enabled})"
        )