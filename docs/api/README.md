# 🔧 API Reference

Complete API documentation for all BioCode components.

## 📚 API Documentation

### Core Components
- **[Core API](core.md)** - Essential biological components
  - `EnhancedCodeCell` - The basic unit of life
  - `AdvancedCodeTissue` - Multi-cell container
  - `CodeOrgan` - Module-level organization
  - `CodeSystem` - Complete organism

### Supporting Components
- **[Components API](components.md)** - Supporting systems
  - `ExtracellularMatrix` - Shared resources
  - `HomeostasisController` - Balance maintenance
  - `VascularizationSystem` - Resource distribution
  - System managers

### Utilities
- **[Utils API](utils.md)** - Helper functions
  - Logging configuration
  - Performance utilities
  - Common helpers

## 🎯 Quick Reference

### Creating a Cell
```python
from src.core.enhanced_codecell import EnhancedCodeCell

cell = EnhancedCodeCell(name="my_cell", cell_type="neuron")
```

### Building Tissue
```python
from src.core.advanced_codetissue import AdvancedCodeTissue

tissue = AdvancedCodeTissue("brain_tissue")
tissue.register_cell_type(NeuronCell)
tissue.grow_cell("neuron_1", "NeuronCell")
```

### Constructing an Organ
```python
from src.core.code_organ import CodeOrgan

organ = CodeOrgan("brain")
organ.add_tissue(tissue)
```

### Creating a System
```python
from src.core.code_system import CodeSystem

system = CodeSystem("human")
system.add_organ(organ)
```

## 📖 API Conventions

### Naming
- Classes: `PascalCase`
- Methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

### Async Methods
Methods that perform I/O or long operations are async:
```python
async def perform_operation(self, data):
    result = await self.process(data)
    return result
```

### Error Handling
All components follow biological error patterns:
```python
try:
    cell.divide()
except InsufficientEnergyError:
    cell.rest()
except CellDeathError:
    tissue.remove_cell(cell)
```

## 🔍 Finding APIs

1. **By Component Type**: Navigate to the appropriate section
2. **By Feature**: Use the search function
3. **By Example**: Check the [Examples](../examples/) section

## 📝 API Documentation Standards

Each API entry includes:
- **Description**: What it does
- **Parameters**: Input requirements
- **Returns**: Output specification
- **Raises**: Possible exceptions
- **Example**: Usage demonstration
- **Since**: Version introduced

---

Need more details? Dive into the specific API sections!