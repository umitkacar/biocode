"""
Membrane Components - Cellular boundary and transport
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Callable
from enum import Enum


class TransportType(Enum):
    """Types of membrane transport"""
    PASSIVE_DIFFUSION = "passive_diffusion"
    FACILITATED_DIFFUSION = "facilitated_diffusion"
    ACTIVE_TRANSPORT = "active_transport"
    ENDOCYTOSIS = "endocytosis"
    EXOCYTOSIS = "exocytosis"


class ReceptorType(Enum):
    """Types of membrane receptors"""
    GPCR = "g_protein_coupled"
    ION_CHANNEL = "ion_channel"
    ENZYME_LINKED = "enzyme_linked"
    NUCLEAR = "nuclear"
    CYTOKINE = "cytokine"
    GROWTH_FACTOR = "growth_factor"


@dataclass
class Receptor:
    """Membrane receptor for signal detection"""
    receptor_type: ReceptorType
    ligand: str  # What it binds to
    sensitivity: float = 1.0
    occupied: bool = False
    activation_threshold: float = 0.5
    downregulation_rate: float = 0.01
    
    def bind_ligand(self, concentration: float) -> bool:
        """Attempt to bind ligand based on concentration"""
        if not self.occupied and concentration * self.sensitivity > self.activation_threshold:
            self.occupied = True
            # Downregulate sensitivity after binding
            self.sensitivity *= (1.0 - self.downregulation_rate)
            return True
        return False
    
    def release_ligand(self):
        """Release bound ligand"""
        self.occupied = False
    
    def recover_sensitivity(self, rate: float = 0.1):
        """Recover receptor sensitivity over time"""
        self.sensitivity = min(1.0, self.sensitivity + rate)


@dataclass
class Transporter:
    """Membrane transporter for molecule movement"""
    transport_type: TransportType
    molecule_type: str  # What it transports
    rate: float = 1.0  # Transport rate
    energy_cost: float = 0.0  # ATP cost per transport
    direction: str = "bidirectional"  # in, out, bidirectional
    saturable: bool = True
    max_rate: float = 10.0
    
    def calculate_transport_rate(self, concentration_gradient: float, 
                               atp_available: float) -> float:
        """Calculate actual transport rate"""
        if self.transport_type == TransportType.PASSIVE_DIFFUSION:
            # Rate proportional to gradient
            rate = self.rate * concentration_gradient
            
        elif self.transport_type == TransportType.ACTIVE_TRANSPORT:
            # Requires energy, can go against gradient
            if atp_available >= self.energy_cost:
                rate = self.rate
            else:
                rate = 0.0
                
        else:
            # Facilitated diffusion
            rate = self.rate * concentration_gradient
            
        # Apply saturation kinetics
        if self.saturable:
            rate = min(rate, self.max_rate)
            
        return rate


@dataclass
class MembraneComponent:
    """Cell membrane with receptors and transporters"""
    # Membrane properties
    integrity: float = 1.0  # 0 = completely damaged, 1 = intact
    fluidity: float = 0.5  # 0 = rigid, 1 = very fluid
    permeability: float = 0.1  # Base permeability to small molecules
    potential: float = -70.0  # Membrane potential in mV
    
    # Surface area and thickness
    surface_area: float = 100.0  # μm²
    thickness: float = 7.5  # nm
    
    # Receptors and transporters
    receptors: Dict[str, Receptor] = field(default_factory=dict)
    transporters: Dict[str, Transporter] = field(default_factory=dict)
    
    # Ion concentrations (mM)
    ion_concentrations: Dict[str, float] = field(default_factory=lambda: {
        "Na+_in": 10.0,
        "Na+_out": 145.0,
        "K+_in": 140.0,
        "K+_out": 5.0,
        "Ca2+_in": 0.0001,
        "Ca2+_out": 2.0,
        "Cl-_in": 10.0,
        "Cl-_out": 110.0
    })
    
    # Active receptor/transporter tracking
    active_receptors: Set[str] = field(default_factory=set)
    transport_queue: List[Dict[str, float]] = field(default_factory=list)
    
    def add_receptor(self, name: str, receptor: Receptor):
        """Add a receptor to the membrane"""
        self.receptors[name] = receptor
    
    def add_transporter(self, name: str, transporter: Transporter):
        """Add a transporter to the membrane"""
        self.transporters[name] = transporter
    
    def damage_membrane(self, damage: float):
        """Apply damage to membrane"""
        self.integrity = max(0.0, self.integrity - damage)
        # Damage increases permeability
        self.permeability = min(1.0, self.permeability + damage * 0.5)
        
    def repair_membrane(self, repair_rate: float):
        """Repair membrane damage"""
        self.integrity = min(1.0, self.integrity + repair_rate)
        # Repair reduces excess permeability
        base_permeability = 0.1
        self.permeability = max(base_permeability, self.permeability - repair_rate * 0.3)
    
    def calculate_nernst_potential(self, ion: str) -> float:
        """Calculate equilibrium potential for an ion"""
        R = 8.314  # Gas constant
        T = 310  # Body temperature in Kelvin  
        F = 96485  # Faraday constant
        
        in_key = f"{ion}_in"
        out_key = f"{ion}_out"
        
        if in_key in self.ion_concentrations and out_key in self.ion_concentrations:
            c_out = self.ion_concentrations[out_key]
            c_in = self.ion_concentrations[in_key]
            
            if c_in > 0:
                # Nernst equation
                z = 1 if "2+" not in ion else 2  # Charge
                if "-" in ion:
                    z = -1
                    
                import math
                return (R * T / (z * F)) * math.log(c_out / c_in) * 1000  # mV
                
        return 0.0
    
    def update_membrane_potential(self):
        """Update membrane potential using Goldman equation (simplified)"""
        # Simplified Goldman-Hodgkin-Katz equation
        # Considering only Na+, K+, and Cl-
        
        # Permeabilities (relative)
        p_K = 1.0
        p_Na = 0.04
        p_Cl = 0.45
        
        # Concentrations
        K_out = self.ion_concentrations.get("K+_out", 5.0)
        K_in = self.ion_concentrations.get("K+_in", 140.0)
        Na_out = self.ion_concentrations.get("Na+_out", 145.0)
        Na_in = self.ion_concentrations.get("Na+_in", 10.0)
        Cl_out = self.ion_concentrations.get("Cl-_out", 110.0)
        Cl_in = self.ion_concentrations.get("Cl-_in", 10.0)
        
        # Goldman equation (simplified)
        import math
        numerator = p_K * K_out + p_Na * Na_out + p_Cl * Cl_in
        denominator = p_K * K_in + p_Na * Na_in + p_Cl * Cl_out
        
        if denominator > 0:
            self.potential = 61.5 * math.log10(numerator / denominator)
    
    def get_ion_gradient(self, ion: str) -> float:
        """Get concentration gradient for an ion"""
        in_key = f"{ion}_in"
        out_key = f"{ion}_out"
        
        if in_key in self.ion_concentrations and out_key in self.ion_concentrations:
            return self.ion_concentrations[out_key] - self.ion_concentrations[in_key]
            
        return 0.0