#!/usr/bin/env python3
"""Test individual analyzers"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from evolution_lab.analyzers.code_analyzer import CodeAnalyzer
from evolution_lab.analyzers.ai_model_analyzer import AIModelAnalyzer

# Test path
project_path = "/home/umit/CLAUDE_PROJECT/Ear-segmentation-ai"

print(f"Testing analyzers on: {project_path}")

# Test CodeAnalyzer
print("\n📝 Testing CodeAnalyzer...")
code_analyzer = CodeAnalyzer(project_path)
code_result = code_analyzer.analyze()
print(f"  Analyzer: {code_result.analyzer_name}")
print(f"  Metrics: {code_result.metrics}")
print(f"  Issues: {len(code_result.issues)}")
print(f"  Suggestions: {len(code_result.suggestions)}")

# Test AIModelAnalyzer
print("\n🤖 Testing AIModelAnalyzer...")
ai_analyzer = AIModelAnalyzer(project_path)
ai_result = ai_analyzer.analyze()
print(f"  Analyzer: {ai_result.analyzer_name}")
print(f"  Metrics: {ai_result.metrics}")
print(f"  Issues: {len(ai_result.issues)}")
print(f"  Suggestions: {len(ai_result.suggestions)}")