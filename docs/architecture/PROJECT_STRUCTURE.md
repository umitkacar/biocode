# 🏗️ BioCode Project Structure

## 📁 Directory Organization

```
biocode/
├── src/                    # Source code
│   ├── biocode/           # Main application package
│   │   ├── domain/        # Business logic & entities
│   │   ├── application/   # Use cases & commands
│   │   ├── infrastructure/# External services
│   │   └── interfaces/    # API, CLI, Dashboard
│   └── evolution_lab/     # Experimental features
│
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── e2e/              # End-to-end tests
│   └── fixtures/         # Test data
│
├── examples/              # Example code
│   ├── demos/            # Demo applications
│   ├── notebooks/        # Jupyter notebooks
│   └── test_scripts/     # Test scripts
│
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   ├── architecture/     # Architecture docs
│   ├── guides/           # User guides
│   └── images/           # Documentation images
│
├── scripts/               # Utility scripts
│   ├── migration/        # Migration tools
│   ├── launchers/        # Launch scripts
│   └── docs/             # Documentation generators
│
├── deployment/            # Deployment configs
│   ├── docker/           # Docker files
│   ├── kubernetes/       # K8s manifests
│   └── terraform/        # Infrastructure as Code
│
├── config/                # Configuration files
│   ├── default.toml      # Default config
│   ├── development.toml  # Dev config
│   └── production.toml   # Prod config
│
├── benchmarks/            # Performance benchmarks
├── tools/                 # Development tools
├── data/                  # Runtime data (gitignored)
└── archive/               # Old/deprecated files
```

## 🚀 Quick Start

```bash
# Activate environment
conda activate biocode

# Install dependencies
poetry install --all-extras

# Run tests
poetry run pytest

# Start API
poetry run uvicorn biocode.interfaces.api.main:app --reload

# Run CLI
poetry run biocode --help
```

## 📋 Key Files

- `pyproject.toml` - Python project configuration
- `poetry.lock` - Locked dependencies
- `.env` - Environment variables
- `Makefile` - Build automation
- `README.md` - Project overview
