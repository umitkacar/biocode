"""
Performance and Optimization Analyzer
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import re
import ast
from typing import Any, Dict, List
from pathlib import Path
from collections import defaultdict

from .base import BaseAnalyzer, AnalysisResult


class PerformanceAnalyzer(BaseAnalyzer):
    """Analyzes performance bottlenecks and optimization opportunities"""
    
    def analyze(self) -> AnalysisResult:
        """Analyze performance characteristics"""
        self.start_timer()
        
        metrics = {
            'algorithmic_complexity': self._analyze_algorithmic_complexity(),
            'database_operations': self._analyze_database_operations(),
            'memory_usage': self._analyze_memory_patterns(),
            'async_patterns': self._analyze_async_patterns(),
            'caching': self._analyze_caching_strategies(),
            'loops_analysis': self._analyze_loops(),
            'api_performance': self._analyze_api_performance(),
            'file_operations': self._analyze_file_operations(),
            'concurrency': self._analyze_concurrency(),
            'profiling': self._check_profiling_tools(),
        }
        
        metrics['performance_score'] = self._calculate_performance_score(metrics)
        metrics['analysis_time'] = self.get_elapsed_time()
        
        issues = self._detect_performance_issues(metrics)
        suggestions = self._generate_performance_suggestions(metrics)
        
        return AnalysisResult(
            analyzer_name=self.name,
            metrics=metrics,
            issues=issues,
            suggestions=suggestions,
            metadata={
                'project_path': str(self.project_path),
                'optimization_opportunities': len(suggestions),
            },
        )
    
    def _analyze_algorithmic_complexity(self) -> Dict[str, Any]:
        """Analyze algorithmic complexity patterns"""
        complexity_info = {
            'nested_loops': [],
            'recursive_functions': [],
            'quadratic_operations': [],
            'sorting_operations': 0,
            'searching_operations': 0,
        }
        
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                
                # Analyze AST for complexity patterns
                for node in ast.walk(tree):
                    # Detect nested loops
                    if isinstance(node, ast.For):
                        for child in ast.walk(node):
                            if child != node and isinstance(child, ast.For):
                                line_num = node.lineno
                                complexity_info['nested_loops'].append({
                                    'file': str(file_path.relative_to(self.project_path)),
                                    'line': line_num,
                                    'depth': self._get_loop_depth(node),
                                })
                                break
                    
                    # Detect recursive functions
                    elif isinstance(node, ast.FunctionDef):
                        if self._is_recursive(node):
                            complexity_info['recursive_functions'].append({
                                'function': node.name,
                                'file': str(file_path.relative_to(self.project_path)),
                                'line': node.lineno,
                            })
                    
                    # Detect sorting operations
                    elif isinstance(node, ast.Call):
                        if hasattr(node.func, 'id') and node.func.id in ['sorted', 'sort']:
                            complexity_info['sorting_operations'] += 1
                        elif hasattr(node.func, 'attr') and node.func.attr in ['sort']:
                            complexity_info['sorting_operations'] += 1
                            
            except Exception:
                pass
        
        return complexity_info
    
    def _get_loop_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Get the depth of nested loops"""
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While)):
                child_depth = self._get_loop_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        return max_depth
    
    def _is_recursive(self, func_node: ast.FunctionDef) -> bool:
        """Check if a function is recursive"""
        func_name = func_node.name
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'id') and node.func.id == func_name:
                    return True
        return False
    
    def _analyze_database_operations(self) -> Dict[str, Any]:
        """Analyze database query patterns"""
        db_info = {
            'n_plus_one_queries': [],
            'missing_indexes': [],
            'bulk_operations': 0,
            'raw_queries': 0,
            'query_optimization': [],
            'connection_pooling': False,
        }
        
        # Database operation patterns
        db_patterns = {
            'n_plus_one': r'for\s+\w+\s+in\s+.*\.(?:all|filter|objects).*:\s*\n.*\.(get|filter|all)',
            'raw_query': r'execute\s*\(|raw\s*\(|cursor\.execute',
            'bulk_create': r'bulk_create|bulk_update|bulk_insert',
            'select_related': r'select_related|prefetch_related',
            'connection_pool': r'pool|Pool|CONNECTION_POOL|create_pool',
            'index_hint': r'db_index|index=True|Index\(',
        }
        
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                content = file_path.read_text()
                
                # Check for N+1 query patterns
                n_plus_matches = re.finditer(db_patterns['n_plus_one'], content, re.MULTILINE)
                for match in n_plus_matches:
                    line_num = content[:match.start()].count('\n') + 1
                    db_info['n_plus_one_queries'].append({
                        'file': str(file_path.relative_to(self.project_path)),
                        'line': line_num,
                    })
                
                # Count various operations
                db_info['raw_queries'] += len(re.findall(db_patterns['raw_query'], content))
                db_info['bulk_operations'] += len(re.findall(db_patterns['bulk_create'], content))
                
                if re.search(db_patterns['connection_pool'], content):
                    db_info['connection_pooling'] = True
                    
                # Check for query optimization
                if re.search(db_patterns['select_related'], content):
                    db_info['query_optimization'].append('prefetch_related/select_related')
                    
            except Exception:
                pass
        
        return db_info
    
    def _analyze_memory_patterns(self) -> Dict[str, Any]:
        """Analyze memory usage patterns"""
        memory_info = {
            'large_data_structures': [],
            'memory_leaks_risk': [],
            'generators_used': 0,
            'list_comprehensions': 0,
            'memory_efficient_practices': [],
        }
        
        memory_patterns = {
            'large_list': r'list\s*\(.*range\s*\(\s*\d{4,}',
            'memory_leak': r'global\s+\w+|cache\s*=\s*\{\}|\[\s*\]\s*\*\s*\d{4,}',
            'generator': r'yield|generator|Generator',
            'list_comp': r'\[.*for.*in.*\]',
            'memory_efficient': r'itertools|deque|array\.array|numpy',
        }
        
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                content = file_path.read_text()
                
                # Check for large data structures
                large_matches = re.finditer(memory_patterns['large_list'], content)
                for match in large_matches:
                    line_num = content[:match.start()].count('\n') + 1
                    memory_info['large_data_structures'].append({
                        'file': str(file_path.relative_to(self.project_path)),
                        'line': line_num,
                    })
                
                # Count patterns
                memory_info['generators_used'] += len(re.findall(memory_patterns['generator'], content))
                memory_info['list_comprehensions'] += len(re.findall(memory_patterns['list_comp'], content))
                
                # Check for memory efficient practices
                if re.search(memory_patterns['memory_efficient'], content):
                    memory_info['memory_efficient_practices'].append(str(file_path.relative_to(self.project_path)))
                    
            except Exception:
                pass
        
        return memory_info
    
    def _analyze_async_patterns(self) -> Dict[str, Any]:
        """Analyze asynchronous programming patterns"""
        async_info = {
            'async_functions': 0,
            'await_calls': 0,
            'concurrent_operations': [],
            'async_frameworks': [],
            'sync_in_async': [],
            'proper_async_usage': True,
        }
        
        async_patterns = {
            'async_def': r'async\s+def',
            'await': r'await\s+',
            'asyncio': r'import\s+asyncio|from\s+asyncio',
            'aiohttp': r'import\s+aiohttp|from\s+aiohttp',
            'concurrent': r'asyncio\.gather|asyncio\.create_task|ThreadPoolExecutor|ProcessPoolExecutor',
            'sync_in_async': r'async\s+def.*\n.*(?:time\.sleep|requests\.|urllib)',
        }
        
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                content = file_path.read_text()
                
                # Count async patterns
                async_info['async_functions'] += len(re.findall(async_patterns['async_def'], content))
                async_info['await_calls'] += len(re.findall(async_patterns['await'], content))
                
                # Check for frameworks
                if re.search(async_patterns['asyncio'], content):
                    async_info['async_frameworks'].append('asyncio')
                if re.search(async_patterns['aiohttp'], content):
                    async_info['async_frameworks'].append('aiohttp')
                
                # Check for concurrent operations
                if re.search(async_patterns['concurrent'], content):
                    async_info['concurrent_operations'].append(str(file_path.relative_to(self.project_path)))
                
                # Check for sync operations in async functions
                sync_matches = re.finditer(async_patterns['sync_in_async'], content, re.MULTILINE)
                for match in sync_matches:
                    line_num = content[:match.start()].count('\n') + 1
                    async_info['sync_in_async'].append({
                        'file': str(file_path.relative_to(self.project_path)),
                        'line': line_num,
                    })
                    async_info['proper_async_usage'] = False
                    
            except Exception:
                pass
        
        async_info['async_frameworks'] = list(set(async_info['async_frameworks']))
        return async_info
    
    def _analyze_caching_strategies(self) -> Dict[str, Any]:
        """Analyze caching implementations"""
        cache_info = {
            'cache_decorators': 0,
            'cache_backends': [],
            'memoization': False,
            'cache_invalidation': False,
            'cache_warming': False,
            'ttl_configured': False,
        }
        
        cache_patterns = {
            'decorator': r'@cache|@lru_cache|@cached|@memoize',
            'redis': r'redis|Redis',
            'memcached': r'memcache|Memcache',
            'django_cache': r'cache\.get|cache\.set|cache\.delete',
            'functools': r'functools\.lru_cache',
            'invalidation': r'cache\.delete|cache\.clear|invalidate',
            'ttl': r'timeout=|ttl=|expire|TTL',
        }
        
        for file_path in self.scan_files(['.py']):
            try:
                content = file_path.read_text()
                
                # Count cache decorators
                cache_info['cache_decorators'] += len(re.findall(cache_patterns['decorator'], content))
                
                # Check for cache backends
                if re.search(cache_patterns['redis'], content):
                    cache_info['cache_backends'].append('redis')
                if re.search(cache_patterns['memcached'], content):
                    cache_info['cache_backends'].append('memcached')
                
                # Check for memoization
                if re.search(cache_patterns['functools'], content):
                    cache_info['memoization'] = True
                
                # Check for cache invalidation
                if re.search(cache_patterns['invalidation'], content):
                    cache_info['cache_invalidation'] = True
                
                # Check for TTL configuration
                if re.search(cache_patterns['ttl'], content):
                    cache_info['ttl_configured'] = True
                    
            except Exception:
                pass
        
        cache_info['cache_backends'] = list(set(cache_info['cache_backends']))
        return cache_info
    
    def _analyze_loops(self) -> Dict[str, Any]:
        """Analyze loop patterns and efficiency"""
        loop_info = {
            'total_loops': 0,
            'nested_loops': [],
            'infinite_loop_risk': [],
            'list_operations_in_loops': [],
            'vectorized_operations': 0,
        }
        
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.For, ast.While)):
                        loop_info['total_loops'] += 1
                        
                        # Check for list operations in loops
                        for child in ast.walk(node):
                            if isinstance(child, ast.Call):
                                if hasattr(child.func, 'attr') and child.func.attr in ['append', 'extend', 'insert']:
                                    loop_info['list_operations_in_loops'].append({
                                        'file': str(file_path.relative_to(self.project_path)),
                                        'line': child.lineno,
                                        'operation': child.func.attr,
                                    })
                        
                        # Check for infinite loop risk in while loops
                        if isinstance(node, ast.While):
                            if isinstance(node.test, ast.Constant) and node.test.value is True:
                                loop_info['infinite_loop_risk'].append({
                                    'file': str(file_path.relative_to(self.project_path)),
                                    'line': node.lineno,
                                })
                
                # Check for vectorized operations (numpy, pandas)
                if 'numpy' in content or 'pandas' in content:
                    loop_info['vectorized_operations'] += len(re.findall(r'\.dot\(|\.matmul\(|\.apply\(', content))
                    
            except Exception:
                pass
        
        return loop_info
    
    def _analyze_api_performance(self) -> Dict[str, Any]:
        """Analyze API performance characteristics"""
        api_info = {
            'pagination': False,
            'response_compression': False,
            'query_optimization': False,
            'batch_endpoints': 0,
            'rate_limiting': False,
            'response_caching': False,
            'graphql_optimization': False,
        }
        
        api_patterns = {
            'pagination': r'page|limit|offset|paginate|Paginator',
            'compression': r'gzip|compress|deflate',
            'batch': r'batch|bulk|multiple',
            'rate_limit': r'rate_limit|throttle|RateLimit',
            'cache_control': r'Cache-Control|cache_control|ETag',
            'graphql': r'graphql|GraphQL|dataloader|DataLoader',
        }
        
        for file_path in self.scan_files(['.py', '.js', '.ts']):
            try:
                content = file_path.read_text()
                
                if re.search(api_patterns['pagination'], content, re.IGNORECASE):
                    api_info['pagination'] = True
                    
                if re.search(api_patterns['compression'], content, re.IGNORECASE):
                    api_info['response_compression'] = True
                    
                api_info['batch_endpoints'] += len(re.findall(api_patterns['batch'], content, re.IGNORECASE))
                
                if re.search(api_patterns['rate_limit'], content, re.IGNORECASE):
                    api_info['rate_limiting'] = True
                    
                if re.search(api_patterns['cache_control'], content):
                    api_info['response_caching'] = True
                    
                if re.search(api_patterns['graphql'], content):
                    api_info['graphql_optimization'] = True
                    
            except Exception:
                pass
        
        return api_info
    
    def _analyze_file_operations(self) -> Dict[str, Any]:
        """Analyze file I/O operations"""
        file_info = {
            'streaming_operations': 0,
            'bulk_file_operations': [],
            'async_file_io': False,
            'file_not_closed': [],
            'large_file_handling': False,
        }
        
        file_patterns = {
            'streaming': r'chunk|stream|readline\(\)|iter\(',
            'bulk': r'os\.listdir|glob\.|shutil\.',
            'async_io': r'aiofiles|async.*open|asyncio.*open',
            'context_manager': r'with\s+open',
            'large_file': r'mmap|sendfile|chunk_size',
        }
        
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                content = file_path.read_text()
                
                # Count streaming operations
                file_info['streaming_operations'] += len(re.findall(file_patterns['streaming'], content))
                
                # Check for bulk operations
                if re.search(file_patterns['bulk'], content):
                    file_info['bulk_file_operations'].append(str(file_path.relative_to(self.project_path)))
                
                # Check for async file I/O
                if re.search(file_patterns['async_io'], content):
                    file_info['async_file_io'] = True
                
                # Check for large file handling
                if re.search(file_patterns['large_file'], content):
                    file_info['large_file_handling'] = True
                
                # Check for files not properly closed
                open_calls = re.finditer(r'^(?!.*with).*open\s*\(', content, re.MULTILINE)
                for match in open_calls:
                    line_num = content[:match.start()].count('\n') + 1
                    file_info['file_not_closed'].append({
                        'file': str(file_path.relative_to(self.project_path)),
                        'line': line_num,
                    })
                    
            except Exception:
                pass
        
        return file_info
    
    def _analyze_concurrency(self) -> Dict[str, Any]:
        """Analyze concurrency patterns"""
        concurrency_info = {
            'threading_used': False,
            'multiprocessing_used': False,
            'async_used': False,
            'locks_used': 0,
            'race_conditions_risk': [],
            'deadlock_risk': [],
            'thread_pool_size': None,
        }
        
        concurrency_patterns = {
            'threading': r'import\s+threading|from\s+threading',
            'multiprocessing': r'import\s+multiprocessing|from\s+multiprocessing',
            'async': r'async\s+def|asyncio',
            'locks': r'Lock\(|RLock\(|Semaphore\(|Event\(',
            'global_state': r'global\s+\w+.*\n.*(?:\+=|-=|\*=|/=|=)',
            'thread_pool': r'ThreadPoolExecutor\s*\(\s*max_workers\s*=\s*(\d+)',
        }
        
        for file_path in self.scan_files(['.py']):
            try:
                content = file_path.read_text()
                
                if re.search(concurrency_patterns['threading'], content):
                    concurrency_info['threading_used'] = True
                    
                if re.search(concurrency_patterns['multiprocessing'], content):
                    concurrency_info['multiprocessing_used'] = True
                    
                if re.search(concurrency_patterns['async'], content):
                    concurrency_info['async_used'] = True
                    
                # Count locks
                concurrency_info['locks_used'] += len(re.findall(concurrency_patterns['locks'], content))
                
                # Check for race condition risks
                if re.search(concurrency_patterns['global_state'], content):
                    line_num = content[:re.search(concurrency_patterns['global_state'], content).start()].count('\n') + 1
                    concurrency_info['race_conditions_risk'].append({
                        'file': str(file_path.relative_to(self.project_path)),
                        'line': line_num,
                    })
                
                # Check thread pool size
                pool_match = re.search(concurrency_patterns['thread_pool'], content)
                if pool_match:
                    concurrency_info['thread_pool_size'] = int(pool_match.group(1))
                    
            except Exception:
                pass
        
        return concurrency_info
    
    def _check_profiling_tools(self) -> Dict[str, Any]:
        """Check for profiling and monitoring tools"""
        profiling_info = {
            'profilers': [],
            'apm_tools': [],
            'logging_configured': False,
            'metrics_collection': False,
            'performance_tests': False,
        }
        
        profiling_patterns = {
            'cprofile': r'cProfile|profile',
            'line_profiler': r'line_profiler|@profile',
            'memory_profiler': r'memory_profiler|@profile',
            'timeit': r'timeit|Timer',
            'apm': r'newrelic|datadog|elastic-apm|sentry',
            'prometheus': r'prometheus|metrics',
            'logging': r'logging\.config|logger\.',
            'perf_test': r'test.*performance|benchmark|perf_test',
        }
        
        for file_path in self.scan_files(['.py', '.yml', '.yaml']):
            try:
                content = file_path.read_text()
                
                # Check for profilers
                for profiler, pattern in list(profiling_patterns.items())[:4]:
                    if re.search(pattern, content, re.IGNORECASE):
                        profiling_info['profilers'].append(profiler)
                
                # Check for APM tools
                if re.search(profiling_patterns['apm'], content, re.IGNORECASE):
                    profiling_info['apm_tools'].append('apm')
                    
                if re.search(profiling_patterns['prometheus'], content, re.IGNORECASE):
                    profiling_info['metrics_collection'] = True
                    
                if re.search(profiling_patterns['logging'], content):
                    profiling_info['logging_configured'] = True
                    
                if re.search(profiling_patterns['perf_test'], content, re.IGNORECASE):
                    profiling_info['performance_tests'] = True
                    
            except Exception:
                pass
        
        profiling_info['profilers'] = list(set(profiling_info['profilers']))
        return profiling_info
    
    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall performance score"""
        score = 100.0
        
        # Deduct for algorithmic issues
        score -= len(metrics['algorithmic_complexity']['nested_loops']) * 2
        score -= len(metrics['algorithmic_complexity']['recursive_functions']) * 1
        
        # Deduct for database issues
        score -= len(metrics['database_operations']['n_plus_one_queries']) * 5
        if not metrics['database_operations']['connection_pooling']:
            score -= 5
            
        # Deduct for memory issues
        score -= len(metrics['memory_usage']['large_data_structures']) * 3
        score -= len(metrics['memory_usage']['memory_leaks_risk']) * 5
        
        # Bonus for good practices
        if metrics['memory_usage']['generators_used'] > 5:
            score += 5
            
        # Deduct for async issues
        score -= len(metrics['async_patterns']['sync_in_async']) * 3
        
        # Bonus for caching
        if metrics['caching']['cache_decorators'] > 0:
            score += 5
        if metrics['caching']['cache_backends']:
            score += 5
            
        # Deduct for loop issues
        score -= len(metrics['loops_analysis']['list_operations_in_loops']) * 1
        score -= len(metrics['loops_analysis']['infinite_loop_risk']) * 10
        
        # API performance
        if not metrics['api_performance']['pagination']:
            score -= 5
        if metrics['api_performance']['response_caching']:
            score += 3
            
        # File operations
        score -= len(metrics['file_operations']['file_not_closed']) * 2
        
        # Concurrency issues
        score -= len(metrics['concurrency']['race_conditions_risk']) * 5
        
        # Bonus for profiling
        if metrics['profiling']['performance_tests']:
            score += 5
            
        return max(0.0, min(100.0, score))
    
    def _detect_performance_issues(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect performance issues"""
        issues = []
        
        # Algorithmic complexity issues
        for nested_loop in metrics['algorithmic_complexity']['nested_loops']:
            if nested_loop['depth'] > 2:
                issues.append({
                    'severity': 'high',
                    'type': 'complexity',
                    'message': f"Deeply nested loops (depth {nested_loop['depth']}) at {nested_loop['file']}:{nested_loop['line']}",
                })
        
        # Database issues
        for n_plus_one in metrics['database_operations']['n_plus_one_queries']:
            issues.append({
                'severity': 'high',
                'type': 'database',
                'message': f"Potential N+1 query at {n_plus_one['file']}:{n_plus_one['line']}",
            })
        
        # Memory issues
        for leak_risk in metrics['memory_usage']['memory_leaks_risk']:
            issues.append({
                'severity': 'medium',
                'type': 'memory',
                'message': f"Potential memory leak at {leak_risk['file']}:{leak_risk['line']}",
            })
        
        # Async issues
        for sync_in_async in metrics['async_patterns']['sync_in_async']:
            issues.append({
                'severity': 'high',
                'type': 'async',
                'message': f"Synchronous operation in async function at {sync_in_async['file']}:{sync_in_async['line']}",
            })
        
        # Loop issues
        for infinite_risk in metrics['loops_analysis']['infinite_loop_risk']:
            issues.append({
                'severity': 'critical',
                'type': 'loop',
                'message': f"Potential infinite loop at {infinite_risk['file']}:{infinite_risk['line']}",
            })
        
        # File operation issues
        for not_closed in metrics['file_operations']['file_not_closed']:
            issues.append({
                'severity': 'medium',
                'type': 'file_io',
                'message': f"File not properly closed at {not_closed['file']}:{not_closed['line']}",
            })
        
        # Concurrency issues
        for race_risk in metrics['concurrency']['race_conditions_risk']:
            issues.append({
                'severity': 'high',
                'type': 'concurrency',
                'message': f"Potential race condition at {race_risk['file']}:{race_risk['line']}",
            })
        
        return issues
    
    def _generate_performance_suggestions(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate performance improvement suggestions"""
        suggestions = []
        
        # Algorithmic suggestions
        if metrics['algorithmic_complexity']['nested_loops']:
            suggestions.append("Refactor deeply nested loops using better algorithms or data structures")
            
        if metrics['algorithmic_complexity']['sorting_operations'] > 10:
            suggestions.append("Consider caching sorted results or using more efficient sorting algorithms")
        
        # Database suggestions
        if metrics['database_operations']['n_plus_one_queries']:
            suggestions.append("Use select_related() or prefetch_related() to avoid N+1 queries")
            
        if not metrics['database_operations']['connection_pooling']:
            suggestions.append("Implement database connection pooling for better performance")
            
        if metrics['database_operations']['raw_queries'] > 5:
            suggestions.append("Consider using ORM features instead of raw queries for better optimization")
        
        # Memory suggestions
        if metrics['memory_usage']['generators_used'] < 5:
            suggestions.append("Use generators instead of lists for large data processing")
            
        if metrics['memory_usage']['large_data_structures']:
            suggestions.append("Consider using memory-efficient data structures (numpy arrays, deque)")
        
        # Async suggestions
        if metrics['async_patterns']['async_functions'] > 0 and not metrics['async_patterns']['concurrent_operations']:
            suggestions.append("Use asyncio.gather() or create_task() for concurrent async operations")
            
        if metrics['async_patterns']['sync_in_async']:
            suggestions.append("Replace synchronous operations with async equivalents in async functions")
        
        # Caching suggestions
        if metrics['caching']['cache_decorators'] == 0:
            suggestions.append("Implement caching for frequently accessed data or expensive computations")
            
        if metrics['caching']['cache_backends'] and not metrics['caching']['cache_invalidation']:
            suggestions.append("Implement proper cache invalidation strategies")
        
        # API suggestions
        if not metrics['api_performance']['pagination']:
            suggestions.append("Implement pagination for API endpoints returning large datasets")
            
        if not metrics['api_performance']['response_compression']:
            suggestions.append("Enable response compression (gzip) for API endpoints")
            
        if metrics['api_performance']['batch_endpoints'] == 0:
            suggestions.append("Consider adding batch endpoints to reduce API calls")
        
        # File operation suggestions
        if not metrics['file_operations']['streaming_operations'] and metrics['file_operations']['bulk_file_operations']:
            suggestions.append("Use streaming/chunked file operations for large files")
            
        if metrics['file_operations']['file_not_closed']:
            suggestions.append("Always use context managers (with statement) for file operations")
        
        # Concurrency suggestions
        if metrics['concurrency']['threading_used'] and metrics['concurrency']['locks_used'] == 0:
            suggestions.append("Use proper locking mechanisms to prevent race conditions")
            
        if metrics['concurrency']['thread_pool_size'] and metrics['concurrency']['thread_pool_size'] > 20:
            suggestions.append("Consider reducing thread pool size to avoid context switching overhead")
        
        # Profiling suggestions
        if not metrics['profiling']['performance_tests']:
            suggestions.append("Add performance tests to track and prevent performance regressions")
            
        if not metrics['profiling']['profilers']:
            suggestions.append("Use profiling tools (cProfile, line_profiler) to identify bottlenecks")
        
        return suggestions[:15]  # Return top 15 suggestions