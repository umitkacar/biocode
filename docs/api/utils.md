# Utilities API Reference

Helper functions and utilities for BioCode development.

## Logging Configuration

### BioCodeLogger

Central logging configuration and management.

#### setup_logging

```python
def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[str] = None,
    enable_file_logging: bool = True,
    enable_console_logging: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None
```

Configure global logging settings.

**Parameters:**
- `log_level`: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_dir`: Directory for log files (default: "logs/")
- `enable_file_logging`: Write logs to files
- `enable_console_logging`: Write logs to console
- `max_file_size`: Maximum size before rotation
- `backup_count`: Number of backup files to keep

**Example:**
```python
from src.utils.logging_config import setup_logging

# Development setup
setup_logging(
    log_level="DEBUG",
    log_dir="logs/dev",
    enable_console_logging=True
)

# Production setup
setup_logging(
    log_level="INFO",
    log_dir="/var/log/biocode",
    enable_console_logging=False,
    max_file_size=50 * 1024 * 1024  # 50MB
)
```

#### get_logger

```python
def get_logger(
    name: str,
    cell_id: Optional[str] = None,
    tissue_name: Optional[str] = None,
    organ_name: Optional[str] = None
) -> logging.Logger
```

Get a logger with biological context.

**Parameters:**
- `name`: Logger name (usually `__name__`)
- `cell_id`: Optional cell identifier
- `tissue_name`: Optional tissue name  
- `organ_name`: Optional organ name

**Returns:** Configured logger with context

**Example:**
```python
from src.utils.logging_config import get_logger

# Simple logger
logger = get_logger(__name__)

# Logger with context
logger = get_logger(__name__, 
                   cell_id="neuron_42",
                   tissue_name="brain_cortex",
                   organ_name="brain")

logger.info("Processing signal")
# Output: 2024-06-24 10:30:45.123 | INFO | module [Cell:neuron_42 > Tissue:brain_cortex > Organ:brain] | Processing signal
```

### LoggingMixin

Mixin class for automatic logging setup.

```python
class LoggingMixin:
    """Mixin to add logging capabilities to BioCode components"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_logging()
```

**Usage:**
```python
from src.utils.logging_config import LoggingMixin

class MyCell(LoggingMixin, EnhancedCodeCell):
    def __init__(self, name):
        super().__init__(name)
        # self.logger is automatically available
        
    def process(self):
        self.logger.info("Processing started")
```

### Specialized Loggers

#### get_performance_logger

```python
def get_performance_logger() -> logging.Logger
```

Get logger for performance metrics.

**Example:**
```python
from src.utils.logging_config import BioCodeLogger

perf_logger = BioCodeLogger.get_performance_logger()
perf_logger.info("Operation completed", extra={
    "duration_ms": 45.2,
    "memory_mb": 128.5,
    "cpu_percent": 23.1
})
```

#### get_security_logger

```python
def get_security_logger() -> logging.Logger
```

Get logger for security events.

**Example:**
```python
security_logger = BioCodeLogger.get_security_logger()
security_logger.warning("Unauthorized access attempt", extra={
    "source_ip": "192.168.1.100",
    "target": "admin_panel",
    "action": "login",
    "result": "blocked"
})
```

### Biological Event Helpers

#### log_cell_event

```python
def log_cell_event(
    logger: logging.Logger,
    event: str,
    cell_id: str,
    **kwargs: Any
) -> None
```

Log cell-level events with context.

**Example:**
```python
log_cell_event(
    logger, 
    "Division completed",
    "stem_cell_1",
    daughter_cells=2,
    energy_cost=50,
    duration_ms=120
)
```

#### log_tissue_event

```python
def log_tissue_event(
    logger: logging.Logger,
    event: str,
    tissue_name: str,
    **kwargs: Any
) -> None
```

Log tissue-level events.

**Example:**
```python
log_tissue_event(
    logger,
    "Inflammation detected",
    "muscle_tissue",
    infected_cells=15,
    severity="moderate",
    response="quarantine"
)
```

#### log_system_event

```python
def log_system_event(
    logger: logging.Logger,
    event: str,
    **kwargs: Any
) -> None
```

Log system-level events.

**Example:**
```python
log_system_event(
    logger,
    "Consciousness level changed",
    from_level="aware",
    to_level="focused",
    trigger="high_load"
)
```

#### log_security_event

```python
def log_security_event(
    severity: str,
    event: str,
    details: Dict[str, Any],
    **kwargs: Any
) -> None
```

Log security-related events.

**Example:**
```python
log_security_event(
    "critical",
    "Data breach detected",
    {
        "affected_cells": ["db_cell_1", "db_cell_2"],
        "data_type": "user_credentials",
        "action_taken": "emergency_shutdown"
    },
    source="intrusion_detection"
)
```

## Custom Formatters

### BioCodeFormatter

Custom log formatter with biological context.

```python
class BioCodeFormatter(logging.Formatter):
    """Custom formatter with biological context and colors"""
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors and sys.stdout.isatty()
```

**Features:**
- Biological context in log messages
- Colored output for terminals
- Structured format for parsing
- Exception formatting

**Example:**
```python
import logging
from src.utils.logging_config import BioCodeFormatter

# Create custom handler
handler = logging.StreamHandler()
handler.setFormatter(BioCodeFormatter(use_colors=True))

# Add to logger
logger = logging.getLogger("custom")
logger.addHandler(handler)
```

## Biological Log Levels

### BiologicalLogLevel

Enum mapping traditional levels to biological concepts.

```python
class BiologicalLogLevel(Enum):
    CELLULAR = logging.DEBUG      # Detailed cellular operations
    TISSUE = logging.INFO        # Tissue-level events
    ORGAN = logging.WARNING      # Organ-level warnings
    SYSTEM = logging.ERROR       # System-level errors
    CRITICAL = logging.CRITICAL  # Life-threatening events
```

**Usage:**
```python
from src.utils.logging_config import BiologicalLogLevel

# Set biological log level
logger.setLevel(BiologicalLogLevel.TISSUE.value)

# Log at biological levels
logger.log(BiologicalLogLevel.CELLULAR.value, "Mitochondria producing ATP")
logger.log(BiologicalLogLevel.ORGAN.value, "Liver showing signs of stress")
```

## Configuration File Support

### Loading from YAML

```python
# config/logging.yaml
development:
  level: DEBUG
  console:
    enabled: true
    colorize: true
  file:
    enabled: true
    directory: logs/dev

production:
  level: INFO
  console:
    enabled: false
  file:
    enabled: true
    directory: /var/log/biocode
```

**Usage:**
```python
import yaml
from src.utils.logging_config import setup_logging

# Load configuration
with open("config/logging.yaml") as f:
    config = yaml.safe_load(f)
    
# Apply environment-specific config
env = os.getenv("BIOCODE_ENV", "development")
env_config = config[env]

setup_logging(
    log_level=env_config["level"],
    enable_console_logging=env_config["console"]["enabled"],
    log_dir=env_config["file"]["directory"]
)
```

## Best Practices

### 1. Use Appropriate Context

```python
# Good - includes biological context
logger = get_logger(__name__, cell_id=self.name, tissue_name=self.tissue)

# Less useful - no context
logger = get_logger(__name__)
```

### 2. Structured Logging

```python
# Good - structured data
logger.info("Cell operation completed", extra={
    "operation": "divide",
    "duration_ms": 120,
    "energy_cost": 50,
    "daughter_cells": ["cell_1_d1", "cell_1_d2"]
})

# Less useful - unstructured
logger.info(f"Cell divided in 120ms creating 2 daughters")
```

### 3. Use Biological Events

```python
# Good - uses helper
log_cell_event(logger, "Apoptosis initiated", cell.name,
              trigger="age", cell_age_hours=72)

# Less consistent - manual logging
logger.info(f"Cell {cell.name} dying of old age")
```

### 4. Handle Sensitive Data

```python
# Good - hash sensitive data
logger.info("User authenticated", extra={
    "user_id_hash": hashlib.sha256(user_id.encode()).hexdigest()[:8]
})

# Bad - logs sensitive data
logger.info(f"User {user_id} logged in with password {password}")
```

## Performance Considerations

### Log Level Impact

```python
# In production, avoid DEBUG level
if environment == "production":
    setup_logging(log_level="INFO")  # Skip DEBUG logs
    
# Use guards for expensive operations
if logger.isEnabledFor(logging.DEBUG):
    expensive_debug_info = calculate_detailed_metrics()
    logger.debug("Metrics: %s", expensive_debug_info)
```

### Async Logging

For high-throughput systems:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncLogger:
    def __init__(self, logger):
        self.logger = logger
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def log_async(self, level, msg, **kwargs):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self.logger.log,
            level, msg, kwargs
        )
```

---

This completes the utilities API documentation. The logging system is designed to integrate naturally with BioCode's biological architecture while providing powerful debugging and monitoring capabilities.