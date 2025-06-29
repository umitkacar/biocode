"""
Evolution Lab Optimizers - Multi-objective optimization for code health
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""

# Import optimizers with optional dependencies
try:
    from .pareto_health import ParetoHealthOptimizer, ColonyHealthProblem
    _PARETO_AVAILABLE = True
except ImportError:
    # pymoo not installed
    ParetoHealthOptimizer = None
    ColonyHealthProblem = None
    _PARETO_AVAILABLE = False
    
from .swarm_search import SwarmSearchCV, Particle, SearchSpace

__all__ = [
    'ParetoHealthOptimizer',
    'ColonyHealthProblem',
    'SwarmSearchCV',
    'Particle', 
    'SearchSpace',
]