"""API Dependencies for Dependency Injection"""
from typing import AsyncGenerator
from fastapi import Depends

from biocode.application.interfaces.repositories import (
    CellRepository, TissueRepository, OrganRepository, SystemRepository
)
from biocode.application.interfaces.event_bus import EventBus
from biocode.infrastructure.persistence.memory.cell_repository_impl import InMemoryCellRepository
from biocode.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
from biocode.application.commands.create_cell_command import CreateCellCommand
from biocode.application.queries.get_cell_query import GetCellQuery


# Repository singletons (in production, these would be scoped per request or use connection pooling)
_cell_repository: CellRepository = None
_tissue_repository: TissueRepository = None
_organ_repository: OrganRepository = None
_system_repository: SystemRepository = None
_event_bus: EventBus = None


async def get_repositories():
    """Initialize all repositories"""
    global _cell_repository, _tissue_repository, _organ_repository, _system_repository, _event_bus
    
    if _cell_repository is None:
        _cell_repository = InMemoryCellRepository()
        _event_bus = InMemoryEventBus()
        # Initialize other repositories when implemented
        
    return {
        "cell": _cell_repository,
        "tissue": _tissue_repository,
        "organ": _organ_repository,
        "system": _system_repository,
        "event_bus": _event_bus
    }


# Repository dependencies
async def get_cell_repository() -> CellRepository:
    """Get cell repository instance"""
    if _cell_repository is None:
        await get_repositories()
    return _cell_repository


async def get_tissue_repository() -> TissueRepository:
    """Get tissue repository instance"""
    if _tissue_repository is None:
        await get_repositories()
    return _tissue_repository


async def get_organ_repository() -> OrganRepository:
    """Get organ repository instance"""
    if _organ_repository is None:
        await get_repositories()
    return _organ_repository


async def get_system_repository() -> SystemRepository:
    """Get system repository instance"""
    if _system_repository is None:
        await get_repositories()
    return _system_repository


async def get_event_bus() -> EventBus:
    """Get event bus instance"""
    if _event_bus is None:
        await get_repositories()
    return _event_bus


# Command dependencies
async def get_create_cell_command(
    cell_repository: CellRepository = Depends(get_cell_repository),
    event_bus: EventBus = Depends(get_event_bus)
) -> CreateCellCommand:
    """Get create cell command handler"""
    return CreateCellCommand(cell_repository, event_bus)


# Query dependencies
async def get_cell_query(
    cell_repository: CellRepository = Depends(get_cell_repository)
) -> GetCellQuery:
    """Get cell query handler"""
    return GetCellQuery(cell_repository)


# Database session dependency (for future SQL implementation)
async def get_db_session() -> AsyncGenerator:
    """Get database session"""
    # Placeholder for future database implementation
    # async with SessionLocal() as session:
    #     try:
    #         yield session
    #         await session.commit()
    #     except Exception:
    #         await session.rollback()
    #         raise
    yield None