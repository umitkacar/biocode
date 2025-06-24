# BioCode Logging Guide

## Overview

BioCode uses a centralized, hierarchical logging system that follows biological metaphors. The logging system provides:

- **Consistent formatting** across all components
- **Biological context** (cell, tissue, organ, system levels)
- **Specialized loggers** for security and performance
- **Automatic log rotation** and retention
- **Colored console output** for development
- **Structured logging** support

## Quick Start

### Basic Usage

```python
from src.utils.logging_config import get_logger

# Get a logger for your module
logger = get_logger(__name__)

# Log messages at different levels
logger.debug("Detailed cellular operation")
logger.info("Tissue-level event occurred")
logger.warning("Organ experiencing stress")
logger.error("System failure detected")
logger.critical("Life-threatening event!")
```

### With Biological Context

```python
# Get a logger with biological context
logger = get_logger(__name__, 
                   cell_id="liver_cell_42",
                   tissue_name="hepatic_tissue",
                   organ_name="liver")

logger.info("Cell performing detoxification")
# Output includes: [Cell:liver_cell_42 > Tissue:hepatic_tissue > Organ:liver]
```

## Configuration

### Setup Logging

```python
from src.utils.logging_config import setup_logging

# Configure logging for your environment
setup_logging(
    log_level="INFO",              # Minimum log level
    log_dir="logs/production",     # Directory for log files
    enable_file_logging=True,      # Write to files
    enable_console_logging=True,   # Write to console
    max_file_size=50*1024*1024,   # 50MB per file
    backup_count=10               # Keep 10 backup files
)
```

### Environment-Specific Configuration

The `config/logging.yaml` file defines settings for different environments:

```yaml
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
    directory: logs/prod
```

## Biological Log Levels

BioCode maps traditional log levels to biological concepts:

| Traditional | Biological | Usage |
|------------|------------|-------|
| DEBUG | CELLULAR | Detailed cell operations, state changes |
| INFO | TISSUE | Tissue events, cell interactions |
| WARNING | ORGAN | Performance degradation, resource stress |
| ERROR | SYSTEM | Failed operations, critical errors |
| CRITICAL | CRITICAL | System-wide failures, security breaches |

## Component Integration

### Using LoggingMixin

For BioCode components, use the `LoggingMixin` class:

```python
from src.utils.logging_config import LoggingMixin

class MyBioComponent(LoggingMixin):
    def __init__(self, name):
        self.name = name
        super().__init__()  # Sets up self.logger automatically
        
    def process(self):
        self.logger.info(f"Processing in {self.name}")
```

### Manual Integration

For existing classes:

```python
from src.utils.logging_config import get_logger, log_cell_event

class EnhancedCodeCell:
    def __init__(self, name):
        self.name = name
        self.logger = get_logger(__name__, cell_id=name)
        
    def divide(self):
        # ... division logic ...
        log_cell_event(self.logger, "Cell division", self.name,
                      daughter_count=2, energy_cost=50)
```

## Specialized Logging

### Security Events

```python
from src.utils.logging_config import log_security_event

# Log security-related events
log_security_event(
    severity="warning",  # or "error", "critical"
    event="Unauthorized access attempt",
    details={
        "source": "external_cell",
        "target": "nucleus",
        "action": "dna_modification",
        "result": "blocked"
    }
)
```

### Performance Metrics

```python
from src.utils.logging_config import BioCodeLogger

# Get performance logger
perf_logger = BioCodeLogger.get_performance_logger()

# Log metrics
perf_logger.info("Performance metric", extra={
    "metric": "cell_division_rate",
    "value": 125.5,
    "unit": "divisions/second"
})
```

### Biological Event Helpers

```python
from src.utils.logging_config import log_cell_event, log_tissue_event, log_system_event

# Cell-level events
log_cell_event(logger, "Mitosis initiated", cell_id, 
              parent_health=95, energy_available=80)

# Tissue-level events
log_tissue_event(logger, "Inflammation detected", tissue_name,
                infected_cells=15, response="immune_activation")

# System-level events
log_system_event(logger, "Consciousness level changed",
                from_level="aware", to_level="focused")
```

## Log Files

BioCode creates several log files:

- **`biocode.log`** - All application logs
- **`biocode_errors.log`** - ERROR and CRITICAL logs only
- **`biocode_security.log`** - Security-specific events
- **`biocode_performance.log`** - Performance metrics (if configured)

## Best Practices

1. **Use appropriate log levels**
   ```python
   # Good
   logger.debug(f"Cell {cell_id} energy: {energy}")
   logger.error(f"Failed to connect cells: {error}", exc_info=True)
   
   # Bad
   logger.info(f"DEBUG: Cell energy is {energy}")  # Wrong level
   logger.error(f"Cell created")  # Too high level
   ```

2. **Include biological context**
   ```python
   # Good
   logger = get_logger(__name__, cell_id=self.name, tissue_name=self.tissue)
   
   # Less informative
   logger = get_logger(__name__)
   ```

3. **Log exceptions properly**
   ```python
   try:
       cell.perform_operation()
   except Exception as e:
       logger.error(f"Operation failed for {cell.name}", exc_info=True)
   ```

4. **Use structured data**
   ```python
   # Good - structured
   logger.info("Cell state changed", extra={
       "cell_id": cell.name,
       "old_state": old_state.value,
       "new_state": new_state.value,
       "trigger": trigger_event
   })
   
   # Less useful - unstructured
   logger.info(f"Cell {cell.name} changed from {old_state} to {new_state}")
   ```

5. **Avoid logging sensitive data**
   ```python
   # Bad
   logger.debug(f"Cell DNA: {cell.dna_sequence}")
   
   # Good
   logger.debug(f"Cell DNA hash: {hashlib.sha256(cell.dna_sequence).hexdigest()[:8]}")
   ```

## Example Integration

Here's a complete example showing logging in a BioCode component:

```python
import asyncio
from src.utils.logging_config import LoggingMixin, log_cell_event

class IntelligentCell(LoggingMixin):
    def __init__(self, name, tissue):
        self.name = name
        self.tissue = tissue
        self.health = 100
        super().__init__()  # Sets up logging
        
        self.logger.info(f"Cell {name} initialized in {tissue}")
        
    async def process_nutrients(self, amount):
        self.logger.debug(f"Processing {amount} nutrients")
        
        try:
            # Simulate processing
            await asyncio.sleep(0.1)
            self.health = min(100, self.health + amount * 0.1)
            
            log_cell_event(self.logger, "Nutrients processed", self.name,
                         amount=amount, health=self.health)
                         
        except Exception as e:
            self.logger.error(f"Failed to process nutrients", exc_info=True)
            raise
            
    def check_health(self):
        if self.health < 30:
            self.logger.warning(f"Cell health critical: {self.health}%")
        elif self.health < 60:
            self.logger.info(f"Cell health low: {self.health}%")
            
        return self.health
```

## Troubleshooting

### No logs appearing

1. Check logging is initialized:
   ```python
   from src.utils.logging_config import setup_logging
   setup_logging()  # Call this early in your application
   ```

2. Verify log level:
   ```python
   import logging
   logging.getLogger().setLevel(logging.DEBUG)
   ```

### Log files not created

1. Check directory permissions
2. Ensure `enable_file_logging=True` in setup
3. Verify log directory path exists

### Performance impact

1. Use appropriate log levels (avoid DEBUG in production)
2. Consider async logging for high-throughput scenarios
3. Implement log sampling for very frequent events

## Advanced Features

### Custom Formatters

```python
from src.utils.logging_config import BioCodeFormatter
import logging

# Create custom formatter
formatter = BioCodeFormatter(use_colors=False)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
```

### Log Filtering

```python
import logging

class HealthyOnlyFilter(logging.Filter):
    def filter(self, record):
        # Only log healthy cell events
        return getattr(record, 'cell_state', '') == 'healthy'

logger.addFilter(HealthyOnlyFilter())
```

### Integration with Monitoring

```python
# Send critical logs to monitoring system
import logging

class MonitoringHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            # Send to monitoring service
            monitoring.send_alert(record.getMessage())
```