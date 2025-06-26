"""
Movement System - Handles entity movement and physics
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from typing import Tuple, Type
from ..system import System
from ..entity import Entity
from ..components.movement import MovementComponent, PositionComponent, VelocityComponent


class MovementSystem(System):
    """
    Hareket ve fizik sistemi
    
    - Position updates
    - Velocity and acceleration
    - Collision detection prep
    """
    
    def __init__(self, priority: int = 2):
        super().__init__(priority)
        self.total_distance_traveled = 0.0
        self.boundary_min = (-100.0, -100.0, -100.0)
        self.boundary_max = (100.0, 100.0, 100.0)
        
    def required_components(self) -> Tuple[Type, ...]:
        return (MovementComponent,)
        
    def process(self, entity: Entity, delta_time: float):
        """Update entity movement"""
        movement = entity.get_component(MovementComponent)
        
        # Store old position for distance tracking
        old_x = movement.position.x
        old_y = movement.position.y
        old_z = movement.position.z
        
        # Update movement physics
        movement.update(delta_time)
        
        # Boundary checking and wrapping
        self._apply_boundary_conditions(movement.position)
        
        # Track total distance
        dx = movement.position.x - old_x
        dy = movement.position.y - old_y
        dz = movement.position.z - old_z
        distance = (dx*dx + dy*dy + dz*dz) ** 0.5
        self.total_distance_traveled += distance
        
        # Update position-based tags
        self._update_position_tags(entity, movement.position)
        
    def _apply_boundary_conditions(self, position: PositionComponent):
        """Apply boundary conditions (wrap-around)"""
        # X boundary
        if position.x < self.boundary_min[0]:
            position.x = self.boundary_max[0]
        elif position.x > self.boundary_max[0]:
            position.x = self.boundary_min[0]
            
        # Y boundary
        if position.y < self.boundary_min[1]:
            position.y = self.boundary_max[1]
        elif position.y > self.boundary_max[1]:
            position.y = self.boundary_min[1]
            
        # Z boundary
        if position.z < self.boundary_min[2]:
            position.z = self.boundary_max[2]
        elif position.z > self.boundary_max[2]:
            position.z = self.boundary_min[2]
            
    def _update_position_tags(self, entity: Entity, position: PositionComponent):
        """Update spatial tags based on position"""
        # Remove old quadrant tags
        for tag in ["quadrant_1", "quadrant_2", "quadrant_3", "quadrant_4"]:
            entity.remove_tag(tag)
            
        # Add new quadrant tag (2D simplification)
        if position.x >= 0 and position.y >= 0:
            entity.add_tag("quadrant_1")
        elif position.x < 0 and position.y >= 0:
            entity.add_tag("quadrant_2")
        elif position.x < 0 and position.y < 0:
            entity.add_tag("quadrant_3")
        else:
            entity.add_tag("quadrant_4")
            
    def get_stats(self) -> dict:
        """Get system statistics"""
        stats = super().get_stats()
        stats.update({
            "total_distance_traveled": self.total_distance_traveled,
            "boundary_min": self.boundary_min,
            "boundary_max": self.boundary_max
        })
        return stats