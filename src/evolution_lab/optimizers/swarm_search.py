"""
SwarmSearchCV - Particle Swarm Optimization for Hyperparameter Tuning
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

Uses swarm intelligence for efficient hyperparameter search in ML models.
"""
import numpy as np
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass
import json
from pathlib import Path
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed
import warnings
from sklearn.model_selection import cross_val_score
from sklearn.base import BaseEstimator, clone
import time


@dataclass
class Particle:
    """
    Represents a particle in the swarm.
    
    Each particle has:
    - position: Current hyperparameter values
    - velocity: Rate of change in position
    - best_position: Best position found by this particle
    - best_score: Best score achieved by this particle
    """
    position: np.ndarray
    velocity: np.ndarray
    best_position: np.ndarray
    best_score: float
    current_score: float = -np.inf
    
    def update_best(self, score: float) -> None:
        """Update personal best if new score is better"""
        if score > self.best_score:
            self.best_score = score
            self.best_position = self.position.copy()


@dataclass 
class SearchSpace:
    """
    Defines the hyperparameter search space.
    
    Supports:
    - Continuous parameters (uniform, log-uniform)
    - Integer parameters
    - Categorical parameters
    """
    def __init__(self, param_distributions: Dict[str, Any]):
        """
        Initialize search space.
        
        Args:
            param_distributions: Dict mapping parameter names to distributions
                - tuple (min, max): Continuous uniform
                - tuple (min, max, 'log'): Log-uniform
                - list: Categorical choices
                - tuple (min, max, 'int'): Integer range
        """
        self.param_distributions = param_distributions
        self.param_names = list(param_distributions.keys())
        self.n_params = len(self.param_names)
        
        # Parse parameter types and bounds
        self.param_types = {}
        self.param_bounds = {}
        self.param_choices = {}
        
        for name, dist in param_distributions.items():
            if isinstance(dist, list):
                # Categorical
                self.param_types[name] = 'categorical'
                self.param_choices[name] = dist
                self.param_bounds[name] = (0, len(dist) - 1)
            elif isinstance(dist, tuple) and len(dist) == 3:
                if dist[2] == 'log':
                    # Log-uniform
                    self.param_types[name] = 'log'
                    self.param_bounds[name] = (np.log(dist[0]), np.log(dist[1]))
                elif dist[2] == 'int':
                    # Integer
                    self.param_types[name] = 'int'
                    self.param_bounds[name] = (dist[0], dist[1])
            else:
                # Continuous uniform
                self.param_types[name] = 'continuous'
                self.param_bounds[name] = dist
                
    def sample_random(self) -> np.ndarray:
        """Sample random point from search space"""
        point = np.zeros(self.n_params)
        
        for i, name in enumerate(self.param_names):
            bounds = self.param_bounds[name]
            
            if self.param_types[name] == 'categorical':
                point[i] = np.random.randint(bounds[0], bounds[1] + 1)
            else:
                point[i] = np.random.uniform(bounds[0], bounds[1])
                
        return point
    
    def position_to_params(self, position: np.ndarray) -> Dict[str, Any]:
        """Convert particle position to parameter dict"""
        params = {}
        
        for i, name in enumerate(self.param_names):
            value = position[i]
            
            if self.param_types[name] == 'categorical':
                # Map to categorical choice
                idx = int(np.clip(value, 0, len(self.param_choices[name]) - 1))
                params[name] = self.param_choices[name][idx]
            elif self.param_types[name] == 'log':
                # Convert from log space
                params[name] = np.exp(value)
            elif self.param_types[name] == 'int':
                # Round to integer
                params[name] = int(np.round(value))
            else:
                # Continuous
                params[name] = value
                
        return params
    
    def clip_position(self, position: np.ndarray) -> np.ndarray:
        """Clip position to valid bounds"""
        clipped = position.copy()
        
        for i, name in enumerate(self.param_names):
            bounds = self.param_bounds[name]
            clipped[i] = np.clip(clipped[i], bounds[0], bounds[1])
            
        return clipped


class SwarmSearchCV:
    """
    Particle Swarm Optimization for hyperparameter tuning.
    
    Features:
    - Adaptive inertia weight
    - Social and cognitive learning
    - Early stopping
    - Parallel evaluation
    - Convergence tracking
    - Multi-metric support
    """
    
    def __init__(
        self,
        estimator: BaseEstimator,
        param_distributions: Dict[str, Any],
        n_particles: int = 30,
        n_iterations: int = 50,
        cv: int = 5,
        scoring: Optional[Union[str, Callable]] = None,
        n_jobs: int = -1,
        w_start: float = 0.9,
        w_end: float = 0.4,
        c1: float = 2.0,
        c2: float = 2.0,
        early_stopping: bool = True,
        patience: int = 10,
        verbose: int = 0,
        random_state: Optional[int] = None
    ):
        """
        Initialize SwarmSearchCV.
        
        Args:
            estimator: Scikit-learn estimator to tune
            param_distributions: Parameter search space
            n_particles: Number of particles in swarm
            n_iterations: Maximum iterations
            cv: Cross-validation folds
            scoring: Scoring metric (default: estimator's score)
            n_jobs: Parallel jobs (-1 for all cores)
            w_start: Initial inertia weight
            w_end: Final inertia weight
            c1: Cognitive component weight
            c2: Social component weight
            early_stopping: Enable early stopping
            patience: Iterations without improvement before stopping
            verbose: Verbosity level (0-2)
            random_state: Random seed
        """
        self.estimator = estimator
        self.param_distributions = param_distributions
        self.n_particles = n_particles
        self.n_iterations = n_iterations
        self.cv = cv
        self.scoring = scoring
        self.n_jobs = n_jobs
        self.w_start = w_start
        self.w_end = w_end
        self.c1 = c1
        self.c2 = c2
        self.early_stopping = early_stopping
        self.patience = patience
        self.verbose = verbose
        self.random_state = random_state
        
        # Results
        self.best_params_ = None
        self.best_score_ = -np.inf
        self.best_estimator_ = None
        self.cv_results_ = {}
        self.convergence_history_ = []
        
        # Set random seed
        if random_state is not None:
            np.random.seed(random_state)
            
    def _evaluate_particle(
        self, 
        position: np.ndarray, 
        X, 
        y,
        search_space: SearchSpace
    ) -> float:
        """Evaluate a particle's position"""
        # Convert position to parameters
        params = search_space.position_to_params(position)
        
        # Clone estimator and set parameters
        estimator = clone(self.estimator)
        estimator.set_params(**params)
        
        # Perform cross-validation
        try:
            scores = cross_val_score(
                estimator, X, y, 
                cv=self.cv, 
                scoring=self.scoring,
                n_jobs=1  # Parallelism at swarm level
            )
            return scores.mean()
        except Exception as e:
            if self.verbose > 1:
                print(f"Error evaluating {params}: {e}")
            return -np.inf
            
    def _evaluate_swarm(
        self, 
        particles: List[Particle], 
        X, 
        y,
        search_space: SearchSpace
    ) -> None:
        """Evaluate all particles in parallel"""
        if self.n_jobs == 1:
            # Sequential evaluation
            for particle in particles:
                score = self._evaluate_particle(particle.position, X, y, search_space)
                particle.current_score = score
                particle.update_best(score)
        else:
            # Parallel evaluation
            n_jobs = self.n_jobs if self.n_jobs > 0 else None
            
            with ProcessPoolExecutor(max_workers=n_jobs) as executor:
                # Submit all evaluations
                future_to_particle = {
                    executor.submit(
                        self._evaluate_particle, 
                        particle.position, 
                        X, 
                        y,
                        search_space
                    ): particle
                    for particle in particles
                }
                
                # Collect results
                for future in as_completed(future_to_particle):
                    particle = future_to_particle[future]
                    try:
                        score = future.result()
                        particle.current_score = score
                        particle.update_best(score)
                    except Exception as e:
                        if self.verbose > 0:
                            print(f"Evaluation failed: {e}")
                        particle.current_score = -np.inf
                        
    def _update_velocity(
        self,
        particle: Particle,
        global_best_position: np.ndarray,
        w: float
    ) -> np.ndarray:
        """Update particle velocity using PSO equations"""
        # Random factors
        r1 = np.random.rand(len(particle.position))
        r2 = np.random.rand(len(particle.position))
        
        # Cognitive component (personal best)
        cognitive = self.c1 * r1 * (particle.best_position - particle.position)
        
        # Social component (global best)
        social = self.c2 * r2 * (global_best_position - particle.position)
        
        # Update velocity
        new_velocity = w * particle.velocity + cognitive + social
        
        return new_velocity
        
    def fit(self, X, y):
        """
        Fit the SwarmSearchCV.
        
        Args:
            X: Training features
            y: Training targets
            
        Returns:
            self: Fitted SwarmSearchCV instance
        """
        start_time = time.time()
        
        # Initialize search space
        search_space = SearchSpace(self.param_distributions)
        
        # Initialize swarm
        particles = []
        for _ in range(self.n_particles):
            position = search_space.sample_random()
            velocity = np.random.randn(search_space.n_params) * 0.1
            
            particle = Particle(
                position=position,
                velocity=velocity,
                best_position=position.copy(),
                best_score=-np.inf
            )
            particles.append(particle)
            
        # Initial evaluation
        if self.verbose > 0:
            print("Initializing swarm...")
        self._evaluate_swarm(particles, X, y, search_space)
        
        # Find initial global best
        global_best_particle = max(particles, key=lambda p: p.best_score)
        global_best_position = global_best_particle.best_position.copy()
        global_best_score = global_best_particle.best_score
        
        # Track convergence
        self.convergence_history_ = [global_best_score]
        iterations_without_improvement = 0
        
        # Main PSO loop
        for iteration in range(self.n_iterations):
            # Adaptive inertia weight
            w = self.w_start - (self.w_start - self.w_end) * iteration / self.n_iterations
            
            # Update particles
            for particle in particles:
                # Update velocity
                particle.velocity = self._update_velocity(
                    particle, global_best_position, w
                )
                
                # Update position
                particle.position = particle.position + particle.velocity
                
                # Clip to bounds
                particle.position = search_space.clip_position(particle.position)
                
            # Evaluate new positions
            self._evaluate_swarm(particles, X, y, search_space)
            
            # Update global best
            best_particle = max(particles, key=lambda p: p.best_score)
            if best_particle.best_score > global_best_score:
                global_best_score = best_particle.best_score
                global_best_position = best_particle.best_position.copy()
                iterations_without_improvement = 0
            else:
                iterations_without_improvement += 1
                
            # Track convergence
            self.convergence_history_.append(global_best_score)
            
            # Verbose output
            if self.verbose > 0:
                print(f"Iteration {iteration + 1}/{self.n_iterations}: "
                      f"Best Score = {global_best_score:.4f}")
                
            # Early stopping
            if self.early_stopping and iterations_without_improvement >= self.patience:
                if self.verbose > 0:
                    print(f"Early stopping at iteration {iteration + 1}")
                break
                
        # Store results
        self.best_score_ = global_best_score
        self.best_params_ = search_space.position_to_params(global_best_position)
        
        # Fit best estimator - only with valid parameters
        self.best_estimator_ = clone(self.estimator)
        
        # Filter out invalid parameters
        valid_params = self.best_estimator_.get_params()
        filtered_params = {
            k: v for k, v in self.best_params_.items() 
            if k in valid_params
        }
        
        self.best_estimator_.set_params(**filtered_params)
        self.best_estimator_.fit(X, y)
        
        # Compile cv_results_
        self._compile_cv_results(particles, search_space)
        
        # Total time
        self.refit_time_ = time.time() - start_time
        
        return self
        
    def _compile_cv_results(self, particles: List[Particle], search_space: SearchSpace):
        """Compile cross-validation results"""
        n_candidates = len(particles)
        
        # Initialize result arrays
        self.cv_results_ = {
            'mean_test_score': np.zeros(n_candidates),
            'std_test_score': np.zeros(n_candidates),
            'params': [],
            'rank_test_score': np.zeros(n_candidates, dtype=int)
        }
        
        # Add parameter columns
        for param_name in search_space.param_names:
            self.cv_results_[f'param_{param_name}'] = []
            
        # Fill results
        for i, particle in enumerate(particles):
            params = search_space.position_to_params(particle.best_position)
            
            self.cv_results_['mean_test_score'][i] = particle.best_score
            self.cv_results_['params'].append(params)
            
            for param_name, param_value in params.items():
                self.cv_results_[f'param_{param_name}'].append(param_value)
                
        # Rank results
        scores = self.cv_results_['mean_test_score']
        ranks = (-scores).argsort().argsort() + 1
        self.cv_results_['rank_test_score'] = ranks
        
    def predict(self, X):
        """Predict using best estimator"""
        if self.best_estimator_ is None:
            raise ValueError("Must call fit before predict")
        return self.best_estimator_.predict(X)
        
    def score(self, X, y):
        """Score using best estimator"""
        if self.best_estimator_ is None:
            raise ValueError("Must call fit before score")
        return self.best_estimator_.score(X, y)
        
    def plot_convergence(self, save_path: Optional[str] = None):
        """Plot convergence history"""
        if not self.convergence_history_:
            raise ValueError("No convergence history available. Call fit first.")
            
        plt.figure(figsize=(10, 6))
        plt.plot(self.convergence_history_, 'b-', linewidth=2)
        plt.xlabel('Iteration')
        plt.ylabel('Best Score')
        plt.title('PSO Convergence History')
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        else:
            plt.show()
            
        plt.close()
        
    def get_particle_positions(self) -> Dict[str, List[float]]:
        """Get all particle positions for visualization"""
        if not hasattr(self, '_final_particles'):
            return {}
            
        search_space = SearchSpace(self.param_distributions)
        positions = {name: [] for name in search_space.param_names}
        
        for particle in self._final_particles:
            params = search_space.position_to_params(particle.position)
            for name, value in params.items():
                positions[name].append(value)
                
        return positions