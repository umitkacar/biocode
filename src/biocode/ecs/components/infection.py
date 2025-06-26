"""
Infection Components - Pathogen and immune response
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from enum import Enum


class PathogenType(Enum):
    """Types of pathogens"""
    VIRUS = "virus"
    BACTERIA = "bacteria"
    FUNGUS = "fungus"
    PARASITE = "parasite"
    PRION = "prion"


class AntibodyType(Enum):
    """Types of antibodies"""
    IGG = "IgG"  # Most common, long-term immunity
    IGM = "IgM"  # First response
    IGA = "IgA"  # Mucosal immunity
    IGE = "IgE"  # Allergic response
    IGD = "IgD"  # B cell activation


@dataclass
class Pathogen:
    """Pathogen data"""
    pathogen_type: PathogenType
    strain: str
    virulence: float = 1.0  # How damaging
    replication_rate: float = 2.0  # How fast it multiplies
    antigen_signature: str = ""  # Unique identifier for immune system
    resistance_factors: Set[str] = field(default_factory=set)  # Drug resistances
    
    def mutate(self, mutation_rate: float = 0.001) -> bool:
        """Pathogen mutation"""
        import random
        if random.random() < mutation_rate:
            # Change antigen signature slightly
            self.antigen_signature = f"{self.antigen_signature}_mut{random.randint(1, 1000)}"
            # Potentially gain resistance
            if random.random() < 0.1:
                self.resistance_factors.add(f"resistance_{random.randint(1, 10)}")
            return True
        return False


@dataclass
class Antibody:
    """Antibody for immune response"""
    antibody_type: AntibodyType
    target_antigen: str  # Which pathogen it targets
    affinity: float = 0.5  # How well it binds (0-1)
    concentration: float = 0.0  # Current concentration
    production_rate: float = 1.0
    half_life: float = 21.0  # Days (for IgG)
    
    def binds_to(self, antigen: str) -> bool:
        """Check if antibody binds to specific antigen"""
        if self.target_antigen == antigen:
            return True
        # Check for partial match (cross-reactivity)
        if self.target_antigen in antigen or antigen in self.target_antigen:
            return self.affinity > 0.7
        return False


@dataclass
class InfectionComponent:
    """Infection and immune response data"""
    # Infection status
    infected: bool = False
    pathogens: Dict[str, Pathogen] = field(default_factory=dict)
    pathogen_load: float = 0.0  # Total pathogen count
    
    # Immune response
    inflammation_level: float = 0.0  # 0-1 scale
    fever_response: float = 0.0  # Temperature increase
    antibodies: Dict[str, Antibody] = field(default_factory=dict)
    memory_antigens: Set[str] = field(default_factory=set)  # Remembered pathogens
    
    # Immune cell counts
    white_cell_count: float = 5000.0  # per μL
    neutrophil_percentage: float = 0.60
    lymphocyte_percentage: float = 0.30
    monocyte_percentage: float = 0.08
    
    # Immune system efficiency
    immune_efficiency: float = 1.0  # Overall immune function
    immunosuppressed: bool = False
    
    def add_pathogen(self, name: str, pathogen: Pathogen):
        """Add a pathogen infection"""
        self.pathogens[name] = pathogen
        self.infected = True
        self.pathogen_load += 1.0
        
        # Trigger inflammation
        self.inflammation_level = min(1.0, self.inflammation_level + pathogen.virulence * 0.1)
        
    def remove_pathogen(self, name: str) -> Optional[Pathogen]:
        """Remove cleared pathogen"""
        pathogen = self.pathogens.pop(name, None)
        if pathogen:
            self.pathogen_load = max(0, self.pathogen_load - 1.0)
            if not self.pathogens:
                self.infected = False
        return pathogen
    
    def produce_antibody(self, antigen: str, antibody_type: AntibodyType = AntibodyType.IGG):
        """Produce antibody against specific antigen"""
        antibody_name = f"{antibody_type.value}_{antigen}"
        
        if antibody_name not in self.antibodies:
            # Create new antibody
            self.antibodies[antibody_name] = Antibody(
                antibody_type=antibody_type,
                target_antigen=antigen,
                affinity=0.5  # Starts with low affinity
            )
        else:
            # Increase affinity (affinity maturation)
            self.antibodies[antibody_name].affinity = min(
                1.0, 
                self.antibodies[antibody_name].affinity + 0.1
            )
            
        # Increase concentration
        self.antibodies[antibody_name].concentration += self.antibodies[antibody_name].production_rate
        
        # Add to memory
        self.memory_antigens.add(antigen)
    
    def mount_immune_response(self, delta_time: float) -> float:
        """Calculate immune response effectiveness"""
        if not self.infected:
            return 0.0
            
        total_response = 0.0
        
        # Check each pathogen
        for name, pathogen in list(self.pathogens.items()):
            pathogen_damage = 0.0
            
            # Check for matching antibodies
            for antibody in self.antibodies.values():
                if antibody.binds_to(pathogen.antigen_signature):
                    # Antibody neutralization
                    neutralization = antibody.concentration * antibody.affinity * self.immune_efficiency
                    pathogen_damage += neutralization
                    
            # Innate immune response
            innate_response = (
                self.white_cell_count / 5000.0 *  # Normal WBC count
                self.immune_efficiency * 
                (1.0 + self.inflammation_level * 0.5)  # Inflammation helps
            )
            pathogen_damage += innate_response * 0.1
            
            # Apply damage to pathogen load
            damage_dealt = min(1.0, pathogen_damage * delta_time)
            self.pathogen_load = max(0, self.pathogen_load - damage_dealt)
            
            # Remove if cleared
            if damage_dealt >= 0.99:
                self.remove_pathogen(name)
                
            total_response += damage_dealt
            
        return total_response
    
    def update_inflammation(self, delta_time: float):
        """Update inflammation level"""
        if self.infected:
            # Increase based on pathogen load
            self.inflammation_level = min(
                1.0,
                self.inflammation_level + self.pathogen_load * 0.01 * delta_time
            )
        else:
            # Decrease when not infected
            self.inflammation_level = max(
                0.0,
                self.inflammation_level - 0.1 * delta_time
            )
            
        # Update fever based on inflammation
        self.fever_response = self.inflammation_level * 2.0  # Max 2°C increase
    
    def is_immunocompromised(self) -> bool:
        """Check if immune system is compromised"""
        return (
            self.immunosuppressed or
            self.immune_efficiency < 0.5 or
            self.white_cell_count < 2000
        )