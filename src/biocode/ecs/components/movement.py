"""
Movement Components - Spatial data
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from dataclasses import dataclass
from typing import Tuple, Optional
import math


@dataclass
class PositionComponent:
    """3D position data"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def distance_to(self, other: 'PositionComponent') -> float:
        """Calculate Euclidean distance to another position"""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def as_tuple(self) -> Tuple[float, float, float]:
        """Get position as tuple"""
        return (self.x, self.y, self.z)
    
    def __add__(self, other: 'PositionComponent') -> 'PositionComponent':
        """Add two positions"""
        return PositionComponent(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )
    
    def __sub__(self, other: 'PositionComponent') -> 'PositionComponent':
        """Subtract two positions"""
        return PositionComponent(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )


@dataclass
class VelocityComponent:
    """3D velocity data"""
    dx: float = 0.0
    dy: float = 0.0
    dz: float = 0.0
    
    def magnitude(self) -> float:
        """Calculate velocity magnitude"""
        return math.sqrt(self.dx*self.dx + self.dy*self.dy + self.dz*self.dz)
    
    def normalize(self) -> 'VelocityComponent':
        """Get normalized velocity"""
        mag = self.magnitude()
        if mag > 0:
            return VelocityComponent(
                self.dx / mag,
                self.dy / mag,
                self.dz / mag
            )
        return VelocityComponent(0, 0, 0)
    
    def scale(self, factor: float) -> 'VelocityComponent':
        """Scale velocity by factor"""
        return VelocityComponent(
            self.dx * factor,
            self.dy * factor,
            self.dz * factor
        )


@dataclass
class MovementComponent:
    """Complete movement data combining position and velocity"""
    position: PositionComponent = None
    velocity: VelocityComponent = None
    acceleration: VelocityComponent = None
    max_speed: float = 5.0
    max_acceleration: float = 1.0
    friction: float = 0.1
    
    def __post_init__(self):
        """Initialize sub-components if not provided"""
        if self.position is None:
            self.position = PositionComponent()
        if self.velocity is None:
            self.velocity = VelocityComponent()
        if self.acceleration is None:
            self.acceleration = VelocityComponent()
    
    def apply_force(self, force_x: float, force_y: float, force_z: float):
        """Apply force to acceleration"""
        self.acceleration.dx += force_x
        self.acceleration.dy += force_y
        self.acceleration.dz += force_z
        
        # Limit acceleration
        acc_mag = self.acceleration.magnitude()
        if acc_mag > self.max_acceleration:
            normalized = self.acceleration.normalize()
            self.acceleration = normalized.scale(self.max_acceleration)
    
    def update(self, delta_time: float):
        """Update position based on velocity and acceleration"""
        # Update velocity
        self.velocity.dx += self.acceleration.dx * delta_time
        self.velocity.dy += self.acceleration.dy * delta_time
        self.velocity.dz += self.acceleration.dz * delta_time
        
        # Apply friction
        self.velocity.dx *= (1.0 - self.friction * delta_time)
        self.velocity.dy *= (1.0 - self.friction * delta_time)
        self.velocity.dz *= (1.0 - self.friction * delta_time)
        
        # Limit speed
        speed = self.velocity.magnitude()
        if speed > self.max_speed:
            normalized = self.velocity.normalize()
            self.velocity = normalized.scale(self.max_speed)
        
        # Update position
        self.position.x += self.velocity.dx * delta_time
        self.position.y += self.velocity.dy * delta_time
        self.position.z += self.velocity.dz * delta_time
        
        # Reset acceleration
        self.acceleration = VelocityComponent(0, 0, 0)