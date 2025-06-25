"""Cell API Endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from biocode.application.commands.create_cell_command import (
    CreateCellCommand, CreateCellRequest, CreateCellResponse, CreateCellCommandValidator
)
from biocode.application.queries.get_cell_query import GetCellQuery, GetCellRequest
from biocode.interfaces.api.dependencies import (
    get_create_cell_command, get_cell_query, get_cell_repository
)


router = APIRouter()


# API Models (DTOs)
class CellCreateRequest(BaseModel):
    """API request model for creating a cell"""
    cell_type: str = Field(..., description="Type of cell to create")
    dna_template: Optional[str] = Field(None, description="Optional DNA template")
    initial_energy: float = Field(100.0, ge=0, le=200, description="Initial energy level")
    metadata: Optional[dict] = Field(None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cell_type": "neuron",
                "initial_energy": 100.0,
                "metadata": {"layer": "input", "position": [0, 0, 0]}
            }
        }


class CellResponse(BaseModel):
    """API response model for a cell"""
    id: str
    type: str
    health: float
    energy: float
    state: str
    age: float
    created_at: str
    metadata: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "cell_123abc",
                "type": "neuron",
                "health": 100.0,
                "energy": 85.5,
                "state": "active",
                "age": 120.5,
                "created_at": "2024-01-20T10:30:00Z",
                "metadata": {"layer": "input"}
            }
        }


class CellListResponse(BaseModel):
    """API response model for listing cells"""
    cells: List[CellResponse]
    total: int
    page: int
    page_size: int
    
    
class CellDivideRequest(BaseModel):
    """API request model for cell division"""
    energy_distribution: float = Field(
        0.5, ge=0.1, le=0.9, 
        description="Energy distribution ratio (0.5 = equal split)"
    )
    mutation_rate: float = Field(
        0.01, ge=0, le=1,
        description="Mutation probability"
    )


# Endpoints
@router.post("/", response_model=CellResponse, status_code=status.HTTP_201_CREATED)
async def create_cell(
    request: CellCreateRequest,
    command: CreateCellCommand = Depends(get_create_cell_command)
) -> CellResponse:
    """Create a new cell"""
    # Validate request
    validator = CreateCellCommandValidator()
    errors = validator.validate(CreateCellRequest(
        cell_type=request.cell_type,
        dna_template=request.dna_template,
        initial_energy=request.initial_energy,
        metadata=request.metadata
    ))
    
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": errors}
        )
    
    # Execute command
    try:
        result = await command.execute(CreateCellRequest(
            cell_type=request.cell_type,
            dna_template=request.dna_template,
            initial_energy=request.initial_energy,
            metadata=request.metadata
        ))
        
        # Get the created cell for full response
        query = GetCellQuery(await get_cell_repository())
        cell = await query.execute(GetCellRequest(cell_id=result.cell_id))
        
        return CellResponse(
            id=cell.id,
            type=cell.type,
            health=cell.health,
            energy=cell.energy,
            state=cell.state.value,
            age=cell.get_age(),
            created_at=cell.created_at.isoformat(),
            metadata=cell.metadata
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create cell: {str(e)}"
        )


@router.get("/{cell_id}", response_model=CellResponse)
async def get_cell(
    cell_id: str,
    query: GetCellQuery = Depends(get_cell_query)
) -> CellResponse:
    """Get a specific cell by ID"""
    try:
        cell = await query.execute(GetCellRequest(cell_id=cell_id))
        
        if not cell:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cell not found: {cell_id}"
            )
            
        return CellResponse(
            id=cell.id,
            type=cell.type,
            health=cell.health,
            energy=cell.energy,
            state=cell.state.value,
            age=cell.get_age(),
            created_at=cell.created_at.isoformat(),
            metadata=cell.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cell: {str(e)}"
        )


@router.get("/", response_model=CellListResponse)
async def list_cells(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    cell_type: Optional[str] = Query(None, description="Filter by cell type"),
    min_health: Optional[float] = Query(None, ge=0, le=100, description="Minimum health"),
    repository = Depends(get_cell_repository)
) -> CellListResponse:
    """List cells with pagination and filtering"""
    try:
        # Get all cells (in real implementation, would use query object)
        all_cells = await repository.find_all()
        
        # Apply filters
        filtered_cells = all_cells
        
        if cell_type:
            filtered_cells = [c for c in filtered_cells if c.type == cell_type]
            
        if min_health is not None:
            filtered_cells = [c for c in filtered_cells if c.health >= min_health]
            
        # Pagination
        total = len(filtered_cells)
        start = (page - 1) * page_size
        end = start + page_size
        page_cells = filtered_cells[start:end]
        
        # Convert to response models
        cell_responses = [
            CellResponse(
                id=cell.id,
                type=cell.type,
                health=cell.health,
                energy=cell.energy,
                state=cell.state.value,
                age=cell.get_age(),
                created_at=cell.created_at.isoformat(),
                metadata=cell.metadata
            )
            for cell in page_cells
        ]
        
        return CellListResponse(
            cells=cell_responses,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list cells: {str(e)}"
        )


@router.delete("/{cell_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cell(
    cell_id: str,
    repository = Depends(get_cell_repository)
):
    """Delete a cell"""
    try:
        cell = await repository.find_by_id(cell_id)
        if not cell:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cell not found: {cell_id}"
            )
            
        await repository.delete(cell_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete cell: {str(e)}"
        )


@router.post("/{cell_id}/divide", response_model=CellResponse)
async def divide_cell(
    cell_id: str,
    request: CellDivideRequest,
    repository = Depends(get_cell_repository)
) -> CellResponse:
    """Trigger cell division"""
    try:
        # Get the cell
        cell = await repository.find_by_id(cell_id)
        if not cell:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cell not found: {cell_id}"
            )
            
        # Check if cell can divide
        if not cell.can_divide():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cell cannot divide in its current state"
            )
            
        # Perform division
        child_cell = await cell.divide(
            energy_split_ratio=request.energy_distribution,
            mutation_rate=request.mutation_rate
        )
        
        # Save both cells
        await repository.save(cell)  # Parent with reduced energy
        await repository.save(child_cell)  # New child cell
        
        # Return child cell info
        return CellResponse(
            id=child_cell.id,
            type=child_cell.type,
            health=child_cell.health,
            energy=child_cell.energy,
            state=child_cell.state.value,
            age=child_cell.get_age(),
            created_at=child_cell.created_at.isoformat(),
            metadata=child_cell.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to divide cell: {str(e)}"
        )


@router.put("/{cell_id}/energy", response_model=CellResponse)
async def update_cell_energy(
    cell_id: str,
    energy: float = Query(..., ge=0, le=200, description="New energy level"),
    repository = Depends(get_cell_repository)
) -> CellResponse:
    """Update cell energy level"""
    try:
        cell = await repository.find_by_id(cell_id)
        if not cell:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cell not found: {cell_id}"
            )
            
        # Update energy
        cell.set_energy(energy)
        
        # Save updated cell
        await repository.save(cell)
        
        return CellResponse(
            id=cell.id,
            type=cell.type,
            health=cell.health,
            energy=cell.energy,
            state=cell.state.value,
            age=cell.get_age(),
            created_at=cell.created_at.isoformat(),
            metadata=cell.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update cell energy: {str(e)}"
        )