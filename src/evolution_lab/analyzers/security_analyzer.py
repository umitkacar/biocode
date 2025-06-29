"""
Security Vulnerability Analyzer
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import re
import ast
from typing import Any, Dict, List
from pathlib import Path
from collections import defaultdict

from .base import BaseAnalyzer, AnalysisResult


class SecurityAnalyzer(BaseAnalyzer):
    """Analyzes security vulnerabilities and potential risks"""
    
    # Common security patterns to check
    VULNERABILITY_PATTERNS = {
        'sql_injection': [
            r'execute\s*\(\s*["\'].*%[s|d].*["\']\s*%',
            r'execute\s*\(\s*f["\'].*{.*}.*["\']',
            r'cursor\.execute\s*\(\s*[^,]+\+',
        ],
        'hardcoded_secrets': [
            r'(password|passwd|pwd|secret|api_key|apikey|token)\s*=\s*["\'][^"\']+["\']',
            r'(AWS|aws)_(ACCESS_KEY|SECRET|access_key|secret)\s*=\s*["\'][^"\']+["\']',
            r'(PRIVATE_KEY|private_key|SECRET_KEY|secret_key)\s*=\s*["\'][^"\']+["\']',
        ],
        'command_injection': [
            r'os\.system\s*\(',
            r'subprocess\.(call|run|Popen)\s*\(\s*[^,\]]+\+',
            r'eval\s*\(',
            r'exec\s*\(',
        ],
        'path_traversal': [
            r'open\s*\(\s*[^)]*\.\./[^)]*\)',
            r'Path\s*\(\s*[^)]*\.\./[^)]*\)',
        ],
        'weak_crypto': [
            r'hashlib\.(md5|sha1)\s*\(',
            r'random\.random\s*\(',  # for cryptographic purposes
            r'DES\s*\(',
        ],
        'insecure_deserialization': [
            r'pickle\.loads?\s*\(',
            r'yaml\.load\s*\([^,)]*\)',  # without Loader
        ],
        'xss_vulnerable': [
            r'render_template_string\s*\(',
            r'Markup\s*\(\s*[^)]+\)',
            r'\|safe(?!\w)',
        ],
    }
    
    def analyze(self) -> AnalysisResult:
        """Analyze security vulnerabilities"""
        self.start_timer()
        
        metrics = {
            'vulnerabilities': self._scan_vulnerabilities(),
            'authentication': self._analyze_authentication(),
            'authorization': self._analyze_authorization(),
            'encryption': self._analyze_encryption(),
            'input_validation': self._analyze_input_validation(),
            'dependency_vulnerabilities': self._check_dependencies(),
            'security_headers': self._check_security_headers(),
            'api_security': self._analyze_api_security(),
        }
        
        metrics['security_score'] = self._calculate_security_score(metrics)
        metrics['analysis_time'] = self.get_elapsed_time()
        
        issues = self._detect_security_issues(metrics)
        suggestions = self._generate_security_suggestions(metrics)
        
        return AnalysisResult(
            analyzer_name=self.name,
            metrics=metrics,
            issues=issues,
            suggestions=suggestions,
            metadata={
                'project_path': str(self.project_path),
                'critical_vulnerabilities': len([i for i in issues if i['severity'] == 'critical']),
            },
        )
    
    def _scan_vulnerabilities(self) -> Dict[str, Any]:
        """Scan for common vulnerabilities"""
        vulnerabilities = defaultdict(list)
        
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for vuln_type, patterns in self.VULNERABILITY_PATTERNS.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            vulnerabilities[vuln_type].append({
                                'file': str(file_path.relative_to(self.project_path)),
                                'line': line_num,
                                'code': match.group(0)[:100],
                            })
            except Exception:
                pass
        
        return dict(vulnerabilities)
    
    def _analyze_authentication(self) -> Dict[str, Any]:
        """Analyze authentication mechanisms"""
        auth_info = {
            'methods': [],
            'oauth_providers': [],
            'jwt_usage': False,
            'session_management': False,
            'password_hashing': None,
        }
        
        # Look for authentication patterns
        auth_patterns = {
            'jwt': r'import\s+jwt|from\s+.*\s+import\s+.*jwt',
            'oauth': r'oauth|OAuth',
            'basic_auth': r'BasicAuth|basic_auth',
            'api_key': r'api_key|apikey|API_KEY',
            'session': r'session\[|Session\(',
            'bcrypt': r'bcrypt|Bcrypt',
            'argon2': r'argon2|Argon2',
            'pbkdf2': r'pbkdf2',
        }
        
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for auth_type, pattern in auth_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        if auth_type == 'jwt':
                            auth_info['jwt_usage'] = True
                        elif auth_type == 'session':
                            auth_info['session_management'] = True
                        elif auth_type in ['bcrypt', 'argon2', 'pbkdf2']:
                            auth_info['password_hashing'] = auth_type
                        else:
                            auth_info['methods'].append(auth_type)
            except Exception:
                pass
        
        return auth_info
    
    def _analyze_authorization(self) -> Dict[str, Any]:
        """Analyze authorization mechanisms"""
        authz_info = {
            'rbac': False,
            'decorators': [],
            'middleware': [],
            'permission_checks': 0,
        }
        
        # Look for authorization patterns
        authz_patterns = {
            'role_based': r'role|Role|ROLE',
            'permission': r'permission|Permission|can_|has_perm',
            'decorator': r'@(require_|login_|auth|permission_required)',
            'middleware': r'AuthMiddleware|PermissionMiddleware',
        }
        
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                if re.search(authz_patterns['role_based'], content):
                    authz_info['rbac'] = True
                    
                # Count permission checks
                perm_matches = re.findall(authz_patterns['permission'], content)
                authz_info['permission_checks'] += len(perm_matches)
                
                # Find decorators
                dec_matches = re.findall(authz_patterns['decorator'], content)
                authz_info['decorators'].extend(dec_matches)
                
            except Exception:
                pass
        
        authz_info['decorators'] = list(set(authz_info['decorators']))
        return authz_info
    
    def _analyze_encryption(self) -> Dict[str, Any]:
        """Analyze encryption usage"""
        encryption_info = {
            'tls_ssl': False,
            'data_encryption': [],
            'key_management': False,
            'algorithms': [],
        }
        
        # Check for encryption patterns
        crypto_patterns = {
            'aes': r'AES|aes|Cipher',
            'rsa': r'RSA|rsa',
            'https': r'https://|HTTPS',
            'ssl': r'ssl|SSL|TLS',
            'encrypt': r'encrypt|Encrypt|cipher',
            'cryptography': r'from\s+cryptography|import\s+cryptography',
        }
        
        for file_path in self.scan_files(['.py', '.yml', '.yaml', '.json']):
            try:
                content = file_path.read_text()
                
                for crypto_type, pattern in crypto_patterns.items():
                    if re.search(pattern, content):
                        if crypto_type in ['aes', 'rsa']:
                            encryption_info['algorithms'].append(crypto_type)
                        elif crypto_type in ['https', 'ssl']:
                            encryption_info['tls_ssl'] = True
                        elif crypto_type == 'cryptography':
                            encryption_info['data_encryption'].append(str(file_path.relative_to(self.project_path)))
                            
            except Exception:
                pass
        
        encryption_info['algorithms'] = list(set(encryption_info['algorithms']))
        return encryption_info
    
    def _analyze_input_validation(self) -> Dict[str, Any]:
        """Analyze input validation practices"""
        validation_info = {
            'validators_count': 0,
            'sanitization': False,
            'validation_types': [],
            'frameworks': [],
        }
        
        validation_patterns = {
            'email': r'email.*validat|validat.*email',
            'url': r'url.*validat|validat.*url',
            'sql': r'escape|sanitize|prepared_statement',
            'html': r'escape_html|html\.escape|bleach',
            'marshmallow': r'marshmallow|Schema\(',
            'pydantic': r'pydantic|BaseModel',
            'wtforms': r'wtforms|FlaskForm',
        }
        
        python_files = self.scan_files(['.py'])
        for file_path in python_files:
            try:
                content = file_path.read_text()
                
                for val_type, pattern in validation_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        if val_type in ['email', 'url']:
                            validation_info['validation_types'].append(val_type)
                        elif val_type in ['sql', 'html']:
                            validation_info['sanitization'] = True
                        else:
                            validation_info['frameworks'].append(val_type)
                            
                # Count validators
                validator_count = len(re.findall(r'validat', content, re.IGNORECASE))
                validation_info['validators_count'] += validator_count
                
            except Exception:
                pass
        
        validation_info['validation_types'] = list(set(validation_info['validation_types']))
        validation_info['frameworks'] = list(set(validation_info['frameworks']))
        return validation_info
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check for vulnerable dependencies"""
        dep_info = {
            'outdated_packages': [],
            'known_vulnerabilities': [],
            'license_issues': [],
        }
        
        # Check requirements files
        req_files = ['requirements.txt', 'Pipfile', 'pyproject.toml']
        for req_file in req_files:
            req_path = self.project_path / req_file
            if req_path.exists():
                try:
                    content = req_path.read_text()
                    
                    # Check for packages without version pinning
                    unpinned = re.findall(r'^([a-zA-Z0-9\-_]+)\s*$', content, re.MULTILINE)
                    if unpinned:
                        dep_info['outdated_packages'].extend(unpinned)
                        
                    # Check for known vulnerable packages (simplified)
                    vulnerable_packages = ['pyyaml<5.4', 'django<3.2', 'flask<2.0']
                    for vuln in vulnerable_packages:
                        if vuln.split('<')[0] in content.lower():
                            dep_info['known_vulnerabilities'].append(vuln)
                            
                except Exception:
                    pass
        
        return dep_info
    
    def _check_security_headers(self) -> Dict[str, Any]:
        """Check for security headers implementation"""
        headers_info = {
            'csp': False,
            'x_frame_options': False,
            'x_content_type_options': False,
            'strict_transport_security': False,
            'x_xss_protection': False,
        }
        
        # Look for security header implementations
        header_patterns = {
            'csp': r'Content-Security-Policy',
            'x_frame_options': r'X-Frame-Options',
            'x_content_type_options': r'X-Content-Type-Options',
            'strict_transport_security': r'Strict-Transport-Security',
            'x_xss_protection': r'X-XSS-Protection',
        }
        
        for file_path in self.scan_files(['.py', '.js', '.ts']):
            try:
                content = file_path.read_text()
                
                for header, pattern in header_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        headers_info[header] = True
                        
            except Exception:
                pass
        
        return headers_info
    
    def _analyze_api_security(self) -> Dict[str, Any]:
        """Analyze API security measures"""
        api_info = {
            'rate_limiting': False,
            'api_versioning': False,
            'cors_configured': False,
            'api_authentication': [],
            'endpoints_count': 0,
        }
        
        # API security patterns
        api_patterns = {
            'rate_limit': r'rate_limit|ratelimit|throttle',
            'api_version': r'/v\d+/|/api/v\d+',
            'cors': r'CORS|cors|Access-Control',
            'api_key': r'api[_-]?key|X-API-Key',
            'endpoint': r'@(app|router)\.(get|post|put|delete|patch)',
        }
        
        for file_path in self.scan_files(['.py', '.js', '.ts']):
            try:
                content = file_path.read_text()
                
                if re.search(api_patterns['rate_limit'], content, re.IGNORECASE):
                    api_info['rate_limiting'] = True
                    
                if re.search(api_patterns['api_version'], content):
                    api_info['api_versioning'] = True
                    
                if re.search(api_patterns['cors'], content, re.IGNORECASE):
                    api_info['cors_configured'] = True
                    
                # Count endpoints
                endpoints = re.findall(api_patterns['endpoint'], content)
                api_info['endpoints_count'] += len(endpoints)
                
            except Exception:
                pass
        
        return api_info
    
    def _calculate_security_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall security score"""
        score = 100.0
        
        # Deduct points for vulnerabilities
        vuln_count = sum(len(v) for v in metrics['vulnerabilities'].values())
        score -= vuln_count * 5
        
        # Deduct for missing authentication
        if not metrics['authentication']['methods']:
            score -= 10
            
        # Deduct for weak password hashing
        if not metrics['authentication']['password_hashing']:
            score -= 15
        elif metrics['authentication']['password_hashing'] not in ['bcrypt', 'argon2']:
            score -= 10
            
        # Deduct for missing authorization
        if metrics['authorization']['permission_checks'] == 0:
            score -= 10
            
        # Deduct for missing encryption
        if not metrics['encryption']['tls_ssl']:
            score -= 10
            
        # Deduct for poor input validation
        if metrics['input_validation']['validators_count'] < 5:
            score -= 10
            
        # Deduct for vulnerable dependencies
        score -= len(metrics['dependency_vulnerabilities']['known_vulnerabilities']) * 5
        
        # Deduct for missing security headers
        headers_count = sum(1 for v in metrics['security_headers'].values() if v)
        if headers_count < 3:
            score -= 10
            
        # Deduct for API security issues
        if metrics['api_security']['endpoints_count'] > 0 and not metrics['api_security']['rate_limiting']:
            score -= 5
            
        return max(0.0, score)
    
    def _detect_security_issues(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect security issues"""
        issues = []
        
        # Critical vulnerabilities
        for vuln_type, instances in metrics['vulnerabilities'].items():
            if instances:
                severity = 'critical' if vuln_type in ['sql_injection', 'command_injection'] else 'high'
                issues.append({
                    'severity': severity,
                    'type': 'vulnerability',
                    'message': f"{vuln_type.replace('_', ' ').title()} vulnerability found in {len(instances)} location(s)",
                    'locations': instances[:3],  # First 3 instances
                })
        
        # Authentication issues
        if not metrics['authentication']['password_hashing']:
            issues.append({
                'severity': 'critical',
                'type': 'authentication',
                'message': 'No secure password hashing mechanism found',
            })
        
        # Authorization issues
        if metrics['authorization']['permission_checks'] == 0:
            issues.append({
                'severity': 'high',
                'type': 'authorization',
                'message': 'No authorization checks found in the codebase',
            })
        
        # Encryption issues
        if not metrics['encryption']['tls_ssl']:
            issues.append({
                'severity': 'high',
                'type': 'encryption',
                'message': 'No TLS/SSL implementation found',
            })
        
        # Input validation issues
        if not metrics['input_validation']['sanitization']:
            issues.append({
                'severity': 'high',
                'type': 'validation',
                'message': 'No input sanitization found',
            })
        
        # Dependency issues
        if metrics['dependency_vulnerabilities']['known_vulnerabilities']:
            issues.append({
                'severity': 'high',
                'type': 'dependencies',
                'message': f"Known vulnerabilities in dependencies: {', '.join(metrics['dependency_vulnerabilities']['known_vulnerabilities'])}",
            })
        
        # API security issues
        if metrics['api_security']['endpoints_count'] > 0:
            if not metrics['api_security']['rate_limiting']:
                issues.append({
                    'severity': 'medium',
                    'type': 'api',
                    'message': 'API endpoints found without rate limiting',
                })
            
            if not metrics['api_security']['api_authentication']:
                issues.append({
                    'severity': 'high',
                    'type': 'api',
                    'message': 'API endpoints without authentication mechanism',
                })
        
        return issues
    
    def _generate_security_suggestions(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate security improvement suggestions"""
        suggestions = []
        
        # Authentication suggestions
        if not metrics['authentication']['password_hashing']:
            suggestions.append("Implement secure password hashing using bcrypt or Argon2")
        elif metrics['authentication']['password_hashing'] not in ['bcrypt', 'argon2']:
            suggestions.append("Upgrade password hashing to bcrypt or Argon2")
            
        if not metrics['authentication']['jwt_usage'] and metrics['api_security']['endpoints_count'] > 0:
            suggestions.append("Consider implementing JWT for stateless API authentication")
        
        # Authorization suggestions
        if not metrics['authorization']['rbac']:
            suggestions.append("Implement Role-Based Access Control (RBAC) for better authorization")
            
        if metrics['authorization']['permission_checks'] < 10:
            suggestions.append("Add more granular permission checks throughout the application")
        
        # Encryption suggestions
        if not metrics['encryption']['tls_ssl']:
            suggestions.append("Implement TLS/SSL for all network communications")
            
        if not metrics['encryption']['data_encryption']:
            suggestions.append("Implement encryption for sensitive data at rest")
        
        # Input validation suggestions
        if not metrics['input_validation']['frameworks']:
            suggestions.append("Use validation frameworks like Pydantic or Marshmallow for robust input validation")
            
        if not metrics['input_validation']['sanitization']:
            suggestions.append("Implement input sanitization to prevent XSS and injection attacks")
        
        # Security headers suggestions
        headers_count = sum(1 for v in metrics['security_headers'].values() if v)
        if headers_count < 3:
            suggestions.append("Implement security headers: CSP, X-Frame-Options, X-Content-Type-Options")
        
        # API security suggestions
        if metrics['api_security']['endpoints_count'] > 0:
            if not metrics['api_security']['rate_limiting']:
                suggestions.append("Implement rate limiting for API endpoints")
                
            if not metrics['api_security']['api_versioning']:
                suggestions.append("Implement API versioning for better backward compatibility")
                
            if not metrics['api_security']['cors_configured']:
                suggestions.append("Configure CORS properly for API security")
        
        # Dependency suggestions
        if metrics['dependency_vulnerabilities']['outdated_packages']:
            suggestions.append("Pin all dependency versions to avoid unexpected updates")
            
        if metrics['dependency_vulnerabilities']['known_vulnerabilities']:
            suggestions.append("Update vulnerable dependencies to their latest secure versions")
        
        # General suggestions
        suggestions.append("Conduct regular security audits and penetration testing")
        suggestions.append("Implement security logging and monitoring")
        suggestions.append("Create a security incident response plan")
        
        return suggestions[:10]  # Return top 10 suggestions