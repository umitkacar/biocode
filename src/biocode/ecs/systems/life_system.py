"""
Life System - Manages lifecycle and aging
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from typing import Tuple, Type
from ..system import System
from ..entity import Entity
from ..components.biological import LifeComponent, StateComponent, CellState


class LifeSystem(System):
    """
    Yaşam döngüsü yönetimi
    
    - Aging
    - Death checking
    - State transitions
    """
    
    def __init__(self, priority: int = 0):
        super().__init__(priority)
        self.total_deaths = 0
        self.total_births = 0
        
    def required_components(self) -> Tuple[Type, ...]:
        return (LifeComponent, StateComponent)
        
    def process(self, entity: Entity, delta_time: float):
        """Update entity lifecycle"""
        life = entity.get_component(LifeComponent)
        state = entity.get_component(StateComponent)
        
        # Age the entity
        life.age += delta_time
        
        # Check for death
        if not life.is_alive():
            if state.state != CellState.DEAD:
                state.change_state(CellState.DEAD, life.birth_time + life.age)
                self.total_deaths += 1
                entity.active = False
                entity.add_tag("dead")
                
        # Natural state transitions based on age
        elif state.state == CellState.DORMANT and life.age > 1.0:
            # Wake up after initial dormancy
            state.change_state(CellState.ACTIVE, life.birth_time + life.age)
            
        elif state.state == CellState.ACTIVE:
            # Check for natural death approach
            time_until_death = life.time_until_death()
            if time_until_death < life.lifespan * 0.1:  # Last 10% of life
                state.change_state(CellState.DYING, life.birth_time + life.age)
                
    def on_entity_added(self, entity: Entity):
        """Track births"""
        if entity.has_component(LifeComponent):
            self.total_births += 1
            
    def get_stats(self) -> dict:
        """Get system statistics"""
        stats = super().get_stats()
        stats.update({
            "total_births": self.total_births,
            "total_deaths": self.total_deaths,
            "death_rate": self.total_deaths / max(1, self.total_births)
        })
        return stats