# 🦨 Code Smell Detector Guide

## Overview

The **Code Smell Detector** is an automated code quality analyzer that identifies anti-patterns, bad practices, and potential issues in Python code. It can detect various code smells and, where safe, automatically fix simple issues.

## 🧬 Detected Code Smells

### Structural Smells

#### 1. **God Class**
- Classes with too many methods (>20)
- Classes with too many lines (>500)
- **Severity**: High
- **Fix**: Refactor into smaller, focused classes

#### 2. **Long Method**
- Methods exceeding 50 lines
- **Severity**: Medium
- **Fix**: Extract smaller methods with single responsibilities

#### 3. **Long Parameter List**
- Functions with more than 5 parameters
- **Severity**: Medium
- **Fix**: Use configuration objects or builder pattern

### Code Quality Smells

#### 4. **Magic Numbers**
- Hardcoded numeric literals without context
- **Severity**: Low
- **Auto-fixable**: Adds TODO comment
- **Fix**: Extract to named constants

```python
# Bad
if quantity > 100:
    discount = 0.15

# Good
MIN_BULK_QUANTITY = 100
BULK_DISCOUNT_RATE = 0.15

if quantity > MIN_BULK_QUANTITY:
    discount = BULK_DISCOUNT_RATE
```

#### 5. **Deep Nesting**
- Code nested more than 4 levels deep
- **Severity**: Medium
- **Fix**: Use early returns, extract methods

```python
# Bad
if condition1:
    if condition2:
        if condition3:
            if condition4:
                do_something()

# Good
if not condition1:
    return
if not condition2:
    return
if not condition3:
    return
if condition4:
    do_something()
```

#### 6. **Empty Exception Handlers**
- Catch blocks that silently swallow errors
- **Severity**: High
- **Auto-fixable**: Adds logging
- **Fix**: Log exceptions or handle appropriately

```python
# Bad
try:
    risky_operation()
except:
    pass

# Good
try:
    risky_operation()
except Exception as e:
    logger.exception("Operation failed: %s", e)
```

### Maintenance Smells

#### 7. **Commented Code**
- Code that's been commented out
- **Severity**: Low
- **Auto-fixable**: Removes commented code
- **Fix**: Delete it - version control preserves history

#### 8. **TODO Accumulation**
- Too many TODO/FIXME comments (>10)
- **Severity**: Medium
- **Fix**: Address technical debt or create issues

#### 9. **Global Variables**
- Use of global state
- **Severity**: Medium
- **Fix**: Use dependency injection

### Style Smells

#### 10. **Long Lines**
- Lines exceeding 120 characters
- **Severity**: Low
- **Fix**: Break into multiple lines

## 🚀 Quick Start

### Basic Usage

```python
from src.evolution_lab.analyzers.code_smell_analyzer import CodeSmellAnalyzer

# Analyze a project
analyzer = CodeSmellAnalyzer("/path/to/project")
results = analyzer.analyze()

print(f"Total smells: {results['total_smells']}")
print(f"Health score: {results['health_score']}%")
print(f"Auto-fixable: {results['auto_fixable_count']}")

# Get specific smell types
for smell in results['smells']:
    if smell['severity'] == 'high':
        print(f"{smell['type']}: {smell['message']} at line {smell['line']}")
```

### Auto-Fix Smells

```python
from src.evolution_lab.fixers.smell_fixer import SmellFixer

# Get auto-fixable smells
fixable = [s for s in results['smells'] if s['auto_fixable']]

# Apply fixes
fixer = SmellFixer()
fix_results = fixer.apply_fixes(fixable, dry_run=False)

# Generate report
report = fixer.generate_fix_report(fix_results)
print(report)
```

## 📊 Understanding Results

### Health Score

The health score (0-100) indicates overall code quality:
- **90-100**: Excellent - minimal smells
- **70-89**: Good - some minor issues
- **50-69**: Fair - needs improvement
- **Below 50**: Poor - significant refactoring needed

### Smell Distribution

```python
{
    "smell_distribution": {
        "long_method": 5,
        "magic_number": 12,
        "empty_exception_handler": 3
    },
    "severity_distribution": {
        "low": 15,
        "medium": 8,
        "high": 3,
        "critical": 1
    }
}
```

## 🔧 Configuration

### Custom Thresholds

```python
analyzer = CodeSmellAnalyzer(project_path)

# Adjust thresholds
analyzer.max_method_lines = 75  # Allow longer methods
analyzer.max_params = 7         # Allow more parameters
analyzer.max_nesting_depth = 5  # Allow deeper nesting
```

### Skip Patterns

By default, these directories are skipped:
- `__pycache__`
- `.git`
- `venv`, `env`, `.env`
- `migrations`
- `tests`
- `.pytest_cache`

## 🎯 Best Practices

### 1. **Regular Analysis**
```yaml
# .github/workflows/code-quality.yml
- name: Check Code Smells
  run: |
    python -m biocode analyze-smells .
    if [ $? -ne 0 ]; then
      echo "Code smells detected!"
      exit 1
    fi
```

### 2. **Gradual Improvement**
Don't try to fix everything at once:
1. Fix critical/high severity first
2. Use auto-fix for simple issues
3. Refactor complex smells gradually

### 3. **Team Standards**
Define acceptable thresholds:
```python
# .biocode.yml
code_smell_thresholds:
  max_method_lines: 50
  max_class_methods: 15
  max_complexity: 10
  min_health_score: 75
```

## 🤖 Auto-Fix Safety

### What Gets Auto-Fixed

1. **Safe Removals**:
   - Commented code lines
   - Trailing whitespace

2. **Safe Additions**:
   - TODO comments for magic numbers
   - Logging in empty exception handlers

3. **Safe Replacements**:
   - `pass` → `logging.exception()`

### What Requires Manual Fix

1. **Structural Issues**:
   - God classes
   - Long methods
   - Deep nesting

2. **Design Issues**:
   - Long parameter lists
   - Global variables
   - High coupling

## 📈 Integration Examples

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: code-smells
        name: Check code smells
        entry: python -m biocode check-smells
        language: system
        types: [python]
```

### CI/CD Pipeline

```yaml
# GitHub Actions
- name: Analyze Code Quality
  run: |
    analyzer_output=$(python -m biocode analyze-smells --json)
    health_score=$(echo $analyzer_output | jq '.health_score')
    
    if [ $health_score -lt 70 ]; then
      echo "::error::Code health score too low: $health_score"
      exit 1
    fi
```

### VS Code Integration

```json
// .vscode/tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Check Code Smells",
            "type": "shell",
            "command": "python",
            "args": ["-m", "biocode", "analyze-smells", "${file}"],
            "problemMatcher": "$python"
        }
    ]
}
```

## 🔍 Advanced Features

### Custom Smell Detectors

```python
class CustomSmellAnalyzer(CodeSmellAnalyzer):
    def __init__(self, project_path):
        super().__init__(project_path)
        self.custom_patterns = [
            re.compile(r'print\('),  # Detect print statements
            re.compile(r'import \*')  # Detect wildcard imports
        ]
    
    def _analyze_custom_smells(self, content, file_path):
        # Add your custom smell detection logic
        pass
```

### Smell Trends Over Time

```python
# Track improvement
from datetime import datetime

def track_smell_trends(project_path):
    analyzer = CodeSmellAnalyzer(project_path)
    
    # Store results
    results = analyzer.analyze()
    timestamp = datetime.now()
    
    # Save to history
    with open('.smell_history.json', 'a') as f:
        json.dump({
            'timestamp': timestamp.isoformat(),
            'health_score': results['health_score'],
            'total_smells': results['total_smells']
        }, f)
```

## 📚 References

- [Martin Fowler - Code Smells](https://refactoring.guru/refactoring/smells)
- [Clean Code by Robert C. Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [PEP 8 - Style Guide for Python](https://www.python.org/dev/peps/pep-0008/)

---

*"Code smells are hints that something might be wrong, not necessarily that it is wrong."*