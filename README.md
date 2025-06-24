# 🧬 BioCode - Living Code Architecture

### *Where Code Comes Alive*

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📋 Table of Contents
1. [Concept Introduction](#concept-introduction)
2. [Architecture](#architecture)
3. [Working Example](#working-example)
4. [Usage Guide](#usage-guide)
5. [Future Roadmap](#future-roadmap)

---

## 🧪 Concept Introduction

**BioCode** is a revolutionary framework that brings a **biological organism** approach to software architecture. Instead of traditional class/module structures, your code is organized as living cells, tissues, organs, and systems - just like a real organism!

### 🎯 Why This Approach?

1. **Self-Healing**: Code that can heal itself
2. **Dynamic Growth**: Add new features at runtime
3. **Organic Communication**: Natural communication between components
4. **Health Monitoring**: Continuous code health tracking
5. **Isolation & Recovery**: Isolate and heal faulty components
6. **Biological Logging**: Context-aware logging with cell/tissue/organ hierarchy
7. **Quality Assurance**: Built-in testing and code quality tools
8. **Modern Python**: Type hints, async/await, and latest Python features

---

## 🏗️ Architecture

### 1️⃣ CodeCell (Base Unit - Class)
```python
# Each class behaves like a living cell
class CodeCell:
    - DNA (unique genetic code)
    - Health Score (0-100)
    - Mutations tracking
    - Self-healing ability
    - Cell division (instance creation)
    - Infection & immune response
```

**Features:**
- Each cell has unique DNA (class source code hash)
- Health score tracking
- Mutation recording
- Transition to infected state on errors
- Self-healing mechanism

### 2️⃣ CodeTissue (Multi-Class Container)
```python
# Tissue structure organizing multiple cells
class AdvancedCodeTissue:
    - Cell registry & type management
    - Inter-cell communication
    - Quarantine system
    - Transaction support
    - Performance metrics
    - Dependency injection
```

**Features:**
- Add new cell types at runtime
- Cell-to-cell messaging protocol
- Quarantine infected cells
- Transaction support for atomic operations
- Performance metrics (throughput, latency, error rate)
- Dependency injection container

### 3️⃣ CodeOrgan (Module)
```python
# Organ composed of multiple tissues
class CodeOrgan:
    - tissues: Dict[str, AdvancedCodeTissue]
    - data_flow_controller: DataFlowController
    - compatibility_type: CompatibilityType
    - health_monitoring: OrganHealth
    
    def add_tissue(...)
    def predict_failure(...)
    def hot_swap_tissue(...)
    def prepare_for_transplant(...)
```

**Features:**
- **DataFlowController**: Channel-based data flow, backpressure management
- **BloodTypeCompatibility**: Organ compatibility control (A, B, AB, O)
- **OrganHealth**: Blood flow, oxygen level, toxin level tracking
- **Hot-swap**: Replace tissues at runtime
- **Failure Prediction**: Proactive error prediction

### 4️⃣ CodeSystem (System)
```python
# System composed of organs
class CodeSystem:
    - organs: Dict[str, CodeOrgan]
    - neural_ai: SystemAI
    - memory: SystemMemory
    - circadian: CircadianScheduler
    - consciousness_level: ConsciousnessLevel
    
    def add_organ(...)
    def broadcast(...)
    def self_diagnose(...)
    def optimize(...)
```

**Features:**
- **SystemAI**: Neural pathway learning, pattern recognition
- **SystemMemory**: Short-term, long-term, working memory
- **CircadianScheduler**: Peak/off-peak/sleep phase management
- **ConsciousnessLevel**: Dormant → Awakening → Aware → Focused → Hyperaware → Dreaming
- **Dream State**: Deep optimization and memory consolidation

### 🧪 Tissue Components
```python
# ExtracellularMatrix (ECM)
- Shared resources and standards
- Security barriers
- Connective proteins (utilities)
- Matrix health (integrity, viscosity, permeability)

# HomeostasisController
- Parameter balance maintenance
- Feedback loops
- Auto-regulation

# VascularizationSystem
- Resource distribution channels
- Flow rate control
- Pressure management
```

---

## 🚀 Working Example: Authentication Tissue

### Installation
```bash
# Install dependencies
pip install -r config/requirements.txt

# Run the demo
python examples/auth_tissue_demo.py

# Or try the basic example
python examples/basic_usage.py
```

### Example Scenario

Authentication Tissue consists of 3 different cell types:

1. **LoginCell**: User authentication
   - Username/password validation
   - Failed attempt tracking
   - Account lockout mechanism

2. **TokenCell**: JWT token management
   - Token generation
   - Token validation
   - Token revocation

3. **PermissionCell**: Authorization control
   - Role-based permissions
   - Permission checking

### Demo Flow

```python
# 1. Create tissue
auth_tissue = AdvancedCodeTissue("AuthenticationTissue")

# 2. Register cell types
auth_tissue.register_cell_type(LoginCell)
auth_tissue.register_cell_type(TokenCell)
auth_tissue.register_cell_type(PermissionCell)

# 3. Grow cells
login_cell = auth_tissue.grow_cell("main_login", "LoginCell")
token_cell = auth_tissue.grow_cell("jwt_handler", "TokenCell")
perm_cell = auth_tissue.grow_cell("permission_checker", "PermissionCell")

# 4. Connect cells
auth_tissue.connect_cells("main_login", "jwt_handler")
auth_tissue.connect_cells("jwt_handler", "permission_checker")
```

### Demo Output
```
🧬 Authentication Tissue Demo Starting...

✅ Tissue Created Successfully!
Active Cells: 3

🔐 Testing Authentication Flow...
Login Result: {'success': True, 'user_id': '123', ...}
Token Generated: eyJ0eXAiOiJKV1QiLCJhbGc...
Token Verification: Valid=True
Can Delete: True
User Permissions: ['admin', 'write', 'delete', 'read']

🦠 Testing Error Handling...
Attempt 1-3: Invalid credentials
Attempt 4: Account locked!

📊 Tissue Diagnostics:
Health Score: 100.0
Infected Cells: 1 (login cell infected due to errors)
Cell States: {'main_login': 'infected', 'jwt_handler': 'healthy', ...}
```

---

## 📚 Usage Guide

### 1. Creating a New Cell Type

```python
from src.core.enhanced_codecell import EnhancedCodeCell

class MyCustomCell(EnhancedCodeCell):
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        # Cell-specific properties
        
    async def my_operation(self, data: Any) -> Any:
        try:
            # Perform operation
            return result
        except Exception as e:
            self.infect(e)  # Infect on error
            raise
```

### 2. Adding Cells to Tissue

```python
from src.core.advanced_codetissue import AdvancedCodeTissue

# Create tissue
my_tissue = AdvancedCodeTissue("MyTissue")

# Register cell type
my_tissue.register_cell_type(MyCustomCell)

# Inject dependencies (optional)
my_tissue.inject_dependency('db_connection', db)

# Grow cell
cell = my_tissue.grow_cell("cell_1", "MyCustomCell")
```

### 3. Inter-Cell Communication

```python
# Send signal
await my_tissue.send_signal(
    from_cell="cell_1",
    to_cell="cell_2", 
    signal={'type': 'data', 'content': 'Hello'}
)
```

### 4. Using Transactions

```python
with my_tissue.transaction("critical_operation") as tx:
    # Atomic operations
    tx.affected_cells.add("cell_1")
    tx.affected_cells.add("cell_2")
    
    # Perform operations
    # Automatic rollback on error
```

### 5. Health Monitoring

```python
# Tissue diagnostics
diagnostics = my_tissue.get_tissue_diagnostics()
print(f"Health: {diagnostics['metrics']['health_score']}")
print(f"Error Rate: {diagnostics['metrics']['error_rate']}")
print(f"Quarantined: {diagnostics['quarantine']}")
```

---

## 🛠️ Development Features

### 📝 Logging System

BioCode includes a comprehensive **biological-themed logging system**:

```python
from src.utils.logging_config import get_logger

# Get a logger with biological context
logger = get_logger(__name__, 
                   cell_id="liver_cell_42",
                   tissue_name="hepatic_tissue")

# Log biological events
logger.debug("Cell performing metabolism")  # CELLULAR level
logger.info("Tissue synchronized")          # TISSUE level
logger.warning("Organ stress detected")     # ORGAN level
logger.error("System failure")              # SYSTEM level
```

**Features:**
- Hierarchical biological log levels
- Colored console output
- Automatic log rotation
- Specialized security and performance loggers
- Structured logging with biological context

[📖 See Logging Guide](docs/development/logging-guide.md)

### 🧪 Testing Infrastructure

Comprehensive test suite with biological testing patterns:

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/test_codecell.py
pytest tests/test_codetissue.py

# Run with coverage
pytest --cov=src

# Run only fast tests
pytest -m "not slow"
```

### 🎨 Code Quality Tools

**Pre-commit hooks** ensure code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

**Included tools:**
- **Black** - Code formatting
- **Ruff** - Fast Python linter
- **MyPy** - Type checking
- **Bandit** - Security checking

### 📦 Modern Python Packaging

Using `pyproject.toml` for modern Python packaging:
- PEP 517/518 compliant
- Dependency groups (dev, test, docs)
- Tool configurations in one place

### 📚 Documentation

Comprehensive documentation available:

- **[Documentation Home](docs/)** - Complete documentation index
- **[Quick Start Guide](docs/getting-started/quickstart.md)** - Get started in 5 minutes
- **[Tutorial](docs/getting-started/tutorial.md)** - Build a complete web scraper organism
- **[Advanced Features](docs/guides/advanced-features.md)** - Neural pathways, consciousness levels, stem cells
- **[API Reference](docs/api/)** - Complete API documentation
- **[Contributing Guide](docs/contributing/)** - How to contribute

---

## 🔮 Future Roadmap

### Enhanced Features Coming Soon
- **CodeOrgan**: Complete implementation with advanced features
- **CodeSystem**: Full system consciousness and learning
- **CodeHuman**: Production-ready API layer
- **Visual Dashboard**: Real-time organism health monitoring
- **Plugin Ecosystem**: Extend with custom cell types
- **Cloud Native**: Kubernetes operators for organism deployment

---

## 🏃 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/umitkacar/biocode.git
cd biocode

# 2. Install dependencies
pip install -r config/requirements.txt

# 3. Install pre-commit hooks (for development)
pre-commit install

# 4. Run the demo
python examples/auth_tissue_demo.py

# 5. Try the basic example
python examples/basic_usage.py

# 6. Run tests
pytest

# 7. Create your own tissue!
```

### 🎯 Installation via pip (Coming Soon)

```bash
pip install biocode

# With all features
pip install biocode[all]

# Development installation
pip install biocode[dev]
```

---

## 📁 Project Structure

```
biocode/
├── 📄 README.md                    # Main documentation
├── 📋 FOLDER_STRUCTURE.md          # Detailed folder structure
├── 📝 pyproject.toml               # Modern Python packaging
├── 🧪 pytest.ini                   # Test configuration
├── 🔧 .pre-commit-config.yaml      # Pre-commit hooks
├── 📜 LICENSE                      # MIT License
│
├── 🔧 config/                      # Configuration files
│   ├── requirements.txt            # Python dependencies
│   ├── setup.py                    # Package setup file
│   └── logging.yaml                # Logging configuration
│
├── 📚 docs/                        # Documentation
│   ├── README.md                   # Documentation index
│   ├── getting-started/            # Getting started guides
│   │   ├── installation.md         # Installation guide
│   │   ├── quickstart.md           # Quick start guide
│   │   └── tutorial.md             # Complete tutorial
│   ├── architecture/               # Architecture documentation
│   │   ├── architecture_diagram.md # System design
│   │   ├── biological_features_analysis.md
│   │   └── project-structure.md    # Code organization
│   ├── guides/                     # User guides
│   │   ├── advanced-features.md    # Advanced features
│   │   └── async-style-guide.md    # Async patterns
│   ├── api/                        # API reference
│   │   ├── core.md                 # Core components
│   │   ├── components.md           # Supporting components
│   │   └── utils.md                # Utilities
│   ├── examples/                   # Example documentation
│   │   ├── dashboard_examples.md   # Dashboard examples
│   │   └── use-cases.md            # Real-world use cases
│   ├── development/                # Development guides
│   │   ├── code-style.md           # Code style guide
│   │   └── logging-guide.md        # Logging guide
│   └── contributing/               # Contribution guides
│       ├── CONTRIBUTING.md         # How to contribute
│       ├── development-setup.md    # Dev environment
│       └── testing.md              # Testing guide
│
├── 🔬 examples/                    # Example applications
│   ├── auth_tissue_demo.py         # Authentication demo
│   ├── basic_usage.py              # Basic usage example
│   ├── logging_example.py          # Logging demonstration
│   └── web_scraper_organism.py     # Complete organism example
│
├── 🧬 src/                         # Source code
│   ├── core/                       # Core components
│   │   ├── enhanced_codecell.py    # CodeCell
│   │   ├── advanced_codetissue.py  # CodeTissue
│   │   ├── stem_cell_system.py     # Stem cells
│   │   ├── code_organ.py           # CodeOrgan
│   │   └── code_system.py          # CodeSystem
│   │
│   ├── components/                 # Supporting components
│   │   ├── tissue_components.py    # ECM, Homeostasis
│   │   └── system_managers.py      # System managers
│   │
│   ├── monitoring/                 # Monitoring system
│   │   └── performance_metrics.py  # Metrics & dashboard
│   │
│   ├── security/                   # Security
│   │   └── security_manager.py     # Dynamic security
│   │
│   └── utils/                      # Utilities
│       └── logging_config.py       # Logging system
│
└── 🧪 tests/                       # Test suite
    ├── __init__.py
    ├── conftest.py                 # Test configuration
    ├── test_codecell.py            # Cell tests
    └── test_codetissue.py          # Tissue tests
```

---

## 🎯 Conclusion

With **BioCode**, your code is no longer just a static structure - it's a living, breathing, self-healing organism! Cells can get sick, heal, communicate with each other, and work together as organized tissue.

**"We don't write code, we grow it!"** 🌱

---

## 🤝 Contributing

BioCode is an open-source project and we welcome your contributions!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Nature for inspiring the biological system architecture
- The open-source community
- All contributors

---

<p align="center">
  Made with ❤️ by the BioCode Team<br>
  <em>Where Code Comes Alive</em>
</p>