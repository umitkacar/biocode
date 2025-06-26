# BioCode Project Structure

## 📁 Project Organization

```
biocode/
├── src/biocode/              # Source code
│   ├── ecs/                  # Entity-Component-System core
│   │   ├── entity.py         # Entity class
│   │   ├── component.py      # Component base
│   │   ├── system.py         # System base
│   │   ├── world.py          # World/Registry
│   │   ├── components/       # All components
│   │   └── systems/          # All systems
│   │
│   ├── mixins/               # Framework capabilities
│   │   ├── serializable.py   # JSON/Binary serialization
│   │   ├── observable.py     # Change tracking
│   │   ├── networkable.py    # Network sync
│   │   ├── persistable.py    # Database storage
│   │   ├── cacheable.py      # In-memory caching
│   │   ├── replicable.py     # Deep cloning
│   │   ├── versionable.py    # Version control
│   │   └── validatable.py    # Data validation
│   │
│   ├── aspects/              # Cross-cutting concerns
│   │   ├── base.py           # Aspect base class
│   │   ├── logging_aspect.py # Automatic logging
│   │   ├── performance_aspect.py # Performance monitoring
│   │   ├── security_aspect.py    # Access control
│   │   ├── error_handling_aspect.py # Error management
│   │   ├── transaction_aspect.py # Transaction boundaries
│   │   ├── monitoring_aspect.py  # Health monitoring
│   │   └── weaver.py         # Aspect weaver
│   │
│   ├── factories/            # Entity creation
│   │   ├── cell_factory.py   # Cell creation
│   │   └── organism_factory.py # Complex organisms
│   │
│   ├── domain/               # Business logic
│   │   ├── events/           # Domain events
│   │   ├── exceptions.py     # Custom exceptions
│   │   └── value_objects/    # Value objects
│   │
│   ├── application/          # Use cases
│   │   ├── commands/         # Command handlers
│   │   ├── queries/          # Query handlers
│   │   └── interfaces/       # Application interfaces
│   │
│   ├── infrastructure/       # External concerns
│   │   ├── persistence/      # Database adapters
│   │   ├── messaging/        # Event bus
│   │   └── monitoring/       # Metrics collection
│   │
│   ├── interfaces/           # User interfaces
│   │   ├── api/              # REST API (FastAPI)
│   │   └── cli/              # Command line interface
│   │
│   └── shared/               # Shared utilities
│       ├── config.py         # Configuration
│       └── logging.py        # Logging setup
│
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   │   ├── ecs/              # ECS tests
│   │   ├── mixins/           # Mixin tests
│   │   └── aspects/          # Aspect tests
│   ├── integration/          # Integration tests
│   ├── e2e/                  # End-to-end tests
│   └── performance/          # Performance benchmarks
│
├── docs/                     # Documentation
│   ├── architecture/         # Architecture docs
│   ├── api/                  # API documentation
│   ├── guides/               # User guides
│   └── development/          # Dev guidelines
│
├── demos/                    # Demo applications
│   ├── ecs_demo.py          # Basic ECS demo
│   ├── advanced_ecs_demo.py # Advanced features
│   └── aop_demo.py          # AOP demonstration
│
├── examples/                 # Example code
│   ├── basic/               # Basic examples
│   ├── advanced/            # Advanced examples
│   └── tutorials/           # Tutorial code
│
├── scripts/                  # Utility scripts
│   ├── migration/           # Migration scripts
│   └── launchers/           # Launch scripts
│
├── archive/                  # Archived code
│   ├── old_structure/       # Previous architecture
│   ├── old_domain_entities/ # Old OOP entities
│   └── generated/           # Generated files
│
├── logs/                    # Log files (gitignored)
│   └── archive/             # Archived logs
│
├── pyproject.toml           # Project configuration
├── pytest.ini               # Test configuration
├── README.md                # Project overview
├── CHANGELOG.md             # Version history
├── LICENSE                  # License information
└── .gitignore              # Git ignore rules
```

## 🎯 Key Principles

1. **Separation of Concerns**: Each directory has a single, clear purpose
2. **Clean Architecture**: Dependencies flow inward (interfaces → application → domain)
3. **ECS Pattern**: Data (components) separated from logic (systems)
4. **Testability**: Parallel test structure mirrors source code
5. **Documentation**: Comprehensive docs alongside code

## 📦 Module Responsibilities

### `src/biocode/ecs/`
Core Entity-Component-System implementation. This is the heart of the framework.

### `src/biocode/mixins/`
Optional capabilities that can be mixed into entities without modifying core ECS.

### `src/biocode/aspects/`
Cross-cutting concerns applied via AOP, keeping business logic clean.

### `src/biocode/factories/`
Centralized entity creation with pre-configured templates.

### `src/biocode/domain/`
Pure business logic, domain events, and value objects.

### `src/biocode/application/`
Use cases and application services orchestrating domain logic.

### `src/biocode/infrastructure/`
External integrations: databases, messaging, monitoring.

### `src/biocode/interfaces/`
User-facing interfaces: REST API, CLI, future dashboard.

## 🚀 Quick Navigation

- **Start Here**: `demos/ecs_demo.py` - Simple ECS example
- **Architecture**: `docs/architecture/BIOCODE_ARCHITECTURE_DESIGN_GUIDE.md`
- **API Docs**: Run `uvicorn src.biocode.interfaces.api.main:app`
- **Run Tests**: `pytest tests/unit/`