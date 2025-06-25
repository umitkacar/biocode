"""In-Memory Cell Repository Implementation"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from biocode.application.interfaces.repositories import CellRepository
from biocode.domain.entities.cell import Cell
from biocode.domain.exceptions import CellException


class InMemoryCellRepository(CellRepository):
    """
    In-memory implementation of CellRepository.
    Useful for testing and development.
    """
    
    def __init__(self):
        self._storage: Dict[str, Cell] = {}
        self._lock = asyncio.Lock()
        
        # Additional indexes for efficient queries
        self._by_type_index: Dict[str, List[str]] = {}
        self._by_tissue_index: Dict[str, List[str]] = {}
        self._creation_order: List[str] = []
        
    async def save(self, cell: Cell) -> None:
        """Save a cell to the repository"""
        async with self._lock:
            # Store the cell
            self._storage[cell.id] = cell
            
            # Update indexes
            if cell.id not in self._creation_order:
                self._creation_order.append(cell.id)
                
            # Update type index
            if cell.type not in self._by_type_index:
                self._by_type_index[cell.type] = []
            if cell.id not in self._by_type_index[cell.type]:
                self._by_type_index[cell.type].append(cell.id)
                
            # Update tissue index if cell belongs to a tissue
            tissue_id = cell.get_metadata("tissue_id")
            if tissue_id:
                if tissue_id not in self._by_tissue_index:
                    self._by_tissue_index[tissue_id] = []
                if cell.id not in self._by_tissue_index[tissue_id]:
                    self._by_tissue_index[tissue_id].append(cell.id)
                    
    async def find_by_id(self, cell_id: str) -> Optional[Cell]:
        """Find a cell by its ID"""
        async with self._lock:
            return self._storage.get(cell_id)
            
    async def find_all(self) -> List[Cell]:
        """Retrieve all cells"""
        async with self._lock:
            # Return in creation order
            return [
                self._storage[cell_id] 
                for cell_id in self._creation_order 
                if cell_id in self._storage
            ]
            
    async def delete(self, cell_id: str) -> None:
        """Delete a cell"""
        async with self._lock:
            if cell_id not in self._storage:
                raise CellException(f"Cell not found: {cell_id}")
                
            cell = self._storage[cell_id]
            
            # Remove from storage
            del self._storage[cell_id]
            
            # Remove from indexes
            self._creation_order.remove(cell_id)
            
            if cell.type in self._by_type_index:
                self._by_type_index[cell.type].remove(cell_id)
                if not self._by_type_index[cell.type]:
                    del self._by_type_index[cell.type]
                    
            tissue_id = cell.get_metadata("tissue_id")
            if tissue_id and tissue_id in self._by_tissue_index:
                self._by_tissue_index[tissue_id].remove(cell_id)
                if not self._by_tissue_index[tissue_id]:
                    del self._by_tissue_index[tissue_id]
                    
    # Additional query methods
    async def find_by_type(self, cell_type: str) -> List[Cell]:
        """Find all cells of a specific type"""
        async with self._lock:
            cell_ids = self._by_type_index.get(cell_type, [])
            return [self._storage[cell_id] for cell_id in cell_ids if cell_id in self._storage]
            
    async def find_by_tissue(self, tissue_id: str) -> List[Cell]:
        """Find all cells belonging to a tissue"""
        async with self._lock:
            cell_ids = self._by_tissue_index.get(tissue_id, [])
            return [self._storage[cell_id] for cell_id in cell_ids if cell_id in self._storage]
            
    async def count(self) -> int:
        """Count total cells"""
        async with self._lock:
            return len(self._storage)
            
    async def exists(self, cell_id: str) -> bool:
        """Check if a cell exists"""
        async with self._lock:
            return cell_id in self._storage
            
    async def find_healthy_cells(self, min_health: float = 80.0) -> List[Cell]:
        """Find all healthy cells above a threshold"""
        async with self._lock:
            return [
                cell for cell in self._storage.values()
                if cell.health >= min_health
            ]
            
    async def find_by_age(self, max_age_seconds: float) -> List[Cell]:
        """Find cells younger than specified age"""
        async with self._lock:
            current_time = datetime.now()
            return [
                cell for cell in self._storage.values()
                if (current_time - cell.created_at).total_seconds() <= max_age_seconds
            ]
            
    async def clear(self) -> None:
        """Clear all cells (useful for testing)"""
        async with self._lock:
            self._storage.clear()
            self._by_type_index.clear()
            self._by_tissue_index.clear()
            self._creation_order.clear()
            
    def get_statistics(self) -> Dict[str, any]:
        """Get repository statistics"""
        return {
            "total_cells": len(self._storage),
            "cell_types": list(self._by_type_index.keys()),
            "tissues": list(self._by_tissue_index.keys()),
            "cells_by_type": {
                cell_type: len(cell_ids) 
                for cell_type, cell_ids in self._by_type_index.items()
            },
            "cells_by_tissue": {
                tissue_id: len(cell_ids)
                for tissue_id, cell_ids in self._by_tissue_index.items()
            }
        }