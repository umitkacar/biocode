"""
Code Structure and Quality Analyzer
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import ast
import re
from typing import Any, Dict, List
from pathlib import Path
from collections import defaultdict

from .base import BaseAnalyzer, AnalysisResult


class CodeAnalyzer(BaseAnalyzer):
    """Analyzes code structure, quality, and patterns"""
    
    def analyze(self) -> AnalysisResult:
        """Analyze code structure and quality"""
        self.start_timer()
        
        # Detect primary language
        language_stats = self._detect_languages()
        primary_language = max(language_stats, key=language_stats.get) if language_stats else 'unknown'
        
        # Analyze based on primary language
        if primary_language == 'python':
            metrics = self._analyze_python()
        elif primary_language == 'javascript':
            metrics = self._analyze_javascript()
        else:
            metrics = self._analyze_generic()
            
        # Add language stats
        metrics['languages'] = language_stats
        metrics['primary_language'] = primary_language
        
        # Detect frameworks
        metrics['frameworks'] = self._detect_frameworks()
        
        # Calculate overall metrics
        metrics['analysis_time'] = self.get_elapsed_time()
        
        # Generate issues and suggestions
        issues = self._detect_issues(metrics)
        suggestions = self._generate_suggestions(metrics)
        
        return AnalysisResult(
            analyzer_name=self.name,
            metrics=metrics,
            issues=issues,
            suggestions=suggestions,
            metadata={'project_path': str(self.project_path)},
        )
        
    def _detect_languages(self) -> Dict[str, int]:
        """Detect programming languages used"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
        }
        
        language_counts = defaultdict(int)
        
        for file_path in self.scan_files():
            ext = file_path.suffix.lower()
            if ext in language_map:
                language_counts[language_map[ext]] += 1
                
        return dict(language_counts)
        
    def _analyze_python(self) -> Dict[str, Any]:
        """Analyze Python code"""
        metrics = {
            'total_files': 0,
            'total_lines': 0,
            'total_code_lines': 0,
            'total_classes': 0,
            'total_functions': 0,
            'complexity': [],
            'imports': defaultdict(int),
            'patterns': defaultdict(int),
        }
        
        python_files = self.scan_files(['.py'])
        metrics['total_files'] = len(python_files)
        
        for file_path in python_files:
            try:
                # Count lines
                line_counts = self.count_lines(file_path)
                metrics['total_lines'] += line_counts['total']
                metrics['total_code_lines'] += line_counts['code']
                
                # Parse AST
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                try:
                    tree = ast.parse(content)
                    
                    # Count classes and functions
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            metrics['total_classes'] += 1
                            # Check for patterns
                            if any(base.id for base in node.bases if hasattr(base, 'id') and 'ABC' in base.id):
                                metrics['patterns']['abstract_class'] += 1
                                
                        elif isinstance(node, ast.FunctionDef):
                            metrics['total_functions'] += 1
                            # Calculate complexity (simplified)
                            complexity = self._calculate_complexity(node)
                            metrics['complexity'].append({
                                'function': node.name,
                                'file': str(file_path.relative_to(self.project_path)),
                                'complexity': complexity,
                            })
                            
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                metrics['imports'][alias.name.split('.')[0]] += 1
                                
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                metrics['imports'][node.module.split('.')[0]] += 1
                                
                except SyntaxError:
                    pass
                    
            except Exception:
                pass
                
        # Calculate average complexity
        if metrics['complexity']:
            avg_complexity = sum(c['complexity'] for c in metrics['complexity']) / len(metrics['complexity'])
            metrics['average_complexity'] = round(avg_complexity, 2)
            
            # Find most complex functions
            metrics['most_complex'] = sorted(
                metrics['complexity'], 
                key=lambda x: x['complexity'], 
                reverse=True,
            )[:10]
            
        return metrics
        
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Each decision point adds complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # and/or operations add complexity
                complexity += len(child.values) - 1
                
        return complexity
        
    def _analyze_javascript(self) -> Dict[str, Any]:
        """Analyze JavaScript code"""
        metrics = {
            'total_files': 0,
            'total_lines': 0,
            'total_code_lines': 0,
            'patterns': defaultdict(int),
        }
        
        js_files = self.scan_files(['.js', '.jsx', '.ts', '.tsx'])
        metrics['total_files'] = len(js_files)
        
        for file_path in js_files:
            line_counts = self.count_lines(file_path)
            metrics['total_lines'] += line_counts['total']
            metrics['total_code_lines'] += line_counts['code']
            
            # Simple pattern detection
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Detect patterns
                if 'class ' in content:
                    metrics['patterns']['class'] += content.count('class ')
                if 'function ' in content:
                    metrics['patterns']['function'] += content.count('function ')
                if '=>' in content:
                    metrics['patterns']['arrow_function'] += content.count('=>')
                if 'async ' in content:
                    metrics['patterns']['async'] += content.count('async ')
                if 'import ' in content:
                    metrics['patterns']['es6_import'] += content.count('import ')
                    
            except Exception:
                pass
                
        return metrics
        
    def _analyze_generic(self) -> Dict[str, Any]:
        """Generic code analysis for any language"""
        metrics = {
            'total_files': 0,
            'total_lines': 0,
            'total_size': 0,
            'file_types': defaultdict(int),
        }
        
        all_files = self.scan_files()
        metrics['total_files'] = len(all_files)
        
        for file_path in all_files:
            file_info = self.get_file_info(file_path)
            metrics['total_size'] += file_info['size']
            metrics['file_types'][file_info['extension']] += 1
            
            line_counts = self.count_lines(file_path)
            metrics['total_lines'] += line_counts['total']
            
        return metrics
        
    def _detect_frameworks(self) -> List[str]:
        """Detect frameworks and libraries used"""
        frameworks = []
        
        # Check for Python frameworks
        if (self.project_path / 'requirements.txt').exists():
            req_content = (self.project_path / 'requirements.txt').read_text()
            if 'django' in req_content.lower():
                frameworks.append('Django')
            if 'flask' in req_content.lower():
                frameworks.append('Flask')
            if 'fastapi' in req_content.lower():
                frameworks.append('FastAPI')
            if 'tensorflow' in req_content.lower():
                frameworks.append('TensorFlow')
            if 'torch' in req_content.lower() or 'pytorch' in req_content.lower():
                frameworks.append('PyTorch')
                
        # Check for JavaScript frameworks
        if (self.project_path / 'package.json').exists():
            pkg_data = self.load_json_file(self.project_path / 'package.json')
            if pkg_data:
                deps = {**pkg_data.get('dependencies', {}), **pkg_data.get('devDependencies', {})}
                if 'react' in deps:
                    frameworks.append('React')
                if 'vue' in deps:
                    frameworks.append('Vue')
                if 'angular' in deps:
                    frameworks.append('Angular')
                if 'express' in deps:
                    frameworks.append('Express')
                    
        return frameworks
        
    def _detect_issues(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect potential issues in code"""
        issues = []
        
        # High complexity functions
        if 'most_complex' in metrics:
            for func in metrics['most_complex'][:5]:
                if func['complexity'] > 10:
                    issues.append({
                        'severity': 'high' if func['complexity'] > 20 else 'medium',
                        'type': 'complexity',
                        'message': f"High complexity ({func['complexity']}) in {func['function']}",
                        'file': func['file'],
                    })
                    
        # Large files
        if metrics.get('total_files', 0) > 0:
            avg_lines = metrics.get('total_lines', 0) / metrics['total_files']
            if avg_lines > 500:
                issues.append({
                    'severity': 'medium',
                    'type': 'size',
                    'message': f"Large average file size ({int(avg_lines)} lines per file)",
                })
                
        return issues
        
    def _generate_suggestions(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Complexity suggestions
        if metrics.get('average_complexity', 0) > 5:
            suggestions.append("Consider refactoring complex functions to improve maintainability")
            
        # Framework suggestions
        if not metrics.get('frameworks'):
            suggestions.append("Consider using a web framework for better structure")
            
        # Documentation
        if metrics.get('total_code_lines', 0) > 0:
            comment_ratio = metrics.get('total_lines', 0) - metrics.get('total_code_lines', 0)
            if comment_ratio / metrics['total_code_lines'] < 0.1:
                suggestions.append("Add more documentation and comments to improve code clarity")
                
        return suggestions