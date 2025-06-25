"""Get Cell Query Handler - Example of CQRS Query Pattern"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

from biocode.application.interfaces.repositories import CellRepository
from biocode.domain.entities import Cell


@dataclass
class GetCellRequest:
    """Request for getting a single cell"""
    cell_id: str


@dataclass
class GetCellsRequest:
    """Request for getting multiple cells with filters"""
    cell_type: Optional[str] = None
    min_health: Optional[float] = None
    max_age_seconds: Optional[float] = None
    tissue_id: Optional[str] = None
    limit: int = 100
    offset: int = 0


@dataclass
class CellStatisticsRequest:
    """Request for cell statistics"""
    group_by: str = "type"  # type, tissue, health_range


class GetCellQuery:
    """
    Query handler for retrieving cell information.
    Read-only operations following CQRS pattern.
    """
    
    def __init__(self, cell_repository: CellRepository):
        self.cell_repository = cell_repository
        
    async def execute(self, request: GetCellRequest) -> Optional[Cell]:
        """Get a single cell by ID"""
        return await self.cell_repository.find_by_id(request.cell_id)


class GetCellsQuery:
    """Query handler for retrieving multiple cells"""
    
    def __init__(self, cell_repository: CellRepository):
        self.cell_repository = cell_repository
        
    async def execute(self, request: GetCellsRequest) -> List[Cell]:
        """Get cells matching the filter criteria"""
        # Get all cells first (in production, this would be optimized)
        all_cells = await self.cell_repository.find_all()
        
        # Apply filters
        filtered_cells = all_cells
        
        if request.cell_type:
            filtered_cells = [
                cell for cell in filtered_cells 
                if cell.type == request.cell_type
            ]
            
        if request.min_health is not None:
            filtered_cells = [
                cell for cell in filtered_cells 
                if cell.health >= request.min_health
            ]
            
        if request.max_age_seconds is not None:
            current_time = datetime.now()
            filtered_cells = [
                cell for cell in filtered_cells 
                if (current_time - cell.created_at).total_seconds() <= request.max_age_seconds
            ]
            
        if request.tissue_id:
            filtered_cells = [
                cell for cell in filtered_cells 
                if cell.get_metadata("tissue_id") == request.tissue_id
            ]
            
        # Apply pagination
        start = request.offset
        end = start + request.limit
        return filtered_cells[start:end]


class GetCellStatisticsQuery:
    """Query handler for cell statistics"""
    
    def __init__(self, cell_repository: CellRepository):
        self.cell_repository = cell_repository
        
    async def execute(self, request: CellStatisticsRequest) -> Dict[str, Any]:
        """Get statistics about cells"""
        all_cells = await self.cell_repository.find_all()
        
        if not all_cells:
            return {
                "total_cells": 0,
                "groups": {},
                "summary": {}
            }
            
        statistics = {
            "total_cells": len(all_cells),
            "groups": {},
            "summary": {
                "average_health": sum(c.health for c in all_cells) / len(all_cells),
                "average_energy": sum(c.energy for c in all_cells) / len(all_cells),
                "average_age": sum(
                    (datetime.now() - c.created_at).total_seconds() 
                    for c in all_cells
                ) / len(all_cells)
            }
        }
        
        # Group by requested field
        if request.group_by == "type":
            groups = {}
            for cell in all_cells:
                if cell.type not in groups:
                    groups[cell.type] = {
                        "count": 0,
                        "average_health": 0,
                        "average_energy": 0,
                        "cells": []
                    }
                group = groups[cell.type]
                group["count"] += 1
                group["cells"].append(cell.id)
                
            # Calculate averages
            for cell_type, group in groups.items():
                type_cells = [c for c in all_cells if c.type == cell_type]
                group["average_health"] = sum(c.health for c in type_cells) / len(type_cells)
                group["average_energy"] = sum(c.energy for c in type_cells) / len(type_cells)
                del group["cells"]  # Remove cell IDs from response
                
            statistics["groups"] = groups
            
        elif request.group_by == "health_range":
            ranges = {
                "critical": (0, 25),
                "poor": (25, 50),
                "fair": (50, 75),
                "good": (75, 90),
                "excellent": (90, 100)
            }
            
            groups = {name: {"count": 0, "cells": []} for name in ranges}
            
            for cell in all_cells:
                for range_name, (min_health, max_health) in ranges.items():
                    if min_health <= cell.health <= max_health:
                        groups[range_name]["count"] += 1
                        break
                        
            statistics["groups"] = groups
            
        return statistics


class GetCellLineageQuery:
    """Query handler for cell lineage/ancestry"""
    
    def __init__(self, cell_repository: CellRepository):
        self.cell_repository = cell_repository
        
    async def execute(self, cell_id: str) -> Dict[str, Any]:
        """Get the lineage of a cell"""
        cell = await self.cell_repository.find_by_id(cell_id)
        if not cell:
            return {"error": "Cell not found"}
            
        lineage = {
            "cell_id": cell.id,
            "ancestors": [],
            "descendants": [],
            "generation": 0
        }
        
        # Trace ancestors
        current = cell
        while current and hasattr(current, 'parent_id') and current.parent_id:
            parent = await self.cell_repository.find_by_id(current.parent_id)
            if parent:
                lineage["ancestors"].append({
                    "id": parent.id,
                    "type": parent.type,
                    "created_at": parent.created_at.isoformat()
                })
                lineage["generation"] += 1
                current = parent
            else:
                break
                
        # Find descendants
        all_cells = await self.cell_repository.find_all()
        descendants = self._find_descendants(cell.id, all_cells)
        
        lineage["descendants"] = [
            {
                "id": d.id,
                "type": d.type,
                "created_at": d.created_at.isoformat(),
                "generation": self._get_generation_from_ancestor(d, cell.id, all_cells)
            }
            for d in descendants
        ]
        
        return lineage
        
    def _find_descendants(self, ancestor_id: str, all_cells: List[Cell]) -> List[Cell]:
        """Recursively find all descendants of a cell"""
        descendants = []
        
        for cell in all_cells:
            if hasattr(cell, 'parent_id') and cell.parent_id == ancestor_id:
                descendants.append(cell)
                # Recursively find descendants of this cell
                descendants.extend(self._find_descendants(cell.id, all_cells))
                
        return descendants
        
    def _get_generation_from_ancestor(
        self, 
        cell: Cell, 
        ancestor_id: str, 
        all_cells: List[Cell]
    ) -> int:
        """Calculate generation distance from ancestor"""
        generation = 0
        current = cell
        
        while current and hasattr(current, 'parent_id') and current.parent_id:
            generation += 1
            if current.parent_id == ancestor_id:
                return generation
                
            # Find parent
            parent = next(
                (c for c in all_cells if c.id == current.parent_id), 
                None
            )
            current = parent
            
        return generation