"""
Energy System - Manages energy production and consumption
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from typing import Tuple, Type
from ..system import System
from ..entity import Entity
from ..components.biological import EnergyComponent, StateComponent, CellState


class EnergySystem(System):
    """
    Enerji yönetim sistemi
    
    - Energy consumption
    - Energy production
    - Starvation handling
    """
    
    def __init__(self, priority: int = 1):
        super().__init__(priority)
        self.total_energy_consumed = 0.0
        self.total_energy_produced = 0.0
        self.starvation_count = 0
        
    def required_components(self) -> Tuple[Type, ...]:
        return (EnergyComponent,)
        
    def process(self, entity: Entity, delta_time: float):
        """Update entity energy"""
        energy = entity.get_component(EnergyComponent)
        
        # Base energy consumption
        consumption = energy.consumption_rate * delta_time
        
        # Adjust consumption based on state
        if entity.has_component(StateComponent):
            state = entity.get_component(StateComponent)
            
            # State-based consumption multipliers
            if state.state == CellState.DORMANT:
                consumption *= 0.1  # Very low consumption when dormant
            elif state.state == CellState.DIVIDING:
                consumption *= 2.0  # High consumption when dividing
            elif state.state == CellState.DYING:
                consumption *= 0.5  # Reduced consumption when dying
                
        # Apply consumption
        energy.current -= consumption
        self.total_energy_consumed += consumption
        
        # Base energy production (if any)
        production = energy.production_rate * delta_time
        energy.current += production
        self.total_energy_produced += production
        
        # Clamp energy values
        energy.current = max(0, min(energy.current, energy.maximum))
        
        # Check for starvation
        if energy.is_depleted():
            entity.add_tag("starving")
            self.starvation_count += 1
            
            # Trigger death if has state component
            if entity.has_component(StateComponent):
                state = entity.get_component(StateComponent)
                if state.state != CellState.DYING and state.state != CellState.DEAD:
                    state.change_state(CellState.DYING, state.last_state_change)
        else:
            entity.remove_tag("starving")
            
    def get_stats(self) -> dict:
        """Get system statistics"""
        stats = super().get_stats()
        stats.update({
            "total_energy_consumed": self.total_energy_consumed,
            "total_energy_produced": self.total_energy_produced,
            "net_energy": self.total_energy_produced - self.total_energy_consumed,
            "starvation_count": self.starvation_count
        })
        return stats