"""Code-Snippet: A biological-inspired code organization system."""

__version__ = "0.1.0"
__author__ = "Code-Snippet Team"

# Make imports easier
from . import core
from . import components
from . import monitoring
from . import security

__all__ = ["core", "components", "monitoring", "security"]