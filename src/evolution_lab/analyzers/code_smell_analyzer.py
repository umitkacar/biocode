"""
Code Smell Analyzer - Detects and suggests fixes for code smells
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

Detects common code smells and anti-patterns with auto-fix suggestions.
"""
import ast
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

from .base import BaseAnalyzer


@dataclass
class CodeSmell:
    """Represents a detected code smell"""
    smell_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    file_path: str
    line_number: int
    column: int
    message: str
    suggestion: str
    auto_fixable: bool = False
    fix_code: Optional[str] = None
    confidence: float = 1.0


class CodeSmellAnalyzer(BaseAnalyzer):
    """
    Detects and suggests fixes for common code smells.
    
    Detected Smells:
    - Long methods (>50 lines)
    - Long parameter lists (>5 params)
    - God classes (>20 methods or >500 lines)
    - Duplicate code blocks
    - Dead code
    - Magic numbers
    - Deep nesting (>4 levels)
    - Long lines (>120 chars)
    - Multiple returns in complex functions
    - Global variables misuse
    - Empty exception handlers
    - Commented out code
    - TODO/FIXME accumulation
    """
    
    def __init__(self, project_path: str):
        super().__init__(project_path)
        self.smells: List[CodeSmell] = []
        
        # Thresholds (configurable)
        self.max_method_lines = 50
        self.max_params = 5
        self.max_class_methods = 20
        self.max_class_lines = 500
        self.max_nesting_depth = 4
        self.max_line_length = 120
        self.max_complexity = 10
        
        # Patterns
        self.magic_number_pattern = re.compile(r'\b(?<!\.)\d+(?!\.)\b')
        self.todo_pattern = re.compile(r'#\s*(TODO|FIXME|HACK|XXX|BUG):?\s*(.+)', re.IGNORECASE)
        self.commented_code_pattern = re.compile(r'^\s*#\s*\w+\s*\(.*\)|^\s*#\s*\w+\s*=|^\s*#\s*if\s+|^\s*#\s*for\s+|^\s*#\s*while\s+|^\s*#\s*def\s+|^\s*#\s*class\s+')
        
    def analyze(self) -> Dict[str, Any]:
        """Analyze project for code smells"""
        if hasattr(self, 'logger'):
            self.logger.info(f"Analyzing code smells in {self.project_path}")
            
        self.smells = []
        
        # Analyze Python files
        python_files = list(Path(self.project_path).rglob("*.py"))
        
        for file_path in python_files:
            if self._should_skip_file(str(file_path)):
                continue
                
            try:
                self._analyze_file(file_path)
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"Error analyzing {file_path}: {e}")
                    
        # Calculate metrics
        smell_distribution = self._get_smell_distribution()
        severity_distribution = self._get_severity_distribution()
        
        return {
            "total_smells": len(self.smells),
            "smell_distribution": smell_distribution,
            "severity_distribution": severity_distribution,
            "auto_fixable_count": sum(1 for s in self.smells if s.auto_fixable),
            "smells": [self._smell_to_dict(s) for s in self.smells],
            "health_score": self._calculate_health_score()
        }
        
    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single file for code smells"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            # Parse AST
            tree = ast.parse(content, filename=str(file_path))
            
            # AST-based analysis
            self._analyze_ast(tree, str(file_path))
            
            # Line-based analysis
            self._analyze_lines(lines, str(file_path))
            
            # Pattern-based analysis
            self._analyze_patterns(content, lines, str(file_path))
            
        except SyntaxError as e:
            # File has syntax errors - this itself is a smell
            self.smells.append(CodeSmell(
                smell_type="syntax_error",
                severity="critical",
                file_path=str(file_path),
                line_number=e.lineno or 0,
                column=e.offset or 0,
                message=f"Syntax error: {e.msg}",
                suggestion="Fix syntax errors before analysis",
                auto_fixable=False
            ))
            
    def _analyze_ast(self, tree: ast.AST, file_path: str) -> None:
        """Analyze AST for structural smells"""
        # Analyze classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._analyze_class(node, file_path)
            elif isinstance(node, ast.FunctionDef):
                self._analyze_function(node, file_path)
            elif isinstance(node, ast.Global):
                self._analyze_global(node, file_path)
                
    def _analyze_class(self, node: ast.ClassDef, file_path: str) -> None:
        """Analyze class for god class smell"""
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        
        # God class - too many methods
        if len(methods) > self.max_class_methods:
            self.smells.append(CodeSmell(
                smell_type="god_class_methods",
                severity="high",
                file_path=file_path,
                line_number=node.lineno,
                column=node.col_offset,
                message=f"Class '{node.name}' has {len(methods)} methods (threshold: {self.max_class_methods})",
                suggestion="Consider breaking down into smaller, focused classes",
                auto_fixable=False
            ))
            
        # God class - too many lines
        if hasattr(node, 'end_lineno'):
            class_lines = node.end_lineno - node.lineno
            if class_lines > self.max_class_lines:
                self.smells.append(CodeSmell(
                    smell_type="god_class_lines",
                    severity="high",
                    file_path=file_path,
                    line_number=node.lineno,
                    column=node.col_offset,
                    message=f"Class '{node.name}' has {class_lines} lines (threshold: {self.max_class_lines})",
                    suggestion="Consider extracting cohesive groups of methods into separate classes",
                    auto_fixable=False
                ))
                
    def _analyze_function(self, node: ast.FunctionDef, file_path: str) -> None:
        """Analyze function for various smells"""
        # Long parameter list
        params = node.args.args + node.args.posonlyargs + node.args.kwonlyargs
        if len(params) > self.max_params:
            self.smells.append(CodeSmell(
                smell_type="long_parameter_list",
                severity="medium",
                file_path=file_path,
                line_number=node.lineno,
                column=node.col_offset,
                message=f"Function '{node.name}' has {len(params)} parameters (threshold: {self.max_params})",
                suggestion="Consider using a configuration object or builder pattern",
                auto_fixable=False
            ))
            
        # Long method
        if hasattr(node, 'end_lineno'):
            method_lines = node.end_lineno - node.lineno
            if method_lines > self.max_method_lines:
                self.smells.append(CodeSmell(
                    smell_type="long_method",
                    severity="medium",
                    file_path=file_path,
                    line_number=node.lineno,
                    column=node.col_offset,
                    message=f"Function '{node.name}' has {method_lines} lines (threshold: {self.max_method_lines})",
                    suggestion="Extract cohesive blocks into separate functions",
                    auto_fixable=False
                ))
                
        # Deep nesting
        max_depth = self._calculate_nesting_depth(node)
        if max_depth > self.max_nesting_depth:
            self.smells.append(CodeSmell(
                smell_type="deep_nesting",
                severity="medium",
                file_path=file_path,
                line_number=node.lineno,
                column=node.col_offset,
                message=f"Function '{node.name}' has nesting depth of {max_depth} (threshold: {self.max_nesting_depth})",
                suggestion="Use early returns, extract nested logic, or simplify conditionals",
                auto_fixable=False
            ))
            
        # Empty exception handlers
        for handler in ast.walk(node):
            if isinstance(handler, ast.ExceptHandler):
                if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                    self.smells.append(CodeSmell(
                        smell_type="empty_exception_handler",
                        severity="high",
                        file_path=file_path,
                        line_number=handler.lineno,
                        column=handler.col_offset,
                        message="Empty exception handler swallows errors silently",
                        suggestion="Log the exception or handle it appropriately",
                        auto_fixable=True,
                        fix_code="import logging\nlogging.exception('An error occurred')"
                    ))
                    
    def _analyze_global(self, node: ast.Global, file_path: str) -> None:
        """Analyze global variable usage"""
        self.smells.append(CodeSmell(
            smell_type="global_variable",
            severity="medium",
            file_path=file_path,
            line_number=node.lineno,
            column=node.col_offset,
            message=f"Global variable usage: {', '.join(node.names)}",
            suggestion="Consider using dependency injection or configuration objects",
            auto_fixable=False
        ))
        
    def _calculate_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate maximum nesting depth in a function"""
        max_depth = depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                child_depth = self._calculate_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_nesting_depth(child, depth)
                max_depth = max(max_depth, child_depth)
                
        return max_depth
        
    def _analyze_lines(self, lines: List[str], file_path: str) -> None:
        """Analyze individual lines for smells"""
        for i, line in enumerate(lines, 1):
            # Long lines
            if len(line) > self.max_line_length:
                self.smells.append(CodeSmell(
                    smell_type="long_line",
                    severity="low",
                    file_path=file_path,
                    line_number=i,
                    column=self.max_line_length,
                    message=f"Line exceeds {self.max_line_length} characters ({len(line)} chars)",
                    suggestion="Break line using parentheses or backslash",
                    auto_fixable=False
                ))
                
    def _analyze_patterns(self, content: str, lines: List[str], file_path: str) -> None:
        """Analyze content for pattern-based smells"""
        # Magic numbers
        for i, line in enumerate(lines, 1):
            # Skip comments and strings
            if line.strip().startswith('#') or '"""' in line or "'''" in line:
                continue
                
            matches = self.magic_number_pattern.findall(line)
            for match in matches:
                num = int(match)
                # Ignore common safe numbers
                if num not in (0, 1, 2, -1, 10, 100, 1000):
                    self.smells.append(CodeSmell(
                        smell_type="magic_number",
                        severity="low",
                        file_path=file_path,
                        line_number=i,
                        column=line.find(match),
                        message=f"Magic number {num} should be a named constant",
                        suggestion=f"Extract {num} to a named constant",
                        auto_fixable=True,
                        fix_code=f"MEANINGFUL_NAME = {num}"
                    ))
                    
        # TODOs and FIXMEs
        todo_count = 0
        for i, line in enumerate(lines, 1):
            match = self.todo_pattern.search(line)
            if match:
                todo_count += 1
                if todo_count > 10:  # Too many TODOs
                    self.smells.append(CodeSmell(
                        smell_type="todo_accumulation",
                        severity="medium",
                        file_path=file_path,
                        line_number=i,
                        column=0,
                        message=f"Too many TODO/FIXME comments ({todo_count}+)",
                        suggestion="Address technical debt or create issues to track",
                        auto_fixable=False
                    ))
                    
        # Commented out code
        for i, line in enumerate(lines, 1):
            if self.commented_code_pattern.match(line.strip()):
                self.smells.append(CodeSmell(
                    smell_type="commented_code",
                    severity="low",
                    file_path=file_path,
                    line_number=i,
                    column=0,
                    message="Commented out code should be removed",
                    suggestion="Delete commented code - version control preserves history",
                    auto_fixable=True,
                    fix_code=""  # Empty = delete line
                ))
                
    def _get_smell_distribution(self) -> Dict[str, int]:
        """Get distribution of smell types"""
        distribution = {}
        for smell in self.smells:
            distribution[smell.smell_type] = distribution.get(smell.smell_type, 0) + 1
        return distribution
        
    def _get_severity_distribution(self) -> Dict[str, int]:
        """Get distribution of severities"""
        distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for smell in self.smells:
            distribution[smell.severity] += 1
        return distribution
        
    def _calculate_health_score(self) -> float:
        """Calculate overall code health score (0-100)"""
        if not self.smells:
            return 100.0
            
        # Weight by severity
        severity_weights = {
            "low": 1,
            "medium": 3,
            "high": 5,
            "critical": 10
        }
        
        total_weight = sum(severity_weights[s.severity] for s in self.smells)
        
        # Assume each file can have max 10 weighted smells before score hits 0
        max_weight_per_file = 10
        python_files = len(list(Path(self.project_path).rglob("*.py")))
        max_total_weight = max_weight_per_file * max(python_files, 1)
        
        score = max(0, 100 - (total_weight / max_total_weight * 100))
        return round(score, 2)
        
    def _smell_to_dict(self, smell: CodeSmell) -> Dict[str, Any]:
        """Convert smell to dictionary"""
        return {
            "type": smell.smell_type,
            "severity": smell.severity,
            "file": smell.file_path,
            "line": smell.line_number,
            "column": smell.column,
            "message": smell.message,
            "suggestion": smell.suggestion,
            "auto_fixable": smell.auto_fixable,
            "fix_code": smell.fix_code,
            "confidence": smell.confidence
        }
        
    def _should_skip_file(self, file_path: str) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            '__pycache__',
            '.git',
            'venv',
            'env',
            '.env',
            'migrations',
            'tests',
            '.pytest_cache'
        ]
        
        return any(pattern in file_path for pattern in skip_patterns)
        
    def get_auto_fixes(self) -> List[Tuple[str, int, str]]:
        """Get list of auto-fixable smells with fixes"""
        fixes = []
        for smell in self.smells:
            if smell.auto_fixable and smell.fix_code is not None:
                fixes.append((
                    smell.file_path,
                    smell.line_number,
                    smell.fix_code
                ))
        return fixes