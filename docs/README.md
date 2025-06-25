# 📚 BioCode Documentation

**Version 0.2.0** - Domain-Driven Design Architecture

Welcome to the BioCode documentation! This guide will help you understand and use the BioCode framework - a revolutionary approach that brings biological organism concepts to software architecture.

## 🎉 Current Status (v0.2.0)

### ✅ Completed
- **Domain-Driven Design Migration** - Complete architectural overhaul
- **FastAPI Integration** - RESTful API with Swagger documentation at `/docs`
- **Python 3.11 Support** - Using conda environment
- **Core Components Working** - Cell → Tissue → Organ → System flow operational
- **Critical Fixes Applied** - Fixed duplicate methods, memory leaks, routing logic
- **88% Test Pass Rate** - Core components working harmoniously

### 🚧 In Progress
- **Enhanced Cell Operations** - Moving from pass/NotImplementedError to real functionality
- **Event System Activation** - Implementing domain events
- **Dashboard Development** - Real-time monitoring interface

### 📋 Known Limitations
- `perform_operation` in Cell currently simplified
- Evolution system needs more sophisticated implementation
- Memory consolidation is basic
- Some methods still returning placeholder values

## 📖 Documentation Structure

### 🚀 [Getting Started](getting-started/)
- [Installation Guide](getting-started/installation.md) - How to install BioCode
- [Quick Start](getting-started/quickstart.md) - Get up and running in 5 minutes
- [Tutorial](getting-started/tutorial.md) - Build your first organism

### 🏗️ [Architecture](architecture/)
- [Architecture Overview](architecture/architecture_diagram.md) - System design and components
- [Biological Features Analysis](architecture/biological_features_analysis.md) - Deep dive into biological concepts
- [Project Structure](architecture/project-structure.md) - Code organization

### 📘 [Guides](guides/)
- [Advanced Features](guides/advanced-features.md) - Neural pathways, consciousness, stem cells
- [Async Style Guide](guides/async-style-guide.md) - Async/await best practices

### 🛠️ [Development](development/)
- [Code Style Guide](development/code-style.md) - Coding standards and conventions
- [Logging Guide](development/logging-guide.md) - Using the biological logging system

### 🔧 [API Reference](api/)
- [Core Components](api/core.md) - CodeCell, CodeTissue, CodeOrgan, CodeSystem
- [Components](api/components.md) - Supporting components
- [Utilities](api/utils.md) - Utility functions and helpers

### 💡 [Examples](examples/)
- [Dashboard Examples](examples/dashboard_examples.md) - Monitoring and visualization
- [Real-World Use Cases](examples/use-cases.md) - Production examples

### 🤝 [Contributing](contributing/)
- [Contribution Guide](contributing/CONTRIBUTING.md) - How to contribute
- [Development Setup](contributing/development-setup.md) - Setting up your environment
- [Testing Guide](contributing/testing.md) - Writing and running tests

## 🎯 Quick Links

### For New Users
1. Start with [Installation](getting-started/installation.md)
2. Follow the [Quick Start Guide](getting-started/quickstart.md)
3. Try the [Tutorial](getting-started/tutorial.md)
4. **NEW**: Run `python demo_biocode_flow.py` for a working example!

### For Developers
1. Read the [Architecture Overview](architecture/architecture_diagram.md)
2. Check the [Code Style Guide](development/code-style.md)
3. Learn about [Advanced Features](guides/advanced-features.md)
4. **NEW**: API available at `http://localhost:8000/docs`

### For Contributors
1. Read [How to Contribute](contributing/CONTRIBUTING.md)
2. Set up your [Development Environment](contributing/development-setup.md)
3. Understand the [Testing Strategy](contributing/testing.md)
4. **NEW**: Use conda environment with Python 3.11

## 🚀 Quick Start Commands

```bash
# Setup environment
conda create -n biocode python=3.11
conda activate biocode
pip install -e .

# Start API server
python -m uvicorn biocode.interfaces.api.main:app --reload

# Run demo
python demo_biocode_flow.py

# Run tests
pytest tests/unit/domain/entities/ -v
```

## 🔍 Search Documentation

Looking for something specific? Use GitHub's search feature to search within the `/docs` folder.

## 🏗️ New Domain-Driven Design Structure

```
src/biocode/
├── domain/         # Core business logic
│   ├── entities/   # Cell, Tissue, Organ, System
│   ├── events/     # Domain events
│   └── value_objects/  # Value types
├── application/    # Use cases
│   ├── services/   # Application services
│   └── use_cases/  # Business operations
├── infrastructure/ # External concerns
│   ├── persistence/  # Data storage
│   ├── monitoring/   # Health & metrics
│   └── messaging/    # Event bus
└── interfaces/     # User interfaces
    ├── api/        # REST API (FastAPI)
    ├── cli/        # Command line
    └── dashboard/  # Web dashboard
```

## 📝 Documentation Standards

All documentation follows these principles:
- **Clear and Concise** - Easy to understand
- **Example-Driven** - Code examples for every concept
- **Up-to-Date** - Synchronized with code changes
- **Biological Metaphors** - Consistent with BioCode's philosophy

## 🐛 Found an Issue?

If you find any issues with the documentation:
1. [Open an issue](https://github.com/umitkacar/biocode/issues/new)
2. Or submit a PR with fixes
3. Tag it with `documentation` label

---

<p align="center">
  <strong>BioCode v0.2.0</strong><br>
  <em>Where Code Comes Alive! 🧬</em><br>
  <small>Created by <strong>Umit Kacar, PhD</strong></small><br>
  <small>© 2024 All Rights Reserved | Built with Domain-Driven Design & FastAPI</small>
</p>