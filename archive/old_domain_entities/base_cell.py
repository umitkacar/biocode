"""Base Cell implementation for legacy compatibility"""
import hashlib
import inspect
from datetime import datetime
from typing import Any, Callable, Dict, Optional


class CellState:
    """Cell'in sağlık durumu"""
    
    HEALTHY = "healthy"
    INFECTED = "infected"
    INFLAMED = "inflamed"
    HEALING = "healing"
    DEAD = "dead"


class CodeCell:
    """Base CodeCell - Her class'ın genetik DNA'sı"""
    
    def __init__(self, name: str):
        self.name = name
        self.dna = self._generate_dna()
        self.birth_time = datetime.now()
        self.mutations = []
        self.health_score = 100
        self.metabolism_rate = 1.0
        self.state = CellState.HEALTHY
        self.error_count = 0
        self.immune_response: Optional[Callable] = None
    
    def _generate_dna(self) -> str:
        """Class'ın unique genetic code'u"""
        source = inspect.getsource(self.__class__)
        return hashlib.md5(source.encode()).hexdigest()
    
    def mutate(self, mutation_type: str, details: Dict[str, Any]):
        """Code mutation tracking"""
        self.mutations.append(
            {"type": mutation_type, "details": details, "timestamp": datetime.now()}
        )
        self.health_score -= 5  # Her mutation sağlığı etkiler
    
    def heal(self):
        """Self-healing mechanism"""
        if self.health_score < 100:
            self.health_score = min(100, self.health_score + 10)
    
    def divide(self) -> "CodeCell":
        """Cell division - new instance creation"""
        child = self.__class__(f"{self.name}_child")
        child.dna = self.dna  # Inherit parent DNA
        child.metabolism_rate = self.metabolism_rate * 0.95
        return child
    
    def perform_operation(self, operation: Any) -> Any:
        """Perform a generic operation"""
        return f"Operation {operation} performed by {self.name}"
    
    def get_state(self) -> str:
        """Get current cell state"""
        return self.state
    
    def set_energy(self, energy: float):
        """Set cell energy level"""
        self.health_score = max(0, min(100, energy))
    
    @property
    def energy(self) -> float:
        """Get cell energy (health score)"""
        return self.health_score