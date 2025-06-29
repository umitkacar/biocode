"""
Tests for Dependency Graph Analyzer
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""

import pytest
import tempfile
import os
from pathlib import Path
import networkx as nx

from src.evolution_lab.analyzers.dependency_graph_analyzer import (
    DependencyGraphAnalyzer, CodeNode, CodeEdge
)


@pytest.fixture
def test_project():
    """Create a test project with dependencies"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create project structure
        project_dir = Path(tmpdir) / "test_project"
        project_dir.mkdir()
        
        # Create module A
        module_a = project_dir / "module_a.py"
        module_a.write_text("""
import module_b
from module_c import ClassC

class ClassA:
    def __init__(self):
        self.b = module_b.ClassB()
        self.c = ClassC()
    
    def method_a(self):
        result = self.b.method_b()
        return self.process(result)
    
    def process(self, data):
        return data * 2

def function_a():
    a = ClassA()
    return a.method_a()
""")
        
        # Create module B
        module_b = project_dir / "module_b.py"
        module_b.write_text("""
class ClassB:
    def method_b(self):
        return self.helper()
    
    def helper(self):
        return 42

def function_b():
    b = ClassB()
    return b.method_b()
""")
        
        # Create module C with circular dependency
        module_c = project_dir / "module_c.py"
        module_c.write_text("""
import module_a  # Circular dependency

class ClassC(object):
    def method_c(self):
        return "C"

class ClassD(ClassC):
    def method_d(self):
        return super().method_c() + "D"
""")
        
        # Create a complex module with nested functions
        complex_module = project_dir / "complex.py"
        complex_module.write_text("""
def outer_function():
    def inner_function():
        def deeply_nested():
            return 1
        return deeply_nested()
    
    for i in range(10):
        if i > 5:
            while i < 9:
                try:
                    result = inner_function()
                except Exception:
                    pass
                i += 1
    
    return result

class GodClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass
    def method12(self): pass
    def method13(self): pass
    def method14(self): pass
    def method15(self): pass
    def method16(self): pass
    def method17(self): pass
    def method18(self): pass
    def method19(self): pass
    def method20(self): pass
    def method21(self): pass
""")
        
        yield str(project_dir)


@pytest.mark.asyncio
async def test_dependency_graph_analyzer_init(test_project):
    """Test analyzer initialization"""
    analyzer = DependencyGraphAnalyzer(test_project)
    
    assert analyzer.project_path == test_project
    assert isinstance(analyzer.module_graph, nx.DiGraph)
    assert isinstance(analyzer.class_graph, nx.DiGraph)
    assert isinstance(analyzer.function_graph, nx.DiGraph)
    assert len(analyzer.nodes) == 0
    assert len(analyzer.edges) == 0


@pytest.mark.asyncio
async def test_module_dependency_detection(test_project):
    """Test module-level dependency detection"""
    analyzer = DependencyGraphAnalyzer(test_project)
    result = await analyzer.analyze()
    
    # Check module graph
    assert analyzer.module_graph.number_of_nodes() >= 3  # At least 3 modules
    
    # Check imports detected
    assert 'module_b' in analyzer.import_map['module_a.py']
    assert 'module_c' in analyzer.import_map['module_a.py']
    assert 'module_a' in analyzer.import_map['module_c.py']  # Circular
    
    # Check circular dependency detected
    cycles = result.metrics['module_metrics']['cycles']
    assert len(cycles) > 0  # Should detect circular dependency


@pytest.mark.asyncio
async def test_class_hierarchy_detection(test_project):
    """Test class hierarchy and inheritance detection"""
    analyzer = DependencyGraphAnalyzer(test_project)
    result = await analyzer.analyze()
    
    # Check class nodes exist
    class_nodes = [n for n in analyzer.nodes.values() if n.type == 'class']
    assert len(class_nodes) >= 4  # ClassA, ClassB, ClassC, ClassD
    
    # Check inheritance
    assert 'module_c.py.ClassC' in analyzer.inheritance_map['module_c.py.ClassD']
    
    # Check class metrics
    class_metrics = result.metrics['class_metrics']
    assert class_metrics['total_classes'] >= 4
    assert class_metrics['inheritance_depth'] >= 1


@pytest.mark.asyncio
async def test_function_call_graph(test_project):
    """Test function call graph construction"""
    analyzer = DependencyGraphAnalyzer(test_project)
    result = await analyzer.analyze()
    
    # Check function nodes exist
    function_nodes = [n for n in analyzer.nodes.values() if n.type in ['function', 'method']]
    assert len(function_nodes) > 0
    
    # Check call relationships
    assert len(analyzer.call_graph) > 0
    
    # Check function metrics
    func_metrics = result.metrics['function_metrics']
    assert func_metrics['total_functions'] > 0
    assert 'call_depth' in func_metrics


@pytest.mark.asyncio
async def test_complexity_calculation(test_project):
    """Test cyclomatic complexity calculation"""
    analyzer = DependencyGraphAnalyzer(test_project)
    await analyzer.analyze()
    
    # Find the complex function
    complex_func = None
    for node in analyzer.nodes.values():
        if node.name == 'outer_function':
            complex_func = node
            break
    
    assert complex_func is not None
    assert complex_func.complexity > 5  # Has loops, conditions, try/except


@pytest.mark.asyncio
async def test_god_class_detection(test_project):
    """Test god class detection"""
    analyzer = DependencyGraphAnalyzer(test_project)
    result = await analyzer.analyze()
    
    # Check god class detected
    god_classes = result.metrics['class_metrics']['god_classes']
    assert len(god_classes) > 0
    assert any('GodClass' in class_name for class_name in god_classes)


@pytest.mark.asyncio
async def test_coupling_analysis(test_project):
    """Test coupling analysis"""
    analyzer = DependencyGraphAnalyzer(test_project)
    result = await analyzer.analyze()
    
    # Check coupling metrics exist
    class_metrics = result.metrics['class_metrics']
    assert 'coupling_scores' in class_metrics
    assert 'avg_coupling' in class_metrics
    
    # ClassA should have coupling to ClassB and ClassC
    coupling_scores = class_metrics['coupling_scores']
    class_a_coupling = coupling_scores.get('module_a.py.ClassA', {})
    if class_a_coupling:
        assert class_a_coupling['efferent_coupling'] >= 2  # Depends on B and C


@pytest.mark.asyncio
async def test_centrality_metrics(test_project):
    """Test centrality metrics calculation"""
    analyzer = DependencyGraphAnalyzer(test_project)
    result = await analyzer.analyze()
    
    # Check centrality metrics
    module_metrics = result.metrics['module_metrics']
    assert 'centrality' in module_metrics
    
    centrality = module_metrics['centrality']
    assert 'degree' in centrality
    assert 'betweenness' in centrality
    assert 'closeness' in centrality


@pytest.mark.asyncio
async def test_health_score_calculation(test_project):
    """Test health score calculation"""
    analyzer = DependencyGraphAnalyzer(test_project)
    result = await analyzer.analyze()
    
    # Check health score
    assert 0 <= result.score <= 100
    
    # With circular dependencies and god class, score should be < 100
    assert result.score < 100


@pytest.mark.asyncio
async def test_issue_detection(test_project):
    """Test issue detection"""
    analyzer = DependencyGraphAnalyzer(test_project)
    result = await analyzer.analyze()
    
    # Check issues detected
    assert len(result.issues) > 0
    
    # Check for specific issue types
    issue_types = {issue['type'] for issue in result.issues}
    assert 'circular_dependency' in issue_types
    assert 'god_class' in issue_types


@pytest.mark.asyncio
async def test_suggestions_generation(test_project):
    """Test suggestion generation"""
    analyzer = DependencyGraphAnalyzer(test_project)
    result = await analyzer.analyze()
    
    # Check suggestions generated
    assert len(result.suggestions) > 0
    
    # Check for specific suggestions
    suggestions_text = ' '.join(result.suggestions).lower()
    assert 'circular' in suggestions_text or 'dependency' in suggestions_text
    assert 'god class' in suggestions_text or 'split' in suggestions_text


@pytest.mark.asyncio
async def test_export_graphs(test_project):
    """Test graph export functionality"""
    analyzer = DependencyGraphAnalyzer(test_project)
    await analyzer.analyze()
    
    with tempfile.TemporaryDirectory() as export_dir:
        analyzer.export_graphs(export_dir)
        
        # Check files created
        assert os.path.exists(os.path.join(export_dir, 'dependency_graphs.json'))
        assert os.path.exists(os.path.join(export_dir, 'module_graph.graphml'))
        assert os.path.exists(os.path.join(export_dir, 'class_graph.graphml'))
        assert os.path.exists(os.path.join(export_dir, 'function_graph.graphml'))


@pytest.mark.asyncio
async def test_empty_project():
    """Test analyzer with empty project"""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = DependencyGraphAnalyzer(tmpdir)
        result = await analyzer.analyze()
        
        # Should handle empty project gracefully
        assert result.score >= 0
        assert result.metrics['module_metrics'] == {}
        assert result.metrics['class_metrics'] == {}
        assert result.metrics['function_metrics'] == {}


@pytest.mark.asyncio
async def test_single_file_project():
    """Test analyzer with single file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        single_file = Path(tmpdir) / "single.py"
        single_file.write_text("""
def hello():
    return "world"
""")
        
        analyzer = DependencyGraphAnalyzer(tmpdir)
        result = await analyzer.analyze()
        
        # Should handle single file
        assert analyzer.module_graph.number_of_nodes() == 1
        assert result.score > 0


@pytest.mark.asyncio
async def test_recursive_function_detection(test_project):
    """Test recursive function detection"""
    with tempfile.TemporaryDirectory() as tmpdir:
        recursive_file = Path(tmpdir) / "recursive.py"
        recursive_file.write_text("""
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
""")
        
        analyzer = DependencyGraphAnalyzer(tmpdir)
        result = await analyzer.analyze()
        
        # Check recursive functions detected
        func_metrics = result.metrics['function_metrics']
        recursive_funcs = func_metrics.get('recursive_functions', [])
        assert len(recursive_funcs) >= 2


@pytest.mark.asyncio
async def test_performance():
    """Test analyzer performance with larger project"""
    import time
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create 50 files with dependencies
        for i in range(50):
            module = Path(tmpdir) / f"module_{i}.py"
            content = f"""
import module_{(i+1) % 50}

class Class{i}:
    def method{i}(self):
        return {i}
"""
            module.write_text(content)
        
        analyzer = DependencyGraphAnalyzer(tmpdir)
        
        start_time = time.time()
        result = await analyzer.analyze()
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert elapsed_time < 10.0  # 10 seconds for 50 files
        assert analyzer.module_graph.number_of_nodes() == 50