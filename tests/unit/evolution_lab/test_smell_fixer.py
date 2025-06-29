"""
Tests for Smell Fixer
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import pytest
import tempfile
from pathlib import Path
import textwrap

from src.evolution_lab.fixers.smell_fixer import SmellFixer, FixResult


@pytest.fixture
def temp_file():
    """Create a temporary file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        content = textwrap.dedent("""
            # This is a test file
            
            def calculate(x):
                # def old_calculate(x):
                #     return x * 2
                
                if x > 100:  # Magic number
                    return x * 0.9
                    
                try:
                    result = x / 2
                except:
                    pass
                    
                return result
                
            # This is a very long line that exceeds the maximum line length threshold and should be broken into multiple lines
        """)
        f.write(content)
        f.flush()
        yield Path(f.name)
        
    # Cleanup
    Path(f.name).unlink(missing_ok=True)


class TestSmellFixer:
    """Test SmellFixer class"""
    
    def test_fixer_initialization(self):
        """Test fixer initialization"""
        fixer = SmellFixer()
        
        assert fixer.fix_handlers is not None
        assert 'commented_code' in fixer.fix_handlers
        assert 'magic_number' in fixer.fix_handlers
        assert 'empty_exception_handler' in fixer.fix_handlers
        
    def test_fix_commented_code(self, temp_file):
        """Test fixing commented code"""
        fixer = SmellFixer()
        
        smells = [{
            'type': 'commented_code',
            'file': str(temp_file),
            'line': 4,
            'auto_fixable': True,
            'message': 'Commented out code'
        }]
        
        results = fixer.apply_fixes(smells, dry_run=False)
        
        assert len(results) == 1
        result = results[0]
        assert result.success
        assert len(result.changes_made) > 0
        
        # Check that line was removed
        fixed_content = temp_file.read_text()
        assert '# def old_calculate(x):' not in fixed_content
        
    def test_fix_magic_number(self, temp_file):
        """Test fixing magic numbers"""
        fixer = SmellFixer()
        
        smells = [{
            'type': 'magic_number',
            'file': str(temp_file),
            'line': 7,
            'message': 'Magic number 100 should be a named constant',
            'auto_fixable': True
        }]
        
        results = fixer.apply_fixes(smells, dry_run=False)
        
        assert len(results) == 1
        result = results[0]
        assert result.success
        
        # Check that TODO was added
        fixed_content = temp_file.read_text()
        assert 'TODO: Extract 100 to named constant' in fixed_content
        
    def test_fix_empty_exception(self, temp_file):
        """Test fixing empty exception handlers"""
        fixer = SmellFixer()
        
        smells = [{
            'type': 'empty_exception_handler',
            'file': str(temp_file),
            'line': 10,
            'auto_fixable': True,
            'fix_code': "import logging\nlogging.exception('An error occurred')"
        }]
        
        results = fixer.apply_fixes(smells, dry_run=False)
        
        assert len(results) == 1
        result = results[0]
        assert result.success
        
        # Check that logging was added
        fixed_content = temp_file.read_text()
        assert 'import logging' in fixed_content
        assert "logging.exception('An error occurred')" in fixed_content
        assert 'pass' not in fixed_content or fixed_content.count('pass') < result.original_content.count('pass')
        
    def test_fix_long_line(self, temp_file):
        """Test fixing long lines"""
        fixer = SmellFixer()
        
        smells = [{
            'type': 'long_line',
            'file': str(temp_file),
            'line': 17,
            'auto_fixable': True
        }]
        
        results = fixer.apply_fixes(smells, dry_run=False)
        
        assert len(results) == 1
        result = results[0]
        assert result.success
        
        # Check that comment was added
        fixed_content = temp_file.read_text()
        assert '# Break into multiple lines' in fixed_content or '# Long string' in fixed_content
        
    def test_dry_run_mode(self, temp_file):
        """Test dry run mode doesn't modify files"""
        fixer = SmellFixer()
        original_content = temp_file.read_text()
        
        smells = [{
            'type': 'commented_code',
            'file': str(temp_file),
            'line': 4,
            'auto_fixable': True
        }]
        
        results = fixer.apply_fixes(smells, dry_run=True)
        
        assert len(results) == 1
        assert results[0].success
        
        # File should not be modified
        current_content = temp_file.read_text()
        assert current_content == original_content
        
    def test_multiple_fixes_same_file(self, temp_file):
        """Test applying multiple fixes to the same file"""
        fixer = SmellFixer()
        
        smells = [
            {
                'type': 'commented_code',
                'file': str(temp_file),
                'line': 4,
                'auto_fixable': True
            },
            {
                'type': 'magic_number',
                'file': str(temp_file),
                'line': 7,
                'message': 'Magic number 100',
                'auto_fixable': True
            }
        ]
        
        results = fixer.apply_fixes(smells, dry_run=False)
        
        assert len(results) == 1
        result = results[0]
        assert result.success
        assert len(result.changes_made) >= 2
        
    def test_error_handling(self):
        """Test error handling for non-existent files"""
        fixer = SmellFixer()
        
        smells = [{
            'type': 'commented_code',
            'file': '/non/existent/file.py',
            'line': 1,
            'auto_fixable': True
        }]
        
        results = fixer.apply_fixes(smells, dry_run=False)
        
        assert len(results) == 1
        result = results[0]
        assert not result.success
        assert result.error is not None
        
    def test_fix_result_dataclass(self):
        """Test FixResult dataclass"""
        result = FixResult(
            success=True,
            file_path="/test/file.py",
            original_content="original",
            fixed_content="fixed",
            changes_made=["change1", "change2"]
        )
        
        assert result.success is True
        assert result.file_path == "/test/file.py"
        assert len(result.changes_made) == 2
        assert result.error is None
        
    def test_generate_fix_report(self, temp_file):
        """Test fix report generation"""
        fixer = SmellFixer()
        
        # Create a successful fix result
        result = FixResult(
            success=True,
            file_path=str(temp_file),
            original_content="def foo():\n    pass",
            fixed_content="def foo():\n    return None",
            changes_made=["Replaced pass with return None"]
        )
        
        report = fixer.generate_fix_report([result])
        
        assert "# Code Smell Fix Report" in report
        assert "Files processed: 1" in report
        assert "Total changes: 1" in report
        assert str(temp_file) in report
        
    def test_generate_pr_description(self):
        """Test PR description generation"""
        fixer = SmellFixer()
        
        results = [
            FixResult(
                success=True,
                file_path="file1.py",
                original_content="",
                fixed_content="",
                changes_made=["Removed commented code: # old code"]
            ),
            FixResult(
                success=True,
                file_path="file2.py",
                original_content="",
                fixed_content="",
                changes_made=["Added TODO for magic number 42"]
            )
        ]
        
        description = fixer.generate_pr_description(results)
        
        assert "Automated Code Smell Fixes" in description
        assert "2 automated fixes" in description
        assert "Review checklist" in description
        assert "BioCode Smell Fixer" in description