"""
Tests for Code Embedding Analyzer
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""

import pytest
import tempfile
import os
import numpy as np
from pathlib import Path

from src.evolution_lab.analyzers.code_embedding_analyzer import (
    CodeEmbeddingAnalyzer, CodeElement, SimilarityMatch
)


@pytest.fixture
def test_project_with_duplicates():
    """Create a test project with various types of code duplicates"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir) / "test_project"
        project_dir.mkdir()
        
        # Type 1 clone: Exact duplicate
        utils1 = project_dir / "utils1.py"
        utils1.write_text("""
def calculate_average(numbers):
    '''Calculate the average of a list of numbers'''
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def find_maximum(numbers):
    '''Find the maximum value in a list'''
    if not numbers:
        return None
    return max(numbers)
""")
        
        # Type 1 clone: Exact duplicate in another file
        utils2 = project_dir / "utils2.py"
        utils2.write_text("""
def calculate_average(numbers):
    '''Calculate the average of a list of numbers'''
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def process_data(data):
    '''Process some data'''
    return [x * 2 for x in data]
""")
        
        # Type 2 clone: Renamed variables
        stats = project_dir / "stats.py"
        stats.write_text("""
def compute_mean(values):
    '''Calculate the average of a list of numbers'''
    if not values:
        return 0
    return sum(values) / len(values)

def find_max_value(items):
    '''Find the maximum value in a list'''
    if not items:
        return None
    return max(items)
""")
        
        # Type 3 clone: Modified with added/removed statements
        math_utils = project_dir / "math_utils.py"
        math_utils.write_text("""
def calculate_avg_with_logging(numbers):
    '''Calculate average with logging'''
    print(f"Calculating average of {len(numbers)} numbers")
    if not numbers:
        print("Empty list, returning 0")
        return 0
    result = sum(numbers) / len(numbers)
    print(f"Average is {result}")
    return result
""")
        
        # Type 4 clone: Semantic similarity (different implementation)
        algorithms = project_dir / "algorithms.py"
        algorithms.write_text("""
def mean_calculation(data_points):
    '''Compute arithmetic mean'''
    total = 0
    count = 0
    for value in data_points:
        total += value
        count += 1
    if count == 0:
        return 0
    return total / count

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def add_data(self, value):
        self.data.append(value)
    
    def get_average(self):
        if not self.data:
            return 0
        return sum(self.data) / len(self.data)
""")
        
        # Unique functions (no duplicates)
        unique_module = project_dir / "unique.py"
        unique_module.write_text("""
def binary_search(arr, target):
    '''Binary search implementation'''
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

def quicksort(arr):
    '''Quicksort implementation'''
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
""")
        
        yield str(project_dir)


@pytest.mark.asyncio
async def test_code_embedding_analyzer_init():
    """Test analyzer initialization"""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = CodeEmbeddingAnalyzer(tmpdir)
        
        assert str(analyzer.project_path) == tmpdir
        # Since sentence_transformers is not installed, it should be None
        assert analyzer.embedding_model is None
        assert len(analyzer.code_elements) == 0
        assert analyzer.embeddings_matrix is None


@pytest.mark.asyncio
async def test_code_element_extraction(test_project_with_duplicates):
    """Test extraction of code elements"""
    analyzer = CodeEmbeddingAnalyzer(test_project_with_duplicates)
    analyzer._extract_code_elements()
    
    # Should extract all functions and classes
    assert len(analyzer.code_elements) > 0
    
    # Check specific elements
    element_names = [elem.name for elem in analyzer.code_elements.values()]
    assert 'calculate_average' in element_names
    assert 'compute_mean' in element_names
    assert 'binary_search' in element_names
    assert 'DataProcessor' in element_names
    
    # Check element properties
    for element in analyzer.code_elements.values():
        assert element.id
        assert element.name
        assert element.type in ['function', 'class', 'method']
        assert element.file_path
        assert element.line_start > 0
        assert element.code


@pytest.mark.asyncio
async def test_embedding_generation(test_project_with_duplicates):
    """Test embedding generation"""
    analyzer = CodeEmbeddingAnalyzer(test_project_with_duplicates)
    analyzer._extract_code_elements()
    analyzer._generate_embeddings()
    
    # Check embeddings generated
    assert analyzer.embeddings_matrix is not None
    assert len(analyzer.element_ids) == len(analyzer.code_elements)
    assert analyzer.embeddings_matrix.shape[0] == len(analyzer.code_elements)
    
    # Check individual embeddings
    for element in analyzer.code_elements.values():
        assert element.embedding is not None
        assert isinstance(element.embedding, np.ndarray)
        assert element.embedding.shape[0] > 0  # Has dimensions


@pytest.mark.asyncio
async def test_type1_clone_detection(test_project_with_duplicates):
    """Test exact clone detection"""
    analyzer = CodeEmbeddingAnalyzer(test_project_with_duplicates)
    result = await analyzer.analyze()
    
    # Extract similarities from metrics
    clone_stats = result.metrics.get('clone_statistics', {})
    
    # Should detect type 1 clones (calculate_average is duplicated exactly)
    assert clone_stats.get('type1_clones', 0) > 0
    
    # Check that calculate_average is identified as duplicate
    top_dups = result.metrics.get('top_duplicated_elements', [])
    dup_names = [d['element'] for d in top_dups]
    assert any('calculate_average' in name for name in dup_names)


@pytest.mark.asyncio
async def test_type2_clone_detection(test_project_with_duplicates):
    """Test renamed clone detection"""
    analyzer = CodeEmbeddingAnalyzer(test_project_with_duplicates)
    result = await analyzer.analyze()
    
    clone_stats = result.metrics.get('clone_statistics', {})
    
    # Should detect type 2 clones (compute_mean is renamed calculate_average)
    assert clone_stats.get('type2_clones', 0) > 0 or clone_stats.get('type3_clones', 0) > 0


@pytest.mark.asyncio
async def test_semantic_similarity_detection(test_project_with_duplicates):
    """Test semantic similarity detection"""
    analyzer = CodeEmbeddingAnalyzer(test_project_with_duplicates)
    result = await analyzer.analyze()
    
    clone_stats = result.metrics.get('clone_statistics', {})
    total_clones = clone_stats.get('total_clones', 0)
    
    # Should detect various types of clones
    assert total_clones > 0
    
    # Should detect semantic clones (mean_calculation vs calculate_average)
    assert clone_stats.get('type4_clones', 0) > 0 or clone_stats.get('type3_clones', 0) > 0


@pytest.mark.asyncio
async def test_duplication_metrics(test_project_with_duplicates):
    """Test duplication metrics calculation"""
    analyzer = CodeEmbeddingAnalyzer(test_project_with_duplicates)
    result = await analyzer.analyze()
    
    # Check metrics
    assert 'duplication_ratio' in result.metrics
    assert 0 <= result.metrics['duplication_ratio'] <= 1
    
    assert 'code_quality_score' in result.metrics
    assert 0 <= result.metrics['code_quality_score'] <= 100
    
    # With duplicates, quality score should be < 100
    assert result.metrics['code_quality_score'] < 100


@pytest.mark.asyncio
async def test_semantic_search():
    """Test semantic code search"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("""
def sort_numbers(nums):
    '''Sort a list of numbers'''
    return sorted(nums)

def find_median(numbers):
    '''Find the median value'''
    sorted_nums = sorted(numbers)
    n = len(sorted_nums)
    if n % 2 == 0:
        return (sorted_nums[n//2-1] + sorted_nums[n//2]) / 2
    return sorted_nums[n//2]

def calculate_sum(values):
    '''Calculate sum of values'''
    return sum(values)
""")
        
        analyzer = CodeEmbeddingAnalyzer(tmpdir)
        analyzer._extract_code_elements()
        analyzer._generate_embeddings()
        
        # Search for "average calculation"
        results = analyzer.semantic_search("calculate average mean", top_k=3)
        
        assert len(results) > 0
        # Should find calculate_sum and find_median as related
        result_names = [elem.name for elem, score in results]
        assert any('sum' in name.lower() or 'median' in name.lower() for name in result_names)


@pytest.mark.asyncio
async def test_find_similar_code():
    """Test finding similar code snippets"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("""
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr
""")
        
        analyzer = CodeEmbeddingAnalyzer(tmpdir)
        analyzer._extract_code_elements()
        analyzer._generate_embeddings()
        
        # Search for similar sorting algorithm
        code_snippet = """
def insertion_sort(items):
    for i in range(1, len(items)):
        key = items[i]
        j = i - 1
        while j >= 0 and items[j] > key:
            items[j + 1] = items[j]
            j -= 1
        items[j + 1] = key
    return items
"""
        
        results = analyzer.find_similar_code(code_snippet, top_k=2)
        
        assert len(results) > 0
        # Should find bubble_sort and selection_sort as similar
        result_names = [elem.name for elem, score in results]
        assert any('sort' in name for name in result_names)


@pytest.mark.asyncio
async def test_issue_detection(test_project_with_duplicates):
    """Test issue detection based on duplicates"""
    analyzer = CodeEmbeddingAnalyzer(test_project_with_duplicates)
    result = await analyzer.analyze()
    
    # Should detect duplication issues
    assert len(result.issues) > 0
    
    issue_types = {issue['type'] for issue in result.issues}
    # Should detect exact clones
    assert 'exact_clones' in issue_types or 'high_duplication' in issue_types


@pytest.mark.asyncio
async def test_suggestions_generation(test_project_with_duplicates):
    """Test suggestion generation"""
    analyzer = CodeEmbeddingAnalyzer(test_project_with_duplicates)
    result = await analyzer.analyze()
    
    # Should generate suggestions
    assert len(result.suggestions) > 0
    
    # Should suggest refactoring duplicates
    suggestions_text = ' '.join(result.suggestions).lower()
    assert 'refactor' in suggestions_text or 'duplicate' in suggestions_text


@pytest.mark.asyncio
async def test_cache_functionality():
    """Test embedding cache save/load"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("""
def test_function():
    return 42
""")
        
        analyzer = CodeEmbeddingAnalyzer(tmpdir)
        analyzer._extract_code_elements()
        analyzer._generate_embeddings()
        
        # Cache should be saved
        assert analyzer.cache_file.exists()
        
        # Create new analyzer and load from cache
        analyzer2 = CodeEmbeddingAnalyzer(tmpdir)
        analyzer2._extract_code_elements()
        
        # Clear embeddings to test loading
        analyzer2.embeddings_matrix = None
        analyzer2._generate_embeddings()
        
        # Should have loaded from cache
        assert analyzer2.embeddings_matrix is not None
        assert np.array_equal(analyzer.embeddings_matrix, analyzer2.embeddings_matrix)


@pytest.mark.asyncio
async def test_export_embeddings():
    """Test embedding export functionality"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("""
def function_a():
    return 1

def function_b():
    return 2
""")
        
        analyzer = CodeEmbeddingAnalyzer(tmpdir)
        analyzer._extract_code_elements()
        analyzer._generate_embeddings()
        
        # Export embeddings
        export_path = os.path.join(tmpdir, "embeddings.json")
        analyzer.export_embeddings(export_path)
        
        assert os.path.exists(export_path)
        
        # Load and verify
        import json
        with open(export_path, 'r') as f:
            data = json.load(f)
            
        assert 'elements' in data
        assert 'embeddings' in data
        assert 'metadata' in data
        assert len(data['elements']) == 2
        assert len(data['embeddings']) == 2


@pytest.mark.asyncio
async def test_empty_project():
    """Test analyzer with empty project"""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = CodeEmbeddingAnalyzer(tmpdir)
        result = await analyzer.analyze()
        
        # Should handle empty project gracefully
        assert result.metrics['total_elements'] == 0
        assert result.metrics['duplication_ratio'] == 0
        assert len(result.issues) == 0


@pytest.mark.asyncio
async def test_single_file_no_duplicates():
    """Test analyzer with single file and no duplicates"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "unique.py"
        test_file.write_text("""
def unique_function_1():
    return "unique1"

def unique_function_2():
    return "unique2"

def unique_function_3():
    return "unique3"
""")
        
        analyzer = CodeEmbeddingAnalyzer(tmpdir)
        result = await analyzer.analyze()
        
        # Should detect no duplicates
        clone_stats = result.metrics.get('clone_statistics', {})
        assert clone_stats.get('total_clones', 0) == 0
        assert result.metrics['code_quality_score'] == 100.0


@pytest.mark.asyncio
async def test_ast_hash_computation():
    """Test AST hash computation for structural comparison"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create two files with structurally identical functions
        file1 = Path(tmpdir) / "file1.py"
        file1.write_text("""
def calculate(x, y):
    result = x + y
    return result
""")
        
        file2 = Path(tmpdir) / "file2.py"
        file2.write_text("""
def compute(a, b):
    output = a + b
    return output
""")
        
        analyzer = CodeEmbeddingAnalyzer(tmpdir)
        analyzer._extract_code_elements()
        
        # Get AST hashes
        elements = list(analyzer.code_elements.values())
        assert len(elements) == 2
        
        # AST hashes should be the same (same structure, different names)
        assert elements[0].ast_hash == elements[1].ast_hash