"""
Pareto Health Optimizer - Multi-objective optimization for colony health
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

Balances multiple objectives:
- Security Score (maximize)
- Performance Score (maximize) 
- Test Coverage (maximize)
- Code Complexity (minimize)
- Duplication Ratio (minimize)
"""
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging

from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.termination import get_termination
from pymoo.optimize import minimize
from pymoo.util.ref_dirs import get_reference_directions


@dataclass
class OptimizationObjective:
    """Represents an optimization objective"""
    name: str
    direction: str  # 'maximize' or 'minimize'
    weight_range: Tuple[float, float] = (0.0, 1.0)
    current_value: float = 0.0
    
    def normalize(self, value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
        """Normalize value to [0, 1] range"""
        return (value - min_val) / (max_val - min_val)


@dataclass
class ParetoSolution:
    """A Pareto optimal solution"""
    weights: Dict[str, float]  # Analyzer weights
    objectives: Dict[str, float]  # Objective values
    fitness: np.ndarray
    is_selected: bool = False
    
    @property
    def summary(self) -> str:
        """Human-readable summary"""
        obj_str = ", ".join([f"{k}={v:.2f}" for k, v in self.objectives.items()])
        return f"Solution: {obj_str}"


class ColonyHealthProblem(Problem):
    """
    Multi-objective optimization problem for colony health.
    
    Decision variables: Weights for each analyzer
    Objectives: Security, Performance, Coverage (max), Complexity, Duplication (min)
    Constraints: Sum of weights = 1.0
    """
    
    def __init__(self, analyzer_results: Dict[str, Dict[str, Any]]):
        """
        Initialize problem with analyzer results.
        
        Args:
            analyzer_results: Dict of analyzer_name -> metrics
        """
        self.analyzers = list(analyzer_results.keys())
        self.analyzer_results = analyzer_results
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Define objectives
        self.objectives = [
            OptimizationObjective("security_score", "maximize"),
            OptimizationObjective("performance_score", "maximize"),
            OptimizationObjective("test_coverage", "maximize"),
            OptimizationObjective("code_complexity", "minimize"),
            OptimizationObjective("duplication_ratio", "minimize"),
        ]
        
        # Problem dimensions
        n_var = len(self.analyzers)  # One weight per analyzer
        n_obj = len(self.objectives)  # Number of objectives
        n_constr = 1  # Sum of weights = 1
        
        super().__init__(
            n_var=n_var,
            n_obj=n_obj,
            n_constr=n_constr,
            xl=0.1,  # Min weight per analyzer
            xu=0.9,  # Max weight per analyzer
        )
        
    def _evaluate(self, x, out, *args, **kwargs):
        """
        Evaluate objective functions for given weights.
        
        Args:
            x: Population of weight configurations (n_pop x n_var)
        """
        n_pop = x.shape[0]
        objectives = np.zeros((n_pop, self.n_obj))
        constraints = np.zeros((n_pop, self.n_constr))
        
        for i in range(n_pop):
            weights = x[i]
            
            # Normalize weights to sum to 1
            weights_norm = weights / weights.sum()
            
            # Calculate weighted objectives
            obj_values = self._calculate_objectives(weights_norm)
            
            # Convert maximization to minimization (pymoo minimizes by default)
            for j, obj in enumerate(self.objectives):
                if obj.direction == "maximize":
                    objectives[i, j] = -obj_values[j]  # Negate for maximization
                else:
                    objectives[i, j] = obj_values[j]
                    
            # Constraint: sum of weights should be close to 1
            constraints[i, 0] = abs(weights_norm.sum() - 1.0) - 0.01
            
        out["F"] = objectives
        out["G"] = constraints
        
    def _calculate_objectives(self, weights: np.ndarray) -> np.ndarray:
        """Calculate objective values for given analyzer weights"""
        obj_values = np.zeros(len(self.objectives))
        
        # Security score (from SecurityAnalyzer)
        if "SecurityAnalyzer" in self.analyzer_results:
            security = self.analyzer_results["SecurityAnalyzer"].get("security_score", 50)
            obj_values[0] = security * weights[self.analyzers.index("SecurityAnalyzer")]
        
        # Performance score (from PerformanceAnalyzer)
        if "PerformanceAnalyzer" in self.analyzer_results:
            performance = self.analyzer_results["PerformanceAnalyzer"].get("performance_score", 50)
            obj_values[1] = performance * weights[self.analyzers.index("PerformanceAnalyzer")]
            
        # Test coverage (from TestCoverageAnalyzer)
        if "TestCoverageAnalyzer" in self.analyzer_results:
            coverage = self.analyzer_results["TestCoverageAnalyzer"].get("coverage_report", {}).get("total_coverage", 0)
            obj_values[2] = coverage * weights[self.analyzers.index("TestCoverageAnalyzer")]
            
        # Code complexity (from CodeAnalyzer)
        if "CodeAnalyzer" in self.analyzer_results:
            complexity = self.analyzer_results["CodeAnalyzer"].get("average_complexity", 10)
            # Normalize complexity (lower is better)
            obj_values[3] = complexity * weights[self.analyzers.index("CodeAnalyzer")]
            
        # Duplication ratio (from CodeEmbeddingAnalyzer)
        if "CodeEmbeddingAnalyzer" in self.analyzer_results:
            duplication = self.analyzer_results["CodeEmbeddingAnalyzer"].get("duplication_ratio", 0.1)
            obj_values[4] = duplication * 100 * weights[self.analyzers.index("CodeEmbeddingAnalyzer")]
            
        return obj_values


class ParetoHealthOptimizer:
    """
    Optimizer for finding Pareto-optimal analyzer weight configurations.
    
    Uses NSGA-III for many-objective optimization (>3 objectives).
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.problem: Optional[ColonyHealthProblem] = None
        self.solutions: List[ParetoSolution] = []
        
    def optimize(self, 
                analyzer_results: Dict[str, Dict[str, Any]], 
                n_gen: int = 100,
                pop_size: int = 100,
                algorithm: str = "nsga3") -> List[ParetoSolution]:
        """
        Find Pareto-optimal weight configurations.
        
        Args:
            analyzer_results: Results from all analyzers
            n_gen: Number of generations
            pop_size: Population size
            algorithm: Algorithm to use ('nsga2' or 'nsga3')
            
        Returns:
            List of Pareto-optimal solutions
        """
        self.logger.info(f"Starting Pareto optimization with {algorithm.upper()}")
        
        # Create problem
        self.problem = ColonyHealthProblem(analyzer_results)
        
        # Select algorithm
        if algorithm == "nsga3":
            # Reference directions for NSGA-III
            ref_dirs = get_reference_directions("das-dennis", self.problem.n_obj, n_partitions=12)
            algo = NSGA3(
                pop_size=pop_size,
                ref_dirs=ref_dirs,
                sampling=FloatRandomSampling(),
                crossover=SBX(prob=0.9, eta=15),
                mutation=PM(prob=1.0/self.problem.n_var, eta=20),
                eliminate_duplicates=True,
            )
        else:  # nsga2
            algo = NSGA2(
                pop_size=pop_size,
                sampling=FloatRandomSampling(),
                crossover=SBX(prob=0.9, eta=15),
                mutation=PM(prob=1.0/self.problem.n_var, eta=20),
                eliminate_duplicates=True,
            )
            
        # Termination criterion
        termination = get_termination("n_gen", n_gen)
        
        # Optimize
        self.logger.info(f"Running optimization for {n_gen} generations...")
        res = minimize(
            self.problem,
            algo,
            termination,
            seed=42,
            save_history=True,
            verbose=False,
        )
        
        # Extract Pareto solutions
        self.solutions = self._extract_solutions(res)
        self.logger.info(f"Found {len(self.solutions)} Pareto-optimal solutions")
        
        return self.solutions
        
    def _extract_solutions(self, result) -> List[ParetoSolution]:
        """Extract Pareto solutions from optimization result"""
        solutions = []
        
        if result.X is None:
            return solutions
            
        # Handle both single and multiple solutions
        X = result.X if result.X.ndim == 2 else result.X.reshape(1, -1)
        F = result.F if result.F.ndim == 2 else result.F.reshape(1, -1)
        
        for i in range(X.shape[0]):
            weights_array = X[i]
            weights_norm = weights_array / weights_array.sum()
            
            # Create weight dictionary
            weights = {
                analyzer: float(weights_norm[j]) 
                for j, analyzer in enumerate(self.problem.analyzers)
            }
            
            # Calculate actual objective values (not negated)
            obj_values = self.problem._calculate_objectives(weights_norm)
            objectives = {
                self.problem.objectives[j].name: float(obj_values[j])
                for j in range(len(self.problem.objectives))
            }
            
            solution = ParetoSolution(
                weights=weights,
                objectives=objectives,
                fitness=F[i],
            )
            solutions.append(solution)
            
        return solutions
        
    def select_balanced_solution(self) -> Optional[ParetoSolution]:
        """Select the most balanced solution (closest to ideal point)"""
        if not self.solutions:
            return None
            
        # Find solution closest to ideal point (all objectives optimized)
        ideal_point = np.zeros(self.problem.n_obj)
        for i, obj in enumerate(self.problem.objectives):
            if obj.direction == "maximize":
                ideal_point[i] = -100  # Negated max
            else:
                ideal_point[i] = 0  # Min
                
        # Calculate distances to ideal point
        distances = []
        for sol in self.solutions:
            dist = np.linalg.norm(sol.fitness - ideal_point)
            distances.append(dist)
            
        # Select closest
        best_idx = np.argmin(distances)
        selected = self.solutions[best_idx]
        selected.is_selected = True
        
        self.logger.info(f"Selected balanced solution: {selected.summary}")
        return selected
        
    def get_trade_off_data(self) -> Dict[str, List[float]]:
        """Get data for trade-off visualization"""
        if not self.solutions:
            return {}
            
        data = {obj.name: [] for obj in self.problem.objectives}
        data["solution_id"] = []
        
        for i, sol in enumerate(self.solutions):
            data["solution_id"].append(i)
            for obj_name, obj_value in sol.objectives.items():
                data[obj_name].append(obj_value)
                
        return data
        
    def export_solutions(self, filepath: str):
        """Export solutions to JSON"""
        import json
        
        export_data = {
            "solutions": [
                {
                    "id": i,
                    "weights": sol.weights,
                    "objectives": sol.objectives,
                    "is_selected": sol.is_selected,
                }
                for i, sol in enumerate(self.solutions)
            ],
            "problem": {
                "analyzers": self.problem.analyzers if self.problem else [],
                "objectives": [
                    {"name": obj.name, "direction": obj.direction}
                    for obj in (self.problem.objectives if self.problem else [])
                ],
            },
        }
        
        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)
            
        self.logger.info(f"Exported {len(self.solutions)} solutions to {filepath}")