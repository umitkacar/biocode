"""
BioCode ECS (Entity-Component-System) Architecture
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

WARNING: This is LIVING CODE with autonomous behaviors.
It can grow, reproduce, mutate, and die. Use at your own risk.
"""
from .entity import Entity
from .component import Component
from .system import System
from .world import World

# Import all components
from .components import (
    # Biological
    LifeComponent,
    EnergyComponent,
    DNAComponent,
    HealthComponent,
    StateComponent,
    MemoryComponent,
    # Movement
    PositionComponent,
    VelocityComponent,
    MovementComponent,
    # Communication
    CommunicationComponent,
    SignalComponent,
    # Specialized
    PhotosynthesisComponent,
    NeuralComponent,
    DifferentiationComponent,
    # Organelles
    OrganelleComponent,
    Mitochondria,
    Nucleus,
    Lysosome,
    EndoplasmicReticulum,
    # Membrane
    MembraneComponent,
    Receptor,
    Transporter,
    # Infection
    InfectionComponent,
    Pathogen,
    Antibody
)

# Import enums
from .components.biological import CellState
from .components.communication import SignalType
from .components.specialized import NeuronType, CellType
from .components.organelles import OrganelleType
from .components.membrane import TransportType, ReceptorType
from .components.infection import PathogenType, AntibodyType

# Import all systems
from .systems import (
    LifeSystem,
    EnergySystem,
    MovementSystem,
    CommunicationSystem,
    NeuralSystem,
    PhotosynthesisSystem,
    OrganelleSystem,
    MembraneSystem,
    InfectionSystem
)

__all__ = [
    # Core
    'Entity',
    'Component',
    'System',
    'World',
    # Components
    'LifeComponent',
    'EnergyComponent',
    'DNAComponent',
    'HealthComponent',
    'StateComponent',
    'MemoryComponent',
    'PositionComponent',
    'VelocityComponent',
    'MovementComponent',
    'CommunicationComponent',
    'SignalComponent',
    'PhotosynthesisComponent',
    'NeuralComponent',
    'DifferentiationComponent',
    'OrganelleComponent',
    'Mitochondria',
    'Nucleus',
    'Lysosome',
    'EndoplasmicReticulum',
    'MembraneComponent',
    'Receptor',
    'Transporter',
    'InfectionComponent',
    'Pathogen',
    'Antibody',
    # Enums
    'CellState',
    'SignalType',
    'NeuronType',
    'CellType',
    'OrganelleType',
    'TransportType',
    'ReceptorType',
    'PathogenType',
    'AntibodyType',
    # Systems
    'LifeSystem',
    'EnergySystem',
    'MovementSystem',
    'CommunicationSystem',
    'NeuralSystem',
    'PhotosynthesisSystem',
    'OrganelleSystem',
    'MembraneSystem',
    'InfectionSystem'
]