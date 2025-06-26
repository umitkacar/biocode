"""
Specialized Components - Domain-specific behaviors
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum


class NeuronType(Enum):
    """Types of neurons"""
    SENSORY = "sensory"
    MOTOR = "motor"
    INTERNEURON = "interneuron"
    PYRAMIDAL = "pyramidal"
    PURKINJE = "purkinje"


class CellType(Enum):
    """Cell differentiation types"""
    STEM = "stem"
    MUSCLE = "muscle"
    NERVE = "nerve"
    EPITHELIAL = "epithelial"
    BLOOD = "blood"
    BONE = "bone"
    FAT = "fat"


@dataclass
class PhotosynthesisComponent:
    """Fotosentez verisi"""
    chlorophyll_content: float = 1.0
    light_absorption_rate: float = 0.8
    co2_consumption_rate: float = 0.5
    oxygen_production_rate: float = 0.4
    glucose_production_rate: float = 0.3
    
    # Environmental factors
    light_intensity: float = 0.0  # Current light level
    co2_concentration: float = 0.0  # Current CO2 level
    water_availability: float = 1.0
    
    # Efficiency modifiers
    temperature_efficiency: float = 1.0
    ph_efficiency: float = 1.0
    nutrient_efficiency: float = 1.0
    
    def calculate_glucose_production(self, delta_time: float) -> float:
        """Calculate glucose production based on conditions"""
        # Limiting factors (Liebig's law)
        limiting_factor = min(
            self.light_intensity,
            self.co2_concentration,
            self.water_availability
        )
        
        # Environmental efficiency
        total_efficiency = (
            self.temperature_efficiency * 
            self.ph_efficiency * 
            self.nutrient_efficiency
        )
        
        # Glucose production
        production = (
            self.glucose_production_rate * 
            self.chlorophyll_content * 
            limiting_factor * 
            total_efficiency * 
            delta_time
        )
        
        return max(0.0, production)
    
    def calculate_oxygen_production(self, glucose_produced: float) -> float:
        """Calculate O2 production from glucose synthesis"""
        # 6CO2 + 6H2O -> C6H12O6 + 6O2
        return glucose_produced * self.oxygen_production_rate


@dataclass
class NeuralComponent:
    """Sinir hücresi verisi"""
    neuron_type: NeuronType = NeuronType.INTERNEURON
    
    # Electrical properties
    resting_potential: float = -70.0  # mV
    membrane_potential: float = -70.0  # mV
    threshold_potential: float = -55.0  # mV
    refractory_period: float = 0.002  # seconds
    last_spike_time: float = -1.0
    
    # Synaptic properties
    synaptic_weights: Dict[str, float] = field(default_factory=dict)
    neurotransmitter_level: float = 1.0
    receptor_sensitivity: float = 1.0
    
    # Network properties
    dendrite_connections: Set[str] = field(default_factory=set)  # Input entity IDs
    axon_connections: Set[str] = field(default_factory=set)  # Output entity IDs
    
    # Activity tracking
    spike_count: int = 0
    spike_history: List[float] = field(default_factory=list)
    max_history_size: int = 100
    
    def integrate_input(self, input_current: float, delta_time: float):
        """Integrate input current (leaky integrate-and-fire model)"""
        tau = 0.02  # Membrane time constant
        leak = (self.resting_potential - self.membrane_potential) / tau
        
        self.membrane_potential += (leak + input_current) * delta_time
        self.membrane_potential = max(-100.0, min(50.0, self.membrane_potential))
    
    def check_spike(self, current_time: float) -> bool:
        """Check if neuron should spike"""
        # Check refractory period
        if current_time - self.last_spike_time < self.refractory_period:
            return False
            
        # Check threshold
        if self.membrane_potential >= self.threshold_potential:
            self.spike(current_time)
            return True
            
        return False
    
    def spike(self, current_time: float):
        """Generate action potential"""
        self.membrane_potential = 30.0  # Spike peak
        self.last_spike_time = current_time
        self.spike_count += 1
        
        # Record in history
        self.spike_history.append(current_time)
        if len(self.spike_history) > self.max_history_size:
            self.spike_history.pop(0)
    
    def reset_after_spike(self):
        """Reset membrane potential after spike"""
        self.membrane_potential = self.resting_potential - 10.0  # Hyperpolarization
    
    def get_firing_rate(self, time_window: float = 1.0) -> float:
        """Calculate recent firing rate (Hz)"""
        if not self.spike_history:
            return 0.0
            
        current_time = self.spike_history[-1] if self.spike_history else 0
        recent_spikes = sum(
            1 for t in self.spike_history 
            if current_time - t <= time_window
        )
        
        return recent_spikes / time_window


@dataclass
class DifferentiationComponent:
    """Hücre farklılaşma verisi"""
    current_type: CellType = CellType.STEM
    differentiation_potential: float = 1.0  # 1.0 = totipotent, 0.0 = fully differentiated
    commitment_level: float = 0.0  # How committed to current type
    
    # Differentiation factors
    growth_factors: Dict[str, float] = field(default_factory=dict)
    transcription_factors: Dict[str, bool] = field(default_factory=dict)
    environmental_signals: Dict[str, float] = field(default_factory=dict)
    
    # Differentiation history
    differentiation_path: List[CellType] = field(default_factory=list)
    differentiation_times: List[float] = field(default_factory=list)
    
    def can_differentiate(self) -> bool:
        """Check if cell can still differentiate"""
        return self.differentiation_potential > 0.0 and self.commitment_level < 1.0
    
    def differentiate_to(self, new_type: CellType, current_time: float) -> bool:
        """Attempt differentiation to new type"""
        if not self.can_differentiate():
            return False
            
        # Record history
        self.differentiation_path.append(self.current_type)
        self.differentiation_times.append(current_time)
        
        # Update state
        self.current_type = new_type
        self.differentiation_potential *= 0.5  # Reduce potential
        self.commitment_level = min(1.0, self.commitment_level + 0.3)
        
        # Clear growth factors after differentiation
        self.growth_factors.clear()
        
        return True
    
    def add_growth_factor(self, factor: str, concentration: float):
        """Add growth factor influence"""
        self.growth_factors[factor] = concentration
    
    def evaluate_differentiation_signals(self) -> Optional[CellType]:
        """Evaluate signals to determine differentiation fate"""
        if not self.can_differentiate():
            return None
            
        # Simple rule-based differentiation logic
        # (In reality, this would be much more complex)
        
        if self.growth_factors.get("BMP", 0) > 0.7:
            return CellType.BONE
        elif self.growth_factors.get("MyoD", 0) > 0.7:
            return CellType.MUSCLE
        elif self.growth_factors.get("Neurogenin", 0) > 0.7:
            return CellType.NERVE
        elif self.growth_factors.get("VEGF", 0) > 0.7:
            return CellType.BLOOD
            
        return None