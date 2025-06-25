"""Domain Events for Cell aggregate"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4


def generate_event_id() -> str:
    """Generate unique event ID"""
    return str(uuid4())


def get_current_time() -> datetime:
    """Get current timestamp"""
    return datetime.now()


@dataclass(frozen=True)
class CellCreatedEvent:
    """Event raised when a new cell is created"""
    cell_id: str
    cell_type: str
    initial_energy: float = 100.0
    dna_sequence: Optional[str] = None
    event_id: str = field(default_factory=generate_event_id)
    occurred_at: datetime = field(default_factory=get_current_time)
    
    def get_aggregate_id(self) -> str:
        return self.cell_id
        
    def get_event_type(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class CellDividedEvent:
    """Event raised when a cell divides"""
    parent_cell_id: str
    child_cell_id: str
    parent_energy_after: float
    child_energy: float
    mutation_occurred: bool = False
    event_id: str = field(default_factory=generate_event_id)
    occurred_at: datetime = field(default_factory=get_current_time)
    
    def get_aggregate_id(self) -> str:
        return self.parent_cell_id
        
    def get_event_type(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class CellDiedEvent:
    """Event raised when a cell dies"""
    cell_id: str
    cause_of_death: str
    age_at_death: float  # seconds
    final_health: float
    event_id: str = field(default_factory=generate_event_id)
    occurred_at: datetime = field(default_factory=get_current_time)
    
    def get_aggregate_id(self) -> str:
        return self.cell_id
        
    def get_event_type(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class CellMutatedEvent:
    """Event raised when a cell mutates"""
    cell_id: str
    mutation_type: str
    old_trait: Dict[str, Any] = field(default_factory=dict)
    new_trait: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=generate_event_id)
    occurred_at: datetime = field(default_factory=get_current_time)
    
    def get_aggregate_id(self) -> str:
        return self.cell_id
        
    def get_event_type(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class CellStateChangedEvent:
    """Event raised when cell state changes"""
    cell_id: str
    old_state: str
    new_state: str
    trigger: str  # What caused the state change
    event_id: str = field(default_factory=generate_event_id)
    occurred_at: datetime = field(default_factory=get_current_time)
    
    def get_aggregate_id(self) -> str:
        return self.cell_id
        
    def get_event_type(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class CellEnergyDepletedEvent:
    """Event raised when cell energy falls below critical threshold"""
    cell_id: str
    current_energy: float
    threshold: float = 10.0
    event_id: str = field(default_factory=generate_event_id)
    occurred_at: datetime = field(default_factory=get_current_time)
    
    def get_aggregate_id(self) -> str:
        return self.cell_id
        
    def get_event_type(self) -> str:
        return self.__class__.__name__