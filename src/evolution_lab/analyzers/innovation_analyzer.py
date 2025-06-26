"""
Innovation and Pattern Analyzer
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import re
import ast
from typing import Any
from pathlib import Path
from collections import defaultdict, Counter

from .base import BaseAnalyzer, AnalysisResult


class InnovationAnalyzer(BaseAnalyzer):
    """Analyzes innovative patterns, design patterns, and architectural decisions"""
    
    def analyze(self) -> AnalysisResult:
        """Analyze innovative patterns and architectural quality"""
        self.start_timer()
        
        metrics = {
            'design_patterns': self._analyze_design_patterns(),
            'architectural_patterns': self._analyze_architectural_patterns(),
            'modern_features': self._analyze_modern_features(),
            'code_reusability': self._analyze_code_reusability(),
            'api_design': self._analyze_api_design(),
            'innovation_indicators': self._analyze_innovation_indicators(),
            'tech_stack_maturity': self._analyze_tech_stack(),
            'best_practices': self._analyze_best_practices(),
        }
        
        metrics['innovation_score'] = self._calculate_innovation_score(metrics)
        metrics['analysis_time'] = self.get_elapsed_time()
        
        issues = self._detect_innovation_issues(metrics)
        suggestions = self._generate_innovation_suggestions(metrics)
        
        return AnalysisResult(
            analyzer_name=self.name,
            metrics=metrics,
            issues=issues,
            suggestions=suggestions,
            metadata={
                'project_path': str(self.project_path),
                'innovation_level': self._get_innovation_level(metrics['innovation_score']),
            },
        )
    
    def _analyze_design_patterns(self) -> dict[str, Any]:
        """Analyze software design patterns usage"""
        patterns = {
            'singleton': [],
            'factory': [],
            'strategy': [],
            'observer': [],
            'decorator': [],
            'command': [],
            'adapter': [],
            'facade': [],
            'repository': [],
            'dependency_injection': [],
            'mvc_mvvm': [],
            'builder': [],
        }
        
        # Pattern detection rules
        pattern_rules = {
            'singleton': [
                r'__new__.*instance.*cls\._instance',
                r'@singleton',
                r'class.*Singleton',
            ],
            'factory': [
                r'class.*Factory',
                r'def create_',
                r'@factory',
                r'factory_method',
            ],
            'strategy': [
                r'class.*Strategy',
                r'@strategy',
                r'set_strategy',
            ],
            'observer': [
                r'class.*Observer',
                r'def notify',
                r'subscribe|unsubscribe',
                r'add_observer|remove_observer',
            ],
            'decorator': [
                r'@\w+\s*\n\s*def',
                r'functools\.wraps',
                r'class.*Decorator',
            ],
            'command': [
                r'class.*Command',
                r'def execute\(',
                r'def undo\(',
            ],
            'adapter': [
                r'class.*Adapter',
                r'@adapter',
            ],
            'facade': [
                r'class.*Facade',
                r'@facade',
            ],
            'repository': [
                r'class.*Repository',
                r'def find_by',
                r'def save\(',
                r'def delete\(',
            ],
            'dependency_injection': [
                r'@inject',
                r'__init__.*\):.*# injected',
                r'Container\.',
                r'@provide',
            ],
            'mvc_mvvm': [
                r'class.*Controller',
                r'class.*View',
                r'class.*Model',
                r'class.*ViewModel',
            ],
            'builder': [
                r'class.*Builder',
                r'def build\(',
                r'with_\w+\(',
            ],
        }
        
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                content = file_path.read_text()
                
                for pattern_name, rules in pattern_rules.items():
                    for rule in rules:
                        if re.search(rule, content, re.IGNORECASE | re.MULTILINE):
                            patterns[pattern_name].append({
                                'file': str(file_path.relative_to(self.project_path)),
                                'pattern': rule,
                            })
                            break
                            
            except Exception:
                pass
        
        # Count unique patterns used
        patterns_used = {k: len(v) for k, v in patterns.items() if v}
        
        return {
            'patterns_detected': patterns,
            'unique_patterns_count': len(patterns_used),
            'total_pattern_instances': sum(patterns_used.values()),
            'most_used_patterns': sorted(patterns_used.items(), key=lambda x: x[1], reverse=True)[:5],
        }
    
    def _analyze_architectural_patterns(self) -> dict[str, Any]:
        """Analyze architectural patterns and structures"""
        arch_patterns = {
            'layered_architecture': False,
            'microservices': False,
            'event_driven': False,
            'domain_driven_design': False,
            'clean_architecture': False,
            'hexagonal_architecture': False,
            'cqrs': False,
            'event_sourcing': False,
            'api_first': False,
            'plugin_architecture': False,
        }
        
        # Check directory structure for architectural patterns
        dirs = set()
        for file_path in self.scan_files():
            dirs.update(file_path.parts[:-1])
        
        # Layered architecture indicators
        layer_dirs = ['domain', 'application', 'infrastructure', 'presentation', 'api', 'services', 'repositories']
        if sum(1 for d in layer_dirs if any(d in str(dir_).lower() for dir_ in dirs)) >= 3:
            arch_patterns['layered_architecture'] = True
        
        # DDD indicators
        ddd_dirs = ['domain', 'entities', 'value_objects', 'aggregates', 'repositories', 'services']
        if sum(1 for d in ddd_dirs if any(d in str(dir_).lower() for dir_ in dirs)) >= 4:
            arch_patterns['domain_driven_design'] = True
        
        # Clean architecture indicators
        clean_dirs = ['entities', 'use_cases', 'interfaces', 'frameworks', 'adapters']
        if sum(1 for d in clean_dirs if any(d in str(dir_).lower() for dir_ in dirs)) >= 3:
            arch_patterns['clean_architecture'] = True
        
        # Check for architectural patterns in code
        arch_indicators = {
            'microservices': [r'@app\.route', r'FastAPI', r'Flask', r'service_discovery', r'circuit_breaker'],
            'event_driven': [r'EventBus', r'publish|subscribe', r'emit_event', r'on_event', r'message_queue'],
            'hexagonal_architecture': [r'Port', r'Adapter', r'UseCase', r'ports/', r'adapters/'],
            'cqrs': [r'Command', r'Query', r'CommandHandler', r'QueryHandler', r'ReadModel'],
            'event_sourcing': [r'EventStore', r'event_stream', r'replay_events', r'aggregate_id'],
            'api_first': [r'openapi', r'swagger', r'@api', r'api_spec', r'api_blueprint'],
            'plugin_architecture': [r'Plugin', r'Extension', r'register_plugin', r'load_plugins'],
        }
        
        for file_path in self.scan_files(['.py', '.yml', '.yaml']):
            try:
                content = file_path.read_text()
                
                for pattern, indicators in arch_indicators.items():
                    if any(re.search(ind, content, re.IGNORECASE) for ind in indicators):
                        arch_patterns[pattern] = True
                        
            except Exception:
                pass
        
        return arch_patterns
    
    def _analyze_modern_features(self) -> dict[str, Any]:
        """Analyze usage of modern language features and paradigms"""
        modern_features = {
            'type_hints': 0,
            'async_await': 0,
            'dataclasses': 0,
            'f_strings': 0,
            'walrus_operator': 0,
            'pattern_matching': 0,
            'context_managers': 0,
            'generators': 0,
            'decorators': 0,
            'metaclasses': 0,
            'protocols': 0,
            'generic_types': 0,
        }
        
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                content = file_path.read_text()
                tree = ast.parse(content)
                
                # Count type hints
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.returns or any(arg.annotation for arg in node.args.args):
                            modern_features['type_hints'] += 1
                    
                    # Count async functions
                    if isinstance(node, ast.AsyncFunctionDef):
                        modern_features['async_await'] += 1
                    
                    # Count decorators
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.decorator_list:
                        modern_features['decorators'] += len(node.decorator_list)
                
                # Pattern-based detection
                modern_features['dataclasses'] += len(re.findall(r'@dataclass', content))
                modern_features['f_strings'] += len(re.findall(r'f["\']', content))
                modern_features['walrus_operator'] += len(re.findall(r':=', content))
                modern_features['pattern_matching'] += len(re.findall(r'match\s+\w+:', content))
                modern_features['context_managers'] += len(re.findall(r'with\s+', content))
                modern_features['generators'] += len(re.findall(r'yield\s+', content))
                modern_features['metaclasses'] += len(re.findall(r'metaclass=', content))
                modern_features['protocols'] += len(re.findall(r'Protocol\[|@runtime_checkable', content))
                modern_features['generic_types'] += len(re.findall(r'Generic\[|TypeVar', content))
                
            except Exception:
                pass
        
        # Calculate adoption rate
        total_features = sum(modern_features.values())
        feature_diversity = len([f for f in modern_features.values() if f > 0])
        
        return {
            'features_used': modern_features,
            'total_modern_features': total_features,
            'feature_diversity': feature_diversity,
            'adoption_rate': feature_diversity / len(modern_features) * 100,
        }
    
    def _analyze_code_reusability(self) -> dict[str, Any]:
        """Analyze code reusability metrics"""
        reusability = {
            'abstract_classes': 0,
            'interfaces': 0,
            'mixins': 0,
            'utility_modules': 0,
            'shared_components': 0,
            'generic_functions': 0,
            'configuration_driven': False,
            'modular_structure': False,
        }
        
        # Analyze Python files
        python_files = self.scan_files(['.py'])
        imports_counter = Counter()
        module_functions = defaultdict(int)
        
        for file_path in python_files:
            try:
                content = file_path.read_text()
                tree = ast.parse(content)
                
                # Count imports to find shared modules
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports_counter[alias.name] += 1
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports_counter[node.module] += 1
                    
                    # Count abstract classes and interfaces
                    elif isinstance(node, ast.ClassDef):
                        for base in node.bases:
                            if hasattr(base, 'id'):
                                if base.id in ['ABC', 'ABCMeta']:
                                    reusability['abstract_classes'] += 1
                                elif 'Interface' in base.id or 'Protocol' in base.id:
                                    reusability['interfaces'] += 1
                                elif 'Mixin' in base.id:
                                    reusability['mixins'] += 1
                    
                    # Count functions in modules
                    elif isinstance(node, ast.FunctionDef):
                        module_functions[str(file_path)] += 1
                
                # Check for generic/template functions
                if re.search(r'TypeVar|Generic', content):
                    reusability['generic_functions'] += 1
                    
            except Exception:
                pass
        
        # Identify utility modules (high function count, frequently imported)
        for module, import_count in imports_counter.most_common(10):
            if 'util' in module.lower() or 'helper' in module.lower() or 'common' in module.lower():
                reusability['utility_modules'] += 1
        
        # Shared components (imported by many files)
        reusability['shared_components'] = len([m for m, count in imports_counter.items() if count > 3])
        
        # Check for configuration-driven behavior
        config_files = list(self.project_path.glob('**/config.*')) + list(self.project_path.glob('**/settings.*'))
        reusability['configuration_driven'] = len(config_files) > 0
        
        # Check modular structure
        if len(set(p.parent for p in python_files)) > 5:
            reusability['modular_structure'] = True
        
        return reusability
    
    def _analyze_api_design(self) -> dict[str, Any]:
        """Analyze API design quality and patterns"""
        api_design = {
            'rest_endpoints': 0,
            'graphql_endpoints': 0,
            'grpc_services': 0,
            'versioning': False,
            'documentation': False,
            'rate_limiting': False,
            'authentication': False,
            'validation': False,
            'error_handling': False,
            'hateoas': False,
            'openapi_spec': False,
        }
        
        # API patterns
        api_patterns = {
            'rest': [r'@(app|router)\.(get|post|put|delete|patch)', r'methods=\[', r'RESTful'],
            'graphql': [r'@strawberry', r'graphene', r'type Query', r'type Mutation'],
            'grpc': [r'\.proto', r'grpc\.', r'servicer', r'stub'],
            'versioning': [r'/v\d+/', r'api/v\d+', r'version\s*='],
            'documentation': [r'@api\.doc', r'swagger', r'openapi', r'""".*:param.*"""'],
            'rate_limiting': [r'@rate_limit', r'RateLimit', r'throttle'],
            'authentication': [r'@auth', r'Bearer', r'JWT', r'OAuth'],
            'validation': [r'@validate', r'ValidationError', r'pydantic', r'marshmallow'],
            'error_handling': [r'@error_handler', r'HTTPException', r'error_response'],
            'hateoas': [r'_links', r'href.*self', r'hypermedia'],
            'openapi': [r'openapi', r'swagger', r'@api\.response'],
        }
        
        for file_path in self.scan_files(['.py', '.yml', '.yaml', '.proto']):
            try:
                content = file_path.read_text()
                
                # Count REST endpoints
                api_design['rest_endpoints'] += len(re.findall(api_patterns['rest'][0], content))
                
                # Check for other patterns
                for pattern_name, patterns in api_patterns.items():
                    if pattern_name != 'rest':
                        if any(re.search(p, content, re.IGNORECASE) for p in patterns):
                            if pattern_name in ['graphql_endpoints', 'grpc_services']:
                                api_design[pattern_name] += 1
                            else:
                                api_design[pattern_name] = True
                                
            except Exception:
                pass
        
        return api_design
    
    def _analyze_innovation_indicators(self) -> dict[str, Any]:
        """Analyze indicators of innovative practices"""
        innovation = {
            'machine_learning': False,
            'blockchain': False,
            'iot_integration': False,
            'real_time_features': False,
            'progressive_web_app': False,
            'serverless': False,
            'container_orchestration': False,
            'edge_computing': False,
            'ar_vr': False,
            'quantum_computing': False,
            'custom_algorithms': 0,
            'research_implementations': 0,
        }
        
        # Innovation patterns
        innovation_patterns = {
            'machine_learning': ['tensorflow', 'pytorch', 'sklearn', 'keras', 'neural', 'model.fit'],
            'blockchain': ['blockchain', 'smart_contract', 'ethereum', 'web3', 'crypto', 'ledger'],
            'iot_integration': ['mqtt', 'iot', 'sensor', 'arduino', 'raspberry', 'zigbee'],
            'real_time_features': ['websocket', 'socket.io', 'real-time', 'streaming', 'pubsub'],
            'progressive_web_app': ['service_worker', 'manifest.json', 'pwa', 'offline_first'],
            'serverless': ['lambda', 'serverless', 'function-as-a-service', 'faas'],
            'container_orchestration': ['kubernetes', 'k8s', 'docker-compose', 'helm', 'container'],
            'edge_computing': ['edge_computing', 'fog_computing', 'edge_device', 'local_processing'],
            'ar_vr': ['augmented_reality', 'virtual_reality', 'arcore', 'arkit', 'vr_'],
            'quantum_computing': ['quantum', 'qubit', 'qiskit', 'quantum_circuit'],
        }
        
        all_files = self.scan_files()
        for file_path in all_files:
            try:
                content = file_path.read_text()
                
                for feature, patterns in innovation_patterns.items():
                    if any(pattern in content.lower() for pattern in patterns):
                        innovation[feature] = True
                
                # Look for custom algorithm implementations
                if re.search(r'class.*Algorithm|def.*algorithm|# Algorithm:', content, re.IGNORECASE):
                    innovation['custom_algorithms'] += 1
                
                # Look for research paper implementations
                if re.search(r'paper:|Paper:|arxiv|doi:|DOI:', content):
                    innovation['research_implementations'] += 1
                    
            except Exception:
                pass
        
        return innovation
    
    def _analyze_tech_stack(self) -> dict[str, Any]:
        """Analyze technology stack maturity and diversity"""
        tech_stack = {
            'languages': set(),
            'frameworks': set(),
            'databases': set(),
            'tools': set(),
            'cloud_services': set(),
            'ci_cd': set(),
        }
        
        # File extensions to languages
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.cs': 'C#',
            '.rb': 'Ruby',
            '.php': 'PHP',
        }
        
        # Detect languages
        for ext, lang in lang_map.items():
            if list(self.project_path.rglob(f'*{ext}')):
                tech_stack['languages'].add(lang)
        
        # Check configuration files for frameworks and tools
        config_checks = {
            'requirements.txt': ['flask', 'django', 'fastapi', 'pandas', 'numpy', 'scipy'],
            'package.json': ['react', 'vue', 'angular', 'express', 'next', 'nest'],
            'docker-compose.yml': ['redis', 'postgres', 'mysql', 'mongodb', 'elasticsearch'],
            '.github/workflows': ['github-actions'],
            'Jenkinsfile': ['jenkins'],
            '.gitlab-ci.yml': ['gitlab-ci'],
        }
        
        for config_file, techs in config_checks.items():
            config_path = self.project_path / config_file
            if config_path.exists() and config_path.is_file():
                try:
                    content = config_path.read_text().lower()
                    for tech in techs:
                        if tech in content:
                            if tech in ['redis', 'postgres', 'mysql', 'mongodb', 'elasticsearch']:
                                tech_stack['databases'].add(tech)
                            elif tech in ['github-actions', 'jenkins', 'gitlab-ci']:
                                tech_stack['ci_cd'].add(tech)
                            else:
                                tech_stack['frameworks'].add(tech)
                except Exception:
                    pass
        
        # Cloud service detection
        cloud_patterns = {
            'aws': ['aws', 's3', 'ec2', 'lambda', 'dynamodb'],
            'gcp': ['google-cloud', 'gcp', 'bigquery', 'firestore'],
            'azure': ['azure', 'cosmos', 'blob-storage'],
            'heroku': ['heroku', 'procfile'],
            'vercel': ['vercel', 'now.json'],
        }
        
        for file_path in self.scan_files():
            try:
                content = file_path.read_text().lower()
                for cloud, patterns in cloud_patterns.items():
                    if any(pattern in content for pattern in patterns):
                        tech_stack['cloud_services'].add(cloud)
            except Exception:
                pass
        
        # Calculate diversity score
        total_technologies = sum(len(s) for s in tech_stack.values())
        
        return {
            'stack_components': {k: list(v) for k, v in tech_stack.items()},
            'total_technologies': total_technologies,
            'stack_diversity': len([v for v in tech_stack.values() if v]),
            'polyglot': len(tech_stack['languages']) > 1,
        }
    
    def _analyze_best_practices(self) -> dict[str, Any]:
        """Analyze adherence to best practices"""
        best_practices = {
            'documentation': {
                'readme': False,
                'api_docs': False,
                'code_comments': 0,
                'docstrings': 0,
            },
            'code_quality': {
                'linting': False,
                'formatting': False,
                'type_checking': False,
                'code_review': False,
            },
            'testing': {
                'unit_tests': False,
                'integration_tests': False,
                'coverage_config': False,
                'ci_tests': False,
            },
            'security': {
                'dependency_scanning': False,
                'secrets_management': False,
                'security_headers': False,
            },
            'deployment': {
                'containerization': False,
                'infrastructure_as_code': False,
                'monitoring': False,
                'logging': False,
            },
        }
        
        # Check for documentation
        if (self.project_path / 'README.md').exists() or (self.project_path / 'README.rst').exists():
            best_practices['documentation']['readme'] = True
        
        # Check for code quality tools
        quality_files = {
            '.flake8': 'linting',
            '.pylintrc': 'linting',
            '.eslintrc': 'linting',
            '.prettierrc': 'formatting',
            'pyproject.toml': 'formatting',  # black config
            'mypy.ini': 'type_checking',
            '.pre-commit-config.yaml': 'code_review',
        }
        
        for file_name, practice in quality_files.items():
            if (self.project_path / file_name).exists():
                best_practices['code_quality'][practice] = True
        
        # Check pyproject.toml for tools
        pyproject_path = self.project_path / 'pyproject.toml'
        if pyproject_path.exists():
            try:
                content = pyproject_path.read_text()
                if '[tool.black]' in content:
                    best_practices['code_quality']['formatting'] = True
                if '[tool.mypy]' in content:
                    best_practices['code_quality']['type_checking'] = True
                if '[tool.pytest' in content:
                    best_practices['testing']['unit_tests'] = True
                if '[tool.coverage' in content:
                    best_practices['testing']['coverage_config'] = True
            except Exception:
                pass
        
        # Check for test directories
        test_dirs = ['tests', 'test', 'spec', '__tests__']
        if any((self.project_path / d).exists() for d in test_dirs):
            best_practices['testing']['unit_tests'] = True
        
        # Check for containerization
        if (self.project_path / 'Dockerfile').exists():
            best_practices['deployment']['containerization'] = True
        
        # Check for IaC
        iac_files = ['terraform', 'cloudformation', 'kubernetes', 'k8s', 'helm']
        if any(self.project_path.rglob(f'*{pattern}*') for pattern in iac_files):
            best_practices['deployment']['infrastructure_as_code'] = True
        
        # Count code comments and docstrings
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                content = file_path.read_text()
                best_practices['documentation']['code_comments'] += len(re.findall(r'#[^#]', content))
                best_practices['documentation']['docstrings'] += len(re.findall(r'""".*?"""', content, re.DOTALL))
            except Exception:
                pass
        
        return best_practices
    
    def _calculate_innovation_score(self, metrics: dict[str, Any]) -> float:
        """Calculate overall innovation score"""
        score = 0.0
        
        # Design patterns (20 points)
        pattern_score = min(metrics['design_patterns']['unique_patterns_count'] * 2, 20)
        score += pattern_score
        
        # Architectural patterns (20 points)
        arch_patterns_used = sum(1 for v in metrics['architectural_patterns'].values() if v)
        score += min(arch_patterns_used * 4, 20)
        
        # Modern features (15 points)
        score += min(metrics['modern_features']['adoption_rate'] * 0.15, 15)
        
        # Code reusability (15 points)
        reuse_score = 0
        if metrics['code_reusability']['abstract_classes'] > 0:
            reuse_score += 3
        if metrics['code_reusability']['interfaces'] > 0:
            reuse_score += 3
        if metrics['code_reusability']['shared_components'] > 5:
            reuse_score += 3
        if metrics['code_reusability']['modular_structure']:
            reuse_score += 3
        if metrics['code_reusability']['configuration_driven']:
            reuse_score += 3
        score += reuse_score
        
        # API design (10 points)
        api_score = 0
        if metrics['api_design']['rest_endpoints'] > 0 or metrics['api_design']['graphql_endpoints'] > 0:
            api_score += 2
        if metrics['api_design']['versioning']:
            api_score += 2
        if metrics['api_design']['documentation']:
            api_score += 2
        if metrics['api_design']['validation']:
            api_score += 2
        if metrics['api_design']['openapi_spec']:
            api_score += 2
        score += api_score
        
        # Innovation indicators (10 points)
        innovation_count = sum(1 for k, v in metrics['innovation_indicators'].items() 
                             if k not in ['custom_algorithms', 'research_implementations'] and v)
        score += min(innovation_count * 2, 10)
        
        # Tech stack (5 points)
        if metrics['tech_stack_maturity']['stack_diversity'] >= 4:
            score += 5
        elif metrics['tech_stack_maturity']['stack_diversity'] >= 2:
            score += 3
        
        # Best practices (5 points)
        practices_score = 0
        if metrics['best_practices']['documentation']['readme']:
            practices_score += 1
        if metrics['best_practices']['code_quality']['linting']:
            practices_score += 1
        if metrics['best_practices']['testing']['unit_tests']:
            practices_score += 1
        if metrics['best_practices']['deployment']['containerization']:
            practices_score += 1
        if metrics['best_practices']['deployment']['infrastructure_as_code']:
            practices_score += 1
        score += practices_score
        
        return min(score, 100.0)
    
    def _get_innovation_level(self, score: float) -> str:
        """Determine innovation level based on score"""
        if score >= 80:
            return "Highly Innovative"
        elif score >= 60:
            return "Innovative"
        elif score >= 40:
            return "Moderately Innovative"
        elif score >= 20:
            return "Traditional"
        else:
            return "Legacy"
    
    def _detect_innovation_issues(self, metrics: dict[str, Any]) -> list[dict[str, Any]]:
        """Detect issues related to innovation and architecture"""
        issues = []
        
        # Pattern issues
        if metrics['design_patterns']['unique_patterns_count'] == 0:
            issues.append({
                'severity': 'medium',
                'type': 'patterns',
                'message': 'No design patterns detected - consider using established patterns',
            })
        
        # Architecture issues
        arch_count = sum(1 for v in metrics['architectural_patterns'].values() if v)
        if arch_count == 0:
            issues.append({
                'severity': 'high',
                'type': 'architecture',
                'message': 'No clear architectural pattern detected',
            })
        
        # Modern features issues
        if metrics['modern_features']['adoption_rate'] < 30:
            issues.append({
                'severity': 'medium',
                'type': 'modernization',
                'message': f"Low adoption of modern features ({metrics['modern_features']['adoption_rate']:.1f}%)",
            })
        
        # Reusability issues
        if not metrics['code_reusability']['modular_structure']:
            issues.append({
                'severity': 'medium',
                'type': 'structure',
                'message': 'Code lacks modular structure',
            })
        
        # API design issues
        if metrics['api_design']['rest_endpoints'] > 0:
            if not metrics['api_design']['versioning']:
                issues.append({
                    'severity': 'medium',
                    'type': 'api',
                    'message': 'API lacks versioning strategy',
                })
            if not metrics['api_design']['documentation']:
                issues.append({
                    'severity': 'high',
                    'type': 'api',
                    'message': 'API lacks proper documentation',
                })
        
        # Best practices issues
        if not metrics['best_practices']['documentation']['readme']:
            issues.append({
                'severity': 'high',
                'type': 'documentation',
                'message': 'Missing README documentation',
            })
        
        if not metrics['best_practices']['testing']['unit_tests']:
            issues.append({
                'severity': 'high',
                'type': 'testing',
                'message': 'No unit tests detected',
            })
        
        return issues
    
    def _generate_innovation_suggestions(self, metrics: dict[str, Any]) -> list[str]:
        """Generate suggestions for improving innovation and architecture"""
        suggestions = []
        
        # Pattern suggestions
        if metrics['design_patterns']['unique_patterns_count'] < 3:
            suggestions.append("Implement design patterns like Factory, Strategy, or Observer for better code organization")
        
        # Architecture suggestions
        if not metrics['architectural_patterns']['layered_architecture']:
            suggestions.append("Consider adopting a layered architecture for better separation of concerns")
            
        if not metrics['architectural_patterns']['domain_driven_design'] and metrics['api_design']['rest_endpoints'] > 10:
            suggestions.append("Consider Domain-Driven Design for complex business logic")
        
        # Modern features suggestions
        if metrics['modern_features']['features_used']['type_hints'] < 10:
            suggestions.append("Add type hints to improve code clarity and enable better tooling")
            
        if metrics['modern_features']['features_used']['async_await'] == 0 and metrics['api_design']['rest_endpoints'] > 0:
            suggestions.append("Consider using async/await for better API performance")
        
        # Reusability suggestions
        if metrics['code_reusability']['abstract_classes'] == 0:
            suggestions.append("Create abstract base classes for common interfaces")
            
        if metrics['code_reusability']['shared_components'] < 3:
            suggestions.append("Extract common functionality into shared utility modules")
        
        # API suggestions
        if metrics['api_design']['rest_endpoints'] > 0 and not metrics['api_design']['openapi_spec']:
            suggestions.append("Add OpenAPI/Swagger documentation for your REST API")
        
        # Innovation suggestions
        if not any(metrics['innovation_indicators'][k] for k in ['real_time_features', 'machine_learning'] if k in metrics['innovation_indicators']):
            suggestions.append("Consider adding real-time features or ML capabilities for competitive advantage")
        
        # Tech stack suggestions
        if not metrics['tech_stack_maturity']['polyglot']:
            suggestions.append("Consider polyglot architecture for optimal tool selection per component")
        
        # Best practices suggestions
        if not metrics['best_practices']['code_quality']['linting']:
            suggestions.append("Set up code linting (flake8, pylint, ESLint) for consistent code quality")
            
        if not metrics['best_practices']['deployment']['containerization']:
            suggestions.append("Containerize your application with Docker for better deployment")
            
        if not metrics['best_practices']['deployment']['monitoring']:
            suggestions.append("Implement application monitoring and observability")
        
        return suggestions[:15]  # Return top 15 suggestions