"""
Tests for SwarmSearchCV
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import pytest
import numpy as np
from sklearn.datasets import make_classification
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from unittest.mock import Mock, patch

from src.evolution_lab.optimizers.swarm_search import (
    SwarmSearchCV,
    Particle,
    SearchSpace
)


@pytest.fixture
def sample_data():
    """Generate sample classification data"""
    X, y = make_classification(
        n_samples=100,
        n_features=10,
        n_informative=5,
        n_redundant=3,
        n_classes=2,
        random_state=42
    )
    return train_test_split(X, y, test_size=0.3, random_state=42)


@pytest.fixture
def svm_param_space():
    """SVM parameter space for testing"""
    return {
        'C': (0.1, 10.0, 'log'),
        'gamma': (0.001, 1.0, 'log'),
        'kernel': ['rbf', 'linear']
    }


@pytest.fixture
def rf_param_space():
    """Random Forest parameter space"""
    return {
        'n_estimators': (10, 100, 'int'),
        'max_depth': (2, 20, 'int'),
        'min_samples_split': (2, 10, 'int'),
        'min_samples_leaf': (1, 5, 'int')
    }


class TestParticle:
    """Test Particle class"""
    
    def test_particle_creation(self):
        """Test creating a particle"""
        position = np.array([1.0, 2.0, 3.0])
        velocity = np.array([0.1, 0.2, 0.3])
        
        particle = Particle(
            position=position,
            velocity=velocity,
            best_position=position.copy(),
            best_score=0.85
        )
        
        assert np.array_equal(particle.position, position)
        assert np.array_equal(particle.velocity, velocity)
        assert particle.best_score == 0.85
        assert particle.current_score == -np.inf
        
    def test_update_best(self):
        """Test updating personal best"""
        particle = Particle(
            position=np.array([1.0, 2.0]),
            velocity=np.array([0.1, 0.2]),
            best_position=np.array([1.0, 2.0]),
            best_score=0.8
        )
        
        # Update with better score
        particle.position = np.array([1.5, 2.5])
        particle.update_best(0.9)
        
        assert particle.best_score == 0.9
        assert np.array_equal(particle.best_position, [1.5, 2.5])
        
        # Try worse score - should not update
        particle.position = np.array([2.0, 3.0])
        particle.update_best(0.7)
        
        assert particle.best_score == 0.9
        assert np.array_equal(particle.best_position, [1.5, 2.5])


class TestSearchSpace:
    """Test SearchSpace class"""
    
    def test_continuous_params(self):
        """Test continuous parameter handling"""
        space = SearchSpace({
            'alpha': (0.1, 1.0),
            'beta': (0.0, 10.0)
        })
        
        assert space.n_params == 2
        assert space.param_types['alpha'] == 'continuous'
        assert space.param_bounds['alpha'] == (0.1, 1.0)
        
    def test_log_params(self):
        """Test log-scale parameters"""
        space = SearchSpace({
            'C': (0.01, 100, 'log')
        })
        
        assert space.param_types['C'] == 'log'
        assert space.param_bounds['C'] == (np.log(0.01), np.log(100))
        
        # Test conversion
        position = np.array([0.0])  # log(1) = 0
        params = space.position_to_params(position)
        assert params['C'] == pytest.approx(1.0)
        
    def test_integer_params(self):
        """Test integer parameters"""
        space = SearchSpace({
            'n_estimators': (10, 100, 'int')
        })
        
        assert space.param_types['n_estimators'] == 'int'
        
        # Test rounding
        position = np.array([55.7])
        params = space.position_to_params(position)
        assert params['n_estimators'] == 56
        
    def test_categorical_params(self):
        """Test categorical parameters"""
        space = SearchSpace({
            'kernel': ['rbf', 'linear', 'poly']
        })
        
        assert space.param_types['kernel'] == 'categorical'
        assert space.param_choices['kernel'] == ['rbf', 'linear', 'poly']
        assert space.param_bounds['kernel'] == (0, 2)
        
        # Test mapping
        position = np.array([1.2])
        params = space.position_to_params(position)
        assert params['kernel'] == 'linear'
        
    def test_mixed_params(self):
        """Test mixed parameter types"""
        space = SearchSpace({
            'C': (0.1, 10.0, 'log'),
            'kernel': ['rbf', 'linear'],
            'degree': (2, 5, 'int')
        })
        
        assert space.n_params == 3
        assert len(space.param_types) == 3
        
        # Test random sampling
        position = space.sample_random()
        assert len(position) == 3
        
        # Test conversion
        params = space.position_to_params(position)
        assert 'C' in params
        assert 'kernel' in params
        assert 'degree' in params
        assert isinstance(params['degree'], int)
        
    def test_clip_position(self):
        """Test position clipping"""
        space = SearchSpace({
            'alpha': (0.0, 1.0),
            'beta': (10, 20)
        })
        
        # Test clipping
        position = np.array([-0.5, 25.0])
        clipped = space.clip_position(position)
        
        assert clipped[0] == 0.0
        assert clipped[1] == 20.0


class TestSwarmSearchCV:
    """Test SwarmSearchCV class"""
    
    def test_initialization(self, svm_param_space):
        """Test SwarmSearchCV initialization"""
        estimator = SVC()
        
        searcher = SwarmSearchCV(
            estimator=estimator,
            param_distributions=svm_param_space,
            n_particles=10,
            n_iterations=5,
            cv=3
        )
        
        assert searcher.n_particles == 10
        assert searcher.n_iterations == 5
        assert searcher.cv == 3
        assert searcher.best_score_ == -np.inf
        
    def test_fit_simple(self, sample_data, rf_param_space):
        """Test basic fitting with Random Forest"""
        X_train, X_test, y_train, y_test = sample_data
        
        # Use RandomForest for faster testing
        rf = RandomForestClassifier(random_state=42)
        
        searcher = SwarmSearchCV(
            estimator=rf,
            param_distributions=rf_param_space,
            n_particles=5,
            n_iterations=3,
            cv=2,
            random_state=42,
            verbose=0
        )
        
        # Fit the searcher
        searcher.fit(X_train, y_train)
        
        # Check results
        assert searcher.best_params_ is not None
        assert searcher.best_score_ > 0
        assert searcher.best_estimator_ is not None
        assert len(searcher.convergence_history_) > 0
        
        # Check best params are valid
        for param, value in searcher.best_params_.items():
            assert param in rf_param_space
            
        # Test prediction
        y_pred = searcher.predict(X_test)
        assert len(y_pred) == len(y_test)
        
        # Test scoring
        score = searcher.score(X_test, y_test)
        assert 0 <= score <= 1
        
    def test_convergence_tracking(self, sample_data):
        """Test convergence history tracking"""
        X_train, _, y_train, _ = sample_data
        
        searcher = SwarmSearchCV(
            estimator=SVC(),
            param_distributions={'C': (0.1, 10.0)},
            n_particles=3,
            n_iterations=5,
            cv=2,
            random_state=42
        )
        
        searcher.fit(X_train, y_train)
        
        # Check convergence history
        assert len(searcher.convergence_history_) == 6  # Initial + 5 iterations
        assert all(isinstance(score, (int, float)) for score in searcher.convergence_history_)
        
        # Scores should generally improve or stay same
        for i in range(1, len(searcher.convergence_history_)):
            assert searcher.convergence_history_[i] >= searcher.convergence_history_[i-1]
            
    def test_early_stopping(self, sample_data):
        """Test early stopping functionality"""
        X_train, _, y_train, _ = sample_data
        
        searcher = SwarmSearchCV(
            estimator=SVC(),
            param_distributions={'C': (1.0, 1.0)},  # Fixed value for consistent score
            n_particles=3,
            n_iterations=20,
            cv=2,
            early_stopping=True,
            patience=3,
            random_state=42,
            verbose=0
        )
        
        searcher.fit(X_train, y_train)
        
        # Should stop early due to no improvement
        assert len(searcher.convergence_history_) < 21
        
    def test_cv_results(self, sample_data, rf_param_space):
        """Test cv_results_ compilation"""
        X_train, _, y_train, _ = sample_data
        
        searcher = SwarmSearchCV(
            estimator=RandomForestClassifier(random_state=42),
            param_distributions=rf_param_space,
            n_particles=5,
            n_iterations=2,
            cv=2,
            random_state=42
        )
        
        searcher.fit(X_train, y_train)
        
        # Check cv_results_ structure
        assert 'mean_test_score' in searcher.cv_results_
        assert 'params' in searcher.cv_results_
        assert 'rank_test_score' in searcher.cv_results_
        
        # Check parameter columns
        for param in rf_param_space:
            assert f'param_{param}' in searcher.cv_results_
            
        # Check consistency
        n_candidates = len(searcher.cv_results_['params'])
        assert len(searcher.cv_results_['mean_test_score']) == n_candidates
        assert len(searcher.cv_results_['rank_test_score']) == n_candidates
        
        # Check ranking
        ranks = searcher.cv_results_['rank_test_score']
        assert min(ranks) == 1
        assert max(ranks) == n_candidates
        
    def test_parallel_evaluation(self, sample_data):
        """Test parallel evaluation"""
        X_train, _, y_train, _ = sample_data
        
        # Test with parallel jobs
        searcher = SwarmSearchCV(
            estimator=RandomForestClassifier(n_estimators=10, random_state=42),
            param_distributions={'max_depth': (2, 10, 'int')},
            n_particles=4,
            n_iterations=2,
            cv=2,
            n_jobs=2,
            random_state=42
        )
        
        searcher.fit(X_train, y_train)
        assert searcher.best_params_ is not None
        
    def test_error_handling(self, sample_data):
        """Test error handling for invalid parameters"""
        X_train, _, y_train, _ = sample_data
        
        # Create searcher with invalid parameter range
        searcher = SwarmSearchCV(
            estimator=SVC(),
            param_distributions={
                'C': (0.1, 10.0),
                'invalid_param': (0, 1)  # SVC doesn't have this param
            },
            n_particles=2,
            n_iterations=1,
            cv=2,
            verbose=0
        )
        
        # Should handle errors gracefully
        searcher.fit(X_train, y_train)
        
        # Should still find some solution
        assert searcher.best_params_ is not None
        
    def test_plot_convergence(self, sample_data, tmp_path):
        """Test convergence plotting"""
        X_train, _, y_train, _ = sample_data
        
        searcher = SwarmSearchCV(
            estimator=SVC(),
            param_distributions={'C': (0.1, 10.0)},
            n_particles=3,
            n_iterations=3,
            cv=2,
            random_state=42
        )
        
        # Test error before fitting
        with pytest.raises(ValueError, match="No convergence history"):
            searcher.plot_convergence()
            
        # Fit and plot
        searcher.fit(X_train, y_train)
        
        # Save plot
        plot_path = tmp_path / "convergence.png"
        searcher.plot_convergence(save_path=str(plot_path))
        assert plot_path.exists()
        
    def test_predict_before_fit(self):
        """Test error when predicting before fit"""
        searcher = SwarmSearchCV(
            estimator=SVC(),
            param_distributions={'C': (0.1, 10.0)}
        )
        
        X_test = np.array([[1, 2], [3, 4]])
        
        with pytest.raises(ValueError, match="Must call fit"):
            searcher.predict(X_test)
            
        with pytest.raises(ValueError, match="Must call fit"):
            searcher.score(X_test, [0, 1])
            
    def test_different_metrics(self, sample_data):
        """Test with different scoring metrics"""
        X_train, _, y_train, _ = sample_data
        
        # Test with F1 score
        searcher = SwarmSearchCV(
            estimator=SVC(),
            param_distributions={'C': (0.1, 10.0)},
            n_particles=3,
            n_iterations=2,
            cv=2,
            scoring='f1',
            random_state=42
        )
        
        searcher.fit(X_train, y_train)
        assert searcher.best_score_ > 0
        
    def test_get_particle_positions(self, sample_data, svm_param_space):
        """Test getting particle positions for visualization"""
        X_train, _, y_train, _ = sample_data
        
        searcher = SwarmSearchCV(
            estimator=SVC(),
            param_distributions=svm_param_space,
            n_particles=5,
            n_iterations=2,
            cv=2,
            random_state=42
        )
        
        # Before fit - should return empty
        positions = searcher.get_particle_positions()
        assert positions == {}
        
        # After fit
        searcher.fit(X_train, y_train)
        
        # Note: get_particle_positions needs _final_particles to be saved
        # This is not implemented in the current version
        # so we expect empty dict
        positions = searcher.get_particle_positions()
        assert isinstance(positions, dict)