"""
ECS Components - Pure Data Containers
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from .biological import (
    LifeComponent,
    EnergyComponent,
    DNAComponent,
    HealthComponent,
    StateComponent,
    MemoryComponent
)
from .movement import (
    PositionComponent,
    VelocityComponent,
    MovementComponent
)
from .communication import (
    CommunicationComponent,
    SignalComponent
)
from .specialized import (
    PhotosynthesisComponent,
    NeuralComponent,
    DifferentiationComponent
)
from .organelles import (
    OrganelleComponent,
    Mitochondria,
    Nucleus,
    Lysosome,
    EndoplasmicReticulum
)
from .membrane import (
    MembraneComponent,
    Receptor,
    Transporter
)
from .infection import (
    InfectionComponent,
    Pathogen,
    Antibody
)

__all__ = [
    # Biological
    'LifeComponent',
    'EnergyComponent',
    'DNAComponent',
    'HealthComponent',
    'StateComponent',
    'MemoryComponent',
    # Movement
    'PositionComponent',
    'VelocityComponent',
    'MovementComponent',
    # Communication
    'CommunicationComponent',
    'SignalComponent',
    # Specialized
    'PhotosynthesisComponent',
    'NeuralComponent',
    'DifferentiationComponent',
    # Organelles
    'OrganelleComponent',
    'Mitochondria',
    'Nucleus',
    'Lysosome',
    'EndoplasmicReticulum',
    # Membrane
    'MembraneComponent',
    'Receptor',
    'Transporter',
    # Infection
    'InfectionComponent',
    'Pathogen',
    'Antibody'
]