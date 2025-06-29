#!/usr/bin/env python3
"""Debug colony analysis"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from evolution_lab.colony import EvolutionLabColony, AnalyzerCell
from evolution_lab.analyzers.code_analyzer import CodeAnalyzer

async def main():
    # Create a single analyzer cell and test it
    project_path = "/home/umit/CLAUDE_PROJECT/Ear-segmentation-ai"
    
    print("Testing single analyzer cell...")
    cell = AnalyzerCell(CodeAnalyzer, project_path)
    result = await cell.analyze()
    
    print(f"Cell result type: {type(result)}")
    print(f"Has metrics attr: {hasattr(result, 'metrics')}")
    if hasattr(result, 'metrics'):
        print(f"Metrics: {result.metrics.get('primary_language', 'none')}")
        print(f"Total files: {result.metrics.get('total_files', 0)}")
    
    # Now test full colony
    print("\nTesting full colony...")
    colony = EvolutionLabColony()
    snapshot = await colony.analyze_project(project_path)
    
    print(f"Snapshot metrics: {snapshot.metrics}")
    print(f"Snapshot issues: {len(snapshot.issues)}")
    print(f"Snapshot suggestions: {len(snapshot.suggestions)}")

if __name__ == "__main__":
    asyncio.run(main())