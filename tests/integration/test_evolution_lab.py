#!/usr/bin/env python3
"""Test Evolution Lab import and functionality"""
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Import from within src
from evolution_lab.colony import EvolutionLabColony, ProjectSnapshot

async def main():
    """Test evolution lab"""
    print("Testing Evolution Lab imports...")
    
    # Create a mock snapshot
    snapshot = ProjectSnapshot(
        project_path="/home/umit/CLAUDE_PROJECT/Ear-segmentation-ai",
        health_score=85.5,
        metrics={
            'CodeAnalyzer': {
                'primary_language': 'python',
                'total_files': 45,
                'total_lines': 3420,
                'frameworks': ['TensorFlow', 'OpenCV'],
                'average_complexity': 4.2
            }
        }
    )
    
    print(f"✓ Created snapshot: {snapshot.project_path}")
    print(f"  Health Score: {snapshot.health_score}%")
    print(f"  Timestamp: {snapshot.timestamp}")
    
    # Test colony creation
    colony = EvolutionLabColony()
    print("✓ Created Evolution Lab Colony")
    
    # Test colony health
    health = colony.get_colony_health()
    print(f"✓ Colony Health: {health}")
    
    print("\n✅ All imports and basic functionality working!")

if __name__ == "__main__":
    asyncio.run(main())