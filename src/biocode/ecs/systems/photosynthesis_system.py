"""
Photosynthesis System - Manages photosynthetic energy production
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from typing import Tuple, Type
from ..system import System
from ..entity import Entity
from ..components.specialized import PhotosynthesisComponent
from ..components.biological import EnergyComponent
from ..components.movement import PositionComponent
import math


class PhotosynthesisSystem(System):
    """
    Fotosentez sistemi
    
    - Light-based energy production
    - Environmental factors
    - Resource conversion
    """
    
    def __init__(self, priority: int = 5):
        super().__init__(priority)
        self.total_glucose_produced = 0.0
        self.total_oxygen_produced = 0.0
        
        # Environmental parameters
        self.sun_position = (0.0, 100.0, 0.0)  # Simulated sun
        self.ambient_light = 0.3
        self.co2_level = 0.04  # 400 ppm
        self.temperature = 25.0  # Celsius
        
    def required_components(self) -> Tuple[Type, ...]:
        return (PhotosynthesisComponent, EnergyComponent)
        
    def process(self, entity: Entity, delta_time: float):
        """Process photosynthesis for entity"""
        photo = entity.get_component(PhotosynthesisComponent)
        energy = entity.get_component(EnergyComponent)
        
        # Calculate light intensity based on position
        light_intensity = self._calculate_light_intensity(entity)
        photo.light_intensity = light_intensity
        
        # Set environmental factors
        photo.co2_concentration = self.co2_level
        photo.temperature_efficiency = self._calculate_temperature_efficiency()
        
        # Calculate glucose production
        glucose_produced = photo.calculate_glucose_production(delta_time)
        self.total_glucose_produced += glucose_produced
        
        # Calculate oxygen production
        oxygen_produced = photo.calculate_oxygen_production(glucose_produced)
        self.total_oxygen_produced += oxygen_produced
        
        # Convert glucose to energy (simplified)
        energy_gained = glucose_produced * 10.0  # Arbitrary conversion factor
        energy.current = min(energy.maximum, energy.current + energy_gained)
        
        # Tag highly productive entities
        if glucose_produced > 0.5 * delta_time:
            entity.add_tag("high_photosynthesis")
        else:
            entity.remove_tag("high_photosynthesis")
            
    def _calculate_light_intensity(self, entity: Entity) -> float:
        """Calculate light intensity at entity position"""
        base_intensity = self.ambient_light
        
        if entity.has_component(PositionComponent):
            pos = entity.get_component(PositionComponent)
            
            # Simple light model: intensity decreases with distance from sun
            # and based on angle (simulating day/night)
            dx = pos.x - self.sun_position[0]
            dy = pos.y - self.sun_position[1]
            dz = pos.z - self.sun_position[2]
            
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            # Inverse square law with max cap
            if distance > 0:
                sun_intensity = min(1.0, 10000.0 / (distance * distance))
            else:
                sun_intensity = 1.0
                
            # Simple shading: entities below y=0 get less light
            if pos.y < 0:
                sun_intensity *= 0.1
                
            base_intensity += sun_intensity
            
        return min(1.0, base_intensity)
        
    def _calculate_temperature_efficiency(self) -> float:
        """Calculate photosynthesis efficiency based on temperature"""
        # Optimal around 25°C, decreases outside range
        optimal_temp = 25.0
        temp_diff = abs(self.temperature - optimal_temp)
        
        if temp_diff < 5:
            return 1.0
        elif temp_diff < 10:
            return 0.8
        elif temp_diff < 15:
            return 0.5
        else:
            return 0.2
            
    def set_environmental_conditions(self, temperature: float, co2_level: float,
                                   sun_position: Tuple[float, float, float]):
        """Update environmental conditions"""
        self.temperature = temperature
        self.co2_level = co2_level
        self.sun_position = sun_position
        
    def get_stats(self) -> dict:
        """Get system statistics"""
        stats = super().get_stats()
        stats.update({
            "total_glucose_produced": self.total_glucose_produced,
            "total_oxygen_produced": self.total_oxygen_produced,
            "temperature": self.temperature,
            "co2_level": self.co2_level,
            "sun_position": self.sun_position
        })
        return stats