import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..core.codecell_example import CodeCell
from ..utils.logging_config import get_logger


class ResourceType(Enum):
    """Tissue kaynakları"""

    CONFIG = "config"
    UTILITY = "utility"
    STANDARD = "standard"
    TEMPLATE = "template"
    CACHE = "cache"


@dataclass
class SharedResource:
    """Paylaşılan kaynak"""

    name: str
    type: ResourceType
    value: Any
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    accessed_count: int = 0
    last_accessed: Optional[datetime] = None

    def access(self) -> Any:
        """Kaynağa erişim"""
        self.accessed_count += 1
        self.last_accessed = datetime.now()
        return self.value


class ExtracellularMatrix:
    """Tissue içi ortak yapı ve standartlar (ECM)"""

    def __init__(self, tissue_name: str):
        self.tissue_name = tissue_name
        self.resources: Dict[str, SharedResource] = {}
        self.standards: Dict[str, Any] = {}
        self.barriers: List[Callable] = []  # Security filters
        self.connective_proteins: Dict[str, Callable] = {}  # Utility functions
        self.resource_locks: Dict[str, asyncio.Lock] = {}

        # Matrix health
        self.integrity = 1.0  # 0-1, structural integrity
        self.viscosity = 0.5  # 0-1, resource flow speed
        self.permeability = 0.8  # 0-1, barrier effectiveness

    def add_resource(
        self, name: str, resource_type: ResourceType, value: Any, version: str = "1.0.0"
    ):
        """Yeni kaynak ekle"""
        resource = SharedResource(
            name=name, type=resource_type, value=value, version=version
        )
        self.resources[name] = resource
        self.resource_locks[name] = asyncio.Lock()

    async def get_resource(self, name: str) -> Optional[Any]:
        """Kaynağa thread-safe erişim"""
        if name not in self.resources:
            return None

        async with self.resource_locks[name]:
            return self.resources[name].access()

    def set_standard(self, standard_name: str, standard_value: Any):
        """Tissue standardı belirle"""
        self.standards[standard_name] = standard_value

    def add_barrier(self, barrier_func: Callable[[Any], bool]):
        """Güvenlik filtresi ekle"""
        self.barriers.append(barrier_func)

    def add_connective_protein(self, name: str, protein_func: Callable):
        """Utility function ekle"""
        self.connective_proteins[name] = protein_func

    async def filter_through_barriers(self, data: Any) -> Tuple[bool, Optional[str]]:
        """Veriyi barrier'lardan geçir"""
        for barrier in self.barriers:
            try:
                if asyncio.iscoroutinefunction(barrier):
                    passed = await barrier(data)
                else:
                    passed = barrier(data)

                if not passed:
                    return False, f"Blocked by barrier: {barrier.__name__}"
            except Exception as e:
                logging.error(f"Barrier error: {e}")
                return False, f"Barrier error: {str(e)}"

        return True, None

    def apply_connective_protein(self, protein_name: str, *args, **kwargs) -> Any:
        """Connective protein (utility) uygula"""
        if protein_name not in self.connective_proteins:
            raise ValueError(f"Unknown protein: {protein_name}")

        protein = self.connective_proteins[protein_name]
        return protein(*args, **kwargs)

    def degrade(self, amount: float = 0.01):
        """Matrix degradation over time"""
        self.integrity = max(0, self.integrity - amount)
        self.viscosity = min(1.0, self.viscosity + amount * 0.5)

    def repair(self, amount: float = 0.05):
        """Matrix repair"""
        self.integrity = min(1.0, self.integrity + amount)
        self.viscosity = max(0.1, self.viscosity - amount * 0.3)

    def get_matrix_health(self) -> Dict[str, float]:
        """Matrix sağlık durumu"""
        return {
            "integrity": self.integrity,
            "viscosity": self.viscosity,
            "permeability": self.permeability,
            "resource_count": len(self.resources),
            "barrier_count": len(self.barriers),
            "protein_count": len(self.connective_proteins),
        }


class HomeostasisController:
    """Tissue dengesini koruyan sistem"""

    def __init__(self, tissue_name: str):
        self.tissue_name = tissue_name
        self.target_values = {
            "health": 85.0,
            "energy": 70.0,
            "stress": 20.0,
            "temperature": 37.0,
            "ph": 7.4,
        }
        self.current_values = self.target_values.copy()
        self.tolerance = 0.1  # %10 tolerance
        self.feedback_loops: Dict[str, Callable] = {}
        self.regulation_active = True
        self.last_check = datetime.now()

    def set_target(self, parameter: str, value: float):
        """Hedef değer belirle"""
        self.target_values[parameter] = value

    def update_current(self, parameter: str, value: float):
        """Güncel değeri güncelle"""
        self.current_values[parameter] = value

    def add_feedback_loop(self, parameter: str, regulator: Callable):
        """Feedback loop ekle"""
        self.feedback_loops[parameter] = regulator

    async def maintain_balance(self, cells: Dict[str, CodeCell]) -> Dict[str, Any]:
        """Dengeyi koru"""
        if not self.regulation_active:
            return {"status": "inactive"}

        adjustments = {}

        for parameter, target in self.target_values.items():
            current = self.current_values.get(parameter, target)
            deviation = abs(current - target) / target

            if deviation > self.tolerance:
                # Adjustment needed
                adjustment = await self._regulate_parameter(
                    parameter, current, target, cells
                )
                adjustments[parameter] = adjustment

        self.last_check = datetime.now()

        return {
            "status": "active",
            "adjustments": adjustments,
            "deviations": {
                param: abs(self.current_values.get(param, target) - target) / target
                for param, target in self.target_values.items()
            },
        }

    async def _regulate_parameter(
        self, parameter: str, current: float, target: float, cells: Dict[str, CodeCell]
    ) -> Dict[str, Any]:
        """Parametreyi düzenle"""
        adjustment = {
            "parameter": parameter,
            "current": current,
            "target": target,
            "action": "none",
        }

        if parameter in self.feedback_loops:
            regulator = self.feedback_loops[parameter]

            try:
                if asyncio.iscoroutinefunction(regulator):
                    result = await regulator(current, target, cells)
                else:
                    result = regulator(current, target, cells)

                adjustment["action"] = result
                adjustment["success"] = True

                # Update current value based on regulation
                if parameter == "health":
                    avg_health = sum(c.health_score for c in cells.values()) / len(
                        cells
                    )
                    self.current_values["health"] = avg_health
                elif parameter == "energy":
                    avg_energy = sum(c.energy_level for c in cells.values()) / len(
                        cells
                    )
                    self.current_values["energy"] = avg_energy
                elif parameter == "stress":
                    avg_stress = sum(c.stress_level for c in cells.values()) / len(
                        cells
                    )
                    self.current_values["stress"] = avg_stress

            except Exception as e:
                adjustment["success"] = False
                adjustment["error"] = str(e)
                logging.error(f"Regulation error for {parameter}: {e}")

        return adjustment

    def get_balance_report(self) -> Dict[str, Any]:
        """Denge durumu raporu"""
        return {
            "tissue": self.tissue_name,
            "regulation_active": self.regulation_active,
            "last_check": self.last_check.isoformat(),
            "parameters": {
                param: {
                    "current": self.current_values.get(param, 0),
                    "target": self.target_values.get(param, 0),
                    "deviation": abs(
                        self.current_values.get(param, 0)
                        - self.target_values.get(param, 0)
                    )
                    / self.target_values.get(param, 1),
                    "in_balance": abs(
                        self.current_values.get(param, 0)
                        - self.target_values.get(param, 0)
                    )
                    / self.target_values.get(param, 1)
                    <= self.tolerance,
                }
                for param in self.target_values
            },
        }


class VascularizationSystem:
    """Resource distribution system (blood vessel analogy)"""

    def __init__(self, tissue_name: str):
        self.tissue_name = tissue_name
        self.vessels: Dict[str, asyncio.Queue] = {}  # Named channels
        self.flow_rates: Dict[str, float] = {}
        self.pressure: float = 1.0  # System pressure
        self.oxygen_saturation: float = 0.98  # Resource availability

    async def create_vessel(self, vessel_name: str, capacity: int = 100):
        """Yeni vessel (channel) oluştur"""
        self.vessels[vessel_name] = asyncio.Queue(maxsize=capacity)
        self.flow_rates[vessel_name] = 1.0

    async def pump_resource(self, vessel_name: str, resource: Any) -> bool:
        """Kaynağı vessel'a pompalama"""
        if vessel_name not in self.vessels:
            return False

        vessel = self.vessels[vessel_name]

        # Apply pressure for flow rate
        flow_delay = 1.0 / (self.flow_rates[vessel_name] * self.pressure)
        await asyncio.sleep(flow_delay)

        try:
            await vessel.put(resource)
            return True
        except asyncio.QueueFull:
            # Backpressure - vessel is full
            return False

    async def receive_resource(
        self, vessel_name: str, timeout: Optional[float] = None
    ) -> Optional[Any]:
        """Vessel'dan kaynak al"""
        if vessel_name not in self.vessels:
            return None

        vessel = self.vessels[vessel_name]

        try:
            if timeout:
                resource = await asyncio.wait_for(vessel.get(), timeout)
            else:
                resource = await vessel.get()

            # Resource received successfully
            return resource

        except asyncio.TimeoutError:
            return None

    def adjust_flow_rate(self, vessel_name: str, new_rate: float):
        """Flow rate ayarla"""
        if vessel_name in self.vessels:
            self.flow_rates[vessel_name] = max(0.1, min(10.0, new_rate))

    def adjust_pressure(self, new_pressure: float):
        """System pressure ayarla"""
        self.pressure = max(0.5, min(2.0, new_pressure))

    def get_circulation_status(self) -> Dict[str, Any]:
        """Dolaşım durumu"""
        vessel_stats = {}
        for name, vessel in self.vessels.items():
            vessel_stats[name] = {
                "current_load": vessel.qsize(),
                "capacity": vessel.maxsize,
                "utilization": (
                    vessel.qsize() / vessel.maxsize if vessel.maxsize > 0 else 0
                ),
                "flow_rate": self.flow_rates.get(name, 1.0),
            }

        return {
            "pressure": self.pressure,
            "oxygen_saturation": self.oxygen_saturation,
            "vessels": vessel_stats,
            "total_flow": sum(self.flow_rates.values()),
        }


# Utility functions for tissue components
def create_standard_barriers() -> List[Callable]:
    """Standart güvenlik barrier'ları oluştur"""
    barriers = []

    # SQL Injection barrier
    def sql_injection_barrier(data: Any) -> bool:
        if isinstance(data, str):
            dangerous_patterns = ["DROP", "DELETE", "INSERT", "UPDATE", "--", ";"]
            data_upper = data.upper()
            return not any(pattern in data_upper for pattern in dangerous_patterns)
        return True

    # Size limit barrier
    def size_limit_barrier(data: Any) -> bool:
        if isinstance(data, (str, bytes)):
            return len(data) < 1_000_000  # 1MB limit
        elif isinstance(data, (list, dict)):
            return len(str(data)) < 1_000_000
        return True

    # Rate limit barrier (simplified)
    request_counts = defaultdict(int)

    def rate_limit_barrier(data: Any) -> bool:
        if isinstance(data, dict) and "source" in data:
            source = data["source"]
            request_counts[source] += 1
            return request_counts[source] < 100  # Max 100 requests per source
        return True

    barriers.extend([sql_injection_barrier, size_limit_barrier, rate_limit_barrier])
    return barriers


def create_health_regulators() -> Dict[str, Callable]:
    """Sağlık regülatörleri oluştur"""

    async def health_regulator(
        current: float, target: float, cells: Dict[str, CodeCell]
    ) -> str:
        """Sağlık regülatörü"""
        if current < target:
            # Heal cells
            for cell in cells.values():
                if cell.health_score < target:
                    cell.heal()
            return "healing_applied"
        return "no_action"

    async def energy_regulator(
        current: float, target: float, cells: Dict[str, CodeCell]
    ) -> str:
        """Enerji regülatörü"""
        if current < target:
            # Boost energy production
            for cell in cells.values():
                if hasattr(cell, "organelles") and "mitochondria" in cell.organelles:
                    # Increase ATP production
                    cell.energy_level = min(100, cell.energy_level + 10)
            return "energy_boosted"
        return "no_action"

    async def stress_regulator(
        current: float, target: float, cells: Dict[str, CodeCell]
    ) -> str:
        """Stres regülatörü"""
        if current > target:
            # Reduce stress
            for cell in cells.values():
                if hasattr(cell, "stress_level"):
                    cell.stress_level = max(0, cell.stress_level - 5)
            return "stress_reduced"
        return "no_action"

    return {
        "health": health_regulator,
        "energy": energy_regulator,
        "stress": stress_regulator,
    }
