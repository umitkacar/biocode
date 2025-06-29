# 🎯 Pareto Health Optimizer Guide

## Overview

The **Pareto Health Optimizer** is a multi-objective optimization system that finds the optimal balance between competing code health metrics. Instead of optimizing a single metric (which often degrades others), it discovers the Pareto-optimal frontier where no single solution dominates all objectives.

## 🧬 Key Concepts

### What is Pareto Optimization?

Pareto optimization finds solutions where improving one objective would worsen another. These solutions form the "Pareto frontier" - a set of equally good trade-offs.

### Our Objectives

The system optimizes 5 objectives simultaneously:

1. **Security Score** (maximize) - From SecurityAnalyzer
2. **Performance Score** (maximize) - From PerformanceAnalyzer  
3. **Test Coverage** (maximize) - From TestCoverageAnalyzer
4. **Code Complexity** (minimize) - From CodeAnalyzer
5. **Duplication Ratio** (minimize) - From CodeEmbeddingAnalyzer

## 🚀 Quick Start

### Basic Usage

```python
from src.evolution_lab.optimizers.pareto_health import ParetoHealthOptimizer
from src.evolution_lab.colony import EvolutionLabColony

# Analyze project
colony = EvolutionLabColony()
snapshot = await colony.analyze_project("/path/to/project")

# Extract results
analyzer_results = snapshot.metrics

# Optimize
optimizer = ParetoHealthOptimizer()
solutions = optimizer.optimize(
    analyzer_results,
    n_gen=100,      # Generations
    pop_size=100,   # Population size
    algorithm="nsga3"  # or "nsga2"
)

# Select balanced solution
balanced = optimizer.select_balanced_solution()
print(f"Optimal weights: {balanced.weights}")
```

### Understanding Results

Each solution contains:
- **weights**: Optimal weight for each analyzer (sums to 1.0)
- **objectives**: Achieved values for each objective
- **fitness**: Internal fitness values used by the algorithm

## 📊 Visualization

The system generates multiple visualizations:

### 2D Trade-off Plots
- Security vs Performance
- Coverage vs Complexity  
- Security vs Duplication

### 3D Trade-off Space
- Shows relationship between top 3 objectives

### Example Output
```
🎯 Top Pareto-Optimal Solutions
┏━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ ID ┃ Security ┃ Performance ┃ Coverage ┃ Complexity ┃ Duplication ┃
┡━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 1  │ 85.0     │ 72.5        │ 65.0     │ 8.5        │ 0.15        │
│ 2  │ 80.0     │ 78.0        │ 62.0     │ 9.0        │ 0.12        │
│ 3  │ 90.0     │ 68.0        │ 70.0     │ 7.5        │ 0.18        │
└────┴──────────┴─────────────┴──────────┴────────────┴─────────────┘
```

## 🔧 Advanced Configuration

### Algorithm Selection

**NSGA-III** (default):
- Better for many objectives (>3)
- Uses reference directions
- More diverse solutions

**NSGA-II**:
- Classic algorithm
- Good for 2-3 objectives
- Faster convergence

### Customizing Objectives

```python
class CustomProblem(ColonyHealthProblem):
    def __init__(self, analyzer_results):
        super().__init__(analyzer_results)
        
        # Add custom objective
        self.objectives.append(
            OptimizationObjective("custom_metric", "maximize")
        )
```

### Weight Constraints

By default, analyzer weights are constrained between 0.1 and 0.9. Modify in the Problem class:

```python
super().__init__(
    n_var=n_var,
    n_obj=n_obj,
    n_constr=n_constr,
    xl=0.05,  # Min weight 5%
    xu=0.95,  # Max weight 95%
)
```

## 🎯 Use Cases

### 1. CI/CD Pipeline Configuration

Use optimal weights to configure your pipeline:

```yaml
# .github/workflows/biocode.yml
- uses: biocode/analyze
  with:
    weights:
      SecurityAnalyzer: 0.25
      PerformanceAnalyzer: 0.20
      TestCoverageAnalyzer: 0.30
      CodeAnalyzer: 0.15
      CodeEmbeddingAnalyzer: 0.10
```

### 2. Team-Specific Profiles

Create profiles for different teams:

```python
# Security-focused team
security_weights = optimizer.optimize_for_objective("security_score")

# Performance-critical team  
perf_weights = optimizer.optimize_for_objective("performance_score")

# Balanced team
balanced_weights = optimizer.select_balanced_solution()
```

### 3. Progressive Improvement

Track Pareto frontier evolution over time:

```python
# Week 1
solutions_week1 = optimizer.optimize(results_week1)

# Week 2 
solutions_week2 = optimizer.optimize(results_week2)

# Compare frontiers
improvement = compare_pareto_fronts(solutions_week1, solutions_week2)
```

## 🧪 Testing

Run comprehensive tests:

```bash
pytest tests/unit/evolution_lab/test_pareto_health.py -v
```

Test coverage includes:
- Objective calculation
- Multi-objective optimization
- Solution selection
- Data export/visualization

## 📈 Performance Tips

1. **Population Size**: Use at least 100 for good diversity
2. **Generations**: 50-200 typically sufficient
3. **Reference Directions**: For NSGA-III, ensure pop_size ≥ ref_dirs
4. **Parallel Evaluation**: Set `n_jobs=-1` for parallel processing

## 🔍 Troubleshooting

### No Improvement Over Generations
- Increase population size
- Check objective scaling (normalize to similar ranges)
- Verify analyzer results are meaningful

### Too Few Solutions
- Increase population diversity
- Reduce constraints
- Use NSGA-III for better exploration

### Visualization Issues
- Ensure matplotlib is installed
- Check data ranges for outliers
- Use log scale for large differences

## 📚 References

- [NSGA-III Paper](https://doi.org/10.1109/TEVC.2013.2281535)
- [pymoo Documentation](https://pymoo.org/)
- [Multi-Objective Optimization Theory](https://en.wikipedia.org/wiki/Multi-objective_optimization)

---

*"In multi-objective optimization, there is no single best solution - only intelligent trade-offs."*