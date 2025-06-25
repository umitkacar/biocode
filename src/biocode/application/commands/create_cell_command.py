"""Create Cell Command Handler - Example of CQRS Pattern"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from biocode.application.interfaces.repositories import CellRepository
from biocode.application.interfaces.event_bus import EventBus
from biocode.domain.entities import Cell
from biocode.domain.value_objects.dna import DNA
from biocode.domain.events.cell_events import CellCreatedEvent


@dataclass
class CreateCellRequest:
    """DTO for cell creation request"""
    cell_type: str
    dna_template: Optional[str] = None
    initial_energy: float = 100.0
    metadata: dict = None


@dataclass
class CreateCellResponse:
    """DTO for cell creation response"""
    cell_id: str
    cell_type: str
    created_at: datetime
    initial_health: float


class CreateCellCommand:
    """
    Command handler for creating new cells.
    Implements the command pattern from CQRS.
    """
    
    def __init__(
        self, 
        cell_repository: CellRepository,
        event_bus: EventBus
    ):
        self.cell_repository = cell_repository
        self.event_bus = event_bus
        
    async def execute(self, request: CreateCellRequest) -> CreateCellResponse:
        """Execute the create cell command"""
        
        # Create DNA from template or generate random
        if request.dna_template:
            dna = DNA.from_template(request.dna_template)
        else:
            dna = DNA.random()
            
        # Create domain entity
        cell = Cell(
            cell_type=request.cell_type,
            dna=dna,
            initial_energy=request.initial_energy
        )
        
        # Apply any metadata
        if request.metadata:
            for key, value in request.metadata.items():
                cell.set_metadata(key, value)
                
        # Persist the cell
        await self.cell_repository.save(cell)
        
        # Publish domain event
        event = CellCreatedEvent(
            cell_id=cell.id,
            cell_type=cell.type,
            timestamp=cell.created_at
        )
        await self.event_bus.publish(event)
        
        # Return response DTO
        return CreateCellResponse(
            cell_id=cell.id,
            cell_type=cell.type,
            created_at=cell.created_at,
            initial_health=cell.health
        )


class CreateCellCommandValidator:
    """Validates create cell requests"""
    
    VALID_CELL_TYPES = ["neuron", "muscle", "epithelial", "stem", "immune"]
    
    def validate(self, request: CreateCellRequest) -> list[str]:
        """Validate the request and return list of errors"""
        errors = []
        
        # Validate cell type
        if not request.cell_type:
            errors.append("Cell type is required")
        elif request.cell_type not in self.VALID_CELL_TYPES:
            errors.append(f"Invalid cell type: {request.cell_type}")
            
        # Validate energy
        if request.initial_energy <= 0:
            errors.append("Initial energy must be positive")
        elif request.initial_energy > 200:
            errors.append("Initial energy cannot exceed 200")
            
        # Validate DNA template if provided
        if request.dna_template:
            if len(request.dna_template) < 10:
                errors.append("DNA template too short")
            elif not all(c in "ACGT" for c in request.dna_template.upper()):
                errors.append("DNA template contains invalid nucleotides")
                
        return errors