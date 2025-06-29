#!/usr/bin/env python3
"""
Runner script for Python 3.11 environment
This ensures proper imports and environment setup
"""
import os
import sys
import subprocess
from pathlib import Path

# Get the project root
PROJECT_ROOT = Path(__file__).parent.resolve()
SRC_PATH = PROJECT_ROOT / "src"

# Setup environment
os.environ["PYTHONPATH"] = str(SRC_PATH)

def run_command(cmd: list[str]) -> int:
    """Run a command with proper environment"""
    env = os.environ.copy()
    
    # Activate conda environment
    conda_setup = ["source", "~/miniconda/etc/profile.d/conda.sh", "&&", "conda", "activate", "biocode", "&&"]
    
    # Build full command
    full_cmd = " ".join(conda_setup + cmd)
    
    # Run with shell
    result = subprocess.run(full_cmd, shell=True, env=env)
    return result.returncode

def main():
    """Main entry point"""
    print("🐍 Python 3.11 BioCode Runner")
    print("=" * 50)
    
    # Check if running specific command
    if len(sys.argv) > 1:
        cmd = sys.argv[1:]
        print(f"Running: {' '.join(cmd)}")
        return run_command(cmd)
    
    # Default: run evolution lab demo
    print("Running Evolution Lab Demo...")
    os.chdir(SRC_PATH)
    
    # Import and run directly
    sys.path.insert(0, str(SRC_PATH))
    
    # Now we can import
    from evolution_lab.colony import EvolutionLabColony
    import asyncio
    
    async def run_demo():
        colony = EvolutionLabColony()
        project_path = "/home/umit/CLAUDE_PROJECT/Ear-segmentation-ai"
        
        print(f"🔬 Analyzing: {project_path}")
        snapshot = await colony.analyze_project(project_path)
        
        print(f"\n📊 Results:")
        print(f"  Health Score: {snapshot.health_score}%")
        print(f"  Metrics: {len(snapshot.metrics)} analyzers")
        print(f"  Issues: {len(snapshot.issues)}")
        print(f"  Suggestions: {len(snapshot.suggestions)}")
    
    asyncio.run(run_demo())

if __name__ == "__main__":
    main()