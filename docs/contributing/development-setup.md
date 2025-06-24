# 🛠️ Development Setup

This guide will help you set up your development environment for contributing to BioCode.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Git**: 2.0 or higher
- **OS**: Linux, macOS, or Windows (with WSL)

### Recommended Tools
- **IDE**: VSCode, PyCharm, or similar
- **Terminal**: With color support
- **GitHub Account**: For contributions

## 🚀 Setup Steps

### 1. Fork and Clone

```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/biocode.git
cd biocode

# Add upstream remote
git remote add upstream https://github.com/umitkacar/biocode.git
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install all dependencies
pip install -e ".[all,dev]"

# Or install from requirements
pip install -r config/requirements.txt
pip install -r config/requirements-dev.txt
```

### 4. Setup Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files (optional)
pre-commit run --all-files
```

### 5. Configure IDE

#### VSCode
Create `.vscode/settings.json`:
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": false,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false
}
```

#### PyCharm
1. Set Python interpreter to virtual environment
2. Enable Black formatter
3. Configure pytest as test runner

## 🧪 Verify Installation

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_codecell.py

# Run with verbose output
pytest -v
```

### Check Code Style
```bash
# Format code
black src/ tests/

# Check linting
ruff check src/

# Type checking
mypy src/
```

### Run Examples
```bash
# Basic example
python examples/basic_usage.py

# Authentication demo
python examples/auth_tissue_demo.py

# Logging demo
python examples/logging_example.py
```

## 📁 Project Layout

```
biocode/
├── src/               # Source code
│   ├── core/         # Core components
│   ├── components/   # Supporting components
│   ├── monitoring/   # Monitoring system
│   ├── security/     # Security features
│   └── utils/        # Utilities
├── tests/            # Test suite
├── examples/         # Example code
├── docs/            # Documentation
└── config/          # Configuration
```

## 🔧 Development Workflow

### 1. Create Feature Branch
```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature
```

### 2. Make Changes
- Write code following [style guide](../development/code-style.md)
- Add tests for new features
- Update documentation

### 3. Test Changes
```bash
# Run tests
pytest

# Check style
pre-commit run --all-files

# Build docs (optional)
cd docs && make html
```

### 4. Commit Changes
```bash
# Stage changes
git add .

# Commit with conventional message
git commit -m "feat: add cell hibernation feature"
```

### 5. Push and Create PR
```bash
# Push to your fork
git push origin feature/your-feature

# Create PR on GitHub
```

## 🐛 Debugging

### Enable Debug Logging
```python
from src.utils.logging_config import setup_logging

setup_logging(log_level="DEBUG")
```

### Use Python Debugger
```python
import pdb

def my_function():
    pdb.set_trace()  # Breakpoint
    # Your code here
```

### VSCode Debugging
Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        },
        {
            "name": "Python: Pytest",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["-v"],
            "console": "integratedTerminal"
        }
    ]
}
```

## 📊 Performance Profiling

```bash
# Profile with cProfile
python -m cProfile -o profile.stats examples/basic_usage.py

# Visualize with snakeviz
pip install snakeviz
snakeviz profile.stats
```

## 🔄 Keeping Up to Date

```bash
# Fetch upstream changes
git fetch upstream

# Merge or rebase
git checkout main
git merge upstream/main

# Update dependencies
pip install -e ".[all,dev]" --upgrade
```

## 💡 Development Tips

1. **Use Type Hints**
   ```python
   def process_cell(cell: EnhancedCodeCell) -> Dict[str, Any]:
       return {"health": cell.health_score}
   ```

2. **Write Docstrings**
   ```python
   def divide_cell(parent: EnhancedCodeCell) -> Optional[EnhancedCodeCell]:
       """
       Perform cell division (mitosis).
       
       Args:
           parent: The parent cell
           
       Returns:
           New daughter cell or None if division fails
       """
   ```

3. **Follow Biological Metaphors**
   - Use biological terms consistently
   - Maintain realistic biological behavior
   - Document biological inspiration

4. **Test Edge Cases**
   - Test error conditions
   - Test boundary values
   - Test concurrent operations

## 🆘 Troubleshooting

### Import Errors
```bash
# Ensure package is installed in development mode
pip install -e .
```

### Test Failures
```bash
# Run specific test with output
pytest -xvs tests/test_codecell.py::test_cell_division
```

### Pre-commit Issues
```bash
# Skip hooks temporarily
git commit --no-verify -m "WIP: debugging"

# Fix and amend
pre-commit run --all-files
git commit --amend
```

## 📚 Additional Resources

- [Python Best Practices](https://docs.python-guide.org/)
- [Async Programming](https://docs.python.org/3/library/asyncio.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Formatter](https://black.readthedocs.io/)

---

Ready to start developing? Check out the [Testing Guide](testing.md) next! 🧪