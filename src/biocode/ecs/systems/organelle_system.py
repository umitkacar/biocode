"""
Organelle System - Manages cellular organelles
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from typing import Tuple, Type
from ..system import System
from ..entity import Entity
from ..components.organelles import OrganelleComponent, OrganelleType
from ..components.biological import EnergyComponent, HealthComponent, StateComponent, CellState


class OrganelleSystem(System):
    """
    Organelle yönetim sistemi
    
    - ATP production
    - Waste management
    - DNA repair
    - Protein synthesis
    """
    
    def __init__(self, priority: int = 6):
        super().__init__(priority)
        self.total_atp_produced = 0.0
        self.total_waste_processed = 0.0
        self.oxygen_level = 0.8  # Environmental oxygen
        
    def required_components(self) -> Tuple[Type, ...]:
        return (OrganelleComponent, EnergyComponent)
        
    def process(self, entity: Entity, delta_time: float):
        """Process organelle functions"""
        organelles = entity.get_component(OrganelleComponent)
        energy = entity.get_component(EnergyComponent)
        
        # Mitochondrial ATP production
        atp_produced = organelles.get_total_atp_production(self.oxygen_level) * delta_time
        self.total_atp_produced += atp_produced
        
        # Convert ATP to energy component
        energy.current = min(energy.maximum, energy.current + atp_produced * 0.1)
        
        # Lysosomal waste processing
        if organelles.lysosomes is not None:
            # Generate waste based on metabolic activity
            metabolic_waste = energy.consumption_rate * delta_time * 0.5
            
            # Process waste
            waste_cleared = organelles.lysosomes.digest_waste(metabolic_waste)
            self.total_waste_processed += waste_cleared
            
            # Accumulate unprocessed waste
            organelles.lysosomes.current_waste += (metabolic_waste - waste_cleared)
            
            # Waste accumulation damages cell
            if organelles.lysosomes.current_waste > organelles.lysosomes.waste_capacity * 0.8:
                if entity.has_component(HealthComponent):
                    health = entity.get_component(HealthComponent)
                    health.current -= 0.5 * delta_time  # Gradual damage
                    
        # Nuclear DNA repair
        if organelles.nucleus and entity.has_component(HealthComponent):
            health = entity.get_component(HealthComponent)
            
            # DNA repair based on nuclear efficiency
            if organelles.nucleus.dna_integrity < 1.0:
                repair_amount = organelles.nucleus.repair_efficiency * delta_time * 0.1
                organelles.nucleus.dna_integrity = min(
                    1.0,
                    organelles.nucleus.dna_integrity + repair_amount
                )
                
            # Critical DNA damage triggers apoptosis
            if organelles.nucleus.dna_integrity < 0.3:
                if entity.has_component(StateComponent):
                    state = entity.get_component(StateComponent)
                    if state.state not in [CellState.DYING, CellState.DEAD]:
                        state.change_state(CellState.DYING, state.last_state_change)
                        entity.add_tag("apoptotic")
                        
        # ER stress response
        if organelles.endoplasmic_reticulum:
            er = organelles.endoplasmic_reticulum
            
            # Check for ER stress
            if er.is_stressed():
                # Reduce protein synthesis
                if organelles.nucleus:
                    organelles.nucleus.transcription_rate *= 0.5
                    
                # Trigger unfolded protein response
                entity.add_tag("er_stress")
            else:
                entity.remove_tag("er_stress")
                
        # Update overall organelle health
        self._update_organelle_damage(organelles, delta_time)
        
    def _update_organelle_damage(self, organelles: OrganelleComponent, delta_time: float):
        """Apply age-related organelle damage"""
        # Gradual organelle deterioration
        damage_rate = 0.001 * delta_time
        
        # Mitochondria are especially vulnerable to oxidative damage
        organelles.update_organelle_health(OrganelleType.MITOCHONDRIA, damage_rate * 2)
        
        # Other organelles deteriorate slower
        organelles.update_organelle_health(OrganelleType.NUCLEUS, damage_rate * 0.5)
        if organelles.lysosomes is not None:
            organelles.update_organelle_health(OrganelleType.LYSOSOME, damage_rate)
        organelles.update_organelle_health(OrganelleType.ENDOPLASMIC_RETICULUM, damage_rate)
        
    def set_oxygen_level(self, level: float):
        """Set environmental oxygen level"""
        self.oxygen_level = max(0.0, min(1.0, level))
        
    def get_stats(self) -> dict:
        """Get system statistics"""
        stats = super().get_stats()
        stats.update({
            "total_atp_produced": self.total_atp_produced,
            "total_waste_processed": self.total_waste_processed,
            "oxygen_level": self.oxygen_level
        })
        return stats