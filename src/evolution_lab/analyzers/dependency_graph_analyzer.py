"""
Dependency Graph Analyzer - Advanced Code Relationship Mapping
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

Analyzes and visualizes multi-level code dependencies:
- Module dependencies
- Class hierarchies
- Function call graphs
- Data flow analysis
"""

import ast
import os
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
import json
import networkx as nx
from dataclasses import dataclass, field

from .base import BaseAnalyzer, AnalysisResult


@dataclass
class CodeNode:
    """Represents a node in the dependency graph"""
    id: str
    name: str
    type: str  # 'module', 'class', 'function', 'method'
    file_path: str
    line_number: int
    complexity: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeEdge:
    """Represents an edge in the dependency graph"""
    source: str
    target: str
    edge_type: str  # 'import', 'inheritance', 'call', 'data_flow'
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class DependencyGraphAnalyzer(BaseAnalyzer):
    """
    Creates comprehensive dependency graphs for Python projects.
    
    Features:
    - Multi-level analysis (module, class, function)
    - Cycle detection
    - Centrality metrics
    - Coupling/cohesion analysis
    - Architecture smell detection
    """
    
    def __init__(self, project_path: str):
        super().__init__(project_path)
        self.module_graph = nx.DiGraph()
        self.class_graph = nx.DiGraph()
        self.function_graph = nx.DiGraph()
        self.nodes: Dict[str, CodeNode] = {}
        self.edges: List[CodeEdge] = []
        self.import_map: Dict[str, Set[str]] = defaultdict(set)
        self.call_graph: Dict[str, Set[str]] = defaultdict(set)
        self.inheritance_map: Dict[str, Set[str]] = defaultdict(set)
        
    async def analyze(self) -> AnalysisResult:
        """Perform comprehensive dependency analysis"""
        python_files = self._get_python_files()
        
        # Phase 1: Parse all files and build initial maps
        for file_path in python_files:
            self._analyze_file(file_path)
            
        # Phase 2: Build graphs
        self._build_module_graph()
        self._build_class_graph()
        self._build_function_graph()
        
        # Phase 3: Analyze graph properties
        metrics = self._analyze_graph_metrics()
        
        # Phase 4: Detect issues
        issues = self._detect_dependency_issues()
        
        # Phase 5: Generate suggestions
        suggestions = self._generate_suggestions(metrics, issues)
        
        # Add score to metrics
        metrics['score'] = metrics.get('health_score', 70.0)
        
        return AnalysisResult(
            analyzer_name="DependencyGraphAnalyzer",
            metrics=metrics,
            issues=issues,
            suggestions=suggestions
        )
        
    def _analyze_file(self, file_path: str):
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            relative_path = os.path.relpath(file_path, self.project_path)
            
            # Create module node
            module_id = self._path_to_module_id(relative_path)
            self.nodes[module_id] = CodeNode(
                id=module_id,
                name=module_id,
                type='module',
                file_path=relative_path,
                line_number=0
            )
            
            # Visit AST nodes
            visitor = DependencyVisitor(
                file_path=relative_path,
                module_id=module_id,
                analyzer=self
            )
            visitor.visit(tree)
            
        except Exception as e:
            self.logger.error(f"Error analyzing {file_path}: {e}")
            
    def _build_module_graph(self):
        """Build module-level dependency graph"""
        # Add nodes
        for node_id, node in self.nodes.items():
            if node.type == 'module':
                self.module_graph.add_node(
                    node_id,
                    name=node.name,
                    file_path=node.file_path,
                    complexity=node.complexity
                )
                
        # Add edges from imports
        for module, imports in self.import_map.items():
            for imported in imports:
                if imported in self.nodes:
                    self.module_graph.add_edge(
                        module, imported,
                        edge_type='import',
                        weight=1.0
                    )
                    
    def _build_class_graph(self):
        """Build class hierarchy and relationship graph"""
        # Add class nodes
        for node_id, node in self.nodes.items():
            if node.type == 'class':
                self.class_graph.add_node(
                    node_id,
                    name=node.name,
                    file_path=node.file_path,
                    line_number=node.line_number,
                    complexity=node.complexity
                )
                
        # Add inheritance edges
        for child, parents in self.inheritance_map.items():
            for parent in parents:
                if parent in self.nodes:
                    self.class_graph.add_edge(
                        child, parent,
                        edge_type='inheritance',
                        weight=2.0  # Higher weight for inheritance
                    )
                    
        # Add usage edges from call graph
        for caller, callees in self.call_graph.items():
            if caller in self.class_graph:
                for callee in callees:
                    if callee in self.class_graph and caller != callee:
                        self.class_graph.add_edge(
                            caller, callee,
                            edge_type='usage',
                            weight=1.0
                        )
                        
    def _build_function_graph(self):
        """Build function call graph"""
        # Add function/method nodes
        for node_id, node in self.nodes.items():
            if node.type in ['function', 'method']:
                self.function_graph.add_node(
                    node_id,
                    name=node.name,
                    file_path=node.file_path,
                    line_number=node.line_number,
                    complexity=node.complexity,
                    parent_class=node.metadata.get('parent_class')
                )
                
        # Add call edges
        for caller, callees in self.call_graph.items():
            if caller in self.function_graph:
                for callee in callees:
                    if callee in self.function_graph and caller != callee:
                        self.function_graph.add_edge(
                            caller, callee,
                            edge_type='call',
                            weight=1.0
                        )
                        
    def _analyze_graph_metrics(self) -> Dict[str, Any]:
        """Analyze graph properties and metrics"""
        metrics = {
            'module_metrics': self._analyze_module_metrics(),
            'class_metrics': self._analyze_class_metrics(),
            'function_metrics': self._analyze_function_metrics(),
            'overall_metrics': self._calculate_overall_metrics(),
            'health_score': 0.0
        }
        
        # Calculate health score based on metrics
        metrics['health_score'] = self._calculate_health_score(metrics)
        
        return metrics
        
    def _analyze_module_metrics(self) -> Dict[str, Any]:
        """Analyze module-level metrics"""
        if not self.module_graph.nodes():
            return {}
            
        return {
            'total_modules': self.module_graph.number_of_nodes(),
            'total_dependencies': self.module_graph.number_of_edges(),
            'avg_dependencies': self.module_graph.number_of_edges() / max(1, self.module_graph.number_of_nodes()),
            'cycles': list(nx.simple_cycles(self.module_graph)),
            'strongly_connected_components': list(nx.strongly_connected_components(self.module_graph)),
            'centrality': {
                'degree': dict(nx.degree_centrality(self.module_graph)),
                'betweenness': dict(nx.betweenness_centrality(self.module_graph)),
                'closeness': dict(nx.closeness_centrality(self.module_graph))
            }
        }
        
    def _analyze_class_metrics(self) -> Dict[str, Any]:
        """Analyze class-level metrics"""
        if not self.class_graph.nodes():
            return {}
            
        # Calculate coupling and cohesion
        coupling_scores = {}
        for node in self.class_graph.nodes():
            out_degree = self.class_graph.out_degree(node)
            in_degree = self.class_graph.in_degree(node)
            coupling_scores[node] = {
                'afferent_coupling': in_degree,  # Classes that depend on this
                'efferent_coupling': out_degree,  # Classes this depends on
                'instability': out_degree / max(1, in_degree + out_degree)
            }
            
        return {
            'total_classes': self.class_graph.number_of_nodes(),
            'inheritance_depth': self._calculate_max_inheritance_depth(),
            'avg_coupling': sum(c['efferent_coupling'] for c in coupling_scores.values()) / max(1, len(coupling_scores)),
            'coupling_scores': coupling_scores,
            'cycles': list(nx.simple_cycles(self.class_graph)),
            'god_classes': self._detect_god_classes()
        }
        
    def _analyze_function_metrics(self) -> Dict[str, Any]:
        """Analyze function-level metrics"""
        if not self.function_graph.nodes():
            return {}
            
        return {
            'total_functions': self.function_graph.number_of_nodes(),
            'total_calls': self.function_graph.number_of_edges(),
            'avg_calls_per_function': self.function_graph.number_of_edges() / max(1, self.function_graph.number_of_nodes()),
            'call_depth': self._calculate_max_call_depth(),
            'recursive_functions': self._detect_recursive_functions(),
            'unreachable_functions': self._detect_unreachable_functions(),
            'hotspots': self._detect_function_hotspots()
        }
        
    def _calculate_overall_metrics(self) -> Dict[str, Any]:
        """Calculate overall project metrics"""
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'modularity': self._calculate_modularity(),
            'maintainability_index': self._calculate_maintainability_index(),
            'architectural_debt': self._estimate_architectural_debt()
        }
        
    def _detect_dependency_issues(self) -> List[Dict[str, Any]]:
        """Detect dependency-related issues"""
        issues = []
        
        # Circular dependencies
        module_cycles = list(nx.simple_cycles(self.module_graph))
        for cycle in module_cycles:
            issues.append({
                'type': 'circular_dependency',
                'severity': 'high',
                'message': f"Circular dependency detected: {' -> '.join(cycle)}",
                'nodes': cycle
            })
            
        # God classes
        god_classes = self._detect_god_classes()
        for class_name, metrics in god_classes.items():
            issues.append({
                'type': 'god_class',
                'severity': 'medium',
                'message': f"God class detected: {class_name} (coupling: {metrics['coupling']}, methods: {metrics['methods']})",
                'node': class_name
            })
            
        # Deep inheritance
        max_depth = self._calculate_max_inheritance_depth()
        if max_depth > 4:
            issues.append({
                'type': 'deep_inheritance',
                'severity': 'medium',
                'message': f"Deep inheritance hierarchy detected (depth: {max_depth})",
                'metric': max_depth
            })
            
        # High coupling
        if hasattr(self, 'class_graph'):
            for node in self.class_graph.nodes():
                out_degree = self.class_graph.out_degree(node)
                if out_degree > 10:
                    issues.append({
                        'type': 'high_coupling',
                        'severity': 'medium',
                        'message': f"High coupling in {node} ({out_degree} dependencies)",
                        'node': node,
                        'metric': out_degree
                    })
                    
        return issues
        
    def _generate_suggestions(self, metrics: Dict[str, Any], issues: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Based on circular dependencies
        if any(i['type'] == 'circular_dependency' for i in issues):
            suggestions.append("Refactor circular dependencies by introducing interfaces or dependency injection")
            
        # Based on god classes
        god_classes = [i for i in issues if i['type'] == 'god_class']
        if god_classes:
            suggestions.append("Split god classes using Single Responsibility Principle")
            suggestions.append("Consider extracting behavior into smaller, focused classes")
            
        # Based on coupling
        high_coupling = [i for i in issues if i['type'] == 'high_coupling']
        if high_coupling:
            suggestions.append("Reduce coupling by using dependency injection and interfaces")
            suggestions.append("Consider applying the Dependency Inversion Principle")
            
        # Based on metrics
        if metrics.get('module_metrics', {}).get('avg_dependencies', 0) > 5:
            suggestions.append("Consider modularizing the codebase to reduce average dependencies")
            
        if metrics.get('function_metrics', {}).get('call_depth', 0) > 10:
            suggestions.append("Refactor deep call chains to improve readability and testability")
            
        # Architecture suggestions
        suggestions.append("Generate dependency graph visualization for better understanding")
        suggestions.append("Use layered architecture to enforce dependency rules")
        
        return suggestions
        
    def _calculate_health_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall health score"""
        score = 100.0
        
        # Deduct for circular dependencies
        module_cycles = len(metrics.get('module_metrics', {}).get('cycles', []))
        score -= module_cycles * 10
        
        # Deduct for high coupling
        avg_coupling = metrics.get('class_metrics', {}).get('avg_coupling', 0)
        if avg_coupling > 5:
            score -= (avg_coupling - 5) * 2
            
        # Deduct for deep inheritance
        inheritance_depth = metrics.get('class_metrics', {}).get('inheritance_depth', 0)
        if inheritance_depth > 4:
            score -= (inheritance_depth - 4) * 5
            
        # Deduct for maintainability issues
        maintainability = metrics.get('overall_metrics', {}).get('maintainability_index', 100)
        score = score * (maintainability / 100)
        
        return max(0, min(100, score))
        
    def _get_python_files(self) -> List[str]:
        """Get all Python files in the project"""
        python_files = []
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files
        
    def _path_to_module_id(self, path: str) -> str:
        """Convert file path to module ID"""
        return path.replace('/', '.').replace('\\', '.').replace('.py', '')
        
    def _calculate_max_inheritance_depth(self) -> int:
        """Calculate maximum inheritance depth"""
        if not self.class_graph.nodes():
            return 0
            
        max_depth = 0
        for node in self.class_graph.nodes():
            depth = self._get_inheritance_depth(node)
            max_depth = max(max_depth, depth)
            
        return max_depth
        
    def _get_inheritance_depth(self, node: str, visited: Optional[Set[str]] = None) -> int:
        """Get inheritance depth for a class"""
        if visited is None:
            visited = set()
            
        if node in visited:
            return 0
            
        visited.add(node)
        
        parents = list(self.class_graph.successors(node))
        if not parents:
            return 0
            
        return 1 + max(self._get_inheritance_depth(p, visited.copy()) for p in parents)
        
    def _detect_god_classes(self) -> Dict[str, Dict[str, Any]]:
        """Detect god classes based on coupling and size"""
        god_classes = {}
        
        for node_id, node in self.nodes.items():
            if node.type == 'class':
                # Check coupling
                if node_id in self.class_graph:
                    coupling = self.class_graph.out_degree(node_id)
                    methods = len([n for n in self.nodes.values() 
                                 if n.type == 'method' and n.metadata.get('parent_class') == node_id])
                    
                    # God class criteria
                    if coupling > 10 or methods > 20:
                        god_classes[node_id] = {
                            'coupling': coupling,
                            'methods': methods,
                            'complexity': node.complexity
                        }
                        
        return god_classes
        
    def _calculate_max_call_depth(self) -> int:
        """Calculate maximum call depth"""
        if not self.function_graph.nodes():
            return 0
            
        max_depth = 0
        for node in self.function_graph.nodes():
            if self.function_graph.in_degree(node) == 0:  # Entry points
                depth = self._get_call_depth(node)
                max_depth = max(max_depth, depth)
                
        return max_depth
        
    def _get_call_depth(self, node: str, visited: Optional[Set[str]] = None) -> int:
        """Get call depth from a function"""
        if visited is None:
            visited = set()
            
        if node in visited:
            return 0
            
        visited.add(node)
        
        callees = list(self.function_graph.successors(node))
        if not callees:
            return 0
            
        return 1 + max(self._get_call_depth(c, visited.copy()) for c in callees)
        
    def _detect_recursive_functions(self) -> List[str]:
        """Detect recursive function calls"""
        recursive = []
        
        for node in self.function_graph.nodes():
            if self.function_graph.has_edge(node, node):
                recursive.append(node)
            else:
                # Check for indirect recursion
                for path in nx.all_simple_paths(self.function_graph, node, node):
                    if len(path) > 1:
                        recursive.append(node)
                        break
                        
        return recursive
        
    def _detect_unreachable_functions(self) -> List[str]:
        """Detect unreachable functions"""
        # Entry points: functions with no incoming calls or special names
        entry_points = set()
        special_names = {'main', '__init__', 'setup', 'teardown', 'test_'}
        
        for node in self.function_graph.nodes():
            if (self.function_graph.in_degree(node) == 0 or 
                any(node.endswith(name) for name in special_names)):
                entry_points.add(node)
                
        # Find all reachable nodes from entry points
        reachable = set()
        for entry in entry_points:
            reachable.update(nx.descendants(self.function_graph, entry))
            reachable.add(entry)
            
        # Unreachable = all nodes - reachable
        unreachable = set(self.function_graph.nodes()) - reachable
        
        return list(unreachable)
        
    def _detect_function_hotspots(self) -> List[Tuple[str, float]]:
        """Detect function hotspots (highly connected functions)"""
        if not self.function_graph.nodes():
            return []
            
        # Use degree centrality as a simpler alternative to PageRank
        # (in-degree + out-degree) as importance metric
        hotspots = []
        for node in self.function_graph.nodes():
            in_degree = self.function_graph.in_degree(node)
            out_degree = self.function_graph.out_degree(node)
            total_degree = in_degree + out_degree
            if total_degree > 0:
                hotspots.append((node, total_degree))
        
        # Sort by importance
        hotspots.sort(key=lambda x: x[1], reverse=True)
        
        # Return top 10
        return hotspots[:10]
        
    def _calculate_modularity(self) -> float:
        """Calculate modularity score"""
        if not self.module_graph.nodes():
            return 0.0
            
        # Use Louvain method for community detection
        try:
            import community
            partition = community.best_partition(self.module_graph.to_undirected())
            modularity = community.modularity(partition, self.module_graph.to_undirected())
            return modularity
        except:
            # Fallback: simple ratio of internal vs external edges
            internal_edges = 0
            external_edges = 0
            
            for edge in self.module_graph.edges():
                src_module = edge[0].split('.')[0]
                dst_module = edge[1].split('.')[0]
                
                if src_module == dst_module:
                    internal_edges += 1
                else:
                    external_edges += 1
                    
            total_edges = internal_edges + external_edges
            if total_edges == 0:
                return 1.0
                
            return internal_edges / total_edges
            
    def _calculate_maintainability_index(self) -> float:
        """Calculate maintainability index"""
        # Simplified maintainability index based on:
        # - Cyclomatic complexity
        # - Lines of code
        # - Coupling
        
        avg_complexity = sum(n.complexity for n in self.nodes.values()) / max(1, len(self.nodes))
        avg_coupling = self.module_graph.number_of_edges() / max(1, self.module_graph.number_of_nodes())
        
        # Formula: MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)
        # Simplified version
        maintainability = 100 - (avg_complexity * 2) - (avg_coupling * 5)
        
        return max(0, min(100, maintainability))
        
    def _estimate_architectural_debt(self) -> float:
        """Estimate architectural technical debt in hours"""
        debt_hours = 0.0
        
        # Circular dependencies: 8 hours each
        module_cycles = list(nx.simple_cycles(self.module_graph))
        debt_hours += len(module_cycles) * 8
        
        # God classes: 16 hours each
        god_classes = self._detect_god_classes()
        debt_hours += len(god_classes) * 16
        
        # High coupling: 4 hours per highly coupled class
        if hasattr(self, 'class_graph'):
            for node in self.class_graph.nodes():
                if self.class_graph.out_degree(node) > 10:
                    debt_hours += 4
                    
        # Deep inheritance: 2 hours per level beyond 4
        max_depth = self._calculate_max_inheritance_depth()
        if max_depth > 4:
            debt_hours += (max_depth - 4) * 2
            
        return debt_hours
        
    def export_graphs(self, output_dir: str):
        """Export graphs in various formats"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Export as JSON for visualization
        graphs = {
            'module_graph': nx.node_link_data(self.module_graph),
            'class_graph': nx.node_link_data(self.class_graph),
            'function_graph': nx.node_link_data(self.function_graph)
        }
        
        with open(os.path.join(output_dir, 'dependency_graphs.json'), 'w') as f:
            json.dump(graphs, f, indent=2)
            
        # Export as GraphML for tools like Gephi
        nx.write_graphml(self.module_graph, os.path.join(output_dir, 'module_graph.graphml'))
        nx.write_graphml(self.class_graph, os.path.join(output_dir, 'class_graph.graphml'))
        nx.write_graphml(self.function_graph, os.path.join(output_dir, 'function_graph.graphml'))
        
        # Export as DOT for Graphviz
        try:
            from networkx.drawing.nx_agraph import write_dot
            write_dot(self.module_graph, os.path.join(output_dir, 'module_graph.dot'))
            write_dot(self.class_graph, os.path.join(output_dir, 'class_graph.dot'))
            write_dot(self.function_graph, os.path.join(output_dir, 'function_graph.dot'))
        except ImportError:
            self.logger.warning("pygraphviz not installed, skipping DOT export")


class DependencyVisitor(ast.NodeVisitor):
    """AST visitor to extract dependencies"""
    
    def __init__(self, file_path: str, module_id: str, analyzer: DependencyGraphAnalyzer):
        self.file_path = file_path
        self.module_id = module_id
        self.analyzer = analyzer
        self.current_class = None
        self.current_function = None
        
    def visit_Import(self, node):
        """Handle import statements"""
        for alias in node.names:
            imported_module = alias.name
            self.analyzer.import_map[self.module_id].add(imported_module)
            
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        """Handle from...import statements"""
        if node.module:
            self.analyzer.import_map[self.module_id].add(node.module)
            
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        """Handle class definitions"""
        class_id = f"{self.module_id}.{node.name}"
        
        # Create class node
        self.analyzer.nodes[class_id] = CodeNode(
            id=class_id,
            name=node.name,
            type='class',
            file_path=self.file_path,
            line_number=node.lineno,
            complexity=len(node.body)
        )
        
        # Handle inheritance
        for base in node.bases:
            if isinstance(base, ast.Name):
                parent_id = f"{self.module_id}.{base.id}"
                self.analyzer.inheritance_map[class_id].add(parent_id)
            elif isinstance(base, ast.Attribute):
                # Handle module.Class inheritance
                parent_id = self._get_full_name(base)
                if parent_id:
                    self.analyzer.inheritance_map[class_id].add(parent_id)
                    
        # Visit class body
        old_class = self.current_class
        self.current_class = class_id
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_FunctionDef(self, node):
        """Handle function definitions"""
        if self.current_class:
            func_id = f"{self.current_class}.{node.name}"
            func_type = 'method'
            parent_class = self.current_class
        else:
            func_id = f"{self.module_id}.{node.name}"
            func_type = 'function'
            parent_class = None
            
        # Create function node
        self.analyzer.nodes[func_id] = CodeNode(
            id=func_id,
            name=node.name,
            type=func_type,
            file_path=self.file_path,
            line_number=node.lineno,
            complexity=self._calculate_complexity(node),
            metadata={'parent_class': parent_class}
        )
        
        # Visit function body
        old_function = self.current_function
        self.current_function = func_id
        self.generic_visit(node)
        self.current_function = old_function
        
    def visit_Call(self, node):
        """Handle function calls"""
        if self.current_function:
            called_name = self._get_call_name(node.func)
            if called_name:
                # Try to resolve to full name
                if '.' not in called_name and self.current_class:
                    # Could be a method call
                    full_name = f"{self.current_class}.{called_name}"
                    if full_name in self.analyzer.nodes:
                        called_name = full_name
                        
                self.analyzer.call_graph[self.current_function].add(called_name)
                
        self.generic_visit(node)
        
    def _get_full_name(self, node) -> Optional[str]:
        """Get full name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value = self._get_full_name(node.value)
            if value:
                return f"{value}.{node.attr}"
        return None
        
    def _get_call_name(self, node) -> Optional[str]:
        """Extract function name from call node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None
        
    def _calculate_complexity(self, node) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With):
                complexity += 1
            elif isinstance(child, ast.Assert):
                complexity += 1
            elif isinstance(child, ast.Raise):
                complexity += 1
                
        return complexity