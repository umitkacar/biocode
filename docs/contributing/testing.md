# 🧪 Testing Guide

Comprehensive guide for writing and running tests in BioCode.

## 📋 Testing Philosophy

In BioCode, tests are like the **immune system** - they protect the organism from defects and ensure healthy operation.

### Testing Principles
1. **Test Biological Behavior** - Not just code functionality
2. **Isolation** - Each test is a controlled experiment
3. **Reproducibility** - Tests must be deterministic
4. **Coverage** - Comprehensive like a health checkup

## 🏗️ Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_codecell.py      # Cell unit tests
├── test_codetissue.py    # Tissue integration tests
├── test_codeorgan.py     # Organ system tests
├── test_codesystem.py    # Full organism tests
├── test_integration/     # Integration tests
├── test_performance/     # Performance benchmarks
└── test_security/        # Security tests
```

## ✍️ Writing Tests

### Basic Test Structure

```python
import pytest
from src.core.enhanced_codecell import EnhancedCodeCell, CellState

class TestEnhancedCodeCell:
    """Test suite for EnhancedCodeCell"""
    
    def test_cell_creation(self):
        """Test basic cell creation"""
        cell = EnhancedCodeCell("test_cell", cell_type="neuron")
        
        assert cell.name == "test_cell"
        assert cell.cell_type == "neuron"
        assert cell.state == CellState.DORMANT
        assert cell.health_score == 100
    
    def test_cell_infection(self):
        """Test cell infection mechanism"""
        cell = EnhancedCodeCell("test_cell")
        error = ValueError("Test infection")
        
        cell.infect(error)
        
        assert cell.state == CellState.INFECTED
        assert cell.health_score < 100
        assert cell.last_error == error
```

### Using Fixtures

```python
@pytest.fixture
def healthy_cell():
    """Fixture for a healthy cell"""
    cell = EnhancedCodeCell("fixture_cell")
    cell.state = CellState.HEALTHY
    return cell

@pytest.fixture
def tissue_with_cells():
    """Fixture for tissue with multiple cells"""
    tissue = AdvancedCodeTissue("test_tissue")
    tissue.register_cell_type(EnhancedCodeCell)
    
    for i in range(3):
        tissue.grow_cell(f"cell_{i}", "EnhancedCodeCell")
    
    return tissue

def test_cell_division(healthy_cell):
    """Test cell division using fixture"""
    daughter = healthy_cell.divide()
    
    assert daughter is not None
    assert daughter.name == "fixture_cell_d1"
    assert healthy_cell.energy_level == daughter.energy_level
```

### Testing Async Code

```python
@pytest.mark.asyncio
async def test_cell_operation():
    """Test async cell operation"""
    cell = EnhancedCodeCell("async_cell")
    
    result = await cell.perform_operation(
        "process_data",
        energy_cost=10
    )
    
    assert result == "Executed process_data"
    assert cell.energy_level == 90

@pytest.mark.asyncio
async def test_tissue_signaling():
    """Test inter-cell communication"""
    tissue = AdvancedCodeTissue("neural_tissue")
    tissue.register_cell_type(EnhancedCodeCell)
    
    sender = tissue.grow_cell("sender", "EnhancedCodeCell")
    receiver = tissue.grow_cell("receiver", "EnhancedCodeCell")
    
    signal = {"type": "activation", "strength": 0.8}
    await tissue.send_signal("sender", "receiver", signal)
    
    # Assert signal was processed
```

### Testing Exceptions

```python
def test_insufficient_energy():
    """Test operation with insufficient energy"""
    cell = EnhancedCodeCell("tired_cell")
    cell.energy_level = 5
    
    with pytest.raises(Exception, match="Insufficient energy"):
        asyncio.run(cell.perform_operation("heavy_task", energy_cost=50))

def test_cell_death():
    """Test cell death scenarios"""
    cell = EnhancedCodeCell("dying_cell")
    
    # Trigger multiple errors
    for i in range(15):
        cell.infect(Exception(f"Error {i}"))
    
    assert cell.state == CellState.DEAD
```

### Parametrized Tests

```python
@pytest.mark.parametrize("cell_type,expected_organelles", [
    ("neuron", ["mitochondria", "nucleus", "dendrites"]),
    ("muscle", ["mitochondria", "nucleus", "myofibrils"]),
    ("immune", ["mitochondria", "nucleus", "antibodies"]),
])
def test_cell_specialization(cell_type, expected_organelles):
    """Test different cell types have correct organelles"""
    cell = create_specialized_cell(cell_type)
    
    for organelle in expected_organelles:
        assert organelle in cell.organelles
```

## 🎯 Test Categories

### Unit Tests
Test individual components in isolation:
```python
# tests/test_codecell.py
def test_cell_metabolism():
    """Test cellular metabolism"""
    cell = EnhancedCodeCell("test_cell")
    initial_energy = cell.energy_level
    
    cell._metabolize()
    
    assert cell.energy_level != initial_energy
```

### Integration Tests
Test component interactions:
```python
# tests/test_integration/test_tissue_cell_interaction.py
def test_tissue_inflammation_response():
    """Test tissue-wide inflammation response"""
    tissue = create_infected_tissue()
    
    tissue._check_inflammation()
    
    assert tissue.inflammation_level > 0
    assert len(tissue.quarantine) > 0
```

### System Tests
Test complete organism behavior:
```python
# tests/test_integration/test_organism.py
async def test_organism_adaptation():
    """Test organism adapting to environment"""
    organism = create_test_organism()
    
    # Apply environmental pressure
    await organism.expose_to_environment("high_temperature")
    
    # Check adaptation
    assert organism.adaptations["heat_resistance"] > 0
```

### Performance Tests
```python
# tests/test_performance/test_cell_performance.py
@pytest.mark.slow
def test_tissue_scaling():
    """Test tissue performance with many cells"""
    tissue = AdvancedCodeTissue("performance_test")
    tissue.register_cell_type(EnhancedCodeCell)
    
    # Create many cells
    start_time = time.time()
    for i in range(1000):
        tissue.grow_cell(f"cell_{i}", "EnhancedCodeCell")
    
    duration = time.time() - start_time
    assert duration < 5.0  # Should complete within 5 seconds
```

## 🏃 Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_codecell.py

# Run specific test
pytest tests/test_codecell.py::test_cell_division

# Run with verbose output
pytest -v

# Run with print statements
pytest -s

# Stop on first failure
pytest -x
```

### Coverage Reports

```bash
# Run with coverage
pytest --cov=src

# Generate HTML report
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Markers

```bash
# Run only fast tests
pytest -m "not slow"

# Run only async tests
pytest -m asyncio

# Run integration tests
pytest -m integration
```

## 🔧 Test Configuration

### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    asyncio: marks tests as async
```

### conftest.py
```python
import pytest
import asyncio
from src.utils.logging_config import setup_logging

# Configure logging for tests
@pytest.fixture(autouse=True)
def setup_test_logging():
    setup_logging(log_level="WARNING")

# Event loop for async tests
@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

## 📊 Test Metrics

### Coverage Goals
- **Unit Tests**: >90% coverage
- **Integration Tests**: Key workflows covered
- **Edge Cases**: All error paths tested

### Performance Benchmarks
- Cell creation: <1ms
- Tissue operations: <10ms
- System responses: <100ms

## 🐛 Debugging Tests

### Using pytest debugger
```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start of test
pytest --trace
```

### Debug specific test
```python
def test_complex_scenario():
    """Test with debugging"""
    import pdb; pdb.set_trace()  # Breakpoint
    
    cell = EnhancedCodeCell("debug_cell")
    # Continue debugging...
```

### Logging in tests
```python
def test_with_logging(caplog):
    """Test with log capture"""
    with caplog.at_level(logging.DEBUG):
        cell = EnhancedCodeCell("logged_cell")
        cell.divide()
    
    assert "Cell division completed" in caplog.text
```

## ✅ Test Checklist

Before submitting PR, ensure:

- [ ] All tests pass locally
- [ ] New features have tests
- [ ] Edge cases are tested
- [ ] Async operations are tested
- [ ] Error conditions are tested
- [ ] Performance is acceptable
- [ ] Coverage hasn't decreased

## 💡 Best Practices

1. **Test One Thing**: Each test should verify one behavior
2. **Clear Names**: Test names should describe what they test
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Use Fixtures**: Share common setup code
5. **Mock External Dependencies**: Keep tests isolated
6. **Test Biological Behavior**: Not just code mechanics

## 🧬 Biological Testing Patterns

### Health Checks
```python
def test_cell_health_monitoring():
    """Regular health checkups"""
    cell = EnhancedCodeCell("patient")
    
    health_history = []
    for _ in range(10):
        cell.perform_operation("work")
        health_history.append(cell.health_score)
    
    # Health should decline with work
    assert health_history[-1] < health_history[0]
```

### Stress Testing
```python
def test_tissue_under_stress():
    """Test tissue stress response"""
    tissue = create_tissue()
    
    # Apply stress
    for cell in tissue.cells.values():
        cell.stress_level = 80
    
    tissue.check_health()
    
    # Tissue should activate stress response
    assert tissue.stress_response_active
```

### Evolution Testing
```python
def test_cell_adaptation():
    """Test cellular adaptation"""
    cell = EnhancedCodeCell("evolving_cell")
    
    # Expose to challenges
    for _ in range(100):
        try:
            cell.perform_challenging_task()
        except:
            cell.adapt()
    
    # Cell should have evolved
    assert len(cell.adaptations) > 0
```

---

Ready to write tests? Your tests are the immune system that keeps BioCode healthy! 🦠🛡️