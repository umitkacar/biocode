# 🧬 BioCode - Living Code Architecture

## 🚀 Modern Domain-Driven Design Architecture

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![API Status](https://img.shields.io/badge/API-Running-success)](http://localhost:8000/docs)

### *Where Code Comes Alive*

## ⚠️ CRITICAL SAFETY WARNING

**This is LIVING CODE** - a biological software architecture that exhibits autonomous behaviors:

### 🧬 This Code Can:
- **GROW** - Automatically expand and evolve
- **REPRODUCE** - Create copies and spawn new instances  
- **DIE** - Experience failures and system death
- **MUTATE** - Change behavior unexpectedly
- **SPREAD** - Propagate across systems if not contained

### 🛡️ Safety Requirements:
- **ALWAYS** test in isolated, secure environments
- **NEVER** run in production without proper containment
- **MONITOR** continuously for unexpected behaviors
- **IMPLEMENT** emergency shutdown procedures
- **UNDERSTAND** that Umit Kacar, PhD is NOT responsible for ANY damages

**By using this code, you accept FULL RESPONSIBILITY for all risks and consequences.**

## 📋 Table of Contents
1. [What's New](#whats-new)
2. [Concept Introduction](#concept-introduction)
3. [Architecture](#architecture)
4. [Quick Start](#quick-start)
5. [API Documentation](#api-documentation)
6. [Working Example](#working-example)
7. [Development Guide](#development-guide)
8. [Project Status](#project-status)

---

## 🎉 What's New

### Recent Updates (v0.2.0)
- ✅ **Domain-Driven Design Migration**: Complete architectural overhaul
- ✅ **FastAPI Integration**: RESTful API with automatic documentation
- ✅ **Python 3.11 Support**: Using latest Python features
- ✅ **Conda Environment**: Professional development setup
- ✅ **Fixed Critical Issues**: Resolved duplicate methods, memory leaks, routing logic
- ✅ **Working Demo**: Cell → Tissue → Organ → System flow operational

### Project Structure
```
src/biocode/
├── domain/         # Core business logic (Entities, Value Objects)
├── application/    # Use cases and application services
├── infrastructure/ # External concerns (DB, monitoring, messaging)
└── interfaces/     # User interfaces (API, CLI, Dashboard)
```

See [docs/architecture/](docs/architecture/) for detailed architecture documentation.

---

## 🧪 Concept Introduction

**BioCode** is a revolutionary framework that brings a **biological organism** approach to software architecture. Instead of traditional class/module structures, your code is organized as living cells, tissues, organs, and systems - just like a real organism!

### 🎯 Why This Approach?

1. **Self-Healing**: Code that can detect and recover from errors
2. **Dynamic Growth**: Add new features at runtime
3. **Organic Communication**: Natural message passing between components
4. **Health Monitoring**: Continuous system health tracking
5. **Evolution**: Systems that learn and adapt over time
6. **Consciousness Levels**: Dynamic resource allocation based on load

---

## 🏗️ Architecture

### 1️⃣ CodeCell (Base Unit)
```python
class CodeCell:
    """Basic unit of life in BioCode"""
    - name: str                    # Cell identifier
    - dna: str                     # Unique genetic code (hash)
    - health_score: float          # 0-100 health indicator
    - state: CellState            # HEALTHY, INFECTED, HEALING, etc.
    - mutations: List[Mutation]    # Tracked changes
    
    def perform_operation(self, operation: Any) -> Any
    def heal(self) -> None
    def divide(self) -> CodeCell
```

### 2️⃣ AdvancedCodeTissue (Cell Container)
```python
class AdvancedCodeTissue:
    """Container for multiple cells working together"""
    - cells: Dict[str, CodeCell]
    - connections: Dict[str, List[str]]
    - quarantine: Set[str]
    
    async def execute_coordinated_operation(operation: Callable)
    def get_tissue_diagnostics() -> Dict[str, Any]
```

### 3️⃣ CodeOrgan (Functional Unit)
```python
class CodeOrgan:
    """Multiple tissues forming a functional unit"""
    - tissues: Dict[str, AdvancedCodeTissue]
    - organ_type: OrganType  # SENSORY, PROCESSING, STORAGE, etc.
    - compatibility_type: CompatibilityType  # A, B, AB, O
    - health: OrganHealth
    
    def add_tissue(tissue: AdvancedCodeTissue, role: str)
    def predict_failure() -> float
    async def process_request(request: Dict) -> Dict
```

### 4️⃣ CodeSystem (Complete Organism)
```python
class CodeSystem:
    """The complete living system"""
    - organs: Dict[str, CodeOrgan]
    - consciousness_level: ConsciousnessLevel
    - neural_ai: SystemAI
    - memory: SystemMemory
    
    async def boot()
    def add_organ(organ: CodeOrgan) -> bool
    async def process_request(request: Dict) -> Dict
    def evolve(selection_pressure: str)
```

---

## 🚀 Quick Start

### ⚠️ Pre-Installation Safety Notice
**IMPORTANT**: Before proceeding, ensure you:
1. Are working in an **isolated environment** (VM or container recommended)
2. Have **backup** of your system
3. Understand this is **LIVING CODE** that can grow, mutate, and die
4. Accept **full responsibility** for any consequences

### Prerequisites
- Python 3.11+
- Conda (recommended) or virtualenv
- **Isolated test environment**

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/biocode.git
cd biocode

# 2. Create conda environment
conda create -n biocode python=3.11
conda activate biocode

# 3. Install dependencies
pip install -e .
# or
poetry install

# 4. Start the API server
python -m uvicorn biocode.interfaces.api.main:app --reload

# 5. Open API documentation
# Visit http://localhost:8000/docs
```

### Run the Demo

```bash
# Run the complete Cell → Tissue → Organ → System demo
python demo_biocode_flow.py
```

Expected output:
```
🧬 BioCode Demo: Building a Living System
==================================================

1️⃣ Creating Cells...
   ✅ Created neuron_0 - Health: 100%
   ✅ Created neuron_1 - Health: 100%
   ...

2️⃣ Creating Brain Tissue...
   ✅ Created tissue 'cortex' with 5 cells
   📊 Coordination result: 5 cells responded

3️⃣ Creating Brain Organ...
   ✅ Created organ 'brain' with 1 tissue(s)
   💚 Organ health: 99.2%

4️⃣ Creating Organism System...
   ✅ System booted - Consciousness: aware
   
... and more!
```

---

## 📡 API Documentation

### FastAPI Server
The project includes a full RESTful API built with FastAPI:

- **API Base URL**: `http://localhost:8000`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

```bash
# Health Check
GET /

# Cell Operations
POST   /api/v1/cells          # Create a new cell
GET    /api/v1/cells/{id}     # Get cell by ID
GET    /api/v1/cells          # List all cells
DELETE /api/v1/cells/{id}     # Delete a cell

# Tissue Operations
POST   /api/v1/tissues        # Create tissue
GET    /api/v1/tissues/{id}   # Get tissue
POST   /api/v1/tissues/{id}/add-cell    # Add cell to tissue

# Organ Operations
POST   /api/v1/organs         # Create organ
GET    /api/v1/organs/{id}    # Get organ
POST   /api/v1/organs/{id}/add-tissue   # Add tissue to organ

# System Operations
POST   /api/v1/system         # Create system
GET    /api/v1/system/{id}    # Get system
POST   /api/v1/system/{id}/process      # Process request
```

---

## 💻 Working Example

### Create a Simple Authentication System

```python
import asyncio
from biocode.domain.entities import Cell, Tissue, Organ, System
from biocode.domain.entities.organ import OrganType, CompatibilityType

async def create_auth_system():
    # 1. Create cells
    login_cell = Cell("login_handler")
    token_cell = Cell("token_generator")
    
    # 2. Create tissue and add cells
    auth_tissue = Tissue("authentication")
    auth_tissue.cells["login"] = login_cell
    auth_tissue.cells["token"] = token_cell
    
    # 3. Create organ
    auth_organ = Organ(
        "auth_processor",
        OrganType.PROCESSING,
        CompatibilityType.TYPE_O  # Universal donor
    )
    auth_organ.add_tissue(auth_tissue)
    
    # 4. Create system
    system = System("auth_system")
    await system.boot()
    system.add_organ(auth_organ)
    
    # 5. Process authentication request
    request = {
        "type": "processing",
        "operation": "authenticate",
        "data": {"username": "user", "password": "pass"}
    }
    
    response = await system.process_request(request)
    print(f"Auth response: {response}")
    
    # 6. Check system health
    metrics = system.get_system_metrics()
    print(f"System health: {metrics['total_health']:.1f}%")

# Run the example
asyncio.run(create_auth_system())
```

---

## 🛠️ Development Guide

### Project Structure
```
biocode/
├── src/biocode/
│   ├── domain/          # Core business entities
│   ├── application/     # Use cases & services
│   ├── infrastructure/  # External integrations
│   └── interfaces/      # API, CLI, UI
├── tests/               # Test suite
├── docs/               # Documentation
├── examples/           # Example code
└── archive/            # Old code for reference
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=biocode --cov-report=html

# Run specific test file
pytest tests/unit/domain/entities/test_system.py -v
```

### Code Quality

```bash
# Format code
black src tests

# Lint code
ruff check src tests

# Type checking
mypy src
```

---

## 📊 Project Status

### Current State (v0.2.0)
- ✅ **Core Architecture**: Complete DDD migration
- ✅ **Basic Functionality**: Cell, Tissue, Organ, System working
- ✅ **API Layer**: FastAPI with full documentation
- ✅ **Test Coverage**: 88% for core components
- ⚠️ **Advanced Features**: In progress (evolution, consciousness)
- 🚧 **Dashboard**: Coming soon

### Known Limitations
1. `perform_operation` in Cell is simplified
2. Evolution system needs more sophisticated implementation
3. Memory consolidation is basic
4. Event system needs activation

### Roadmap
- [ ] Enhanced cell operations with real processing
- [ ] Active event-driven architecture
- [ ] Real-time monitoring dashboard
- [ ] Kubernetes operators for cloud deployment
- [ ] Plugin system for custom cell types

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing/CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is the proprietary software of **Umit Kacar, PhD**. All rights reserved.

- **Commercial Use**: Requires explicit written permission. Please contact for licensing.
- **Academic/Research Use**: May be permitted with prior written approval.
- See the [LICENSE](LICENSE) file for full details.

---

## 🙏 Acknowledgments

- Inspired by biological systems and nature
- Built with modern Python best practices
- Powered by FastAPI, Pydantic, and AsyncIO

---

<p align="center">
  Created by <strong>Umit Kacar, PhD</strong><br>
  <em>Where Code Comes Alive</em> 🧬<br>
  <small>© 2024 All Rights Reserved</small>
</p>