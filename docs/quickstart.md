# BioCode Quick Start Guide

Welcome to BioCode! This guide will help you get started with the living code architecture in minutes.

## Installation

### From PyPI (Coming Soon)
```bash
pip install biocode
```

### From Source
```bash
git clone https://github.com/umitkacar/biocode.git
cd biocode
pip install -e .
```

## Your First Living Code

### 1. Create a Simple Cell

```python
from biocode.core import EnhancedCodeCell

# Create a cell
cell = EnhancedCodeCell("my_first_cell", cell_type="worker")

# Check its health
print(f"Cell health: {cell.health_score}")
print(f"Cell state: {cell.state.value}")

# Perform an operation
import asyncio
result = asyncio.run(cell.perform_operation("process_data"))
print(f"Operation result: {result}")
```

### 2. Build a Tissue

```python
from biocode.core import AdvancedCodeTissue, EnhancedCodeCell

# Create a tissue
tissue = AdvancedCodeTissue("data_processing_tissue")

# Register cell types
tissue.register_cell_type(EnhancedCodeCell)

# Grow cells
validator_cell = tissue.grow_cell("validator", "EnhancedCodeCell")
processor_cell = tissue.grow_cell("processor", "EnhancedCodeCell")

# Connect cells
tissue.connect_cells("validator", "processor")

# Send signals between cells
asyncio.run(tissue.send_signal("validator", "processor", {"data": "Hello!"}))
```

### 3. Create an Organ

```python
from biocode.core import CodeOrgan, OrganType, CompatibilityType

# Create an organ
organ = CodeOrgan(
    "api_handler",
    OrganType.SENSORY,  # Input/Output organ
    CompatibilityType.TYPE_O  # Universal donor
)

# Add tissues
organ.add_tissue(tissue)

# Process data with flow control
async def process_request(data):
    result = await organ.process_data(data)
    return result

result = asyncio.run(process_request({"request": "user_data"}))
```

### 4. Build a Complete System

```python
from biocode.core import CodeSystem

# Create a system
system = CodeSystem("my_app")

# Add organs
system.add_organ(organ)

# Boot the system
asyncio.run(system.boot())

# System is now alive and ready!
print(f"Consciousness level: {system.consciousness_level.value}")
```

## Key Concepts

### Cell States
- **HEALTHY**: Normal operation
- **STRESSED**: Under load
- **INFECTED**: Has errors
- **DEAD**: No longer functional

### Self-Healing
Cells automatically heal when damaged:
```python
# Cell gets infected
cell.infect(Exception("Error occurred"))
print(f"Health: {cell.health_score}")  # Reduced

# Cell heals itself
cell.heal()
print(f"Health: {cell.health_score}")  # Increased
```

### Transactions
Tissues support transactions:
```python
with tissue.transaction("critical_operation") as tx:
    # Perform operations
    tissue.grow_cell("temp_cell", "EnhancedCodeCell")
    # If error occurs, changes are rolled back
```

### Neural Learning
Systems learn from patterns:
```python
# System observes patterns
system.neural_ai.observe_pattern("user_behavior", {"action": "login"})

# System predicts next action
prediction = system.neural_ai.predict_next("user_behavior")
```

## Common Patterns

### Error Recovery
```python
# Cells handle errors gracefully
try:
    await cell.perform_operation("risky_operation")
except Exception as e:
    # Cell is now infected but not dead
    # It will try to heal itself
    pass
```

### Resource Management
```python
# Organs manage resources efficiently
organ.data_flow_controller.max_buffer_size = 1000
organ.data_flow_controller.backpressure_threshold = 0.8
```

### Health Monitoring
```python
# Get health reports
health = cell.get_health_report()
diagnostics = tissue.get_tissue_diagnostics()
```

## Next Steps

- Read the [Tutorial](tutorial.md) for a deeper dive
- Explore [Advanced Features](advanced-features.md)
- Check out [Examples](../examples/) directory
- Join our [Community](https://github.com/umitkacar/biocode/discussions)

## Need Help?

- 📖 [Full Documentation](../README.md)
- 🐛 [Report Issues](https://github.com/umitkacar/biocode/issues)
- 💬 [Discussions](https://github.com/umitkacar/biocode/discussions)
- 📧 Email: team@biocode.dev

Happy coding with living cells! 🧬