#!/usr/bin/env python3
"""
BioCode Project Structure Migration Script
Migrates from current structure to Domain-Driven Design structure
"""
import os
import shutil
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Define the migration mappings
FILE_MIGRATIONS = {
    # Core domain entities
    "src/core/enhanced_codecell.py": "src/biocode/domain/entities/cell.py",
    "src/core/advanced_codetissue.py": "src/biocode/domain/entities/tissue.py",
    "src/core/code_organ.py": "src/biocode/domain/entities/organ.py",
    "src/core/code_system.py": "src/biocode/domain/entities/system.py",
    
    # Value objects
    "src/core/code_genome.py": "src/biocode/domain/value_objects/dna.py",
    "src/agent/biocode_memory.py": "src/biocode/domain/value_objects/memory.py",
    
    # Domain services
    "src/evolution/evolution_engine.py": "src/biocode/domain/services/evolution.py",
    "src/agent/healing_system.py": "src/biocode/domain/services/healing.py",
    
    # Infrastructure - Persistence
    "src/core/cell_storage.py": "src/biocode/infrastructure/persistence/memory/cell_repository.py",
    
    # Infrastructure - Monitoring
    "src/monitoring/performance_metrics.py": "src/biocode/infrastructure/monitoring/prometheus.py",
    
    # Interfaces - API
    "src/dashboard/api/cells.py": "src/biocode/interfaces/api/v1/cells.py",
    "src/dashboard/api/tissues.py": "src/biocode/interfaces/api/v1/tissues.py",
    "src/dashboard/api/organs.py": "src/biocode/interfaces/api/v1/organs.py",
    
    # Interfaces - Dashboard
    "src/dashboard/app.py": "src/biocode/interfaces/dashboard/app.py",
    "src/dashboard/components/cell_viewer.py": "src/biocode/interfaces/dashboard/components/cell_viewer.py",
    "src/dashboard/components/metrics_display.py": "src/biocode/interfaces/dashboard/components/metrics_display.py",
    
    # Interfaces - CLI
    "src/agent/biocode_agent.py": "src/biocode/interfaces/cli/commands.py",
    
    # Tests
    "tests/test_enhanced_codecell.py": "tests/unit/domain/entities/test_cell.py",
    "tests/test_codetissue.py": "tests/unit/domain/entities/test_tissue.py",
    "tests/test_codeorgan.py": "tests/unit/domain/entities/test_organ.py",
    "tests/test_codesystem.py": "tests/unit/domain/entities/test_system.py",
    "tests/test_evolution_features.py": "tests/unit/domain/services/test_evolution.py",
    
    # Examples
    "examples/basic_tissue_demo.py": "examples/basic/tissue_demo.py",
    "examples/auth_tissue_demo.py": "examples/basic/auth_demo.py",
    "examples/digital_evolution_demo.py": "examples/advanced/evolution_demo.py",
    "examples/integrated_simulation_demo.py": "examples/advanced/full_simulation.py",
}

# New directories to create
NEW_DIRECTORIES = [
    # Source structure
    "src/biocode",
    "src/biocode/domain",
    "src/biocode/domain/entities",
    "src/biocode/domain/value_objects",
    "src/biocode/domain/events",
    "src/biocode/domain/services",
    "src/biocode/application",
    "src/biocode/application/commands",
    "src/biocode/application/queries",
    "src/biocode/application/interfaces",
    "src/biocode/application/dto",
    "src/biocode/infrastructure",
    "src/biocode/infrastructure/persistence",
    "src/biocode/infrastructure/persistence/memory",
    "src/biocode/infrastructure/persistence/file",
    "src/biocode/infrastructure/persistence/database",
    "src/biocode/infrastructure/messaging",
    "src/biocode/infrastructure/monitoring",
    "src/biocode/infrastructure/security",
    "src/biocode/interfaces",
    "src/biocode/interfaces/api",
    "src/biocode/interfaces/api/v1",
    "src/biocode/interfaces/api/middleware",
    "src/biocode/interfaces/cli",
    "src/biocode/interfaces/dashboard",
    "src/biocode/interfaces/dashboard/static",
    "src/biocode/interfaces/dashboard/templates",
    "src/biocode/interfaces/dashboard/components",
    "src/biocode/interfaces/grpc",
    "src/biocode/plugins",
    "src/biocode/plugins/builtin",
    "src/biocode/plugins/builtin/cells",
    "src/biocode/plugins/builtin/organs",
    "src/biocode/plugins/builtin/behaviors",
    "src/biocode/shared",
    "src/evolution_lab",
    "src/evolution_lab/experiments",
    "src/evolution_lab/mutations",
    "src/evolution_lab/scenarios",
    
    # Test structure
    "tests/unit",
    "tests/unit/domain",
    "tests/unit/domain/entities",
    "tests/unit/domain/services",
    "tests/unit/application",
    "tests/unit/infrastructure",
    "tests/integration",
    "tests/integration/api",
    "tests/integration/persistence",
    "tests/e2e",
    "tests/e2e/scenarios",
    "tests/performance",
    "tests/performance/benchmarks",
    "tests/fixtures",
    
    # Other directories
    "scripts",
    "deployment",
    "deployment/docker",
    "deployment/kubernetes",
    "deployment/kubernetes/base",
    "deployment/kubernetes/overlays",
    "deployment/terraform",
    "deployment/terraform/modules",
    "deployment/terraform/environments",
    "deployment/ansible",
    "deployment/ansible/playbooks",
    "deployment/ansible/roles",
    "docs/api",
    "docs/api/postman",
    "docs/architecture",
    "docs/architecture/decisions",
    "docs/architecture/diagrams",
    "docs/guides",
    "docs/guides/advanced",
    "docs/development",
    "config",
    "data",
    "data/cells",
    "data/memory",
    "data/logs",
    "data/plugins",
    "examples/basic",
    "examples/advanced",
    "examples/tutorials",
    "benchmarks",
    "tools",
    "tools/linting",
    "tools/hooks",
    "tools/debugging",
]

# Import statement mappings
IMPORT_MAPPINGS = {
    # Old imports -> New imports
    r"from src\.core\.enhanced_codecell": "from biocode.domain.entities.cell",
    r"from src\.core\.advanced_codetissue": "from biocode.domain.entities.tissue",
    r"from src\.core\.code_organ": "from biocode.domain.entities.organ",
    r"from src\.core\.code_system": "from biocode.domain.entities.system",
    r"from src\.monitoring\.performance_metrics": "from biocode.infrastructure.monitoring.prometheus",
    r"from src\.agent\.biocode_agent": "from biocode.interfaces.cli.commands",
    r"from src\.dashboard\.app": "from biocode.interfaces.dashboard.app",
    r"from \.\.monitoring\.performance_metrics": "from biocode.infrastructure.monitoring.prometheus",
    r"from \.\.core\.": "from biocode.domain.entities.",
    r"from \.\.agent\.": "from biocode.application.",
}


class ProjectMigrator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backup_dir = project_root / "backup_before_migration"
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def run_migration(self):
        """Execute the full migration process"""
        print("🚀 Starting BioCode Project Migration")
        print("=" * 50)
        
        # Step 1: Create backup
        print("\n📦 Step 1: Creating backup...")
        self.create_backup()
        
        # Step 2: Create new directory structure
        print("\n📁 Step 2: Creating new directory structure...")
        self.create_directories()
        
        # Step 3: Migrate files
        print("\n📋 Step 3: Migrating files...")
        self.migrate_files()
        
        # Step 4: Create missing files
        print("\n✨ Step 4: Creating missing files...")
        self.create_missing_files()
        
        # Step 5: Update imports
        print("\n🔄 Step 5: Updating imports...")
        self.update_imports()
        
        # Step 6: Create configuration files
        print("\n⚙️ Step 6: Creating configuration files...")
        self.create_config_files()
        
        # Step 7: Update documentation
        print("\n📚 Step 7: Updating documentation...")
        self.update_documentation()
        
        # Report results
        self.report_results()
        
    def create_backup(self):
        """Create a backup of important files"""
        if self.backup_dir.exists():
            print(f"  ⚠️  Backup directory already exists: {self.backup_dir}")
            return
            
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup important files
        important_files = [
            "src",
            "tests",
            "examples",
            "requirements.txt",
            "setup.py",
            "README.md",
        ]
        
        for item in important_files:
            source = self.project_root / item
            if source.exists():
                dest = self.backup_dir / item
                if source.is_dir():
                    shutil.copytree(source, dest)
                else:
                    shutil.copy2(source, dest)
                print(f"  ✅ Backed up: {item}")
                
    def create_directories(self):
        """Create new directory structure"""
        for dir_path in NEW_DIRECTORIES:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py in Python directories
            if "src/" in dir_path or "tests/" in dir_path:
                init_file = full_path / "__init__.py"
                if not init_file.exists():
                    init_file.write_text("")
                    
        print(f"  ✅ Created {len(NEW_DIRECTORIES)} directories")
        
    def migrate_files(self):
        """Migrate files to new locations"""
        migrated_count = 0
        
        for old_path, new_path in FILE_MIGRATIONS.items():
            source = self.project_root / old_path
            dest = self.project_root / new_path
            
            if source.exists():
                # Ensure destination directory exists
                dest.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file (preserve original for now)
                shutil.copy2(source, dest)
                migrated_count += 1
                print(f"  ✅ Migrated: {old_path} -> {new_path}")
            else:
                self.warnings.append(f"Source file not found: {old_path}")
                
        print(f"  ✅ Migrated {migrated_count} files")
        
    def create_missing_files(self):
        """Create essential files that don't exist yet"""
        files_to_create = {
            # Domain exceptions
            "src/biocode/domain/exceptions.py": '''"""Domain-specific exceptions"""

class DomainException(Exception):
    """Base exception for domain errors"""
    pass

class CellException(DomainException):
    """Cell-related exceptions"""
    pass

class TissueException(DomainException):
    """Tissue-related exceptions"""
    pass

class OrganException(DomainException):
    """Organ-related exceptions"""
    pass

class SystemException(DomainException):
    """System-related exceptions"""
    pass
''',
            
            # Application interfaces
            "src/biocode/application/interfaces/repositories.py": '''"""Repository interfaces"""
from abc import ABC, abstractmethod
from typing import List, Optional
from biocode.domain.entities import Cell, Tissue, Organ, System


class CellRepository(ABC):
    @abstractmethod
    async def save(self, cell: Cell) -> None:
        pass
    
    @abstractmethod
    async def find_by_id(self, cell_id: str) -> Optional[Cell]:
        pass
    
    @abstractmethod
    async def find_all(self) -> List[Cell]:
        pass
    
    @abstractmethod
    async def delete(self, cell_id: str) -> None:
        pass


class TissueRepository(ABC):
    @abstractmethod
    async def save(self, tissue: Tissue) -> None:
        pass
    
    @abstractmethod
    async def find_by_id(self, tissue_id: str) -> Optional[Tissue]:
        pass


class OrganRepository(ABC):
    @abstractmethod
    async def save(self, organ: Organ) -> None:
        pass
    
    @abstractmethod
    async def find_by_id(self, organ_id: str) -> Optional[Organ]:
        pass


class SystemRepository(ABC):
    @abstractmethod
    async def save(self, system: System) -> None:
        pass
    
    @abstractmethod
    async def find_by_id(self, system_id: str) -> Optional[System]:
        pass
''',
            
            # Event bus interface
            "src/biocode/application/interfaces/event_bus.py": '''"""Event bus interface"""
from abc import ABC, abstractmethod
from typing import Any, Callable, Type


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: Any) -> None:
        """Publish an event"""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: Type, handler: Callable) -> None:
        """Subscribe to an event type"""
        pass
''',
            
            # Shared utilities
            "src/biocode/shared/config.py": '''"""Configuration management"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "BioCode"
    environment: str = "development"
    debug: bool = True
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    
    # Database
    db_url: str = "sqlite:///./biocode.db"
    db_echo: bool = False
    
    # Redis
    redis_url: Optional[str] = None
    
    # Monitoring
    prometheus_enabled: bool = True
    metrics_port: int = 9090
    
    class Config:
        env_file = ".env"
        env_prefix = "BIOCODE_"


settings = Settings()
''',
            
            # Logging configuration
            "src/biocode/shared/logging.py": '''"""Logging configuration"""
import logging
import sys
from pathlib import Path


def setup_logging(log_level: str = "INFO"):
    """Configure logging for the application"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(Path("data/logs/biocode.log"))
        ]
    )
    
    # Set third-party loggers to WARNING
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
''',
            
            # Main package init
            "src/biocode/__init__.py": '''"""BioCode - Biological Code Architecture Framework"""

__version__ = "0.2.0"
__author__ = "BioCode Team"

from biocode.domain.entities import Cell, Tissue, Organ, System

__all__ = ["Cell", "Tissue", "Organ", "System"]
''',
            
            # Version file
            "src/biocode/__version__.py": '''"""Version information"""

__version__ = "0.2.0"
''',
        }
        
        created_count = 0
        for file_path, content in files_to_create.items():
            full_path = self.project_root / file_path
            if not full_path.exists():
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
                created_count += 1
                
        print(f"  ✅ Created {created_count} missing files")
        
    def update_imports(self):
        """Update import statements in Python files"""
        python_files = []
        
        # Find all Python files in new structure
        for root, dirs, files in os.walk(self.project_root / "src/biocode"):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)
                    
        for root, dirs, files in os.walk(self.project_root / "tests"):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)
                    
        updated_count = 0
        for file_path in python_files:
            try:
                content = file_path.read_text()
                original_content = content
                
                # Apply import mappings
                for old_import, new_import in IMPORT_MAPPINGS.items():
                    content = re.sub(old_import, new_import, content)
                    
                # Update relative imports
                content = self.update_relative_imports(content, file_path)
                
                if content != original_content:
                    file_path.write_text(content)
                    updated_count += 1
                    
            except Exception as e:
                self.errors.append(f"Failed to update imports in {file_path}: {str(e)}")
                
        print(f"  ✅ Updated imports in {updated_count} files")
        
    def update_relative_imports(self, content: str, file_path: Path) -> str:
        """Update relative imports based on new file location"""
        # This is simplified - would need more complex logic for all cases
        if "src/biocode/domain" in str(file_path):
            # Within domain, imports should be relative
            content = re.sub(
                r"from biocode\.domain\.entities import",
                "from . import",
                content
            )
        return content
        
    def create_config_files(self):
        """Create configuration files"""
        config_files = {
            # Default configuration
            "config/default.toml": '''[app]
name = "BioCode"
version = "0.2.0"

[api]
host = "0.0.0.0"
port = 8000

[database]
url = "sqlite:///./biocode.db"

[monitoring]
enabled = true
port = 9090
''',
            
            # Development configuration
            "config/development.toml": '''[app]
debug = true

[database]
echo = true

[api]
reload = true
''',
            
            # Testing configuration
            "config/testing.toml": '''[app]
debug = false

[database]
url = "sqlite:///:memory:"

[api]
port = 8001
''',
            
            # Production configuration
            "config/production.toml": '''[app]
debug = false

[database]
pool_size = 20
max_overflow = 0

[api]
workers = 4
''',
            
            # Docker compose for development
            "deployment/docker/docker-compose.yml": '''version: '3.8'

services:
  biocode:
    build:
      context: ../..
      dockerfile: deployment/docker/Dockerfile
    ports:
      - "8000:8000"
      - "9090:9090"
    environment:
      - BIOCODE_ENVIRONMENT=development
    volumes:
      - ../../src:/app/src
      - ../../tests:/app/tests
      - biocode_data:/app/data
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      
  prometheus:
    image: prom/prometheus
    ports:
      - "9091:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

volumes:
  biocode_data:
  redis_data:
  prometheus_data:
''',
            
            # Dockerfile
            "deployment/docker/Dockerfile": '''FROM python:3.11-slim as builder

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
COPY config/ ./config/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src:$PYTHONPATH"

EXPOSE 8000 9090

CMD ["python", "-m", "biocode.interfaces.api"]
''',
            
            # Makefile
            "Makefile": '''# BioCode Makefile

.PHONY: help install test lint format clean migrate

help:
	@echo "Available commands:"
	@echo "  install    Install dependencies"
	@echo "  test       Run tests"
	@echo "  lint       Run linters"
	@echo "  format     Format code"
	@echo "  clean      Clean build artifacts"
	@echo "  migrate    Run migration script"
	@echo "  run        Run the application"

install:
	poetry install

test:
	pytest tests/ -v --cov=src/biocode

lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage .mypy_cache

migrate:
	python migrate_to_new_structure.py

run:
	python -m biocode.interfaces.api

dev:
	docker-compose -f deployment/docker/docker-compose.yml up
''',
        }
        
        created_count = 0
        for file_path, content in config_files.items():
            full_path = self.project_root / file_path
            if not full_path.exists():
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
                created_count += 1
                
        print(f"  ✅ Created {created_count} configuration files")
        
    def update_documentation(self):
        """Update README and create additional documentation"""
        # Update README
        readme_path = self.project_root / "README.md"
        if readme_path.exists():
            content = readme_path.read_text()
            
            # Add migration notice
            migration_notice = '''
## 🚀 Project Structure Migration

This project has been migrated to a Domain-Driven Design (DDD) architecture.

### New Structure:
- `src/biocode/domain/` - Core business logic
- `src/biocode/application/` - Use cases and application logic
- `src/biocode/infrastructure/` - External concerns (DB, monitoring, etc.)
- `src/biocode/interfaces/` - User interfaces (API, CLI, Dashboard)

See [ARCHITECTURE_PRINCIPLES.md](ARCHITECTURE_PRINCIPLES.md) for details.

'''
            
            # Insert after first heading
            lines = content.split('\n')
            insert_index = 0
            for i, line in enumerate(lines):
                if line.startswith('# '):
                    insert_index = i + 1
                    break
                    
            lines.insert(insert_index, migration_notice)
            readme_path.write_text('\n'.join(lines))
            
        print("  ✅ Updated documentation")
        
    def report_results(self):
        """Report migration results"""
        print("\n" + "=" * 50)
        print("📊 Migration Results")
        print("=" * 50)
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
                
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
                
        if not self.errors:
            print("\n✅ Migration completed successfully!")
            print("\n📝 Next steps:")
            print("  1. Review the migrated files")
            print("  2. Run tests: make test")
            print("  3. Update any remaining imports manually")
            print("  4. Remove old directory structure when ready")
            print(f"  5. Backup saved in: {self.backup_dir}")
            
        else:
            print("\n❌ Migration completed with errors. Please review and fix them.")


def main():
    """Main entry point"""
    project_root = Path(__file__).parent
    
    print("🧬 BioCode Project Structure Migration Tool")
    print("This will reorganize your project to follow Domain-Driven Design")
    print(f"Project root: {project_root}")
    print()
    
    response = input("Do you want to proceed? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        return
        
    migrator = ProjectMigrator(project_root)
    migrator.run_migration()


if __name__ == "__main__":
    main()