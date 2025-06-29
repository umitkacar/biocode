"""
Base Analyzer for Evolution Lab
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import os
import json
import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AnalysisResult:
    """Result of an analysis operation"""
    analyzer_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    metrics: Dict[str, Any] = field(default_factory=dict)
    issues: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'analyzer': self.analyzer_name,
            'timestamp': self.timestamp.isoformat(),
            'metrics': self.metrics,
            'issues': self.issues,
            'suggestions': self.suggestions,
            'metadata': self.metadata,
        }


class BaseAnalyzer(ABC):
    """Base class for all project analyzers"""
    
    def __init__(self, project_path: str):
        """
        Initialize analyzer
        
        Args:
            project_path: Path to the project to analyze
        """
        self.project_path = Path(project_path)
        if not self.project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
            
        self.name = self.__class__.__name__
        self._cache = {}
        self._start_time = None
        self.logger = logging.getLogger(self.name)
        
    @abstractmethod
    def analyze(self) -> AnalysisResult:
        """
        Perform analysis on the project
        
        Returns:
            AnalysisResult containing metrics, issues, and suggestions
        """
        pass
        
    def scan_files(self, extensions: Optional[List[str]] = None) -> List[Path]:
        """
        Scan project for files with given extensions
        
        Args:
            extensions: List of file extensions to include (e.g., ['.py', '.js'])
            
        Returns:
            List of file paths
        """
        files = []
        for root, _, filenames in os.walk(self.project_path):
            # Skip hidden directories and common ignore patterns
            if any(part.startswith('.') for part in Path(root).parts):
                continue
            if any(ignore in root for ignore in ['__pycache__', 'node_modules', 'venv', '.git']):
                continue
                
            for filename in filenames:
                file_path = Path(root) / filename
                if extensions is None or file_path.suffix in extensions:
                    files.append(file_path)
                    
        return files
        
    def count_lines(self, file_path: Path) -> Dict[str, int]:
        """
        Count lines in a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with line counts
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            total = len(lines)
            blank = sum(1 for line in lines if not line.strip())
            comment = sum(1 for line in lines if line.strip().startswith(('#', '//', '/*', '*')))
            code = total - blank - comment
            
            return {
                'total': total,
                'code': code,
                'blank': blank,
                'comment': comment
            }
        except Exception:
            return {'total': 0, 'code': 0, 'blank': 0, 'comment': 0}
            
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get file information
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file info
        """
        stat = file_path.stat()
        return {
            'name': file_path.name,
            'path': str(file_path.relative_to(self.project_path)),
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'extension': file_path.suffix,
        }
        
    def start_timer(self):
        """Start analysis timer"""
        self._start_time = time.time()
        
    def get_elapsed_time(self) -> float:
        """Get elapsed time since start"""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time
        
    def load_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load and parse JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data or None if error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
            
    def find_pattern_in_file(self, file_path: Path, pattern: str) -> List[int]:
        """
        Find pattern in file and return line numbers
        
        Args:
            file_path: Path to file
            pattern: Pattern to search for
            
        Returns:
            List of line numbers where pattern was found
        """
        matches = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    if pattern in line:
                        matches.append(i)
        except Exception:
            pass
        return matches