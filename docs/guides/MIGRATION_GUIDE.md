# 🚀 BioCode Migration Guide

## Overview

This guide will help you migrate your BioCode project from the current structure to the new Domain-Driven Design (DDD) architecture.

## 🎯 Why Migrate?

The new architecture provides:
- **Better Separation of Concerns**: Clear boundaries between business logic and infrastructure
- **Improved Testability**: Each layer can be tested independently
- **Enhanced Scalability**: Easy to split into microservices later
- **Professional Structure**: Industry-standard patterns that competitors use
- **Plugin Architecture**: Extensible system for custom implementations

## 📋 Pre-Migration Checklist

- [ ] Commit all current changes: `git add . && git commit -m "Pre-migration checkpoint"`
- [ ] Review the `PERFECT_PROJECT_STRUCTURE.md` document
- [ ] Review the `ARCHITECTURE_PRINCIPLES.md` document
- [ ] Ensure all tests are passing: `pytest`

## 🔧 Migration Steps

### Step 1: Run the Migration Script

```bash
# Make the script executable
chmod +x migrate_to_new_structure.py

# Run the migration
python migrate_to_new_structure.py
```

The script will:
1. Create a backup of your current structure
2. Create the new directory structure
3. Migrate files to their new locations
4. Update import statements
5. Create missing configuration files

### Step 2: Install Poetry (if not already installed)

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Or using pip
pip install poetry
```

### Step 3: Update Dependencies

```bash
# Remove old pyproject.toml and use the new one
rm pyproject.toml
mv pyproject_new.toml pyproject.toml

# Install dependencies with Poetry
poetry install --all-extras

# Or install specific feature sets
poetry install --extras "api cli monitoring"
```

### Step 4: Update Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
BIOCODE_ENVIRONMENT=development
BIOCODE_DEBUG=true
BIOCODE_API_PORT=8000
BIOCODE_DB_URL=sqlite:///./biocode.db
```

### Step 5: Verify the Migration

```bash
# Run tests in the new structure
poetry run pytest

# Check the API
poetry run python -m biocode.interfaces.api.main

# Check the CLI
poetry run biocode --help
```

## 📁 New Structure Overview

### Domain Layer (`src/biocode/domain/`)
- **Entities**: Core business objects (Cell, Tissue, Organ, System)
- **Value Objects**: Immutable domain concepts (DNA, Memory)
- **Events**: Domain events for loose coupling
- **Services**: Domain logic that doesn't fit in entities

### Application Layer (`src/biocode/application/`)
- **Commands**: Write operations (CQRS pattern)
- **Queries**: Read operations
- **DTOs**: Data Transfer Objects
- **Interfaces**: Port definitions for infrastructure

### Infrastructure Layer (`src/biocode/infrastructure/`)
- **Persistence**: Repository implementations
- **Messaging**: Event bus implementations
- **Monitoring**: Metrics and logging
- **Security**: Authentication and authorization

### Interface Layer (`src/biocode/interfaces/`)
- **API**: REST API with FastAPI
- **CLI**: Command-line interface with Typer
- **Dashboard**: Web dashboard
- **gRPC**: RPC interface for microservices

## 🔄 Import Changes

### Old Imports
```python
from src.core.enhanced_codecell import EnhancedCodeCell
from src.core.code_organ import CodeOrgan
from src.monitoring.performance_metrics import MetricsCollector
```

### New Imports
```python
from biocode.domain.entities.cell import Cell
from biocode.domain.entities.organ import Organ
from biocode.infrastructure.monitoring.prometheus import MetricsCollector
```

## 🧪 Testing in the New Structure

### Unit Tests
Test domain logic without external dependencies:
```python
# tests/unit/domain/entities/test_cell.py
def test_cell_division():
    cell = Cell(dna=DNA.random())
    child = cell.divide()
    assert child.parent_id == cell.id
```

### Integration Tests
Test use cases with real implementations:
```python
# tests/integration/test_create_cell.py
async def test_create_cell_command():
    repo = InMemoryCellRepository()
    command = CreateCellCommand(repo)
    result = await command.execute(CreateCellRequest(...))
```

### E2E Tests
Test complete workflows:
```python
# tests/e2e/test_cell_lifecycle.py
async def test_full_cell_lifecycle(client):
    response = await client.post("/api/v1/cells", json={...})
    assert response.status_code == 201
```

## 🚀 Running the Application

### API Server
```bash
# Development
poetry run python -m biocode.interfaces.api.main

# Production
poetry run uvicorn biocode.interfaces.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### CLI
```bash
# Run CLI commands
poetry run biocode cell create --type neuron
poetry run biocode system status
```

### Dashboard
```bash
# Start the dashboard
poetry run python -m biocode.interfaces.dashboard.app
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
cd deployment/docker
docker-compose up -d

# Check logs
docker-compose logs -f biocode
```

## 📝 Common Issues and Solutions

### Issue: Import errors after migration
**Solution**: Ensure you're using the new import paths and have run `poetry install`

### Issue: Tests failing
**Solution**: Update test imports and use the new entity names

### Issue: Missing dependencies
**Solution**: Install with `poetry install --all-extras`

### Issue: Configuration not found
**Solution**: Create config files in the `config/` directory

## 🔙 Rollback Plan

If you need to rollback:

1. Your original code is backed up in `backup_before_migration/`
2. Restore from backup:
   ```bash
   rm -rf src tests
   cp -r backup_before_migration/src .
   cp -r backup_before_migration/tests .
   ```

## 📚 Next Steps

1. Review and update any custom scripts
2. Update CI/CD pipelines to use the new structure
3. Train team members on DDD concepts
4. Start implementing new features using the clean architecture
5. Consider splitting into microservices as needed

## 🤝 Getting Help

- Review `ARCHITECTURE_PRINCIPLES.md` for detailed patterns
- Check the example implementations in the new structure
- Create issues for any migration problems

## ✅ Post-Migration Checklist

- [ ] All tests passing
- [ ] API endpoints working
- [ ] CLI commands functioning
- [ ] Documentation updated
- [ ] Team trained on new structure
- [ ] CI/CD pipelines updated
- [ ] Production deployment plan ready

Good luck with your migration! 🚀