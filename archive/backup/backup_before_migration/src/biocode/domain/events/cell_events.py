"""Domain Events for Cell aggregate"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events"""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)
    
    def get_aggregate_id(self) -> str:
        """Get the ID of the aggregate that raised this event"""
        raise NotImplementedError
        
    def get_event_type(self) -> str:
        """Get the event type name"""
        return self.__class__.__name__


@dataclass(frozen=True)
class CellCreatedEvent(DomainEvent):
    """Event raised when a new cell is created"""
    cell_id: str
    cell_type: str
    initial_energy: float = 100.0
    dna_sequence: Optional[str] = None
    
    def get_aggregate_id(self) -> str:
        return self.cell_id


@dataclass(frozen=True)
class CellDividedEvent(DomainEvent):
    """Event raised when a cell divides"""
    parent_cell_id: str
    child_cell_id: str
    parent_energy_after: float
    child_energy: float
    mutation_occurred: bool = False
    
    def get_aggregate_id(self) -> str:
        return self.parent_cell_id


@dataclass(frozen=True)
class CellDiedEvent(DomainEvent):
    """Event raised when a cell dies"""
    cell_id: str
    cause_of_death: str
    age_at_death: float  # seconds
    final_health: float
    
    def get_aggregate_id(self) -> str:
        return self.cell_id


@dataclass(frozen=True)
class CellMutatedEvent(DomainEvent):
    """Event raised when a cell mutates"""
    cell_id: str
    mutation_type: str
    old_trait: Dict[str, Any]
    new_trait: Dict[str, Any]
    
    def get_aggregate_id(self) -> str:
        return self.cell_id


@dataclass(frozen=True)
class CellStateChangedEvent(DomainEvent):
    """Event raised when cell state changes"""
    cell_id: str
    old_state: str
    new_state: str
    trigger: str  # What caused the state change
    
    def get_aggregate_id(self) -> str:
        return self.cell_id


@dataclass(frozen=True)
class CellEnergyDepletedEvent(DomainEvent):
    """Event raised when cell energy falls below critical threshold"""
    cell_id: str
    current_energy: float
    threshold: float = 10.0
    
    def get_aggregate_id(self) -> str:
        return self.cell_id


@dataclass(frozen=True)
class CellHealedEvent(DomainEvent):
    """Event raised when a cell is healed"""
    cell_id: str
    health_before: float
    health_after: float
    healing_amount: float
    healing_source: str  # What healed the cell
    
    def get_aggregate_id(self) -> str:
        return self.cell_id


@dataclass(frozen=True)
class CellDamagedEvent(DomainEvent):
    """Event raised when a cell takes damage"""
    cell_id: str
    health_before: float
    health_after: float
    damage_amount: float
    damage_source: str  # What damaged the cell
    
    def get_aggregate_id(self) -> str:
        return self.cell_id


@dataclass(frozen=True)
class CellSpecializedEvent(DomainEvent):
    """Event raised when a stem cell specializes"""
    cell_id: str
    old_type: str
    new_type: str
    specialization_trigger: str
    
    def get_aggregate_id(self) -> str:
        return self.cell_id


@dataclass(frozen=True)
class CellCommunicationEvent(DomainEvent):
    """Event raised when cells communicate"""
    sender_cell_id: str
    receiver_cell_id: Optional[str]  # None for broadcast
    message_type: str
    message_content: Dict[str, Any]
    
    def get_aggregate_id(self) -> str:
        return self.sender_cell_id