# BioCode Environment Setup

## Python Environment
- **Conda Environment Name**: `biocode`
- **Python Version**: 3.11.13
- **Conda Path**: `~/miniconda`

## Activation Command
```bash
source ~/miniconda/etc/profile.d/conda.sh && conda activate biocode
```

## Important Notes
- Always use the biocode conda environment when working on this project
- Python 3.11.13 is required for all modern Python features
- The project uses modern type hints without __future__ imports

## Dependencies
- See pyproject.toml for full dependency list
- Main dependencies are managed by Poetry
- Development environment uses pytest, black, ruff, mypy

## Running the Project
```bash
# Activate environment
source ~/miniconda/etc/profile.d/conda.sh && conda activate biocode

# Install dependencies (if needed)
poetry install

# Run tests
pytest

# Run demos
python demos/biocode_demo.py
python demos/evolution_lab_demo.py
```