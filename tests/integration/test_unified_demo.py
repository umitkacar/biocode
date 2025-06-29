#!/usr/bin/env python3
"""
Non-interactive test for unified BioCode demo
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Import components
from src.evolution_lab.colony import EvolutionLabColony
from src.evolution_lab.analyzers.code_smell_analyzer import CodeSmellAnalyzer
from src.evolution_lab.optimizers.pareto_health import ParetoHealthOptimizer
from src.evolution_lab.optimizers.swarm_search import SwarmSearchCV
from src.biocode.ecs import World
from src.biocode.ecs.systems import LifeSystem, EnergySystem

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

async def test_unified_features():
    """Test all unified features"""
    print("🧬 Testing BioCode Unified Features\n")
    
    project_path = str(Path(__file__).parent / "src" / "evolution_lab")
    errors = []
    
    # 1. Test Evolution Lab
    print("1️⃣ Testing Evolution Lab...")
    try:
        colony = EvolutionLabColony()
        snapshot = await colony.analyze_project(project_path)
        print(f"   ✓ Colony analysis: {len(snapshot.metrics)} analyzers, health: {snapshot.health_score}%")
    except Exception as e:
        errors.append(f"Evolution Lab: {e}")
        print(f"   ✗ Error: {e}")
    
    # 2. Test Code Smell Detection
    print("\n2️⃣ Testing Code Smell Detection...")
    try:
        analyzer = CodeSmellAnalyzer(project_path)
        results = analyzer.analyze()
        print(f"   ✓ Found {sum(results['smell_distribution'].values())} code smells")
        print(f"   ✓ Health score: {results['health_score']}%")
    except Exception as e:
        errors.append(f"Code Smell: {e}")
        print(f"   ✗ Error: {e}")
    
    # 3. Test Pareto Optimization
    print("\n3️⃣ Testing Pareto Optimization...")
    try:
        if 'snapshot' in locals():
            optimizer = ParetoHealthOptimizer()
            solutions = optimizer.optimize(
                snapshot.metrics,
                n_gen=5,  # Quick test
                pop_size=10
            )
            print(f"   ✓ Found {len(solutions)} Pareto-optimal solutions")
        else:
            print("   ⚠ Skipped - no metrics available")
    except Exception as e:
        errors.append(f"Pareto: {e}")
        print(f"   ✗ Error: {e}")
    
    # 4. Test SwarmSearchCV
    print("\n4️⃣ Testing SwarmSearchCV...")
    try:
        X, y = make_classification(n_samples=100, n_features=5, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        swarm = SwarmSearchCV(
            SVC(),
            {'C': (0.1, 10.0, 'log'), 'gamma': (0.001, 1.0, 'log')},
            n_particles=5,
            n_iterations=5,
            cv=2,
            verbose=0
        )
        swarm.fit(X_train, y_train)
        score = swarm.score(X_test, y_test)
        print(f"   ✓ Best CV score: {swarm.best_score_:.3f}")
        print(f"   ✓ Test score: {score:.3f}")
    except Exception as e:
        errors.append(f"SwarmSearchCV: {e}")
        print(f"   ✗ Error: {e}")
    
    # 5. Test ECS Architecture
    print("\n5️⃣ Testing ECS Architecture...")
    try:
        world = World()
        world.add_system(LifeSystem())
        world.add_system(EnergySystem())
        
        # Run a few ticks
        for _ in range(5):
            world.update(delta_time=0.1)
        
        print("   ✓ ECS world created and running")
    except Exception as e:
        errors.append(f"ECS: {e}")
        print(f"   ✗ Error: {e}")
    
    # Summary
    print(f"\n{'='*50}")
    if not errors:
        print("✅ All features working correctly!")
        print("🎉 Unified demo is ready to use")
    else:
        print(f"❌ Found {len(errors)} errors:")
        for err in errors:
            print(f"   - {err}")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = asyncio.run(test_unified_features())
    sys.exit(0 if success else 1)