"""
Biological Components - Core life data
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime


class CellState(Enum):
    """Cell lifecycle states"""
    DORMANT = "dormant"
    ACTIVE = "active"
    DIVIDING = "dividing"
    DYING = "dying"
    DEAD = "dead"


@dataclass
class LifeComponent:
    """Yaşam döngüsü verisi"""
    birth_time: float
    age: float = 0.0
    lifespan: float = 100.0
    generation: int = 0
    parent_id: Optional[str] = None
    
    def time_until_death(self) -> float:
        """Calculate remaining lifetime"""
        return max(0, self.lifespan - self.age)
    
    def is_alive(self) -> bool:
        """Check if still within lifespan"""
        return self.age < self.lifespan


@dataclass
class EnergyComponent:
    """Enerji yönetimi verisi"""
    current: float = 100.0
    maximum: float = 100.0
    consumption_rate: float = 1.0
    production_rate: float = 0.5
    
    def __post_init__(self):
        """Validate energy values"""
        self.current = max(0, min(self.current, self.maximum))
    
    def percentage(self) -> float:
        """Get energy as percentage"""
        return (self.current / self.maximum * 100) if self.maximum > 0 else 0
    
    def is_depleted(self) -> bool:
        """Check if energy is depleted"""
        return self.current <= 0


@dataclass
class DNAComponent:
    """Genetik bilgi"""
    sequence: str
    mutation_rate: float = 0.001
    dominant_traits: List[str] = field(default_factory=list)
    recessive_traits: List[str] = field(default_factory=list)
    epigenetic_markers: Dict[str, bool] = field(default_factory=dict)
    
    def has_trait(self, trait: str) -> bool:
        """Check if DNA contains a specific trait"""
        return trait in self.dominant_traits or trait in self.recessive_traits
    
    def trait_is_dominant(self, trait: str) -> bool:
        """Check if a trait is dominant"""
        return trait in self.dominant_traits


@dataclass
class HealthComponent:
    """Sağlık verisi"""
    current: float = 100.0
    maximum: float = 100.0
    regeneration_rate: float = 1.0
    damage_resistance: float = 0.0
    
    def __post_init__(self):
        """Validate health values"""
        self.current = max(0, min(self.current, self.maximum))
    
    def percentage(self) -> float:
        """Get health as percentage"""
        return (self.current / self.maximum * 100) if self.maximum > 0 else 0
    
    def is_critical(self) -> bool:
        """Check if health is critically low"""
        return self.percentage() < 20


@dataclass
class StateComponent:
    """Durum verisi"""
    state: CellState = CellState.DORMANT
    last_state_change: float = 0.0
    state_history: List[Tuple[CellState, float]] = field(default_factory=list)
    
    def change_state(self, new_state: CellState, timestamp: float):
        """Change state and record history"""
        if self.state != new_state:
            self.state_history.append((self.state, timestamp))
            self.state = new_state
            self.last_state_change = timestamp
    
    def time_in_current_state(self, current_time: float) -> float:
        """Calculate time spent in current state"""
        return current_time - self.last_state_change


@dataclass
class MemoryComponent:
    """Bellek verisi"""
    short_term: Dict[str, Any] = field(default_factory=dict)
    long_term: Dict[str, Any] = field(default_factory=dict)
    capacity: int = 100
    consolidation_rate: float = 0.1
    
    def store_short_term(self, key: str, value: Any) -> bool:
        """Store in short-term memory"""
        if len(self.short_term) < self.capacity:
            self.short_term[key] = {
                'value': value,
                'timestamp': datetime.now(),
                'access_count': 0
            }
            return True
        return False
    
    def recall(self, key: str) -> Optional[Any]:
        """Recall from memory"""
        if key in self.short_term:
            self.short_term[key]['access_count'] += 1
            return self.short_term[key]['value']
        elif key in self.long_term:
            self.long_term[key]['access_count'] += 1
            return self.long_term[key]['value']
        return None
    
    def consolidate(self, key: str) -> bool:
        """Move from short-term to long-term memory"""
        if key in self.short_term:
            self.long_term[key] = self.short_term.pop(key)
            return True
        return False