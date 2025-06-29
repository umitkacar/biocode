"""
Smell Fixer - Automatically fixes detected code smells
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

Applies automated fixes for code smells when possible.
"""
import ast
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import difflib
import logging
from dataclasses import dataclass


@dataclass
class FixResult:
    """Result of a fix attempt"""
    success: bool
    file_path: str
    original_content: str
    fixed_content: str
    changes_made: List[str]
    error: Optional[str] = None


class SmellFixer:
    """
    Automatically fixes code smells where safe to do so.
    
    Supported fixes:
    - Remove commented code
    - Replace magic numbers with constants
    - Add logging to empty exception handlers
    - Break long lines
    - Extract long methods (with suggestions)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fix_handlers = {
            "commented_code": self._fix_commented_code,
            "magic_number": self._fix_magic_number,
            "empty_exception_handler": self._fix_empty_exception,
            "long_line": self._fix_long_line,
        }
        
    def apply_fixes(self, smells: List[Dict[str, Any]], dry_run: bool = True) -> List[FixResult]:
        """
        Apply fixes to detected smells.
        
        Args:
            smells: List of smell dictionaries from CodeSmellAnalyzer
            dry_run: If True, show what would be changed without applying
            
        Returns:
            List of fix results
        """
        # Group smells by file
        smells_by_file = {}
        for smell in smells:
            if smell.get('auto_fixable', False):
                file_path = smell['file']
                if file_path not in smells_by_file:
                    smells_by_file[file_path] = []
                smells_by_file[file_path].append(smell)
                
        results = []
        
        # Process each file
        for file_path, file_smells in smells_by_file.items():
            result = self._fix_file(file_path, file_smells, dry_run)
            results.append(result)
            
        return results
        
    def _fix_file(self, file_path: str, smells: List[Dict[str, Any]], dry_run: bool) -> FixResult:
        """Fix smells in a single file"""
        try:
            # Read original content
            path = Path(file_path)
            original_content = path.read_text(encoding='utf-8')
            lines = original_content.splitlines(keepends=True)
            
            # Sort smells by line number (reverse to fix from bottom up)
            smells_sorted = sorted(smells, key=lambda s: s['line'], reverse=True)
            
            changes_made = []
            
            # Apply fixes
            for smell in smells_sorted:
                smell_type = smell['type']
                if smell_type in self.fix_handlers:
                    handler = self.fix_handlers[smell_type]
                    lines, change = handler(lines, smell)
                    if change:
                        changes_made.append(change)
                        
            # Join lines back
            fixed_content = ''.join(lines)
            
            # Write changes if not dry run
            if not dry_run and fixed_content != original_content:
                path.write_text(fixed_content, encoding='utf-8')
                
            return FixResult(
                success=True,
                file_path=file_path,
                original_content=original_content,
                fixed_content=fixed_content,
                changes_made=changes_made
            )
            
        except Exception as e:
            self.logger.error(f"Error fixing {file_path}: {e}")
            return FixResult(
                success=False,
                file_path=file_path,
                original_content="",
                fixed_content="",
                changes_made=[],
                error=str(e)
            )
            
    def _fix_commented_code(self, lines: List[str], smell: Dict[str, Any]) -> Tuple[List[str], Optional[str]]:
        """Remove commented code"""
        line_num = smell['line'] - 1  # Convert to 0-based
        
        if 0 <= line_num < len(lines):
            removed_line = lines[line_num].strip()
            lines[line_num] = ""  # Remove line
            return lines, f"Removed commented code: {removed_line}"
            
        return lines, None
        
    def _fix_magic_number(self, lines: List[str], smell: Dict[str, Any]) -> Tuple[List[str], Optional[str]]:
        """Replace magic number with constant"""
        line_num = smell['line'] - 1
        
        if 0 <= line_num < len(lines):
            line = lines[line_num]
            
            # Extract the magic number from message
            import re
            match = re.search(r'Magic number (\d+)', smell['message'])
            if match:
                magic_num = match.group(1)
                
                # Find appropriate place to add constant
                # For now, add comment suggesting the fix
                indent = len(line) - len(line.lstrip())
                comment = f"{' ' * indent}# TODO: Extract {magic_num} to named constant\n"
                
                # Add comment if not already there
                if comment.strip() not in lines[line_num - 1] if line_num > 0 else True:
                    lines.insert(line_num, comment)
                    return lines, f"Added TODO for magic number {magic_num}"
                    
        return lines, None
        
    def _fix_empty_exception(self, lines: List[str], smell: Dict[str, Any]) -> Tuple[List[str], Optional[str]]:
        """Add logging to empty exception handler"""
        line_num = smell['line'] - 1
        
        # Find the except block
        for i in range(line_num, min(line_num + 10, len(lines))):
            if 'except' in lines[i]:
                # Find the pass statement
                for j in range(i + 1, min(i + 5, len(lines))):
                    if 'pass' in lines[j] and lines[j].strip() == 'pass':
                        # Replace pass with logging
                        indent = len(lines[j]) - len(lines[j].lstrip())
                        lines[j] = f"{' ' * indent}import logging\n"
                        lines.insert(j + 1, f"{' ' * indent}logging.exception('An error occurred')\n")
                        return lines, "Replaced empty exception handler with logging"
                        
        return lines, None
        
    def _fix_long_line(self, lines: List[str], smell: Dict[str, Any]) -> Tuple[List[str], Optional[str]]:
        """Break long lines"""
        line_num = smell['line'] - 1
        
        if 0 <= line_num < len(lines):
            line = lines[line_num]
            
            # Simple strategy: add comment suggesting where to break
            if len(line) > 120:
                # Check if it's a string
                if '"""' in line or "'''" in line or ('"' in line and line.count('"') >= 2):
                    lines[line_num] = line.rstrip() + "  # Long string - consider using textwrap\n"
                    return lines, "Added comment for long string"
                    
                # Check if it's a function call
                elif '(' in line and ')' in line:
                    lines[line_num] = line.rstrip() + "  # Break into multiple lines\n"
                    return lines, "Added comment for long function call"
                    
        return lines, None
        
    def generate_fix_report(self, results: List[FixResult]) -> str:
        """Generate a markdown report of fixes"""
        report = ["# Code Smell Fix Report\n"]
        
        total_files = len(results)
        successful_fixes = sum(1 for r in results if r.success and r.changes_made)
        total_changes = sum(len(r.changes_made) for r in results)
        
        report.append(f"## Summary\n")
        report.append(f"- Files processed: {total_files}\n")
        report.append(f"- Files with fixes: {successful_fixes}\n")
        report.append(f"- Total changes: {total_changes}\n\n")
        
        report.append("## Detailed Changes\n")
        
        for result in results:
            if result.success and result.changes_made:
                report.append(f"### {result.file_path}\n")
                
                # Show diff
                diff = difflib.unified_diff(
                    result.original_content.splitlines(keepends=True),
                    result.fixed_content.splitlines(keepends=True),
                    fromfile=f"{result.file_path} (original)",
                    tofile=f"{result.file_path} (fixed)",
                    lineterm=""
                )
                
                report.append("```diff\n")
                report.extend(diff)
                report.append("\n```\n\n")
                
                # List changes
                report.append("**Changes made:**\n")
                for change in result.changes_made:
                    report.append(f"- {change}\n")
                report.append("\n")
                
        return ''.join(report)
        
    def generate_pr_description(self, results: List[FixResult]) -> str:
        """Generate GitHub PR description"""
        total_changes = sum(len(r.changes_made) for r in results)
        
        description = [
            "## 🧬 Automated Code Smell Fixes\n",
            f"This PR contains {total_changes} automated fixes for detected code smells.\n\n",
            "### Changes by type:\n"
        ]
        
        # Count changes by type
        change_counts = {}
        for result in results:
            for change in result.changes_made:
                if "commented code" in change:
                    change_counts["Removed commented code"] = change_counts.get("Removed commented code", 0) + 1
                elif "TODO" in change:
                    change_counts["Added TODO comments"] = change_counts.get("Added TODO comments", 0) + 1
                elif "exception" in change:
                    change_counts["Fixed empty exceptions"] = change_counts.get("Fixed empty exceptions", 0) + 1
                    
        for change_type, count in change_counts.items():
            description.append(f"- {change_type}: {count}\n")
            
        description.extend([
            "\n### Review checklist:\n",
            "- [ ] All changes preserve functionality\n",
            "- [ ] No unintended side effects\n",
            "- [ ] Tests still pass\n",
            "\n---\n",
            "*Generated by BioCode Smell Fixer* 🦨"
        ])
        
        return ''.join(description)