# 🦜 SwarmSearchCV Guide

## Overview

**SwarmSearchCV** is a hyperparameter optimization tool that uses Particle Swarm Optimization (PSO) to efficiently search continuous and mixed parameter spaces. Unlike grid search or random search, PSO uses swarm intelligence - particles communicate and learn from each other to find optimal solutions.

## 🧬 Key Concepts

### What is Particle Swarm Optimization?

PSO is inspired by the social behavior of bird flocks. Each particle (solution) moves through the parameter space influenced by:
- **Personal best**: Its own best position found so far
- **Global best**: The best position found by any particle in the swarm
- **Velocity**: Current direction and speed of exploration

### Advantages over Traditional Methods

| Method | Pros | Cons |
|--------|------|------|
| **Grid Search** | Exhaustive, guaranteed optimum in grid | Exponential complexity, discrete only |
| **Random Search** | Simple, handles high dimensions | No learning, may miss good regions |
| **PSO (SwarmSearchCV)** | Continuous spaces, learns from exploration | May converge to local optima |

## 🚀 Quick Start

### Basic Usage

```python
from src.evolution_lab.optimizers.swarm_search import SwarmSearchCV
from sklearn.svm import SVC
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

# Create dataset
X, y = make_classification(n_samples=1000, n_features=20)
X_train, X_test, y_train, y_test = train_test_split(X, y)

# Define search space
param_distributions = {
    'C': (0.01, 100.0, 'log'),      # Log-uniform distribution
    'gamma': (0.001, 1.0, 'log'),   # Log-uniform distribution
    'kernel': ['rbf', 'poly']        # Categorical choices
}

# Create optimizer
swarm = SwarmSearchCV(
    estimator=SVC(),
    param_distributions=param_distributions,
    n_particles=30,
    n_iterations=50,
    cv=5,
    n_jobs=-1
)

# Optimize
swarm.fit(X_train, y_train)

# Best results
print(f"Best score: {swarm.best_score_}")
print(f"Best params: {swarm.best_params_}")
print(f"Test score: {swarm.score(X_test, y_test)}")
```

## 📊 Parameter Types

### 1. Continuous Parameters
```python
# Uniform distribution
'alpha': (0.0, 1.0)

# Log-uniform (for parameters that vary by orders of magnitude)
'learning_rate': (0.001, 1.0, 'log')
```

### 2. Integer Parameters
```python
# Integer range
'n_estimators': (10, 200, 'int')
'max_depth': (2, 50, 'int')
```

### 3. Categorical Parameters
```python
# List of choices
'kernel': ['linear', 'rbf', 'poly', 'sigmoid']
'criterion': ['gini', 'entropy']
```

## 🎯 Advanced Configuration

### PSO Parameters

```python
swarm = SwarmSearchCV(
    estimator=model,
    param_distributions=params,
    
    # Swarm settings
    n_particles=30,        # Number of particles (solutions)
    n_iterations=100,      # Maximum iterations
    
    # PSO coefficients
    w_start=0.9,          # Initial inertia weight (exploration)
    w_end=0.4,            # Final inertia weight (exploitation)
    c1=2.0,               # Cognitive component (personal best)
    c2=2.0,               # Social component (global best)
    
    # Early stopping
    early_stopping=True,   # Stop if no improvement
    patience=10,          # Iterations without improvement
    
    # Cross-validation
    cv=5,                 # Number of folds
    scoring='accuracy',   # Metric to optimize
    
    # Computation
    n_jobs=-1,            # Use all CPU cores
    verbose=1             # Show progress
)
```

### Custom Scoring Functions

```python
from sklearn.metrics import make_scorer, f1_score

# Custom F1 scorer for multiclass
f1_weighted = make_scorer(f1_score, average='weighted')

swarm = SwarmSearchCV(
    estimator=model,
    param_distributions=params,
    scoring=f1_weighted
)
```

## 🔧 Practical Examples

### Example 1: Neural Network Optimization

```python
from sklearn.neural_network import MLPClassifier

param_distributions = {
    'hidden_layer_sizes': [(50,), (100,), (50, 50), (100, 50)],
    'alpha': (0.0001, 0.1, 'log'),
    'learning_rate_init': (0.001, 0.1, 'log'),
    'activation': ['relu', 'tanh'],
    'solver': ['adam', 'lbfgs']
}

swarm = SwarmSearchCV(
    MLPClassifier(max_iter=500),
    param_distributions,
    n_particles=20,
    n_iterations=30,
    cv=3
)
```

### Example 2: Random Forest with Many Parameters

```python
from sklearn.ensemble import RandomForestClassifier

param_distributions = {
    'n_estimators': (50, 500, 'int'),
    'max_depth': (5, 50, 'int'),
    'min_samples_split': (2, 20, 'int'),
    'min_samples_leaf': (1, 10, 'int'),
    'max_features': ['sqrt', 'log2', None],
    'bootstrap': [True, False]
}

# More particles for complex search space
swarm = SwarmSearchCV(
    RandomForestClassifier(),
    param_distributions,
    n_particles=50,
    n_iterations=100,
    early_stopping=True,
    patience=15
)
```

### Example 3: Pipeline Optimization

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA()),
    ('classifier', SVC())
])

param_distributions = {
    'pca__n_components': (0.5, 0.99),  # Variance ratio
    'classifier__C': (0.1, 100, 'log'),
    'classifier__gamma': (0.001, 1, 'log')
}

swarm = SwarmSearchCV(pipe, param_distributions)
```

## 📈 Visualization and Analysis

### Convergence Plot
```python
# After fitting
swarm.plot_convergence(save_path='convergence.png')
```

### Analyzing Results
```python
# Access CV results
cv_results = swarm.cv_results_

# Best particles
import pandas as pd
results_df = pd.DataFrame(cv_results)
top_10 = results_df.nlargest(10, 'mean_test_score')
print(top_10[['mean_test_score', 'params']])

# Parameter importance
param_scores = {}
for param in param_distributions:
    col = f'param_{param}'
    if col in results_df:
        correlation = results_df[col].corr(results_df['mean_test_score'])
        param_scores[param] = abs(correlation)
```

## 🎓 Best Practices

### 1. Choose Appropriate Number of Particles
- **Rule of thumb**: 10-50 particles
- More particles = better exploration but slower
- Complex spaces need more particles

### 2. Set Search Space Wisely
- Use log scale for parameters that vary by orders of magnitude
- Don't make ranges too wide - include domain knowledge
- Test with smaller ranges first, then expand

### 3. Early Stopping Strategy
```python
# Conservative - wait longer
swarm = SwarmSearchCV(..., patience=20)

# Aggressive - stop quickly
swarm = SwarmSearchCV(..., patience=5)
```

### 4. Parallel Execution
```python
# Use all cores
swarm = SwarmSearchCV(..., n_jobs=-1)

# Leave some cores free
swarm = SwarmSearchCV(..., n_jobs=4)
```

## 🔍 Troubleshooting

### Particles Converging Too Quickly
- Increase `w_start` (e.g., 1.2) for more exploration
- Increase `n_particles`
- Decrease `c2` to reduce social influence

### Poor Final Performance
- Increase `n_iterations`
- Check if search space is too narrow
- Try different `scoring` metrics
- Ensure sufficient `cv` folds

### Memory Issues
- Reduce `n_particles`
- Use `n_jobs=1` for sequential execution
- Simplify the model or use subset of data

## 🚀 Performance Tips

1. **Start Small**: Test with few particles/iterations first
2. **Use Domain Knowledge**: Set reasonable parameter bounds
3. **Monitor Progress**: Use `verbose=1` or `2`
4. **Save Results**: Export cv_results_ for later analysis
5. **Reproducibility**: Always set `random_state`

## 📚 References

- [Original PSO Paper](https://doi.org/10.1109/ICNN.1995.488968)
- [Particle Swarm Optimization Overview](https://en.wikipedia.org/wiki/Particle_swarm_optimization)
- [Hyperparameter Optimization Review](https://arxiv.org/abs/1502.02127)

---

*"The swarm doesn't just search - it learns, adapts, and converges on excellence."*