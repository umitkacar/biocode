# Components API Reference

Supporting components that enable tissue and organ functionality.

## ExtracellularMatrix (ECM)

Shared environment and resources for cells within a tissue.

### Class Definition

```python
@dataclass
class MatrixHealth:
    integrity: float = 100.0      # Structural integrity
    viscosity: float = 1.0        # Communication medium thickness  
    permeability: float = 1.0     # Nutrient flow rate
    toxin_level: float = 0.0      # Accumulated toxins
    inflammation: float = 0.0     # Inflammation markers

class ExtracellularMatrix:
    """The connective tissue between cells"""
```

### Key Methods

#### deposit_resource
```python
def deposit_resource(self, resource_type: ResourceType, resource: SharedResource)
```
Add shared resource to the matrix.

#### retrieve_resource
```python
def retrieve_resource(self, resource_type: ResourceType, name: str) -> Optional[SharedResource]
```
Get resource from the matrix.

#### create_barrier
```python
def create_barrier(self, barrier_name: str, cell_filter: Callable[[CodeCell], bool])
```
Create security barrier with filter function.

### Example Usage

```python
# Create ECM for tissue
ecm = ExtracellularMatrix()

# Add shared configuration
config = SharedResource(
    name="db_config",
    data={"host": "localhost", "port": 5432},
    access_level="tissue"
)
ecm.deposit_resource(ResourceType.CONFIG, config)

# Create security barrier
ecm.create_barrier(
    "auth_only",
    lambda cell: hasattr(cell, 'authenticated') and cell.authenticated
)
```

## HomeostasisController

Maintains balance and stability within a tissue.

### Class Definition

```python
class HomeostasisController:
    """Maintains tissue balance and stability"""
    
    def __init__(self, tissue_name: str):
        self.tissue_name = tissue_name
        self.parameters: Dict[str, HomeostasisParameter] = {}
        self.feedback_loops: List[FeedbackLoop] = []
```

### Key Features

#### Parameter Management
```python
def register_parameter(self, name: str, target: float, min_val: float, max_val: float)
```
Register a parameter to monitor and control.

#### Feedback Loops
```python
def add_feedback_loop(self, 
    parameter: str,
    sensor: Callable[[], float],
    actuator: Callable[[float], None],
    gain: float = 1.0
)
```
Add control loop for parameter regulation.

### Example

```python
# Create homeostasis controller
homeostasis = HomeostasisController("liver_tissue")

# Register parameters
homeostasis.register_parameter("glucose", target=90, min_val=70, max_val=110)
homeostasis.register_parameter("toxins", target=0, min_val=0, max_val=50)

# Add feedback loop
homeostasis.add_feedback_loop(
    parameter="glucose",
    sensor=lambda: tissue.get_glucose_level(),
    actuator=lambda val: tissue.adjust_glucose(val),
    gain=0.8
)

# Run regulation
await homeostasis.regulate()
```

## VascularizationSystem

Resource distribution network within tissues.

### Class Definition

```python
class BloodVessel:
    """A channel for resource flow"""
    
    def __init__(self, vessel_id: str, capacity: float):
        self.id = vessel_id
        self.capacity = capacity
        self.flow_rate = 0.0
        self.pressure = 1.0
        self.oxygen_level = 100.0

class VascularizationSystem:
    """Blood vessel network for resource distribution"""
```

### Key Methods

#### create_vessel
```python
def create_vessel(self, vessel_id: str, capacity: float = 100.0) -> BloodVessel
```
Create new blood vessel.

#### connect_vessels
```python
def connect_vessels(self, vessel1_id: str, vessel2_id: str, flow_rate: float = 1.0)
```
Connect two vessels with specified flow rate.

#### distribute_resources
```python
async def distribute_resources(self, resources: Dict[str, float])
```
Distribute resources through the network.

### Example

```python
# Create vascular system
vascular = VascularizationSystem()

# Create vessels
artery = vascular.create_vessel("main_artery", capacity=1000)
vein1 = vascular.create_vessel("vein_1", capacity=500)
vein2 = vascular.create_vessel("vein_2", capacity=500)

# Connect vessels
vascular.connect_vessels("main_artery", "vein_1", flow_rate=2.0)
vascular.connect_vessels("main_artery", "vein_2", flow_rate=2.0)

# Distribute nutrients
await vascular.distribute_resources({
    "oxygen": 100,
    "glucose": 50,
    "proteins": 30
})
```

## ResourceType Enum

Types of resources that can be shared in the ECM.

```python
class ResourceType(Enum):
    CONFIG = "config"           # Configuration data
    CONNECTION = "connection"   # Database connections
    CACHE = "cache"            # Cached data
    SECURITY = "security"      # Security tokens/keys
    NUTRIENT = "nutrient"      # Data nutrients
```

## SharedResource

Resource that can be shared between cells.

```python
@dataclass
class SharedResource:
    name: str                          # Resource identifier
    resource_type: ResourceType        # Type of resource
    data: Any                         # Resource data
    created_at: datetime              # Creation time
    access_level: str = "public"      # Access control
    expiry: Optional[datetime] = None # Expiration time
```

## System Managers

### SystemBootManager

Manages system initialization sequence.

```python
class SystemBootManager:
    """Manages system boot sequence"""
    
    async def boot(self) -> bool:
        """Execute boot sequence"""
        for stage in self.boot_stages:
            success = await stage()
            if not success:
                await self.handle_boot_failure(stage)
                return False
        return True
```

### MaintenanceManager

Handles system maintenance tasks.

```python
class MaintenanceManager:
    """Manages system maintenance and cleanup"""
    
    def schedule_maintenance(self, task: Callable, interval: timedelta):
        """Schedule recurring maintenance task"""
        
    async def emergency_maintenance(self):
        """Perform emergency maintenance"""
```

### SystemMemoryManager

Manages system-wide memory and caching.

```python
class SystemMemoryManager:
    """Manages system memory and garbage collection"""
    
    def allocate_memory(self, size: int, purpose: str) -> MemoryBlock:
        """Allocate memory block"""
        
    def release_memory(self, block: MemoryBlock):
        """Release memory block"""
        
    async def garbage_collect(self):
        """Run garbage collection"""
```

## Tissue Components

### Transaction Support

```python
@dataclass
class TissueTransaction:
    id: str
    state: TransactionState
    affected_cells: Set[str]
    start_time: datetime
    changes: List[Tuple[str, Any, Any]]  # (cell_id, old_value, new_value)
```

### Metrics

```python
@dataclass
class TissueMetrics:
    request_count: int = 0
    error_count: int = 0
    total_latency: float = 0.0
    active_cells: int = 0
    infected_cells: int = 0
    last_update: datetime = field(default_factory=datetime.now)
```

## Usage Patterns

### Creating a Complete Tissue Environment

```python
# Create tissue with full support system
tissue = AdvancedCodeTissue("liver_tissue")

# Add ECM for shared resources
tissue.ecm = ExtracellularMatrix()

# Add homeostasis
tissue.homeostasis = HomeostasisController("liver_tissue")

# Add vascularization  
tissue.vascular = VascularizationSystem()

# Configure shared resources
db_config = SharedResource(
    name="database",
    resource_type=ResourceType.CONNECTION,
    data=database_connection,
    access_level="protected"
)
tissue.ecm.deposit_resource(ResourceType.CONNECTION, db_config)

# Set homeostasis parameters
tissue.homeostasis.register_parameter(
    "cell_count", 
    target=100, 
    min_val=50, 
    max_val=200
)

# Create vascular network
tissue.vascular.create_vessel("main", capacity=1000)
for i in range(10):
    vessel = tissue.vascular.create_vessel(f"branch_{i}", capacity=100)
    tissue.vascular.connect_vessels("main", f"branch_{i}")
```

### Error Handling

All components follow biological error patterns:

```python
try:
    resource = ecm.retrieve_resource(ResourceType.CONFIG, "missing")
except ResourceNotFoundError:
    # Resource doesn't exist in ECM
    ecm.deposit_resource(ResourceType.CONFIG, default_config)
    
try:
    await vascular.distribute_resources({"toxin": 1000})
except VascularOverloadError:
    # Too much pressure, vessels might burst
    await vascular.reduce_pressure()
```

---

Next: [Utilities API](utils.md) for helper functions and tools.