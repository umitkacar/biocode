"""
BioCode Self-Repair System - Autonomous code healing
"""
import ast
import re
import json
import difflib
import subprocess
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class RepairPattern:
    """Known error pattern and its fix"""
    error_pattern: str
    fix_template: str
    description: str
    confidence: float = 0.8
    test_required: bool = True


@dataclass
class PatchSuggestion:
    """Suggested code patch"""
    file_path: str
    line_number: int
    original_code: str
    suggested_code: str
    error_type: str
    confidence: float
    reasoning: str
    test_command: Optional[str] = None


class RepairKnowledgeBase:
    """Knowledge base for code repairs"""
    
    def __init__(self):
        self.patterns = self._load_repair_patterns()
        self.successful_repairs = []
        self.failed_repairs = []
        
    def _load_repair_patterns(self) -> List[RepairPattern]:
        """Load known repair patterns"""
        return [
            # Import errors
            RepairPattern(
                error_pattern=r"ImportError: cannot import name '(\w+)' from '([\w.]+)'",
                fix_template="from {module} import {name}",
                description="Fix import error by correcting import statement"
            ),
            RepairPattern(
                error_pattern=r"ModuleNotFoundError: No module named '(\w+)'",
                fix_template="import {module}",
                description="Add missing import"
            ),
            
            # Type errors
            RepairPattern(
                error_pattern=r"TypeError: .+ missing (\d+) required positional argument",
                fix_template="# Add missing arguments to function call",
                description="Fix missing function arguments"
            ),
            
            # Attribute errors
            RepairPattern(
                error_pattern=r"AttributeError: '(\w+)' object has no attribute '(\w+)'",
                fix_template="# Check if attribute exists: hasattr({obj}, '{attr}')",
                description="Handle missing attribute"
            ),
            
            # Syntax errors
            RepairPattern(
                error_pattern=r"SyntaxError: invalid syntax",
                fix_template="# Fix syntax error",
                description="Correct syntax error"
            ),
            
            # Index errors
            RepairPattern(
                error_pattern=r"IndexError: list index out of range",
                fix_template="if len({list_var}) > {index}:",
                description="Add bounds checking"
            ),
            
            # Key errors
            RepairPattern(
                error_pattern=r"KeyError: '(\w+)'",
                fix_template="{dict_var}.get('{key}', default_value)",
                description="Use safe dictionary access"
            ),
            
            # Division by zero
            RepairPattern(
                error_pattern=r"ZeroDivisionError: division by zero",
                fix_template="if {divisor} != 0:",
                description="Add zero check before division"
            ),
            
            # File not found
            RepairPattern(
                error_pattern=r"FileNotFoundError: .+ '(.+)'",
                fix_template="if os.path.exists('{filepath}'):",
                description="Add file existence check"
            ),
            
            # Null/None errors
            RepairPattern(
                error_pattern=r"AttributeError: 'NoneType' object",
                fix_template="if {var} is not None:",
                description="Add None check"
            )
        ]
    
    def find_matching_pattern(self, error_message: str) -> Optional[RepairPattern]:
        """Find repair pattern matching error"""
        for pattern in self.patterns:
            if re.search(pattern.error_pattern, error_message):
                return pattern
        return None
    
    def record_repair_result(self, patch: PatchSuggestion, success: bool):
        """Record repair attempt result for learning"""
        repair_record = {
            'patch': patch,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        if success:
            self.successful_repairs.append(repair_record)
        else:
            self.failed_repairs.append(repair_record)


class CodeAnalyzer:
    """Analyze code for potential issues"""
    
    @staticmethod
    def analyze_syntax(code: str) -> List[Dict[str, Any]]:
        """Analyze code for syntax errors"""
        issues = []
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append({
                'type': 'syntax_error',
                'line': e.lineno,
                'offset': e.offset,
                'message': str(e),
                'text': e.text
            })
        
        return issues
    
    @staticmethod
    def analyze_imports(code: str) -> List[Dict[str, Any]]:
        """Analyze import statements"""
        issues = []
        
        try:
            tree = ast.parse(code)
            
            # Check for circular imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module)
            
            # Check for duplicate imports
            seen = set()
            for imp in imports:
                if imp in seen:
                    issues.append({
                        'type': 'duplicate_import',
                        'module': imp,
                        'message': f"Duplicate import: {imp}"
                    })
                seen.add(imp)
                
        except Exception as e:
            logger.debug(f"Import analysis failed: {e}")
        
        return issues
    
    @staticmethod
    def analyze_undefined_variables(code: str) -> List[Dict[str, Any]]:
        """Check for undefined variables"""
        issues = []
        
        try:
            tree = ast.parse(code)
            
            # Simple undefined variable check
            defined_names = set()
            used_names = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    if isinstance(node.ctx, ast.Store):
                        defined_names.add(node.id)
                    elif isinstance(node.ctx, ast.Load):
                        used_names.add(node.id)
                elif isinstance(node, ast.FunctionDef):
                    defined_names.add(node.name)
                elif isinstance(node, ast.ClassDef):
                    defined_names.add(node.name)
            
            # Check for undefined
            builtins = set(dir(__builtins__))
            undefined = used_names - defined_names - builtins
            
            for name in undefined:
                issues.append({
                    'type': 'undefined_variable',
                    'name': name,
                    'message': f"Undefined variable: {name}"
                })
                
        except Exception as e:
            logger.debug(f"Variable analysis failed: {e}")
        
        return issues


class SelfRepairAgent:
    """Agent capability for self-repair"""
    
    def __init__(self):
        self.knowledge_base = RepairKnowledgeBase()
        self.analyzer = CodeAnalyzer()
        self.repair_history = []
        
    def diagnose_error(self, error_info: Dict[str, Any]) -> List[PatchSuggestion]:
        """Diagnose error and suggest patches"""
        suggestions = []
        
        error_message = error_info.get('error_message', '')
        file_path = error_info.get('file_path', '')
        line_number = error_info.get('line_number', 0)
        
        # Try pattern matching first
        pattern = self.knowledge_base.find_matching_pattern(error_message)
        if pattern:
            suggestion = self._create_pattern_based_patch(
                pattern, error_info, file_path, line_number
            )
            if suggestion:
                suggestions.append(suggestion)
        
        # Try code analysis
        if file_path and Path(file_path).exists():
            analysis_suggestions = self._analyze_code_context(
                file_path, line_number, error_message
            )
            suggestions.extend(analysis_suggestions)
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        return suggestions
    
    def _create_pattern_based_patch(
        self, 
        pattern: RepairPattern, 
        error_info: Dict[str, Any],
        file_path: str,
        line_number: int
    ) -> Optional[PatchSuggestion]:
        """Create patch based on known pattern"""
        try:
            # Extract variables from error message
            match = re.search(pattern.error_pattern, error_info['error_message'])
            if not match:
                return None
            
            # Read the problematic line
            if not Path(file_path).exists():
                return None
                
            with open(file_path, 'r') as f:
                lines = f.readlines()
                
            if line_number <= 0 or line_number > len(lines):
                return None
                
            original_line = lines[line_number - 1]
            
            # Generate fix based on template
            fix_vars = {}
            for i, group in enumerate(match.groups(), 1):
                fix_vars[f'var{i}'] = group
                fix_vars[f'module'] = group  # Common names
                fix_vars[f'name'] = group
                fix_vars[f'attr'] = group
                fix_vars[f'key'] = group
            
            suggested_code = pattern.fix_template.format(**fix_vars)
            
            return PatchSuggestion(
                file_path=file_path,
                line_number=line_number,
                original_code=original_line.strip(),
                suggested_code=suggested_code,
                error_type=pattern.description,
                confidence=pattern.confidence,
                reasoning=f"Pattern match: {pattern.description}",
                test_command=self._generate_test_command(file_path)
            )
            
        except Exception as e:
            logger.error(f"Failed to create pattern-based patch: {e}")
            return None
    
    def _analyze_code_context(
        self, 
        file_path: str, 
        line_number: int,
        error_message: str
    ) -> List[PatchSuggestion]:
        """Analyze code context for repairs"""
        suggestions = []
        
        try:
            with open(file_path, 'r') as f:
                code = f.read()
                lines = code.splitlines()
            
            # Syntax analysis
            syntax_issues = self.analyzer.analyze_syntax(code)
            for issue in syntax_issues:
                if issue['line'] == line_number:
                    suggestion = self._fix_syntax_error(
                        file_path, issue, lines
                    )
                    if suggestion:
                        suggestions.append(suggestion)
            
            # Import analysis
            if 'import' in error_message.lower():
                import_issues = self.analyzer.analyze_imports(code)
                for issue in import_issues:
                    suggestion = self._fix_import_error(
                        file_path, issue, lines, error_message
                    )
                    if suggestion:
                        suggestions.append(suggestion)
            
            # Undefined variable analysis
            undefined_issues = self.analyzer.analyze_undefined_variables(code)
            for issue in undefined_issues:
                if issue['name'] in error_message:
                    suggestion = self._fix_undefined_variable(
                        file_path, issue, lines, line_number
                    )
                    if suggestion:
                        suggestions.append(suggestion)
                        
        except Exception as e:
            logger.error(f"Code context analysis failed: {e}")
        
        return suggestions
    
    def _fix_syntax_error(
        self, 
        file_path: str,
        issue: Dict[str, Any],
        lines: List[str]
    ) -> Optional[PatchSuggestion]:
        """Fix syntax errors"""
        line_idx = issue['line'] - 1
        if line_idx < 0 or line_idx >= len(lines):
            return None
            
        original_line = lines[line_idx]
        suggested_line = original_line
        
        # Common syntax fixes
        if ':' not in original_line and any(kw in original_line for kw in ['if', 'for', 'while', 'def', 'class']):
            suggested_line = original_line.rstrip() + ':'
        elif original_line.count('(') != original_line.count(')'):
            # Balance parentheses
            if original_line.count('(') > original_line.count(')'):
                suggested_line = original_line.rstrip() + ')'
            else:
                suggested_line = '(' + original_line.lstrip()
        elif original_line.count('[') != original_line.count(']'):
            # Balance brackets
            if original_line.count('[') > original_line.count(']'):
                suggested_line = original_line.rstrip() + ']'
        elif original_line.count('{') != original_line.count('}'):
            # Balance braces
            if original_line.count('{') > original_line.count('}'):
                suggested_line = original_line.rstrip() + '}'
        
        if suggested_line != original_line:
            return PatchSuggestion(
                file_path=file_path,
                line_number=issue['line'],
                original_code=original_line.strip(),
                suggested_code=suggested_line.strip(),
                error_type='syntax_error',
                confidence=0.7,
                reasoning="Common syntax pattern fix"
            )
        
        return None
    
    def _fix_import_error(
        self,
        file_path: str,
        issue: Dict[str, Any],
        lines: List[str],
        error_message: str
    ) -> Optional[PatchSuggestion]:
        """Fix import errors"""
        # Extract module name from error
        module_match = re.search(r"No module named '([\w.]+)'", error_message)
        if module_match:
            module_name = module_match.group(1)
            
            # Suggest adding import at top
            import_line = f"import {module_name}"
            
            # Find where to insert (after other imports)
            insert_line = 0
            for i, line in enumerate(lines):
                if line.strip().startswith(('import ', 'from ')):
                    insert_line = i + 1
                elif line.strip() and not line.strip().startswith('#'):
                    break
            
            return PatchSuggestion(
                file_path=file_path,
                line_number=insert_line + 1,
                original_code="",
                suggested_code=import_line,
                error_type='missing_import',
                confidence=0.8,
                reasoning=f"Add missing import for {module_name}"
            )
        
        return None
    
    def _fix_undefined_variable(
        self,
        file_path: str,
        issue: Dict[str, Any],
        lines: List[str],
        line_number: int
    ) -> Optional[PatchSuggestion]:
        """Fix undefined variable errors"""
        var_name = issue['name']
        
        # Common fixes
        suggestions = [
            f"{var_name} = None  # Initialize variable",
            f"{var_name} = []  # Initialize as empty list",
            f"{var_name} = {{}}  # Initialize as empty dict",
            f"{var_name} = ''  # Initialize as empty string",
        ]
        
        # Try to infer type from usage
        for i, line in enumerate(lines):
            if var_name in line:
                if f"{var_name}.append" in line:
                    suggested_code = f"{var_name} = []"
                    break
                elif f"{var_name}[" in line and ']' in line:
                    if '{' in line:
                        suggested_code = f"{var_name} = {{}}"
                    else:
                        suggested_code = f"{var_name} = []"
                    break
                elif f"{var_name}." in line:
                    suggested_code = f"{var_name} = None  # TODO: Initialize properly"
                    break
        else:
            suggested_code = suggestions[0]
        
        # Find where to insert
        insert_line = max(0, line_number - 1)
        
        return PatchSuggestion(
            file_path=file_path,
            line_number=insert_line,
            original_code="",
            suggested_code=suggested_code,
            error_type='undefined_variable',
            confidence=0.6,
            reasoning=f"Initialize undefined variable: {var_name}"
        )
    
    def _generate_test_command(self, file_path: str) -> Optional[str]:
        """Generate test command for file"""
        path = Path(file_path)
        
        # Python file
        if path.suffix == '.py':
            # Check for test file
            test_file = path.parent / f"test_{path.name}"
            if test_file.exists():
                return f"python -m pytest {test_file}"
            
            # Check if it's a test file
            if path.name.startswith('test_'):
                return f"python -m pytest {file_path}"
            
            # Try to run the file
            return f"python {file_path}"
        
        return None
    
    def apply_patch(
        self, 
        patch: PatchSuggestion,
        dry_run: bool = False
    ) -> Tuple[bool, str]:
        """Apply a patch to code"""
        try:
            with open(patch.file_path, 'r') as f:
                lines = f.readlines()
            
            # Validate line number
            if patch.line_number <= 0 or patch.line_number > len(lines) + 1:
                return False, "Invalid line number"
            
            # Create backup
            backup_path = f"{patch.file_path}.backup"
            if not dry_run:
                with open(backup_path, 'w') as f:
                    f.writelines(lines)
            
            # Apply patch
            if patch.original_code:
                # Replace existing line
                lines[patch.line_number - 1] = patch.suggested_code + '\n'
            else:
                # Insert new line
                lines.insert(patch.line_number - 1, patch.suggested_code + '\n')
            
            if dry_run:
                # Return diff
                diff = difflib.unified_diff(
                    open(patch.file_path).readlines(),
                    lines,
                    fromfile=patch.file_path,
                    tofile=f"{patch.file_path} (patched)",
                    lineterm=''
                )
                return True, '\n'.join(diff)
            
            # Write patched file
            with open(patch.file_path, 'w') as f:
                f.writelines(lines)
            
            # Test if specified
            if patch.test_command:
                result = subprocess.run(
                    patch.test_command.split(),
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    # Restore backup
                    with open(backup_path, 'r') as f:
                        content = f.read()
                    with open(patch.file_path, 'w') as f:
                        f.write(content)
                    
                    return False, f"Test failed: {result.stderr}"
            
            # Record success
            self.knowledge_base.record_repair_result(patch, True)
            
            # Clean up backup
            if Path(backup_path).exists():
                Path(backup_path).unlink()
            
            return True, "Patch applied successfully"
            
        except Exception as e:
            # Record failure
            self.knowledge_base.record_repair_result(patch, False)
            return False, f"Failed to apply patch: {e}"
    
    def learn_from_fix(
        self,
        error_info: Dict[str, Any],
        successful_patch: PatchSuggestion
    ):
        """Learn from successful repairs"""
        # Add to knowledge base
        new_pattern = RepairPattern(
            error_pattern=re.escape(error_info['error_message']),
            fix_template=successful_patch.suggested_code,
            description=f"Learned fix for {successful_patch.error_type}",
            confidence=0.6
        )
        
        self.knowledge_base.patterns.append(new_pattern)
        
        # Update repair history
        self.repair_history.append({
            'error': error_info,
            'patch': successful_patch,
            'timestamp': datetime.now().isoformat()
        })


# Integration with BioCode Agent
from datetime import datetime

class RepairCell:
    """Cell specialized in code repair"""
    
    def __init__(self, agent):
        self.agent = agent
        self.repair_agent = SelfRepairAgent()
        self.repair_count = 0
        self.success_count = 0
        
    async def check_and_repair(self):
        """Check for errors and attempt repairs"""
        if not self.agent.memory.errors_detected:
            return
        
        # Process recent errors
        recent_errors = self.agent.memory.errors_detected[-10:]
        
        for error_info in recent_errors:
            # Skip if already attempted
            if error_info.get('repair_attempted'):
                continue
            
            # Diagnose error
            suggestions = self.repair_agent.diagnose_error(error_info)
            
            if suggestions:
                # Try the best suggestion
                best_patch = suggestions[0]
                
                # Log attempt
                self.agent._log_to_terminal(
                    f"🔧 Attempting repair: {best_patch.error_type}",
                    "warning"
                )
                
                # Apply patch
                success, message = self.repair_agent.apply_patch(
                    best_patch,
                    dry_run=self.agent.sandbox_mode
                )
                
                if success:
                    self.success_count += 1
                    self.agent._log_to_terminal(
                        f"✅ Repair successful: {best_patch.reasoning}",
                        "success"
                    )
                    
                    # Learn from success
                    self.repair_agent.learn_from_fix(error_info, best_patch)
                else:
                    self.agent._log_to_terminal(
                        f"❌ Repair failed: {message}",
                        "error"
                    )
                
                # Mark as attempted
                error_info['repair_attempted'] = True
                self.repair_count += 1
    
    def get_repair_stats(self) -> Dict[str, Any]:
        """Get repair statistics"""
        return {
            'total_repairs': self.repair_count,
            'successful_repairs': self.success_count,
            'success_rate': self.success_count / self.repair_count if self.repair_count > 0 else 0,
            'knowledge_patterns': len(self.repair_agent.knowledge_base.patterns),
            'repair_history': len(self.repair_agent.repair_history)
        }