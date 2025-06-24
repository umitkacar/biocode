# Code Style Guide

## Overview

BioCode uses automated code formatting and linting to maintain consistent code style across the project. We use:

- **Black** - The uncompromising Python code formatter
- **Ruff** - An extremely fast Python linter
- **MyPy** - Static type checker for Python
- **Pre-commit** - Git hook framework to ensure code quality

## Setup

### Install Pre-commit Hooks

1. Install the development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

2. Install the pre-commit hooks:
   ```bash
   pre-commit install
   ```

3. (Optional) Run against all files:
   ```bash
   pre-commit run --all-files
   ```

## Usage

### Automatic Formatting

Pre-commit hooks will automatically run when you commit code:

```bash
git add .
git commit -m "Add new feature"
# Pre-commit hooks run automatically here
```

If any files are modified by the formatters, the commit will be aborted. Simply add the changes and commit again:

```bash
git add .
git commit -m "Add new feature"
```

### Manual Formatting

You can also run the formatters manually:

```bash
# Format with Black
black src/ tests/

# Lint with Ruff
ruff check src/ tests/ --fix

# Type check with MyPy
mypy src/
```

## Configuration

### Black Configuration

Black is configured in `pyproject.toml`:

```toml
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311']
```

### Ruff Configuration

Ruff is configured in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]  # Line too long (handled by Black)
```

### MyPy Configuration

MyPy is configured in `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.8"
disallow_untyped_defs = true
strict_equality = true
```

## Code Style Guidelines

### Import Order

Imports should be organized in the following order:

1. Standard library imports
2. Third-party imports
3. Local application imports

Example:
```python
import os
import sys
from datetime import datetime

import pytest
import asyncio

from src.core.enhanced_codecell import EnhancedCodeCell
from src.core.advanced_codetissue import AdvancedCodeTissue
```

### Type Hints

Always use type hints for function arguments and return values:

```python
def grow_cell(self, name: str, cell_type: str) -> EnhancedCodeCell:
    """Grow a new cell in the tissue"""
    pass
```

### Docstrings

Use docstrings for all public functions, classes, and modules:

```python
def heal(self, amount: int = 10) -> None:
    """
    Heal the cell by increasing its health score.
    
    Args:
        amount: The amount to heal (default: 10)
        
    Returns:
        None
    """
    pass
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `EnhancedCodeCell`)
- **Functions/Methods**: snake_case (e.g., `trigger_apoptosis`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_HEALTH`)
- **Private methods**: Leading underscore (e.g., `_internal_method`)

## IDE Integration

### VS Code

Install the following extensions:
- Python (Microsoft)
- Black Formatter
- Ruff

Add to `.vscode/settings.json`:
```json
{
    "python.formatting.provider": "black",
    "python.linting.ruffEnabled": true,
    "editor.formatOnSave": true
}
```

### PyCharm

1. Go to Settings → Tools → Black
2. Enable "On save" option
3. Configure Ruff as an external tool

## Continuous Integration

The CI pipeline runs the same checks:

```yaml
- name: Code Quality
  run: |
    black --check src/ tests/
    ruff check src/ tests/
    mypy src/
```

## Troubleshooting

### Pre-commit Hook Failures

If pre-commit hooks fail:

1. Check the error message
2. Fix the issues manually or let the tools auto-fix
3. Stage the changes and commit again

### Skipping Hooks (Emergency Only)

In rare cases where you need to skip hooks:

```bash
git commit --no-verify -m "Emergency fix"
```

**Note**: This should be avoided and the code should be fixed in the next commit.

## Contributing

When contributing to BioCode:

1. Ensure pre-commit hooks are installed
2. Run tests before committing
3. Follow the code style guidelines
4. Add type hints to new code
5. Write clear commit messages

For more information, see our [Contributing Guide](../CONTRIBUTING.md).