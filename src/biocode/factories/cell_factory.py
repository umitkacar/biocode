"""
Cell Factory - Creates various cell types as ECS entities
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import time
import random
from typing import Optional, Dict, Any
from ..ecs import (
    Entity, World,
    # Components
    LifeComponent, EnergyComponent, DNAComponent,
    HealthComponent, StateComponent, MemoryComponent,
    PositionComponent, VelocityComponent, MovementComponent,
    CommunicationComponent, SignalType,
    PhotosynthesisComponent, NeuralComponent, DifferentiationComponent,
    OrganelleComponent, MembraneComponent, InfectionComponent,
    Receptor, Transporter,
    # Enums
    CellState, CellType, NeuronType, ReceptorType, TransportType
)


class CellFactory:
    """
    Hücre üretim fabrikası
    
    Creates different cell types with appropriate component configurations.
    """
    
    def __init__(self, world: World):
        """
        Initialize factory with world reference
        
        Args:
            world: ECS world to create entities in
        """
        self.world = world
        self.cell_count = 0
        
    def create_stem_cell(self, position: tuple = (0, 0, 0), 
                        **kwargs) -> Entity:
        """
        Create a stem cell with full differentiation potential
        
        Args:
            position: Initial position (x, y, z)
            **kwargs: Additional parameters
            
        Returns:
            Created stem cell entity
        """
        entity = self.world.create_entity()
        
        # Core biological components
        entity.add_component(LifeComponent(
            birth_time=time.time(),
            lifespan=kwargs.get('lifespan', 200.0),
            generation=kwargs.get('generation', 0)
        ))
        
        entity.add_component(EnergyComponent(
            current=kwargs.get('energy', 100.0),
            maximum=100.0,
            consumption_rate=0.5,
            production_rate=0.1
        ))
        
        entity.add_component(DNAComponent(
            sequence=kwargs.get('dna', self._generate_dna()),
            mutation_rate=kwargs.get('mutation_rate', 0.001),
            dominant_traits=['pluripotent', 'fast_division'],
            recessive_traits=['slow_metabolism']
        ))
        
        entity.add_component(HealthComponent(
            current=100.0,
            maximum=100.0,
            regeneration_rate=2.0
        ))
        
        entity.add_component(StateComponent(
            state=CellState.DORMANT
        ))
        
        entity.add_component(MemoryComponent(
            capacity=50
        ))
        
        # Movement components
        entity.add_component(MovementComponent(
            position=PositionComponent(*position),
            max_speed=2.0,
            friction=0.3
        ))
        
        # Communication
        entity.add_component(CommunicationComponent(
            emission_types={SignalType.CHEMICAL},
            reception_types={SignalType.CHEMICAL}
        ))
        
        # Differentiation - full potential
        entity.add_component(DifferentiationComponent(
            current_type=CellType.STEM,
            differentiation_potential=1.0,
            commitment_level=0.0
        ))
        
        # Organelles
        entity.add_component(OrganelleComponent())
        
        # Membrane
        membrane = MembraneComponent()
        # Add basic receptors
        membrane.add_receptor("growth_factor_receptor", Receptor(
            receptor_type=ReceptorType.GROWTH_FACTOR,
            ligand="growth_factor"
        ))
        membrane.add_receptor("cytokine_receptor", Receptor(
            receptor_type=ReceptorType.CYTOKINE,
            ligand="cytokine"
        ))
        # Add basic transporters
        membrane.add_transporter("glucose_transporter", Transporter(
            transport_type=TransportType.FACILITATED_DIFFUSION,
            molecule_type="glucose"
        ))
        membrane.add_transporter("ion_pump", Transporter(
            transport_type=TransportType.ACTIVE_TRANSPORT,
            molecule_type="ions",
            energy_cost=1.0
        ))
        entity.add_component(membrane)
        
        # Infection component (healthy by default)
        entity.add_component(InfectionComponent())
        
        # Tags
        entity.add_tag("cell")
        entity.add_tag("stem_cell")
        entity.add_tag("living")
        
        self.cell_count += 1
        return entity
        
    def create_neuron(self, neuron_type: NeuronType = NeuronType.INTERNEURON,
                     position: tuple = (0, 0, 0), **kwargs) -> Entity:
        """
        Create a neural cell
        
        Args:
            neuron_type: Type of neuron
            position: Initial position
            **kwargs: Additional parameters
            
        Returns:
            Created neuron entity
        """
        entity = self.world.create_entity()
        
        # Core biological components
        entity.add_component(LifeComponent(
            birth_time=time.time(),
            lifespan=kwargs.get('lifespan', 500.0),  # Neurons live long
            generation=kwargs.get('generation', 0)
        ))
        
        entity.add_component(EnergyComponent(
            current=80.0,
            maximum=80.0,
            consumption_rate=2.0,  # High energy use
            production_rate=0.0
        ))
        
        entity.add_component(DNAComponent(
            sequence=kwargs.get('dna', self._generate_dna()),
            mutation_rate=0.0001,  # Very stable
            dominant_traits=['electrical_signaling', 'long_axons'],
            recessive_traits=['regeneration']
        ))
        
        entity.add_component(HealthComponent(
            current=100.0,
            maximum=100.0,
            regeneration_rate=0.1  # Poor regeneration
        ))
        
        entity.add_component(StateComponent(
            state=CellState.ACTIVE
        ))
        
        entity.add_component(MemoryComponent(
            capacity=200  # High memory capacity
        ))
        
        # Movement - neurons don't move much
        entity.add_component(MovementComponent(
            position=PositionComponent(*position),
            max_speed=0.0,
            friction=1.0
        ))
        
        # Communication - electrical and chemical
        entity.add_component(CommunicationComponent(
            emission_types={SignalType.ELECTRICAL, SignalType.CHEMICAL},
            reception_types={SignalType.ELECTRICAL, SignalType.CHEMICAL},
            emission_range=20.0,
            reception_range=25.0
        ))
        
        # Neural component
        entity.add_component(NeuralComponent(
            neuron_type=neuron_type,
            threshold_potential=kwargs.get('threshold', -55.0)
        ))
        
        # Differentiation - fully differentiated
        entity.add_component(DifferentiationComponent(
            current_type=CellType.NERVE,
            differentiation_potential=0.0,
            commitment_level=1.0
        ))
        
        # Organelles - neurons have many mitochondria
        organelles = OrganelleComponent()
        organelles.mitochondria.count = 200  # High energy needs
        entity.add_component(organelles)
        
        # Membrane - specialized for electrical signaling
        membrane = MembraneComponent()
        membrane.add_receptor("neurotransmitter_receptor", Receptor(
            receptor_type=ReceptorType.ION_CHANNEL,
            ligand="neurotransmitter"
        ))
        # Voltage-gated ion channels
        membrane.add_transporter("sodium_channel", Transporter(
            transport_type=TransportType.PASSIVE_DIFFUSION,
            molecule_type="Na+",
            rate=10.0  # Fast for action potentials
        ))
        membrane.add_transporter("potassium_channel", Transporter(
            transport_type=TransportType.PASSIVE_DIFFUSION,
            molecule_type="K+",
            rate=10.0
        ))
        entity.add_component(membrane)
        
        # Infection component
        entity.add_component(InfectionComponent())
        
        # Tags
        entity.add_tag("cell")
        entity.add_tag("neuron")
        entity.add_tag(f"neuron_{neuron_type.value}")
        entity.add_tag("living")
        
        self.cell_count += 1
        return entity
        
    def create_plant_cell(self, position: tuple = (0, 0, 0), 
                         **kwargs) -> Entity:
        """
        Create a photosynthetic plant cell
        
        Args:
            position: Initial position
            **kwargs: Additional parameters
            
        Returns:
            Created plant cell entity
        """
        entity = self.world.create_entity()
        
        # Core biological components
        entity.add_component(LifeComponent(
            birth_time=time.time(),
            lifespan=kwargs.get('lifespan', 300.0),
            generation=kwargs.get('generation', 0)
        ))
        
        entity.add_component(EnergyComponent(
            current=50.0,
            maximum=150.0,  # Can store more energy
            consumption_rate=0.3,
            production_rate=0.0  # Uses photosynthesis instead
        ))
        
        entity.add_component(DNAComponent(
            sequence=kwargs.get('dna', self._generate_dna()),
            mutation_rate=0.0005,
            dominant_traits=['chloroplasts', 'cell_wall'],
            recessive_traits=['mobility']
        ))
        
        entity.add_component(HealthComponent(
            current=100.0,
            maximum=100.0,
            regeneration_rate=1.5
        ))
        
        entity.add_component(StateComponent(
            state=CellState.ACTIVE
        ))
        
        # Movement - plant cells are stationary
        entity.add_component(MovementComponent(
            position=PositionComponent(*position),
            max_speed=0.0,
            friction=1.0
        ))
        
        # Communication - mainly chemical
        entity.add_component(CommunicationComponent(
            emission_types={SignalType.CHEMICAL},
            reception_types={SignalType.CHEMICAL},
            emission_range=5.0
        ))
        
        # Photosynthesis component
        entity.add_component(PhotosynthesisComponent(
            chlorophyll_content=kwargs.get('chlorophyll', 1.0),
            light_absorption_rate=0.8
        ))
        
        # Organelles - plant cells have chloroplasts
        organelles = OrganelleComponent()
        # Plant cells don't have lysosomes typically
        organelles.lysosomes = None
        entity.add_component(organelles)
        
        # Membrane - rigid cell wall
        membrane = MembraneComponent()
        membrane.integrity = 1.0
        membrane.fluidity = 0.2  # Less fluid due to cell wall
        membrane.add_transporter("water_channel", Transporter(
            transport_type=TransportType.PASSIVE_DIFFUSION,
            molecule_type="water",
            rate=5.0
        ))
        membrane.add_transporter("co2_channel", Transporter(
            transport_type=TransportType.PASSIVE_DIFFUSION,
            molecule_type="co2",
            rate=3.0
        ))
        entity.add_component(membrane)
        
        # Infection component - plants have different immunity
        infection = InfectionComponent()
        infection.immune_efficiency = 0.7  # Different immune system
        entity.add_component(infection)
        
        # Tags
        entity.add_tag("cell")
        entity.add_tag("plant_cell")
        entity.add_tag("photosynthetic")
        entity.add_tag("living")
        
        self.cell_count += 1
        return entity
        
    def create_muscle_cell(self, position: tuple = (0, 0, 0),
                          **kwargs) -> Entity:
        """
        Create a muscle cell specialized for movement
        
        Args:
            position: Initial position
            **kwargs: Additional parameters
            
        Returns:
            Created muscle cell entity
        """
        entity = self.world.create_entity()
        
        # Core biological components
        entity.add_component(LifeComponent(
            birth_time=time.time(),
            lifespan=kwargs.get('lifespan', 150.0),
            generation=kwargs.get('generation', 0)
        ))
        
        entity.add_component(EnergyComponent(
            current=100.0,
            maximum=100.0,
            consumption_rate=1.5,  # High energy use during contraction
            production_rate=0.2
        ))
        
        entity.add_component(DNAComponent(
            sequence=kwargs.get('dna', self._generate_dna()),
            mutation_rate=0.0002,
            dominant_traits=['contractile_proteins', 'high_mitochondria'],
            recessive_traits=['fast_twitch']
        ))
        
        entity.add_component(HealthComponent(
            current=100.0,
            maximum=100.0,
            regeneration_rate=0.8
        ))
        
        entity.add_component(StateComponent(
            state=CellState.ACTIVE
        ))
        
        # Movement - can contract
        entity.add_component(MovementComponent(
            position=PositionComponent(*position),
            max_speed=5.0,  # Can move fast when contracting
            max_acceleration=3.0,
            friction=0.5
        ))
        
        # Communication
        entity.add_component(CommunicationComponent(
            emission_types={SignalType.MECHANICAL, SignalType.CHEMICAL},
            reception_types={SignalType.ELECTRICAL, SignalType.CHEMICAL}
        ))
        
        # Differentiation - fully differentiated
        entity.add_component(DifferentiationComponent(
            current_type=CellType.MUSCLE,
            differentiation_potential=0.0,
            commitment_level=1.0
        ))
        
        # Organelles - muscle cells have LOTS of mitochondria
        organelles = OrganelleComponent()
        organelles.mitochondria.count = 500  # Very high energy needs
        organelles.mitochondria.efficiency = 0.9
        entity.add_component(organelles)
        
        # Membrane - specialized for calcium signaling
        membrane = MembraneComponent()
        membrane.add_receptor("acetylcholine_receptor", Receptor(
            receptor_type=ReceptorType.ION_CHANNEL,
            ligand="acetylcholine"
        ))
        membrane.add_transporter("calcium_pump", Transporter(
            transport_type=TransportType.ACTIVE_TRANSPORT,
            molecule_type="Ca2+",
            energy_cost=2.0,
            rate=5.0
        ))
        entity.add_component(membrane)
        
        # Infection component
        entity.add_component(InfectionComponent())
        
        # Tags
        entity.add_tag("cell")
        entity.add_tag("muscle_cell")
        entity.add_tag("contractile")
        entity.add_tag("living")
        
        self.cell_count += 1
        return entity
        
    def _generate_dna(self, length: int = 100) -> str:
        """Generate random DNA sequence"""
        bases = ['A', 'T', 'G', 'C']
        return ''.join(random.choice(bases) for _ in range(length))
        
    def create_custom_cell(self, components: Dict[type, Any],
                          tags: list = None, **kwargs) -> Entity:
        """
        Create custom cell with specified components
        
        Args:
            components: Dictionary of component types to component instances
            tags: List of tags to add
            **kwargs: Additional parameters
            
        Returns:
            Created custom cell entity
        """
        entity = self.world.create_entity()
        
        # Add all specified components
        for component in components.values():
            entity.add_component(component)
            
        # Add tags
        if tags:
            for tag in tags:
                entity.add_tag(tag)
                
        entity.add_tag("cell")
        entity.add_tag("custom")
        entity.add_tag("living")
        
        self.cell_count += 1
        return entity
        
    def get_stats(self) -> Dict[str, Any]:
        """Get factory statistics"""
        return {
            "total_cells_created": self.cell_count
        }