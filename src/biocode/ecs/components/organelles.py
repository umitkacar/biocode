"""
Organelle Components - Cellular substructures
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum


class OrganelleType(Enum):
    """Types of cellular organelles"""
    MITOCHONDRIA = "mitochondria"
    NUCLEUS = "nucleus"
    LYSOSOME = "lysosome"
    ENDOPLASMIC_RETICULUM = "endoplasmic_reticulum"
    GOLGI_APPARATUS = "golgi_apparatus"
    RIBOSOME = "ribosome"
    PEROXISOME = "peroxisome"
    CHLOROPLAST = "chloroplast"


@dataclass
class Mitochondria:
    """Powerhouse of the cell"""
    count: int = 100
    efficiency: float = 0.85
    damage_level: float = 0.0
    atp_production_rate: float = 10.0
    oxygen_consumption_rate: float = 5.0
    
    def calculate_atp_production(self, oxygen_available: float) -> float:
        """Calculate ATP production based on oxygen availability"""
        # Aerobic respiration: more efficient
        if oxygen_available > self.oxygen_consumption_rate:
            return self.atp_production_rate * self.efficiency * (1.0 - self.damage_level)
        # Anaerobic: less efficient
        else:
            return self.atp_production_rate * 0.1 * (1.0 - self.damage_level)


@dataclass
class Nucleus:
    """Control center of the cell"""
    dna_integrity: float = 1.0
    transcription_rate: float = 1.0
    repair_efficiency: float = 0.9
    active_genes: Set[str] = field(default_factory=set)
    epigenetic_marks: Dict[str, bool] = field(default_factory=dict)
    
    def can_divide(self) -> bool:
        """Check if nucleus is ready for division"""
        return self.dna_integrity > 0.7 and self.transcription_rate > 0.5


@dataclass
class Lysosome:
    """Cellular waste disposal"""
    count: int = 50
    enzyme_activity: float = 1.0
    ph_level: float = 4.5  # Acidic
    waste_capacity: float = 100.0
    current_waste: float = 0.0
    
    def digest_waste(self, amount: float) -> float:
        """Digest cellular waste"""
        can_digest = min(amount, self.waste_capacity - self.current_waste)
        digestion_rate = can_digest * self.enzyme_activity
        self.current_waste = max(0, self.current_waste - digestion_rate)
        return digestion_rate


@dataclass
class EndoplasmicReticulum:
    """Protein and lipid synthesis"""
    rough_er_activity: float = 1.0  # Protein synthesis
    smooth_er_activity: float = 1.0  # Lipid synthesis
    protein_folding_efficiency: float = 0.95
    calcium_storage: float = 100.0
    stress_level: float = 0.0
    
    def is_stressed(self) -> bool:
        """Check for ER stress"""
        return self.stress_level > 0.7 or self.protein_folding_efficiency < 0.5


@dataclass
class OrganelleComponent:
    """Container for all cellular organelles"""
    mitochondria: Optional[Mitochondria] = None
    nucleus: Optional[Nucleus] = None
    lysosomes: Optional[Lysosome] = None
    endoplasmic_reticulum: Optional[EndoplasmicReticulum] = None
    
    # Organelle health tracking
    organelle_health: Dict[OrganelleType, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default organelles if not provided"""
        if self.mitochondria is None:
            self.mitochondria = Mitochondria()
        if self.nucleus is None:
            self.nucleus = Nucleus()
        if self.lysosomes is None:
            self.lysosomes = Lysosome()
        if self.endoplasmic_reticulum is None:
            self.endoplasmic_reticulum = EndoplasmicReticulum()
            
        # Initialize health tracking
        self.organelle_health[OrganelleType.MITOCHONDRIA] = 1.0
        self.organelle_health[OrganelleType.NUCLEUS] = 1.0
        self.organelle_health[OrganelleType.LYSOSOME] = 1.0
        self.organelle_health[OrganelleType.ENDOPLASMIC_RETICULUM] = 1.0
    
    def get_total_atp_production(self, oxygen_level: float) -> float:
        """Calculate total ATP production from all mitochondria"""
        return self.mitochondria.calculate_atp_production(oxygen_level)
    
    def update_organelle_health(self, organelle_type: OrganelleType, damage: float):
        """Update health of specific organelle"""
        if organelle_type in self.organelle_health:
            self.organelle_health[organelle_type] = max(
                0.0, 
                self.organelle_health[organelle_type] - damage
            )
            
            # Apply damage to specific organelle
            if organelle_type == OrganelleType.MITOCHONDRIA:
                self.mitochondria.damage_level = 1.0 - self.organelle_health[organelle_type]
            elif organelle_type == OrganelleType.NUCLEUS:
                self.nucleus.dna_integrity = self.organelle_health[organelle_type]
            elif organelle_type == OrganelleType.LYSOSOME and self.lysosomes:
                self.lysosomes.enzyme_activity = self.organelle_health[organelle_type]
            elif organelle_type == OrganelleType.ENDOPLASMIC_RETICULUM:
                self.endoplasmic_reticulum.stress_level = 1.0 - self.organelle_health[organelle_type]
    
    def get_overall_health(self) -> float:
        """Calculate overall organelle health"""
        if not self.organelle_health:
            return 0.0
        return sum(self.organelle_health.values()) / len(self.organelle_health)