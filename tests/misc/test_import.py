#!/usr/bin/env python3
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Try importing
try:
    from evolution_lab.colony import EvolutionLabColony
    print("Import successful!")
except Exception as e:
    print(f"Import failed: {e}")
    
# Check sys.path
print("\nPython path:")
for p in sys.path[:3]:
    print(f"  {p}")