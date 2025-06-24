# Core API Reference

## EnhancedCodeCell

The fundamental unit of the BioCode system - a living, breathing code cell.

### Class Definition

```python
class EnhancedCodeCell(LoggingMixin):
    """Enhanced code cell with full biological features"""
```

### Constructor

```python
def __init__(self, name: str, cell_type: str = "generic")
```

**Parameters:**
- `name` (str): Unique identifier for the cell
- `cell_type` (str): Type of cell (default: "generic")

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | str | Cell identifier |
| `cell_type` | str | Cell specialization |
| `state` | CellState | Current cell state |
| `health_score` | int | Health (0-100) |
| `energy_level` | float | Available energy |
| `stress_level` | float | Stress indicator |
| `dna` | str | Unique genetic code |
| `mutations` | List[str] | Genetic mutations |
| `organelles` | Dict[str, Organelle] | Internal components |

### Methods

#### perform_operation
```python
async def perform_operation(self, operation_name: str, *args, **kwargs) -> Any
```
Execute a cell operation with energy consumption.

**Parameters:**
- `operation_name` (str): Name of operation
- `*args`: Positional arguments
- `**kwargs`: Keyword arguments (including `energy_cost`)

**Returns:** Operation result

**Raises:** `Exception` if insufficient energy

#### divide
```python
def divide(self) -> Optional["EnhancedCodeCell"]
```
Cell division (mitosis) creating a daughter cell.

**Returns:** New cell or None if division fails

**Example:**
```python
daughter = parent_cell.divide()
if daughter:
    print(f"Created {daughter.name}")
```

#### infect
```python
def infect(self, error: Exception)
```
Infect the cell with an error.

**Parameters:**
- `error` (Exception): The error/infection

#### heal
```python
def heal(self)
```
Initiate healing process.

#### trigger_apoptosis
```python
def trigger_apoptosis(self)
```
Programmed cell death.

---

## AdvancedCodeTissue

Container for multiple cells working together.

### Class Definition

```python
class AdvancedCodeTissue:
    """Advanced tissue structure with cell management"""
```

### Constructor

```python
def __init__(self, tissue_name: str)
```

### Key Methods

#### register_cell_type
```python
def register_cell_type(self, cell_type: Type[CodeCell])
```
Register a new cell type for this tissue.

#### grow_cell
```python
def grow_cell(self, cell_name: str, cell_type: str, **kwargs) -> CodeCell
```
Create a new cell in the tissue.

**Example:**
```python
tissue = AdvancedCodeTissue("liver")
tissue.register_cell_type(HepaticCell)
cell = tissue.grow_cell("hepatic_1", "HepaticCell")
```

#### connect_cells
```python
def connect_cells(self, cell1: str, cell2: str)
```
Establish connection between cells.

#### send_signal
```python
async def send_signal(self, from_cell: str, to_cell: str, signal: Dict[str, Any])
```
Send signal between cells.

#### transaction
```python
@contextmanager
def transaction(self, transaction_id: str)
```
Atomic operation context.

**Example:**
```python
with tissue.transaction("critical_op") as tx:
    # Perform atomic operations
    pass
```

---

## CodeOrgan

Higher-level organization of tissues.

### Class Definition

```python
class CodeOrgan:
    """Organ composed of multiple tissues with specialized functions"""
```

### Constructor

```python
def __init__(self, name: str, compatibility_type: CompatibilityType = CompatibilityType.O)
```

### Key Features

- **Blood Type Compatibility**: Organ transplant compatibility
- **Data Flow Control**: Backpressure and flow management
- **Health Monitoring**: Comprehensive health metrics
- **Hot Swapping**: Runtime tissue replacement

### Methods

#### add_tissue
```python
def add_tissue(self, tissue: AdvancedCodeTissue, role: str = "general")
```
Add tissue to organ.

#### process_data
```python
async def process_data(self, data: Any, source_tissue: str) -> Any
```
Process data through organ tissues.

---

## CodeSystem

Complete organism with multiple organs.

### Class Definition

```python
class CodeSystem:
    """Complete biological system with consciousness"""
```

### Consciousness Levels

```python
class ConsciousnessLevel(Enum):
    DORMANT = 0      # System sleeping
    AWAKENING = 1    # Boot sequence
    AWARE = 2        # Basic operations
    FOCUSED = 3      # Optimized state
    HYPERAWARE = 4   # Peak performance
    DREAMING = 5     # Deep optimization
```

### Key Components

- **SystemAI**: Neural pathway learning
- **SystemMemory**: Multi-tier memory system
- **CircadianScheduler**: Activity scheduling
- **ConsciousnessManager**: State management

### Methods

#### add_organ
```python
def add_organ(self, organ: CodeOrgan)
```
Add organ to system.

#### evolve
```python
def evolve(self, selection_pressure: str = "efficiency")
```
Trigger system evolution.

#### dream
```python
async def dream(self, duration: float = 10.0)
```
Enter dream state for optimization.

**Example:**
```python
system = CodeSystem("my_organism")
system.add_organ(brain)
system.add_organ(liver)

# Let it evolve
system.evolve("performance")

# Dream for optimization
await system.dream(30.0)
```

---

## Cell States

```python
class CellState(Enum):
    DORMANT = "dormant"      # Sleeping
    HEALTHY = "healthy"      # Normal
    STRESSED = "stressed"    # Under pressure
    INFECTED = "infected"    # Has errors
    INFLAMED = "inflamed"    # Severe stress
    HEALING = "healing"      # Recovering
    APOPTOTIC = "apoptotic"  # Dying
    DEAD = "dead"           # Terminated
```

## Exceptions

### BiologicalError
Base exception for all biological errors.

### InsufficientEnergyError
Raised when cell lacks energy for operation.

### CellDeathError
Raised when operation attempted on dead cell.

### TissueInflammationError
Raised when tissue is too inflamed.

### OrganFailureError
Raised when organ fails critically.