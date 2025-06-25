import asyncio
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type

from src.utils.logging_config import get_logger, log_tissue_event
from .codecell_example import CellState, CodeCell


class TransactionState(Enum):
    """Transaction durumları"""

    PENDING = "pending"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"


@dataclass
class TissueTransaction:
    """Tissue düzeyinde atomik operasyonlar"""

    id: str
    operations: List[Callable]
    affected_cells: Set[str]
    state: TransactionState
    timestamp: datetime
    rollback_operations: List[Callable]


@dataclass
class TissueMetrics:
    """Tissue performans metrikleri"""

    throughput: float = 0.0
    latency_ms: float = 0.0
    error_rate: float = 0.0
    health_score: float = 100.0
    active_cells: int = 0
    infected_cells: int = 0


class AdvancedCodeTissue:
    """Gelişmiş AdvancedCodeTissue - Multi-class container with advanced features"""

    def __init__(self, tissue_name: str):
        self.name = tissue_name
        self.cells: Dict[str, CodeCell] = {}
        self.cell_types: Dict[str, Type[CodeCell]] = {}
        self.connections: Dict[str, List[str]] = {}

        # Gelişmiş özellikler
        self.quarantine: Set[str] = set()  # İzole edilmiş hatalı cells
        self.transactions: Dict[str, TissueTransaction] = {}
        self.metrics = TissueMetrics()
        self.inflammation_threshold = 0.3  # %30 enfeksiyon oranı

        # Dependency injection container
        self.dependencies: Dict[str, Any] = {}
        self.cell_lifecycle_hooks = {
            "pre_create": [],
            "post_create": [],
            "pre_destroy": [],
            "post_destroy": [],
        }

        # Logging
        self.logger = get_logger(__name__, tissue_name=tissue_name)

    def register_cell_type(self, cell_type: Type[CodeCell]):
        """Yeni cell tipi kaydet"""
        self.cell_types[cell_type.__name__] = cell_type

    def inject_dependency(self, name: str, dependency: Any):
        """Dependency injection for cells"""
        self.dependencies[name] = dependency

    def register_lifecycle_hook(self, hook_type: str, callback: Callable):
        """Cell yaşam döngüsü hook'ları"""
        if hook_type in self.cell_lifecycle_hooks:
            self.cell_lifecycle_hooks[hook_type].append(callback)

    def connect_cells(self, cell1: str, cell2: str):
        """İki cell arasında bağlantı kur"""
        # Save connection history for rollback
        if not hasattr(self, "connection_history"):
            self.connection_history = {}

        # Save current state before modification
        if cell1 in self.connections:
            if cell1 not in self.connection_history:
                self.connection_history[cell1] = self.connections[cell1].copy()
            self.connections[cell1].append(cell2)

        if cell2 in self.connections:
            if cell2 not in self.connection_history:
                self.connection_history[cell2] = self.connections[cell2].copy()
            self.connections[cell2].append(cell1)

    def grow_cell(self, cell_name: str, cell_type: str, **kwargs) -> CodeCell:
        """Gelişmiş cell üretimi with lifecycle management"""
        if cell_type not in self.cell_types:
            self.logger.error(f"Unknown cell type: {cell_type}")
            raise ValueError(f"Unknown cell type: {cell_type}")

        self.logger.debug(f"Growing new cell: {cell_name} of type {cell_type}")

        # Pre-create hooks
        for hook in self.cell_lifecycle_hooks["pre_create"]:
            hook(cell_name, cell_type, kwargs)

        # Dependency injection
        kwargs.update(self.dependencies)

        # Cell oluştur
        cell_class = self.cell_types[cell_type]
        new_cell = cell_class(cell_name, **kwargs)

        # Immune response tanımla
        new_cell.immune_response = lambda c: self._handle_cell_infection(c)

        self.cells[cell_name] = new_cell
        self.connections[cell_name] = []

        # Post-create hooks
        for hook in self.cell_lifecycle_hooks["post_create"]:
            hook(new_cell)

        self._update_metrics()
        
        log_tissue_event(self.logger, f"Cell grown: {cell_name}", self.name, cell_type=cell_type)
        return new_cell

    def _handle_cell_infection(self, infected_cell: CodeCell):
        """Enfekte cell'e müdahale"""
        self.logger.warning(f"Cell {infected_cell.name} is infected!")

        # Quarantine the cell
        self.quarantine.add(infected_cell.name)

        # Disconnect from healthy cells
        if infected_cell.name in self.connections:
            for connected in self.connections[infected_cell.name]:
                if connected not in self.quarantine:
                    # Geçici bağlantı kesme
                    self.connections[connected].remove(infected_cell.name)

        # Check for tissue-wide inflammation
        self._check_inflammation()

    def _check_inflammation(self):
        """Tissue genelinde enflamasyon kontrolü"""
        infected_count = sum(
            1
            for cell in self.cells.values()
            if cell.state in [CellState.INFECTED, CellState.INFLAMED]
        )

        infection_rate = infected_count / len(self.cells) if self.cells else 0

        if infection_rate > self.inflammation_threshold:
            self.logger.critical(
                f"Tissue inflammation detected! Rate: {infection_rate:.2%}"
            )
            self._trigger_tissue_immune_response()

    def _trigger_tissue_immune_response(self):
        """Tissue düzeyinde bağışıklık tepkisi"""
        # Tüm sağlıklı cell'leri güçlendir
        for cell in self.cells.values():
            if cell.state == CellState.HEALTHY:
                cell.health_score = min(100, cell.health_score + 20)

        # Quarantine'deki cell'leri iyileştir
        for cell_name in list(self.quarantine):
            cell = self.cells[cell_name]
            cell.trigger_immune_response()

            # İyileşme kontrolü
            if cell.health_score > 50:
                self.quarantine.remove(cell_name)
                cell.state = CellState.HEALTHY

                # Bağlantıları yeniden kur
                self._restore_connections(cell_name)

    def _restore_connections(self, cell_name: str):
        """Cell bağlantılarını restore et"""
        # Check if we have connection history
        if not hasattr(self, "connection_history"):
            self.connection_history = {}

        if cell_name in self.connection_history:
            # Restore previous connections
            previous_connections = self.connection_history[cell_name]
            self.connections[cell_name] = previous_connections.copy()

            # Restore bidirectional connections
            for connected_cell in previous_connections:
                if connected_cell in self.connections:
                    if cell_name not in self.connections[connected_cell]:
                        self.connections[connected_cell].append(cell_name)

            self.logger.info(
                f"Restored {len(previous_connections)} connections for {cell_name}"
            )
        else:
            # No history, start fresh
            self.connections[cell_name] = []

    @contextmanager
    def transaction(self, transaction_id: str):
        """Atomik tissue operasyonları"""
        tx = TissueTransaction(
            id=transaction_id,
            operations=[],
            affected_cells=set(),
            state=TransactionState.PENDING,
            timestamp=datetime.now(),
            rollback_operations=[],
        )

        self.transactions[transaction_id] = tx

        try:
            yield tx
            # Commit
            tx.state = TransactionState.COMMITTED
            self.logger.info(f"Transaction {transaction_id} committed")

        except Exception as e:
            # Rollback
            self.logger.error(f"Transaction {transaction_id} failed: {e}")
            tx.state = TransactionState.ROLLED_BACK

            # Execute rollback operations
            for rollback_op in reversed(tx.rollback_operations):
                try:
                    rollback_op()
                except Exception as rollback_error:
                    self.logger.error(f"Rollback failed: {rollback_error}")

            raise

    def _update_metrics(self):
        """Performans metriklerini güncelle"""
        total_cells = len(self.cells)
        infected = sum(
            1
            for c in self.cells.values()
            if c.state in [CellState.INFECTED, CellState.INFLAMED]
        )

        self.metrics.active_cells = total_cells
        self.metrics.infected_cells = infected
        self.metrics.error_rate = infected / total_cells if total_cells > 0 else 0

        # Ortalama health score
        avg_health = (
            sum(c.health_score for c in self.cells.values()) / total_cells
            if total_cells > 0
            else 100
        )
        self.metrics.health_score = avg_health

    async def execute_coordinated_operation(
        self, operation: Callable, target_cells: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Koordineli async operasyon"""
        target_cells = target_cells or list(self.cells.keys())
        tasks = []

        for cell_name in target_cells:
            if cell_name in self.cells and cell_name not in self.quarantine:
                cell = self.cells[cell_name]
                task = asyncio.create_task(operation(cell))
                tasks.append((cell_name, task))

        results = {}
        for cell_name, task in tasks:
            try:
                results[cell_name] = await task
            except Exception as e:
                self.logger.error(f"Operation failed for {cell_name}: {e}")
                self.cells[cell_name].infect(e)

        return results

    def get_tissue_diagnostics(self) -> Dict[str, Any]:
        """Detaylı tissue teşhis bilgisi"""
        return {
            "name": self.name,
            "metrics": {
                "throughput": self.metrics.throughput,
                "latency_ms": self.metrics.latency_ms,
                "error_rate": f"{self.metrics.error_rate:.2%}",
                "health_score": self.metrics.health_score,
                "active_cells": self.metrics.active_cells,
                "infected_cells": self.metrics.infected_cells,
            },
            "quarantine": list(self.quarantine),
            "cell_states": {
                cell_name: cell.state for cell_name, cell in self.cells.items()
            },
            "transactions": {
                tx_id: tx.state.value for tx_id, tx in self.transactions.items()
            },
        }

    async def send_signal(self, from_cell: str, to_cell: str, signal: Any):
        """Cell'ler arası sinyal gönder"""
        if to_cell in self.cells:
            receiver = self.cells[to_cell]
            if hasattr(receiver, "receive_signal"):
                await receiver.receive_signal(signal)

    def calculate_tissue_health(self) -> float:
        """Calculate overall tissue health"""
        if not self.cells:
            return 100.0

        # Calculate average health of all cells
        total_health = sum(cell.health_score for cell in self.cells.values())
        avg_health = total_health / len(self.cells)

        # Factor in infection rate
        infection_rate = (
            self.metrics.infected_cells / len(self.cells) if len(self.cells) > 0 else 0
        )
        health_penalty = infection_rate * 50  # 50% penalty for full infection

        return max(0, avg_health - health_penalty)
