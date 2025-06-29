"""
Tests for Code Smell Analyzer
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import pytest
import tempfile
from pathlib import Path
import textwrap

from src.evolution_lab.analyzers.code_smell_analyzer import CodeSmellAnalyzer, CodeSmell


@pytest.fixture
def temp_project():
    """Create a temporary project with sample files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Create test files with various smells
        
        # File with long method
        long_method_file = project_path / "long_method.py"
        long_method_file.write_text(textwrap.dedent("""
            def process_data(data):
                # This is a very long method
                result = []
                for item in data:
                    if item > 0:
                        processed = item * 2
                        result.append(processed)
                    else:
                        processed = item * -1
                        result.append(processed)
                
                # More processing
                total = 0
                for item in result:
                    total += item
                    
                average = total / len(result)
                
                # Even more processing
                normalized = []
                for item in result:
                    normalized.append(item / average)
                    
                # Final processing
                output = {}
                for i, item in enumerate(normalized):
                    output[f'item_{i}'] = item
                    
                # Additional logic
                if len(output) > 10:
                    print("Too many items")
                    
                # More logic
                keys = list(output.keys())
                keys.sort()
                
                sorted_output = {}
                for key in keys:
                    sorted_output[key] = output[key]
                    
                # Final return
                return sorted_output
                
                # Add more lines to make it longer
                # Line 40
                # Line 41
                # Line 42
                # Line 43
                # Line 44
                # Line 45
                # Line 46
                # Line 47
                # Line 48
                # Line 49
                # Line 50
                # Line 51
                # Line 52
        """))
        
        # File with god class
        god_class_file = project_path / "god_class.py"
        god_class_file.write_text(textwrap.dedent("""
            class DataProcessor:
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
        """))
        
        # File with code smells
        smelly_file = project_path / "smelly_code.py"
        smelly_file.write_text(textwrap.dedent("""
            # Global variable
            global_config = {}
            
            def calculate_price(quantity, price, tax_rate, discount_rate, shipping_cost, handling_fee):
                # Long parameter list
                global global_config
                
                # Magic numbers
                if quantity > 100:
                    discount = 0.15
                else:
                    discount = 0.05
                    
                # Deep nesting
                if price > 0:
                    if quantity > 0:
                        if tax_rate > 0:
                            if discount_rate > 0:
                                if shipping_cost > 0:
                                    total = price * quantity
                                    
                # Empty exception handler
                try:
                    result = total / quantity
                except:
                    pass
                    
                # Commented out code
                # def old_function():
                #     return "old"
                    
                # TODO: Fix this later
                # FIXME: This is broken
                # TODO: Refactor needed
                
                return 42  # Magic number
                
            # This is a very long line that exceeds the maximum line length threshold and should be broken into multiple lines for better readability
        """))
        
        yield project_path


class TestCodeSmellAnalyzer:
    """Test CodeSmellAnalyzer class"""
    
    def test_analyzer_initialization(self, temp_project):
        """Test analyzer initialization"""
        analyzer = CodeSmellAnalyzer(str(temp_project))
        
        assert str(analyzer.project_path) == str(temp_project)
        assert analyzer.max_method_lines == 50
        assert analyzer.max_params == 5
        assert analyzer.max_class_methods == 20
        
    def test_long_method_detection(self, temp_project):
        """Test detection of long methods"""
        analyzer = CodeSmellAnalyzer(str(temp_project))
        results = analyzer.analyze()
        
        # Find long method smells
        long_methods = [s for s in results['smells'] if s['type'] == 'long_method']
        assert len(long_methods) > 0
        
        # Check the smell details
        smell = long_methods[0]
        assert smell['severity'] == 'medium'
        assert 'process_data' in smell['message']
        assert smell['line'] == 2  # Method starts at line 2
        
    def test_god_class_detection(self, temp_project):
        """Test detection of god classes"""
        analyzer = CodeSmellAnalyzer(str(temp_project))
        results = analyzer.analyze()
        
        # Find god class smells
        god_classes = [s for s in results['smells'] if s['type'] == 'god_class_methods']
        assert len(god_classes) > 0
        
        smell = god_classes[0]
        assert smell['severity'] == 'high'
        assert 'DataProcessor' in smell['message']
        assert '21 methods' in smell['message']
        
    def test_long_parameter_list(self, temp_project):
        """Test detection of long parameter lists"""
        analyzer = CodeSmellAnalyzer(str(temp_project))
        results = analyzer.analyze()
        
        # Find long parameter list smells
        long_params = [s for s in results['smells'] if s['type'] == 'long_parameter_list']
        assert len(long_params) > 0
        
        smell = long_params[0]
        assert smell['severity'] == 'medium'
        assert 'calculate_price' in smell['message']
        assert '6 parameters' in smell['message']
        
    def test_magic_number_detection(self, temp_project):
        """Test detection of magic numbers"""
        analyzer = CodeSmellAnalyzer(str(temp_project))
        results = analyzer.analyze()
        
        # Find magic number smells
        magic_numbers = [s for s in results['smells'] if s['type'] == 'magic_number']
        assert len(magic_numbers) > 0
        
        # Should detect 100, 42, and possibly others
        numbers_found = set()
        for smell in magic_numbers:
            if '100' in smell['message']:
                numbers_found.add(100)
            if '42' in smell['message']:
                numbers_found.add(42)
                
        assert 100 in numbers_found
        assert 42 in numbers_found
        
    def test_empty_exception_handler(self, temp_project):
        """Test detection of empty exception handlers"""
        analyzer = CodeSmellAnalyzer(str(temp_project))
        results = analyzer.analyze()
        
        # Find empty exception handler smells
        empty_handlers = [s for s in results['smells'] if s['type'] == 'empty_exception_handler']
        assert len(empty_handlers) > 0
        
        smell = empty_handlers[0]
        assert smell['severity'] == 'high'
        assert smell['auto_fixable'] is True
        assert smell['fix_code'] is not None
        
    def test_global_variable_detection(self, temp_project):
        """Test detection of global variables"""
        analyzer = CodeSmellAnalyzer(str(temp_project))
        results = analyzer.analyze()
        
        # Find global variable smells
        globals_found = [s for s in results['smells'] if s['type'] == 'global_variable']
        assert len(globals_found) > 0
        
        smell = globals_found[0]
        assert smell['severity'] == 'medium'
        assert 'global_config' in smell['message']
        
    def test_commented_code_detection(self, temp_project):
        """Test detection of commented out code"""
        analyzer = CodeSmellAnalyzer(str(temp_project))
        results = analyzer.analyze()
        
        # Find commented code smells
        commented = [s for s in results['smells'] if s['type'] == 'commented_code']
        assert len(commented) > 0
        
        smell = commented[0]
        assert smell['severity'] == 'low'
        assert smell['auto_fixable'] is True
        
    def test_long_line_detection(self, temp_project):
        """Test detection of long lines"""
        analyzer = CodeSmellAnalyzer(str(temp_project))
        results = analyzer.analyze()
        
        # Find long line smells
        long_lines = [s for s in results['smells'] if s['type'] == 'long_line']
        assert len(long_lines) > 0
        
        smell = long_lines[0]
        assert smell['severity'] == 'low'
        assert smell['column'] == 120
        
    def test_deep_nesting_detection(self, temp_project):
        """Test detection of deep nesting"""
        analyzer = CodeSmellAnalyzer(str(temp_project))
        results = analyzer.analyze()
        
        # Find deep nesting smells
        deep_nesting = [s for s in results['smells'] if s['type'] == 'deep_nesting']
        assert len(deep_nesting) > 0
        
        smell = deep_nesting[0]
        assert smell['severity'] == 'medium'
        assert 'calculate_price' in smell['message']
        
    def test_health_score_calculation(self, temp_project):
        """Test health score calculation"""
        analyzer = CodeSmellAnalyzer(str(temp_project))
        results = analyzer.analyze()
        
        assert 'health_score' in results
        assert 0 <= results['health_score'] <= 100
        
        # With all these smells, score should be less than 100
        assert results['health_score'] < 100
        
    def test_smell_distribution(self, temp_project):
        """Test smell distribution statistics"""
        analyzer = CodeSmellAnalyzer(str(temp_project))
        results = analyzer.analyze()
        
        assert 'smell_distribution' in results
        assert 'severity_distribution' in results
        
        # Check severity distribution
        severity_dist = results['severity_distribution']
        assert all(sev in severity_dist for sev in ['low', 'medium', 'high', 'critical'])
        assert all(count >= 0 for count in severity_dist.values())
        
    def test_auto_fixable_count(self, temp_project):
        """Test counting of auto-fixable smells"""
        analyzer = CodeSmellAnalyzer(str(temp_project))
        results = analyzer.analyze()
        
        assert 'auto_fixable_count' in results
        assert results['auto_fixable_count'] > 0
        
        # Verify count matches actual fixable smells
        fixable = [s for s in results['smells'] if s['auto_fixable']]
        assert len(fixable) == results['auto_fixable_count']
        
    def test_skip_patterns(self, temp_project):
        """Test that certain directories are skipped"""
        # Create a file in __pycache__
        cache_dir = temp_project / "__pycache__"
        cache_dir.mkdir()
        cache_file = cache_dir / "cached.py"
        cache_file.write_text("# This should be skipped")
        
        analyzer = CodeSmellAnalyzer(str(temp_project))
        results = analyzer.analyze()
        
        # Check that no smells are from cache directory
        for smell in results['smells']:
            assert "__pycache__" not in smell['file']
            
    def test_syntax_error_handling(self, temp_project):
        """Test handling of files with syntax errors"""
        # Create a file with syntax error
        bad_file = temp_project / "syntax_error.py"
        bad_file.write_text("def broken(\n    # Missing closing paren")
        
        analyzer = CodeSmellAnalyzer(str(temp_project))
        results = analyzer.analyze()
        
        # Should detect syntax error as a smell
        syntax_errors = [s for s in results['smells'] if s['type'] == 'syntax_error']
        assert len(syntax_errors) > 0
        
        smell = syntax_errors[0]
        assert smell['severity'] == 'critical'
        assert not smell['auto_fixable']
        
    def test_code_smell_dataclass(self):
        """Test CodeSmell dataclass"""
        smell = CodeSmell(
            smell_type="test_smell",
            severity="high",
            file_path="/test/file.py",
            line_number=10,
            column=5,
            message="Test message",
            suggestion="Test suggestion"
        )
        
        assert smell.smell_type == "test_smell"
        assert smell.severity == "high"
        assert smell.auto_fixable is False
        assert smell.confidence == 1.0