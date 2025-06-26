"""
Infection System - Manages pathogens and immune responses
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from typing import Tuple, Type, List, Dict
from ..system import System
from ..entity import Entity
from ..components.infection import InfectionComponent, Pathogen, PathogenType, AntibodyType
from ..components.biological import HealthComponent, StateComponent, CellState, EnergyComponent
from ..components.communication import CommunicationComponent, SignalType
import random
import time


class InfectionSystem(System):
    """
    Enfeksiyon ve bağışıklık sistemi
    
    - Pathogen replication
    - Immune response
    - Antibody production
    - Cell-to-cell spread
    """
    
    def __init__(self, priority: int = 8):
        super().__init__(priority)
        self.total_infections = 0
        self.total_cleared = 0
        self.active_pathogens: Dict[str, int] = {}  # Track pathogen types
        
    def required_components(self) -> Tuple[Type, ...]:
        return (InfectionComponent,)
        
    def process_batch(self, entities: List[Entity], delta_time: float):
        """Process infections across all entities"""
        infected_entities = []
        healthy_entities = []
        
        # Categorize entities
        for entity in entities:
            if not self.matches_entity(entity):
                continue
                
            infection = entity.get_component(InfectionComponent)
            if infection.infected:
                infected_entities.append(entity)
            else:
                healthy_entities.append(entity)
                
        # Process each infected entity
        for entity in infected_entities:
            self._process_infection(entity, delta_time)
            
        # Check for disease spread
        self._check_disease_spread(infected_entities, healthy_entities, delta_time)
        
    def process(self, entity: Entity, delta_time: float):
        """Process single entity - handled in batch"""
        pass
        
    def _process_infection(self, entity: Entity, delta_time: float):
        """Process ongoing infection"""
        infection = entity.get_component(InfectionComponent)
        
        # Update inflammation
        infection.update_inflammation(delta_time)
        
        # Pathogen replication
        for name, pathogen in list(infection.pathogens.items()):
            # Replicate based on rate
            replication = pathogen.replication_rate * delta_time
            
            # Limited by cell resources
            if entity.has_component(EnergyComponent):
                energy = entity.get_component(EnergyComponent)
                if energy.percentage() < 20:
                    replication *= 0.1  # Slow replication in weak cells
                    
            infection.pathogen_load += replication
            
            # Pathogen mutation
            if pathogen.mutate():
                # Create new strain
                new_strain = f"{pathogen.strain}_variant"
                new_pathogen = Pathogen(
                    pathogen_type=pathogen.pathogen_type,
                    strain=new_strain,
                    virulence=pathogen.virulence * random.uniform(0.8, 1.2),
                    replication_rate=pathogen.replication_rate * random.uniform(0.9, 1.1),
                    antigen_signature=pathogen.antigen_signature
                )
                infection.add_pathogen(new_strain, new_pathogen)
                
            # Track active pathogens
            self.active_pathogens[pathogen.strain] = self.active_pathogens.get(pathogen.strain, 0) + 1
            
        # Mount immune response
        immune_effectiveness = infection.mount_immune_response(delta_time)
        
        # Check for antibody production
        for pathogen in infection.pathogens.values():
            # B cell activation
            if pathogen.antigen_signature not in infection.memory_antigens:
                # First exposure - slow response
                if random.random() < 0.1 * delta_time:
                    infection.produce_antibody(pathogen.antigen_signature, AntibodyType.IGM)
            else:
                # Memory response - fast
                infection.produce_antibody(pathogen.antigen_signature, AntibodyType.IGG)
                
        # Apply pathogen damage to cell
        if entity.has_component(HealthComponent):
            health = entity.get_component(HealthComponent)
            total_damage = 0.0
            
            for pathogen in infection.pathogens.values():
                damage = pathogen.virulence * delta_time
                total_damage += damage
                
            health.current -= total_damage
            
            # Check for sepsis (overwhelming infection)
            if infection.pathogen_load > 100:
                entity.add_tag("septic")
                health.current -= 10 * delta_time  # Rapid deterioration
                
        # Update cell state based on infection
        if entity.has_component(StateComponent):
            state = entity.get_component(StateComponent)
            
            if infection.pathogen_load > 50 and state.state != CellState.DYING:
                state.change_state(CellState.DYING, time.time())
            elif infection.inflammation_level > 0.7:
                entity.add_tag("inflamed")
                
        # Check if infection cleared
        if infection.pathogen_load <= 0.01 and infection.infected:
            infection.infected = False
            infection.pathogens.clear()
            infection.pathogen_load = 0.0
            self.total_cleared += 1
            entity.remove_tag("infected")
            entity.add_tag("recovered")
            
            # Reduce inflammation gradually
            infection.inflammation_level *= 0.5
            
        # Cytokine signaling
        if infection.inflammation_level > 0.3 and entity.has_component(CommunicationComponent):
            comm = entity.get_component(CommunicationComponent)
            
            # Release inflammatory signals
            comm.emit_signal(
                signal_type=SignalType.CHEMICAL,
                strength=infection.inflammation_level,
                source_id=entity.id,
                payload={
                    "ligand": "cytokine",
                    "type": "inflammatory",
                    "pathogen": next(iter(infection.pathogens.keys())) if infection.pathogens else "unknown"
                },
                timestamp=time.time()
            )
            
    def _check_disease_spread(self, infected: List[Entity], healthy: List[Entity], 
                            delta_time: float):
        """Check for disease transmission between cells"""
        from ..components.movement import PositionComponent
        
        for infected_entity in infected:
            infection = infected_entity.get_component(InfectionComponent)
            
            # High pathogen load increases transmission
            if infection.pathogen_load < 10:
                continue
                
            infected_pos = None
            if infected_entity.has_component(PositionComponent):
                infected_pos = infected_entity.get_component(PositionComponent)
                
            for healthy_entity in healthy:
                # Check proximity
                if infected_pos and healthy_entity.has_component(PositionComponent):
                    healthy_pos = healthy_entity.get_component(PositionComponent)
                    distance = infected_pos.distance_to(healthy_pos)
                    
                    # Transmission probability decreases with distance
                    if distance < 5.0:  # Close contact
                        transmission_prob = 0.1 * delta_time * (infection.pathogen_load / 50.0)
                        
                        if random.random() < transmission_prob:
                            # Transmit disease
                            healthy_infection = healthy_entity.get_component(InfectionComponent)
                            
                            # Pick random pathogen to transmit
                            if infection.pathogens:
                                pathogen_name, pathogen = random.choice(list(infection.pathogens.items()))
                                
                                # Create new infection
                                new_pathogen = Pathogen(
                                    pathogen_type=pathogen.pathogen_type,
                                    strain=pathogen.strain,
                                    virulence=pathogen.virulence,
                                    replication_rate=pathogen.replication_rate,
                                    antigen_signature=pathogen.antigen_signature,
                                    resistance_factors=pathogen.resistance_factors.copy()
                                )
                                
                                healthy_infection.add_pathogen(pathogen_name, new_pathogen)
                                healthy_entity.add_tag("infected")
                                self.total_infections += 1
                                
    def introduce_pathogen(self, entity: Entity, pathogen_type: PathogenType, 
                          strain: str = "wild_type"):
        """Introduce a pathogen to an entity"""
        if entity.has_component(InfectionComponent):
            infection = entity.get_component(InfectionComponent)
            
            pathogen = Pathogen(
                pathogen_type=pathogen_type,
                strain=strain,
                virulence=random.uniform(0.5, 1.5),
                replication_rate=random.uniform(1.5, 3.0),
                antigen_signature=f"{pathogen_type.value}_{strain}"
            )
            
            infection.add_pathogen(strain, pathogen)
            entity.add_tag("infected")
            self.total_infections += 1
            
    def get_stats(self) -> dict:
        """Get system statistics"""
        stats = super().get_stats()
        stats.update({
            "total_infections": self.total_infections,
            "total_cleared": self.total_cleared,
            "active_pathogens": dict(self.active_pathogens),
            "cure_rate": self.total_cleared / max(1, self.total_infections)
        })
        return stats