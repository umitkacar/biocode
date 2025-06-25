"""Repository interfaces"""
from abc import ABC, abstractmethod
from typing import List, Optional
from biocode.domain.entities import Cell, Tissue, Organ, System


class CellRepository(ABC):
    @abstractmethod
    async def save(self, cell: Cell) -> None:
        pass
    
    @abstractmethod
    async def find_by_id(self, cell_id: str) -> Optional[Cell]:
        pass
    
    @abstractmethod
    async def find_all(self) -> List[Cell]:
        pass
    
    @abstractmethod
    async def delete(self, cell_id: str) -> None:
        pass


class TissueRepository(ABC):
    @abstractmethod
    async def save(self, tissue: Tissue) -> None:
        pass
    
    @abstractmethod
    async def find_by_id(self, tissue_id: str) -> Optional[Tissue]:
        pass


class OrganRepository(ABC):
    @abstractmethod
    async def save(self, organ: Organ) -> None:
        pass
    
    @abstractmethod
    async def find_by_id(self, organ_id: str) -> Optional[Organ]:
        pass


class SystemRepository(ABC):
    @abstractmethod
    async def save(self, system: System) -> None:
        pass
    
    @abstractmethod
    async def find_by_id(self, system_id: str) -> Optional[System]:
        pass
