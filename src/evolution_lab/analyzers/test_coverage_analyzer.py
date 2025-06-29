"""
Test Coverage and Quality Analyzer
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import re
import ast
from typing import Any, Dict, List
from pathlib import Path
from collections import defaultdict

from .base import BaseAnalyzer, AnalysisResult


class TestCoverageAnalyzer(BaseAnalyzer):
    """Analyzes test coverage, quality, and testing practices"""
    
    def analyze(self) -> AnalysisResult:
        """Analyze test coverage and quality"""
        self.start_timer()
        
        metrics = {
            'test_statistics': self._analyze_test_statistics(),
            'test_types': self._categorize_test_types(),
            'coverage_report': self._analyze_coverage_report(),
            'test_quality': self._analyze_test_quality(),
            'mocking_usage': self._analyze_mocking_patterns(),
            'test_fixtures': self._analyze_test_fixtures(),
            'test_performance': self._analyze_test_performance(),
            'ci_integration': self._check_ci_integration(),
        }
        
        metrics['test_score'] = self._calculate_test_score(metrics)
        metrics['analysis_time'] = self.get_elapsed_time()
        
        issues = self._detect_test_issues(metrics)
        suggestions = self._generate_test_suggestions(metrics)
        
        return AnalysisResult(
            analyzer_name=self.name,
            metrics=metrics,
            issues=issues,
            suggestions=suggestions,
            metadata={
                'project_path': str(self.project_path),
                'test_coverage': metrics['coverage_report'].get('total_coverage', 0),
            },
        )
    
    def _analyze_test_statistics(self) -> Dict[str, Any]:
        """Analyze basic test statistics"""
        test_stats = {
            'total_test_files': 0,
            'total_test_functions': 0,
            'total_test_classes': 0,
            'test_to_code_ratio': 0.0,
            'assertions_count': 0,
            'test_line_count': 0,
            'code_line_count': 0,
        }
        
        # Count test files
        test_files = self.scan_files(['.py'])
        test_files = [f for f in test_files if 'test' in f.stem.lower() or f.parts[-2] == 'tests']
        test_stats['total_test_files'] = len(test_files)
        
        # Count code files
        code_files = self.scan_files(['.py'])
        code_files = [f for f in code_files if 'test' not in f.stem.lower() and f.parts[-2] != 'tests']
        
        # Analyze test files
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    test_stats['test_line_count'] += len(content.splitlines())
                    
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    # Count test functions
                    if isinstance(node, ast.FunctionDef):
                        if node.name.startswith('test_'):
                            test_stats['total_test_functions'] += 1
                    
                    # Count test classes
                    elif isinstance(node, ast.ClassDef):
                        if 'Test' in node.name:
                            test_stats['total_test_classes'] += 1
                    
                    # Count assertions
                    elif isinstance(node, ast.Assert):
                        test_stats['assertions_count'] += 1
                    elif isinstance(node, ast.Call):
                        if hasattr(node.func, 'attr') and 'assert' in node.func.attr.lower():
                            test_stats['assertions_count'] += 1
                            
            except Exception:
                pass
        
        # Count code lines
        for code_file in code_files:
            try:
                with open(code_file, 'r', encoding='utf-8', errors='ignore') as f:
                    test_stats['code_line_count'] += len(f.readlines())
            except Exception:
                pass
        
        # Calculate ratio
        if test_stats['code_line_count'] > 0:
            test_stats['test_to_code_ratio'] = test_stats['test_line_count'] / test_stats['code_line_count']
        
        return test_stats
    
    def _categorize_test_types(self) -> Dict[str, Any]:
        """Categorize different types of tests"""
        test_types = {
            'unit_tests': 0,
            'integration_tests': 0,
            'functional_tests': 0,
            'performance_tests': 0,
            'security_tests': 0,
            'e2e_tests': 0,
            'smoke_tests': 0,
            'regression_tests': 0,
        }
        
        # Test type patterns
        type_patterns = {
            'unit': r'unit|Unit',
            'integration': r'integration|Integration',
            'functional': r'functional|Functional',
            'performance': r'performance|Performance|benchmark|Benchmark',
            'security': r'security|Security',
            'e2e': r'e2e|end.to.end|EndToEnd',
            'smoke': r'smoke|Smoke',
            'regression': r'regression|Regression',
        }
        
        test_files = self.scan_files(['.py'])
        test_files = [f for f in test_files if 'test' in f.stem.lower() or f.parts[-2] == 'tests']
        
        for test_file in test_files:
            try:
                # Check directory structure
                path_str = str(test_file)
                for test_type, pattern in type_patterns.items():
                    if re.search(pattern, path_str, re.IGNORECASE):
                        test_types[f'{test_type}_tests'] += 1
                        break
                else:
                    # If not in directory, check content
                    content = test_file.read_text()
                    for test_type, pattern in type_patterns.items():
                        if re.search(pattern, content):
                            test_types[f'{test_type}_tests'] += 1
                            break
                    else:
                        # Default to unit test
                        test_types['unit_tests'] += 1
                        
            except Exception:
                pass
        
        return test_types
    
    def _analyze_coverage_report(self) -> Dict[str, Any]:
        """Analyze test coverage reports"""
        coverage_info = {
            'total_coverage': 0.0,
            'covered_files': 0,
            'uncovered_files': [],
            'coverage_by_module': {},
            'coverage_config_exists': False,
            'coverage_threshold': None,
        }
        
        # Check for coverage configuration
        coverage_files = ['.coveragerc', 'pyproject.toml', 'setup.cfg', 'tox.ini']
        for cov_file in coverage_files:
            cov_path = self.project_path / cov_file
            if cov_path.exists():
                coverage_info['coverage_config_exists'] = True
                try:
                    content = cov_path.read_text()
                    # Look for coverage threshold
                    threshold_match = re.search(r'fail_under\s*=\s*(\d+)', content)
                    if threshold_match:
                        coverage_info['coverage_threshold'] = int(threshold_match.group(1))
                except Exception:
                    pass
        
        # Check for coverage report files
        coverage_report_paths = [
            self.project_path / 'htmlcov' / 'index.html',
            self.project_path / 'coverage.xml',
            self.project_path / '.coverage',
        ]
        
        for report_path in coverage_report_paths:
            if report_path.exists():
                try:
                    if report_path.suffix == '.xml':
                        content = report_path.read_text()
                        # Parse XML coverage report
                        coverage_match = re.search(r'line-rate="([\d.]+)"', content)
                        if coverage_match:
                            coverage_info['total_coverage'] = float(coverage_match.group(1)) * 100
                            
                        # Count covered files
                        coverage_info['covered_files'] = len(re.findall(r'<class ', content))
                        
                except Exception:
                    pass
        
        # If no coverage report, estimate based on test presence
        if coverage_info['total_coverage'] == 0:
            test_count = sum(self._analyze_test_statistics().values())
            if test_count > 0:
                # Rough estimate
                coverage_info['total_coverage'] = min(test_count / 10, 80.0)
        
        return coverage_info
    
    def _analyze_test_quality(self) -> Dict[str, Any]:
        """Analyze test quality metrics"""
        quality_info = {
            'avg_assertions_per_test': 0.0,
            'tests_with_docstrings': 0,
            'parameterized_tests': 0,
            'test_isolation': True,
            'test_naming_convention': True,
            'test_organization': True,
            'flaky_tests': [],
        }
        
        test_files = self.scan_files(['.py'])
        test_files = [f for f in test_files if 'test' in f.stem.lower() or f.parts[-2] == 'tests']
        
        total_tests = 0
        total_assertions = 0
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                        total_tests += 1
                        
                        # Check for docstring
                        if ast.get_docstring(node):
                            quality_info['tests_with_docstrings'] += 1
                        
                        # Check naming convention
                        if not re.match(r'test_[a-z_]+', node.name):
                            quality_info['test_naming_convention'] = False
                        
                        # Count assertions in this test
                        test_assertions = 0
                        for child in ast.walk(node):
                            if isinstance(child, ast.Assert):
                                test_assertions += 1
                            elif isinstance(child, ast.Call):
                                if hasattr(child.func, 'attr') and 'assert' in child.func.attr.lower():
                                    test_assertions += 1
                        
                        total_assertions += test_assertions
                        
                        # Check for parameterized tests
                        for decorator in node.decorator_list:
                            if hasattr(decorator, 'id') and 'parametrize' in str(decorator.id):
                                quality_info['parameterized_tests'] += 1
                
                # Check for test isolation issues (global state modification)
                if re.search(r'global\s+\w+', content):
                    quality_info['test_isolation'] = False
                
                # Check for flaky test indicators
                flaky_patterns = [r'time\.sleep', r'random\.', r'@flaky', r'@retry']
                for pattern in flaky_patterns:
                    if re.search(pattern, content):
                        quality_info['flaky_tests'].append({
                            'file': str(test_file.relative_to(self.project_path)),
                            'pattern': pattern,
                        })
                        
            except Exception:
                pass
        
        # Calculate average assertions
        if total_tests > 0:
            quality_info['avg_assertions_per_test'] = total_assertions / total_tests
        
        return quality_info
    
    def _analyze_mocking_patterns(self) -> Dict[str, Any]:
        """Analyze mocking and stubbing patterns"""
        mocking_info = {
            'mock_library': None,
            'total_mocks': 0,
            'patch_decorators': 0,
            'mock_objects': 0,
            'spy_usage': 0,
            'fixture_mocks': 0,
        }
        
        mock_patterns = {
            'unittest_mock': r'from unittest\.mock|import mock',
            'pytest_mock': r'pytest-mock|mocker\.',
            'patch': r'@patch|patch\(',
            'Mock': r'Mock\(|MagicMock\(',
            'spy': r'spy|Spy',
            'fixture_mock': r'@fixture.*mock|mock.*fixture',
        }
        
        test_files = self.scan_files(['.py'])
        test_files = [f for f in test_files if 'test' in f.stem.lower() or f.parts[-2] == 'tests']
        
        for test_file in test_files:
            try:
                content = test_file.read_text()
                
                # Detect mock library
                if re.search(mock_patterns['unittest_mock'], content):
                    mocking_info['mock_library'] = 'unittest.mock'
                elif re.search(mock_patterns['pytest_mock'], content):
                    mocking_info['mock_library'] = 'pytest-mock'
                
                # Count mocking patterns
                mocking_info['patch_decorators'] += len(re.findall(mock_patterns['patch'], content))
                mocking_info['mock_objects'] += len(re.findall(mock_patterns['Mock'], content))
                mocking_info['spy_usage'] += len(re.findall(mock_patterns['spy'], content))
                mocking_info['fixture_mocks'] += len(re.findall(mock_patterns['fixture_mock'], content))
                
            except Exception:
                pass
        
        mocking_info['total_mocks'] = (
            mocking_info['patch_decorators'] +
            mocking_info['mock_objects'] +
            mocking_info['spy_usage'] +
            mocking_info['fixture_mocks']
        )
        
        return mocking_info
    
    def _analyze_test_fixtures(self) -> Dict[str, Any]:
        """Analyze test fixtures and setup"""
        fixture_info = {
            'fixture_count': 0,
            'conftest_files': 0,
            'setup_teardown': 0,
            'shared_fixtures': [],
            'fixture_scope': defaultdict(int),
        }
        
        # Check for conftest files
        conftest_files = list(self.project_path.rglob('conftest.py'))
        fixture_info['conftest_files'] = len(conftest_files)
        
        # Analyze fixtures
        fixture_patterns = {
            'pytest_fixture': r'@(pytest\.)?fixture',
            'setup_teardown': r'def\s+(setup|teardown|setUp|tearDown)',
            'scope': r'@fixture\s*\(\s*scope\s*=\s*["\'](\w+)["\']',
        }
        
        test_files = self.scan_files(['.py'])
        test_files = [f for f in test_files if 'test' in f.stem.lower() or f.parts[-2] == 'tests']
        
        for test_file in test_files + conftest_files:
            try:
                content = test_file.read_text() if isinstance(test_file, Path) else test_file.read_text()
                
                # Count fixtures
                fixtures = re.findall(fixture_patterns['pytest_fixture'], content)
                fixture_info['fixture_count'] += len(fixtures)
                
                # Count setup/teardown
                setup_teardown = re.findall(fixture_patterns['setup_teardown'], content)
                fixture_info['setup_teardown'] += len(setup_teardown)
                
                # Analyze fixture scope
                scope_matches = re.findall(fixture_patterns['scope'], content)
                for scope in scope_matches:
                    fixture_info['fixture_scope'][scope] += 1
                
                # Find shared fixtures in conftest
                if 'conftest.py' in str(test_file):
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            for decorator in node.decorator_list:
                                if hasattr(decorator, 'id') and 'fixture' in str(decorator.id):
                                    fixture_info['shared_fixtures'].append(node.name)
                                    
            except Exception:
                pass
        
        return fixture_info
    
    def _analyze_test_performance(self) -> Dict[str, Any]:
        """Analyze test performance characteristics"""
        perf_info = {
            'slow_test_markers': 0,
            'timeout_configured': False,
            'parallel_testing': False,
            'test_duration_tracking': False,
            'performance_assertions': 0,
        }
        
        perf_patterns = {
            'slow': r'@slow|@pytest\.mark\.slow',
            'timeout': r'@timeout|timeout\s*=',
            'parallel': r'pytest-xdist|-n\s*\d+|pytest\.mark\.parallel',
            'duration': r'--durations|pytest-benchmark',
            'perf_assert': r'assert.*time|assert.*duration|assert.*performance',
        }
        
        # Check test files
        test_files = self.scan_files(['.py'])
        test_files = [f for f in test_files if 'test' in f.stem.lower() or f.parts[-2] == 'tests']
        
        for test_file in test_files:
            try:
                content = test_file.read_text()
                
                perf_info['slow_test_markers'] += len(re.findall(perf_patterns['slow'], content))
                
                if re.search(perf_patterns['timeout'], content):
                    perf_info['timeout_configured'] = True
                    
                perf_info['performance_assertions'] += len(re.findall(perf_patterns['perf_assert'], content))
                
            except Exception:
                pass
        
        # Check configuration files
        config_files = ['pytest.ini', 'pyproject.toml', 'setup.cfg', 'tox.ini']
        for config_file in config_files:
            config_path = self.project_path / config_file
            if config_path.exists():
                try:
                    content = config_path.read_text()
                    
                    if re.search(perf_patterns['parallel'], content):
                        perf_info['parallel_testing'] = True
                        
                    if re.search(perf_patterns['duration'], content):
                        perf_info['test_duration_tracking'] = True
                        
                except Exception:
                    pass
        
        return perf_info
    
    def _check_ci_integration(self) -> Dict[str, Any]:
        """Check CI/CD integration for tests"""
        ci_info = {
            'ci_configured': False,
            'ci_platforms': [],
            'test_on_push': False,
            'test_on_pr': False,
            'coverage_reporting': False,
            'test_matrix': False,
            'artifact_storage': False,
        }
        
        # CI configuration files
        ci_files = {
            '.github/workflows': 'github_actions',
            '.gitlab-ci.yml': 'gitlab',
            '.travis.yml': 'travis',
            'azure-pipelines.yml': 'azure',
            'Jenkinsfile': 'jenkins',
            '.circleci/config.yml': 'circleci',
        }
        
        for ci_path, platform in ci_files.items():
            full_path = self.project_path / ci_path
            if full_path.exists():
                ci_info['ci_configured'] = True
                ci_info['ci_platforms'].append(platform)
                
                try:
                    if full_path.is_file():
                        content = full_path.read_text()
                    else:
                        # For directories like .github/workflows
                        content = ""
                        for workflow_file in full_path.glob('*.yml'):
                            content += workflow_file.read_text()
                    
                    # Check for test triggers
                    if re.search(r'on:\s*push|on:\s*\[push', content):
                        ci_info['test_on_push'] = True
                        
                    if re.search(r'pull_request|merge_request', content):
                        ci_info['test_on_pr'] = True
                    
                    # Check for test execution
                    if re.search(r'pytest|python.*test|test.*python', content, re.IGNORECASE):
                        # Check for coverage
                        if re.search(r'coverage|codecov|coveralls', content, re.IGNORECASE):
                            ci_info['coverage_reporting'] = True
                        
                        # Check for test matrix
                        if re.search(r'matrix:|strategy:', content):
                            ci_info['test_matrix'] = True
                        
                        # Check for artifacts
                        if re.search(r'artifacts?:|upload-artifact', content):
                            ci_info['artifact_storage'] = True
                            
                except Exception:
                    pass
        
        return ci_info
    
    def _calculate_test_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall test score"""
        score = 0.0
        
        # Coverage score (40 points)
        coverage = metrics['coverage_report']['total_coverage']
        score += min(coverage * 0.4, 40.0)
        
        # Test quantity score (20 points)
        test_ratio = metrics['test_statistics']['test_to_code_ratio']
        score += min(test_ratio * 50, 20.0)
        
        # Test quality score (20 points)
        quality_score = 0
        if metrics['test_quality']['avg_assertions_per_test'] >= 2:
            quality_score += 5
        if metrics['test_quality']['tests_with_docstrings'] > 0:
            quality_score += 5
        if metrics['test_quality']['test_naming_convention']:
            quality_score += 5
        if metrics['test_quality']['parameterized_tests'] > 0:
            quality_score += 5
        score += quality_score
        
        # Test types score (10 points)
        test_types_count = sum(1 for v in metrics['test_types'].values() if v > 0)
        score += min(test_types_count * 2, 10.0)
        
        # CI/CD score (10 points)
        if metrics['ci_integration']['ci_configured']:
            score += 3
        if metrics['ci_integration']['test_on_push']:
            score += 2
        if metrics['ci_integration']['test_on_pr']:
            score += 2
        if metrics['ci_integration']['coverage_reporting']:
            score += 3
        
        return min(score, 100.0)
    
    def _detect_test_issues(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect testing issues"""
        issues = []
        
        # Coverage issues
        coverage = metrics['coverage_report']['total_coverage']
        if coverage < 60:
            issues.append({
                'severity': 'high',
                'type': 'coverage',
                'message': f'Low test coverage: {coverage:.1f}%',
            })
        elif coverage < 80:
            issues.append({
                'severity': 'medium',
                'type': 'coverage',
                'message': f'Test coverage below recommended threshold: {coverage:.1f}%',
            })
        
        # Test quantity issues
        if metrics['test_statistics']['total_test_functions'] == 0:
            issues.append({
                'severity': 'critical',
                'type': 'test_count',
                'message': 'No tests found in the project',
            })
        elif metrics['test_statistics']['test_to_code_ratio'] < 0.2:
            issues.append({
                'severity': 'high',
                'type': 'test_ratio',
                'message': 'Low test-to-code ratio indicates insufficient testing',
            })
        
        # Test quality issues
        if metrics['test_quality']['avg_assertions_per_test'] < 1:
            issues.append({
                'severity': 'medium',
                'type': 'test_quality',
                'message': 'Tests have too few assertions',
            })
        
        if not metrics['test_quality']['test_isolation']:
            issues.append({
                'severity': 'high',
                'type': 'test_isolation',
                'message': 'Tests may have isolation issues due to global state modification',
            })
        
        if metrics['test_quality']['flaky_tests']:
            issues.append({
                'severity': 'medium',
                'type': 'flaky_tests',
                'message': f"Potential flaky tests detected in {len(metrics['test_quality']['flaky_tests'])} files",
            })
        
        # Test type issues
        if metrics['test_types']['integration_tests'] == 0:
            issues.append({
                'severity': 'medium',
                'type': 'test_types',
                'message': 'No integration tests found',
            })
        
        # CI/CD issues
        if not metrics['ci_integration']['ci_configured']:
            issues.append({
                'severity': 'high',
                'type': 'ci_cd',
                'message': 'No CI/CD configuration found for automated testing',
            })
        elif not metrics['ci_integration']['coverage_reporting']:
            issues.append({
                'severity': 'medium',
                'type': 'ci_cd',
                'message': 'CI/CD does not include coverage reporting',
            })
        
        # Performance issues
        if metrics['test_performance']['slow_test_markers'] == 0 and metrics['test_statistics']['total_test_functions'] > 50:
            issues.append({
                'severity': 'low',
                'type': 'performance',
                'message': 'No slow test markers found - consider marking slow tests',
            })
        
        return issues
    
    def _generate_test_suggestions(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate testing improvement suggestions"""
        suggestions = []
        
        # Coverage suggestions
        coverage = metrics['coverage_report']['total_coverage']
        if coverage < 80:
            suggestions.append(f"Increase test coverage from {coverage:.1f}% to at least 80%")
            
        if not metrics['coverage_report']['coverage_config_exists']:
            suggestions.append("Add coverage configuration file (.coveragerc or in pyproject.toml)")
            
        if metrics['coverage_report']['coverage_threshold'] is None:
            suggestions.append("Set a minimum coverage threshold to prevent regression")
        
        # Test quality suggestions
        if metrics['test_quality']['avg_assertions_per_test'] < 2:
            suggestions.append("Add more assertions to tests - aim for at least 2-3 per test")
            
        if metrics['test_quality']['tests_with_docstrings'] < metrics['test_statistics']['total_test_functions'] * 0.5:
            suggestions.append("Add docstrings to test functions to document test purpose")
            
        if metrics['test_quality']['parameterized_tests'] < 5:
            suggestions.append("Use parameterized tests to reduce code duplication and test more cases")
        
        # Test type suggestions
        if metrics['test_types']['integration_tests'] == 0:
            suggestions.append("Add integration tests to verify component interactions")
            
        if metrics['test_types']['performance_tests'] == 0:
            suggestions.append("Add performance tests to catch performance regressions")
            
        if metrics['test_types']['e2e_tests'] == 0:
            suggestions.append("Consider adding end-to-end tests for critical user flows")
        
        # Mocking suggestions
        if metrics['mocking_usage']['total_mocks'] == 0:
            suggestions.append("Use mocking to isolate units under test and improve test speed")
        
        # Fixture suggestions
        if metrics['test_fixtures']['fixture_count'] < 5:
            suggestions.append("Use fixtures to reduce test setup duplication")
            
        if metrics['test_fixtures']['conftest_files'] == 0:
            suggestions.append("Create conftest.py files to share fixtures across test modules")
        
        # Performance suggestions
        if not metrics['test_performance']['parallel_testing'] and metrics['test_statistics']['total_test_functions'] > 100:
            suggestions.append("Enable parallel test execution with pytest-xdist for faster test runs")
            
        if not metrics['test_performance']['test_duration_tracking']:
            suggestions.append("Track test durations to identify slow tests")
        
        # CI/CD suggestions
        if not metrics['ci_integration']['ci_configured']:
            suggestions.append("Set up CI/CD pipeline to run tests automatically")
        else:
            if not metrics['ci_integration']['test_on_pr']:
                suggestions.append("Configure CI to run tests on pull requests")
                
            if not metrics['ci_integration']['test_matrix']:
                suggestions.append("Use test matrix to test against multiple Python versions")
                
            if not metrics['ci_integration']['artifact_storage']:
                suggestions.append("Store test artifacts (coverage reports, test results) in CI")
        
        return suggestions[:12]  # Return top 12 suggestions