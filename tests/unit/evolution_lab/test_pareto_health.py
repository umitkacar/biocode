"""
Tests for Pareto Health Optimizer
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch

from src.evolution_lab.optimizers.pareto_health import (
    ParetoHealthOptimizer, 
    ColonyHealthProblem,
    OptimizationObjective,
    ParetoSolution
)


@pytest.fixture
def sample_analyzer_results():
    """Sample analyzer results for testing"""
    return {
        "SecurityAnalyzer": {
            "security_score": 85.0,
            "vulnerabilities": [],
        },
        "PerformanceAnalyzer": {
            "performance_score": 72.5,
            "bottlenecks": 3,
        },
        "TestCoverageAnalyzer": {
            "coverage_report": {
                "total_coverage": 65.0,
                "line_coverage": 70.0,
            }
        },
        "CodeAnalyzer": {
            "average_complexity": 8.5,
            "total_lines": 1000,
        },
        "CodeEmbeddingAnalyzer": {
            "duplication_ratio": 0.15,
            "total_clones": 25,
        }
    }


class TestOptimizationObjective:
    """Test OptimizationObjective class"""
    
    def test_objective_creation(self):
        """Test creating an objective"""
        obj = OptimizationObjective("security", "maximize")
        assert obj.name == "security"
        assert obj.direction == "maximize"
        assert obj.weight_range == (0.0, 1.0)
        assert obj.current_value == 0.0
        
    def test_normalize(self):
        """Test value normalization"""
        obj = OptimizationObjective("test", "maximize")
        
        # Test normal case
        assert obj.normalize(50, 0, 100) == 0.5
        assert obj.normalize(0, 0, 100) == 0.0
        assert obj.normalize(100, 0, 100) == 1.0
        
        # Test edge cases
        assert obj.normalize(75, 50, 100) == 0.5


class TestColonyHealthProblem:
    """Test ColonyHealthProblem class"""
    
    def test_problem_initialization(self, sample_analyzer_results):
        """Test problem setup"""
        problem = ColonyHealthProblem(sample_analyzer_results)
        
        assert len(problem.analyzers) == 5
        assert problem.n_var == 5  # One weight per analyzer
        assert problem.n_obj == 5  # Five objectives
        assert problem.n_constr == 1  # Sum constraint
        assert (problem.xl == 0.1).all()  # Min weight
        assert (problem.xu == 0.9).all()  # Max weight
        
    def test_calculate_objectives(self, sample_analyzer_results):
        """Test objective calculation"""
        problem = ColonyHealthProblem(sample_analyzer_results)
        
        # Equal weights
        weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
        objectives = problem._calculate_objectives(weights)
        
        assert len(objectives) == 5
        # Security: 85 * 0.2 = 17
        assert objectives[0] == pytest.approx(17.0, rel=0.01)
        # Performance: 72.5 * 0.2 = 14.5
        assert objectives[1] == pytest.approx(14.5, rel=0.01)
        # Coverage: 65 * 0.2 = 13
        assert objectives[2] == pytest.approx(13.0, rel=0.01)
        # Complexity: 8.5 * 0.2 = 1.7
        assert objectives[3] == pytest.approx(1.7, rel=0.01)
        # Duplication: 0.15 * 100 * 0.2 = 3
        assert objectives[4] == pytest.approx(3.0, rel=0.01)
        
    def test_evaluate(self, sample_analyzer_results):
        """Test evaluation function"""
        problem = ColonyHealthProblem(sample_analyzer_results)
        
        # Test with single solution
        x = np.array([[0.3, 0.2, 0.2, 0.2, 0.1]])
        out = {}
        problem._evaluate(x, out)
        
        assert "F" in out  # Objectives
        assert "G" in out  # Constraints
        assert out["F"].shape == (1, 5)
        assert out["G"].shape == (1, 1)
        
        # Check constraint (sum = 1)
        assert out["G"][0, 0] <= 0  # Feasible


class TestParetoSolution:
    """Test ParetoSolution class"""
    
    def test_solution_creation(self):
        """Test creating a solution"""
        weights = {"analyzer1": 0.5, "analyzer2": 0.5}
        objectives = {"security": 80, "performance": 70}
        fitness = np.array([80, 70])
        
        solution = ParetoSolution(
            weights=weights,
            objectives=objectives,
            fitness=fitness
        )
        
        assert solution.weights == weights
        assert solution.objectives == objectives
        assert np.array_equal(solution.fitness, fitness)
        assert not solution.is_selected
        
    def test_summary(self):
        """Test solution summary"""
        solution = ParetoSolution(
            weights={"a": 0.5},
            objectives={"security": 80.5, "performance": 70.25},
            fitness=np.array([80.5, 70.25])
        )
        
        summary = solution.summary
        assert "security=80.50" in summary
        assert "performance=70.25" in summary


class TestParetoHealthOptimizer:
    """Test ParetoHealthOptimizer class"""
    
    def test_optimizer_initialization(self):
        """Test optimizer creation"""
        optimizer = ParetoHealthOptimizer()
        assert optimizer.problem is None
        assert optimizer.solutions == []
        
    @patch('src.evolution_lab.optimizers.pareto_health.minimize')
    def test_optimize_nsga3(self, mock_minimize, sample_analyzer_results):
        """Test optimization with NSGA-III"""
        # Mock optimization result
        mock_result = Mock()
        mock_result.X = np.array([[0.3, 0.2, 0.2, 0.2, 0.1],
                                  [0.2, 0.3, 0.2, 0.2, 0.1]])
        mock_result.F = np.array([[-80, -70, -60, 10, 5],
                                  [-75, -75, -65, 8, 3]])
        mock_minimize.return_value = mock_result
        
        optimizer = ParetoHealthOptimizer()
        solutions = optimizer.optimize(
            sample_analyzer_results,
            n_gen=10,
            pop_size=20,
            algorithm="nsga3"
        )
        
        assert len(solutions) == 2
        assert all(isinstance(s, ParetoSolution) for s in solutions)
        assert mock_minimize.called
        
    @patch('src.evolution_lab.optimizers.pareto_health.minimize')
    def test_optimize_nsga2(self, mock_minimize, sample_analyzer_results):
        """Test optimization with NSGA-II"""
        # Mock result
        mock_result = Mock()
        mock_result.X = np.array([[0.2, 0.2, 0.2, 0.2, 0.2]])
        mock_result.F = np.array([[-77, -72, -62, 9, 4]])
        mock_minimize.return_value = mock_result
        
        optimizer = ParetoHealthOptimizer()
        solutions = optimizer.optimize(
            sample_analyzer_results,
            n_gen=5,
            pop_size=10,
            algorithm="nsga2"
        )
        
        assert len(solutions) == 1
        assert solutions[0].weights["SecurityAnalyzer"] == 0.2
        
    def test_select_balanced_solution(self, sample_analyzer_results):
        """Test balanced solution selection"""
        optimizer = ParetoHealthOptimizer()
        
        # Create mock solutions
        optimizer.problem = ColonyHealthProblem(sample_analyzer_results)
        optimizer.solutions = [
            ParetoSolution(
                weights={"a": 0.5},
                objectives={"security": 80, "performance": 70},
                fitness=np.array([-80, -70, -60, 10, 5])
            ),
            ParetoSolution(
                weights={"a": 0.5},
                objectives={"security": 90, "performance": 90},
                fitness=np.array([-90, -90, -80, 5, 2])  # Better
            ),
        ]
        
        selected = optimizer.select_balanced_solution()
        assert selected is not None
        assert selected.is_selected
        assert selected == optimizer.solutions[1]  # Second is better
        
    def test_get_trade_off_data(self, sample_analyzer_results):
        """Test trade-off data extraction"""
        optimizer = ParetoHealthOptimizer()
        optimizer.problem = ColonyHealthProblem(sample_analyzer_results)
        
        # Add mock solutions
        optimizer.solutions = [
            ParetoSolution(
                weights={"a": 0.5},
                objectives={
                    "security_score": 80,
                    "performance_score": 70,
                    "test_coverage": 60,
                    "code_complexity": 10,
                    "duplication_ratio": 5
                },
                fitness=np.array([80, 70, 60, 10, 5])
            ),
            ParetoSolution(
                weights={"a": 0.3},
                objectives={
                    "security_score": 85,
                    "performance_score": 65,
                    "test_coverage": 70,
                    "code_complexity": 8,
                    "duplication_ratio": 3
                },
                fitness=np.array([85, 65, 70, 8, 3])
            ),
        ]
        
        data = optimizer.get_trade_off_data()
        
        assert "solution_id" in data
        assert "security_score" in data
        assert len(data["solution_id"]) == 2
        assert data["security_score"] == [80, 85]
        assert data["performance_score"] == [70, 65]
        
    def test_export_solutions(self, sample_analyzer_results, tmp_path):
        """Test solution export"""
        optimizer = ParetoHealthOptimizer()
        optimizer.problem = ColonyHealthProblem(sample_analyzer_results)
        optimizer.solutions = [
            ParetoSolution(
                weights={"SecurityAnalyzer": 0.5, "PerformanceAnalyzer": 0.5},
                objectives={"security_score": 80, "performance_score": 70},
                fitness=np.array([80, 70])
            )
        ]
        
        export_file = tmp_path / "solutions.json"
        optimizer.export_solutions(str(export_file))
        
        assert export_file.exists()
        
        # Verify content
        import json
        with open(export_file) as f:
            data = json.load(f)
            
        assert "solutions" in data
        assert "problem" in data
        assert len(data["solutions"]) == 1
        assert data["solutions"][0]["weights"]["SecurityAnalyzer"] == 0.5
        
    def test_empty_optimization(self):
        """Test optimization with no results"""
        optimizer = ParetoHealthOptimizer()
        
        # Test with empty solutions
        selected = optimizer.select_balanced_solution()
        assert selected is None
        
        data = optimizer.get_trade_off_data()
        assert data == {}