import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from biocode.infrastructure.monitoring.prometheus import (
    MetricDefinition,
    MetricsCollector,
    MetricType,
)
from biocode.domain.entities.tissue import AdvancedCodeTissue
from biocode.domain.entities.cell import CellState


class OrganType(Enum):
    """Organ tipleri"""

    SENSORY = "sensory"  # Input/Output organs
    PROCESSING = "processing"  # Business logic organs
    STORAGE = "storage"  # Data storage organs
    REGULATORY = "regulatory"  # Control and monitoring
    DEFENSIVE = "defensive"  # Security organs


class CompatibilityType(Enum):
    """Organ uyumluluk tipleri (Blood Type analogy)"""

    TYPE_A = "A"  # Strict interface, limited compatibility
    TYPE_B = "B"  # Flexible interface, moderate compatibility
    TYPE_AB = "AB"  # Universal receiver
    TYPE_O = "O"  # Universal donor


@dataclass
class DataFlow:
    """Organ'lar arası veri akışı"""

    source_tissue: str
    target_tissue: str
    data_type: type
    flow_rate: float  # messages per second
    priority: int = 5
    backpressure_threshold: int = 1000


@dataclass
class OrganHealth:
    """Organ sağlık durumu"""

    overall_health: float = 100.0
    tissue_healths: Dict[str, float] = field(default_factory=dict)
    blood_flow: float = 100.0  # Data flow efficiency (percentage)
    oxygen_level: float = 98.0  # Resource availability (percentage)
    toxin_level: float = 0.0  # Error accumulation
    temperature: float = 37.0  # Load indicator
    inflammation: float = 0.0  # Stress/error response
    scar_tissue: float = 0.0  # Permanent damage accumulation


class DataFlowController:
    """Organ içi veri akışı kontrolü (Blood circulation analogy)"""

    def __init__(self, organ_name: str):
        self.organ_name = organ_name
        self.channels: Dict[str, asyncio.Queue] = {}
        self.flow_metrics: Dict[str, DataFlow] = {}
        self.backpressure_handlers: Dict[str, Callable] = {}
        self.flow_rate_limiters: Dict[str, asyncio.Semaphore] = {}

    def create_channel(self, channel_id: str, capacity: int = 1000):
        """Yeni data channel oluştur"""
        self.channels[channel_id] = asyncio.Queue(maxsize=capacity)
        self.flow_rate_limiters[channel_id] = asyncio.Semaphore(capacity)
        
        # Return a channel info object for testing
        class ChannelInfo:
            def __init__(self, queue):
                self.queue = queue
                self.capacity = queue.maxsize
                self.flow_rate = 1.0
            
            @property
            def current_load(self):
                return self.queue.qsize()
            
            @property
            def pressure(self):
                return self.current_load / self.capacity if self.capacity > 0 else 0
        
        channel_info = ChannelInfo(self.channels[channel_id])
        self.channels[channel_id].flow_rate = 1.0  # Add flow_rate attribute
        return channel_info

    async def send_data(self, channel_id: str, data: Any, priority: int = 5):
        """Kanala veri gönder"""
        if channel_id not in self.channels:
            raise ValueError(f"Unknown channel: {channel_id}")

        channel = self.channels[channel_id]

        # Check backpressure
        if channel.qsize() > channel.maxsize * 0.8:
            await self._handle_backpressure(channel_id)

        # Rate limiting
        async with self.flow_rate_limiters[channel_id]:
            await channel.put((priority, data))

    async def receive_data(
        self, channel_id: str, timeout: Optional[float] = None
    ) -> Any:
        """Kanaldan veri al"""
        if channel_id not in self.channels:
            raise ValueError(f"Unknown channel: {channel_id}")

        channel = self.channels[channel_id]

        try:
            if timeout:
                _, data = await asyncio.wait_for(channel.get(), timeout)
            else:
                _, data = await channel.get()
            return data
        except asyncio.TimeoutError:
            return None

    async def _handle_backpressure(self, channel_id: str):
        """Backpressure durumunu yönet"""
        if channel_id in self.backpressure_handlers:
            handler = self.backpressure_handlers[channel_id]
            await handler(channel_id, self.channels[channel_id].qsize())
        else:
            # Default: slow down
            await asyncio.sleep(0.1)

    def get_flow_statistics(self) -> Dict[str, Any]:
        """Data flow istatistikleri"""
        stats = {}
        for channel_id, channel in self.channels.items():
            stats[channel_id] = {
                "current_size": channel.qsize(),
                "max_size": channel.maxsize,
                "utilization": (
                    channel.qsize() / channel.maxsize if channel.maxsize > 0 else 0
                ),
            }
        return stats

    def set_flow_rate(self, channel_id: str, rate: float):
        """Set flow rate for a channel"""
        if channel_id in self.channels:
            self.channels[channel_id].flow_rate = rate


class BloodTypeCompatibility:
    """Organ compatibility checking (Blood type matching analogy)"""

    # Compatibility matrix
    COMPATIBILITY = {
        CompatibilityType.TYPE_A: [CompatibilityType.TYPE_A, CompatibilityType.TYPE_AB],
        CompatibilityType.TYPE_B: [CompatibilityType.TYPE_B, CompatibilityType.TYPE_AB],
        CompatibilityType.TYPE_AB: [CompatibilityType.TYPE_AB],
        CompatibilityType.TYPE_O: [
            CompatibilityType.TYPE_A,
            CompatibilityType.TYPE_B,
            CompatibilityType.TYPE_AB,
            CompatibilityType.TYPE_O,
        ],
    }

    @classmethod
    def can_connect(cls, donor: CompatibilityType, receiver: CompatibilityType) -> bool:
        """İki organ bağlanabilir mi?"""
        return receiver in cls.COMPATIBILITY.get(donor, [])

    @classmethod
    def compatibility_score(
        cls, organ1_type: CompatibilityType, organ2_type: CompatibilityType
    ) -> float:
        """Compatibility score hesapla (0-1)"""
        if cls.can_connect(organ1_type, organ2_type):
            if organ1_type == organ2_type:
                return 1.0  # Perfect match
            elif organ2_type == CompatibilityType.TYPE_AB:
                return 0.8  # Universal receiver
            elif organ1_type == CompatibilityType.TYPE_O:
                return 0.8  # Universal donor
            else:
                return 0.6  # Compatible but not ideal
        return 0.0  # Incompatible


class CodeOrgan:
    """Code Organ - Multiple tissues working together"""

    def __init__(
        self,
        organ_name: str,
        organ_type: OrganType = OrganType.PROCESSING,
        compatibility: CompatibilityType = CompatibilityType.TYPE_O,
    ):
        self.organ_name = organ_name
        self.name = organ_name  # Alias for compatibility with tests
        self.organ_type = organ_type
        self.compatibility_type = compatibility
        self.creation_time = datetime.now()

        # Tissues
        self.tissues: Dict[str, AdvancedCodeTissue] = {}
        self.tissue_roles: Dict[str, str] = {}  # tissue_name -> role

        # Data flow
        self.data_flow_controller = DataFlowController(organ_name)
        self.inter_tissue_connections: Dict[Tuple[str, str], DataFlow] = {}

        # Health monitoring
        self.health = OrganHealth()
        self.failure_predictors: List[Callable] = []
        self.last_health_check = datetime.now()

        # Metrics
        self.metrics_collector = MetricsCollector(f"organ_{organ_name}")
        self._register_metrics()

        # Transplant support
        self.is_transplantable = True
        self.transplant_history: List[Dict[str, Any]] = []
        
        # Failure tracking
        self.failure_patterns: List[str] = []

    def _register_metrics(self):
        """Organ metrikleri tanımla"""
        self.metrics_collector.register_metric(
            MetricDefinition(
                name="organ_health",
                type=MetricType.GAUGE,
                unit="score",
                description="Overall organ health",
                alert_thresholds={"critical": 30, "warning": 50},
            )
        )

        self.metrics_collector.register_metric(
            MetricDefinition(
                name="blood_flow",
                type=MetricType.GAUGE,
                unit="rate",
                description="Data flow efficiency",
                alert_thresholds={"low": 0.3},
            )
        )

        self.metrics_collector.register_metric(
            MetricDefinition(
                name="tissue_count",
                type=MetricType.GAUGE,
                unit="count",
                description="Number of active tissues",
            )
        )

    def add_tissue(self, tissue: AdvancedCodeTissue, role: str = "general"):
        """Organ'a tissue ekle"""
        if tissue.name in self.tissues:
            raise ValueError(f"Tissue '{tissue.name}' already exists in organ")
        
        self.tissues[tissue.name] = tissue
        self.tissue_roles[tissue.name] = role

        # Create data channels for the tissue
        self.data_flow_controller.create_channel(f"{tissue.name}_in")
        self.data_flow_controller.create_channel(f"{tissue.name}_out")

        # Update metrics
        self.metrics_collector.record("tissue_count", len(self.tissues))

    def is_compatible_with(self, other_type: CompatibilityType) -> bool:
        """Check if this organ can connect with another based on compatibility type"""
        return BloodTypeCompatibility.can_connect(self.compatibility_type, other_type)

    def remove_tissue(self, tissue_name: str) -> Optional[AdvancedCodeTissue]:
        """Remove tissue from organ"""
        if tissue_name not in self.tissues:
            return None
        
        tissue = self.tissues.pop(tissue_name)
        self.tissue_roles.pop(tissue_name, None)
        
        # Update metrics
        self.metrics_collector.record("tissue_count", len(self.tissues))
        
        return tissue

    def update_health(self):
        """Update organ health based on current conditions"""
        # Calculate health degradation based on toxins and inflammation
        health_penalty = (self.health.toxin_level * 0.5 + self.health.inflammation * 0.3)
        
        # Update blood flow
        self.health.blood_flow = max(20.0, 100.0 - health_penalty)
        
        # Update oxygen level
        self.health.oxygen_level = max(50.0, 98.0 - (health_penalty * 0.8))
        
        # Calculate overall health
        self.health.overall_health = (
            self.health.blood_flow * 0.4 +
            self.health.oxygen_level * 0.4 +
            (100 - self.health.toxin_level) * 0.1 +
            (100 - self.health.inflammation) * 0.1
        )
        
        # Update metrics
        self.metrics_collector.record("organ_health", self.health.overall_health)
        self.metrics_collector.record("blood_flow", self.health.blood_flow / 100.0)

    def predict_failure(self) -> float:
        """Predict organ failure risk (0-1)"""
        # Initialize failure patterns tracking
        self.failure_patterns = []
        
        # Check various health indicators
        risk_score = 0.0
        
        if self.health.blood_flow < 50.0:
            risk_score += 0.3
            self.failure_patterns.append("blood_flow")
        
        if self.health.oxygen_level < 70.0:
            risk_score += 0.2
            self.failure_patterns.append("oxygen")
        
        if self.health.toxin_level > 40.0:
            risk_score += 0.3
            self.failure_patterns.append("toxins")
        
        if self.health.inflammation > 30.0:
            risk_score += 0.2
            self.failure_patterns.append("inflammation")
        
        return min(1.0, risk_score)

    def prepare_for_transplant(self) -> Dict[str, Any]:
        """Prepare organ for transplantation"""
        # Pause all operations
        for tissue in self.tissues.values():
            # Set all cells to dormant
            for cell in tissue.cells.values():
                cell.state = CellState.DORMANT

        # Save state
        state = {
            "organ_name": self.organ_name,
            "organ_type": self.organ_type.value,
            "compatibility_type": self.compatibility_type.value,
            "health_status": {
                "overall": self.health.overall_health,
                "blood_flow": self.health.blood_flow,
                "oxygen_level": self.health.oxygen_level,
                "toxin_level": self.health.toxin_level,
                "inflammation": self.health.inflammation,
                "scar_tissue": self.health.scar_tissue,
            },
            "tissues": list(self.tissues.keys()),
            "tissue_count": len(self.tissues),
            "connections": [
                {"source": source, "target": target, "flow": flow.__dict__}
                for (source, target), flow in self.inter_tissue_connections.items()
            ],
            "creation_time": self.creation_time.isoformat(),
            "is_transplantable": self.is_transplantable,
        }

        self.transplant_history.append({
            "action": "prepared_for_transplant",
            "timestamp": datetime.now(),
            "state": state,
        })

        return {"success": True, "state": state}

    async def process_data(self, data: Any, tissue_name: Optional[str] = None) -> Any:
        """Process data through a specific tissue or auto-select"""
        if tissue_name:
            if tissue_name not in self.tissues:
                raise ValueError(f"Tissue '{tissue_name}' not found in organ")
            tissue = self.tissues[tissue_name]
            # Process through specific tissue
            return await tissue.execute_coordinated_operation(
                lambda cell: cell.perform_operation(data)
            )
        else:
            # Auto-select first available tissue
            if not self.tissues:
                raise ValueError("No tissues available in organ")
            first_tissue = next(iter(self.tissues.values()))
            return await first_tissue.execute_coordinated_operation(
                lambda cell: cell.perform_operation(data)
            )

    def connect_tissues(
        self, source: str, target: str, data_type: type = Any, flow_rate: float = 100.0
    ):
        """İki tissue arasında bağlantı kur"""
        if source not in self.tissues or target not in self.tissues:
            raise ValueError("Both tissues must exist in the organ")

        flow = DataFlow(
            source_tissue=source,
            target_tissue=target,
            data_type=data_type,
            flow_rate=flow_rate,
        )

        self.inter_tissue_connections[(source, target)] = flow

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Organ seviyesinde request işleme"""
        # Route to appropriate tissue based on request type
        request_type = request.get("type", "default")

        # Find tissue with matching role
        target_tissue = None
        for tissue_name, role in self.tissue_roles.items():
            if role == request_type or role == "general":
                target_tissue = tissue_name
                break

        if not target_tissue:
            return {"error": "No tissue available for request type"}

        # Send to tissue via data flow
        channel_in = f"{target_tissue}_in"
        channel_out = f"{target_tissue}_out"

        await self.data_flow_controller.send_data(channel_in, request)

        # Process in tissue
        tissue = self.tissues[target_tissue]
        # Simplified - normally tissue would process async
        result = await tissue.execute_coordinated_operation(
            lambda cell: cell.perform_operation(request.get("operation", "default"))
        )

        # Get response
        response = await self.data_flow_controller.receive_data(
            channel_out, timeout=5.0
        )

        return response or result

    def calculate_health(self) -> float:
        """Organ sağlığını hesapla"""
        if not self.tissues:
            return 100.0

        # Tissue health average
        tissue_healths = []
        for tissue in self.tissues.values():
            tissue_health = tissue.calculate_tissue_health()
            tissue_healths.append(tissue_health)
            self.health.tissue_healths[tissue.name] = tissue_health

        avg_tissue_health = sum(tissue_healths) / len(tissue_healths)

        # Data flow health
        flow_stats = self.data_flow_controller.get_flow_statistics()
        flow_utilizations = [stat["utilization"] for stat in flow_stats.values()]
        avg_flow = 1.0 - (
            sum(flow_utilizations) / len(flow_utilizations) if flow_utilizations else 0
        )
        self.health.blood_flow = avg_flow

        # Resource health (simplified)
        self.health.oxygen_level = max(0, 100 - (self.health.toxin_level * 2))

        # Overall health calculation
        overall = (
            avg_tissue_health * 0.6
            + self.health.blood_flow * 100 * 0.2
            + self.health.oxygen_level * 0.2
        )

        self.health.overall_health = overall
        self.metrics_collector.record("organ_health", overall)
        self.metrics_collector.record("blood_flow", self.health.blood_flow)

        return overall

    def hot_swap_tissue(
        self, old_tissue_name: str, new_tissue: AdvancedCodeTissue
    ) -> bool:
        """Hot-swap tissue replacement"""
        if old_tissue_name not in self.tissues:
            return False

        old_role = self.tissue_roles[old_tissue_name]

        # Gradually redirect traffic
        # 1. Add new tissue
        self.add_tissue(new_tissue, old_role)

        # 2. Copy connections
        for (source, target), flow in list(self.inter_tissue_connections.items()):
            if source == old_tissue_name:
                self.connect_tissues(
                    new_tissue.name, target, flow.data_type, flow.flow_rate
                )
            elif target == old_tissue_name:
                self.connect_tissues(
                    source, new_tissue.name, flow.data_type, flow.flow_rate
                )

        # 3. Wait for old tissue to drain
        # Simplified - in real implementation would wait for queue to empty

        # 4. Remove old tissue
        del self.tissues[old_tissue_name]
        del self.tissue_roles[old_tissue_name]

        # 5. Clean up old connections
        self.inter_tissue_connections = {
            k: v
            for k, v in self.inter_tissue_connections.items()
            if old_tissue_name not in k
        }

        return True

    def get_diagnostics(self) -> Dict[str, Any]:
        """Detailed organ diagnostics"""
        self.calculate_health()

        return {
            "organ_name": self.organ_name,
            "organ_type": self.organ_type.value,
            "compatibility": self.compatibility_type.value,
            "health": {
                "overall": self.health.overall_health,
                "blood_flow": self.health.blood_flow,
                "oxygen_level": self.health.oxygen_level,
                "toxin_level": self.health.toxin_level,
                "temperature": self.health.temperature,
            },
            "tissues": {
                name: {
                    "role": self.tissue_roles[name],
                    "health": self.health.tissue_healths.get(name, 0),
                    "cell_count": len(tissue.cells),
                }
                for name, tissue in self.tissues.items()
            },
            "data_flow": self.data_flow_controller.get_flow_statistics(),
            "failure_risk": self.predict_failure(),
            "uptime": (datetime.now() - self.creation_time).total_seconds(),
            "transplant_history": len(self.transplant_history),
        }
