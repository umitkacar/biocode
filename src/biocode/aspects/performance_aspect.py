"""
Performance Aspect - Method performance monitoring
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import time
import statistics
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, deque
from .base import Aspect, JoinPoint


class PerformanceMetrics:
    """Performance metrics for a method"""
    
    def __init__(self, window_size: int = 100):
        self.call_count = 0
        self.total_time = 0.0
        self.min_time = float('inf')
        self.max_time = 0.0
        self.recent_times = deque(maxlen=window_size)
        self.error_count = 0
        
    def record_execution(self, duration: float, error: bool = False):
        """Record a method execution"""
        self.call_count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        self.recent_times.append(duration)
        
        if error:
            self.error_count += 1
            
    @property
    def average_time(self) -> float:
        """Get average execution time"""
        return self.total_time / self.call_count if self.call_count > 0 else 0.0
        
    @property
    def median_time(self) -> float:
        """Get median execution time from recent executions"""
        if not self.recent_times:
            return 0.0
        return statistics.median(self.recent_times)
        
    @property
    def success_rate(self) -> float:
        """Get success rate (1 - error rate)"""
        if self.call_count == 0:
            return 1.0
        return 1.0 - (self.error_count / self.call_count)
        
    def get_percentile(self, percentile: float) -> float:
        """Get percentile from recent executions"""
        if not self.recent_times:
            return 0.0
        return statistics.quantiles(self.recent_times, n=100)[int(percentile)]
        
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return {
            'call_count': self.call_count,
            'total_time': self.total_time,
            'average_time': self.average_time,
            'median_time': self.median_time,
            'min_time': self.min_time if self.min_time != float('inf') else 0.0,
            'max_time': self.max_time,
            'success_rate': self.success_rate,
            'error_count': self.error_count
        }


class PerformanceAspect(Aspect):
    """
    Performance monitoring aspect
    
    Tracks execution time, call counts, and performance statistics.
    """
    
    def __init__(self, alert_threshold_ms: float = 100.0,
                 track_memory: bool = False):
        """
        Initialize performance aspect
        
        Args:
            alert_threshold_ms: Alert if method takes longer than this (ms)
            track_memory: Whether to track memory usage
        """
        super().__init__()
        
        self.alert_threshold_ms = alert_threshold_ms
        self.track_memory = track_memory
        self.metrics: Dict[str, PerformanceMetrics] = defaultdict(
            lambda: PerformanceMetrics()
        )
        self.alerts: List[Dict[str, Any]] = []
        
    def get_pointcut(self) -> str:
        """Monitor all System methods"""
        return "System.*"
        
    def before(self, join_point: JoinPoint):
        """Record method start time"""
        join_point.metadata['perf_start_time'] = time.perf_counter()
        
        if self.track_memory:
            import psutil
            process = psutil.Process()
            join_point.metadata['perf_start_memory'] = process.memory_info().rss
            
    def after(self, join_point: JoinPoint):
        """Record method execution time"""
        start_time = join_point.metadata.get('perf_start_time')
        if start_time is None:
            return
            
        # Calculate duration
        duration = time.perf_counter() - start_time
        duration_ms = duration * 1000
        
        # Get method signature
        class_name = join_point.target.__class__.__name__
        method_sig = f"{class_name}.{join_point.method_name}"
        
        # Record metrics
        metrics = self.metrics[method_sig]
        error = join_point.exception is not None
        metrics.record_execution(duration, error)
        
        # Check for performance alerts
        if duration_ms > self.alert_threshold_ms:
            alert = {
                'timestamp': time.time(),
                'method': method_sig,
                'duration_ms': duration_ms,
                'threshold_ms': self.alert_threshold_ms,
                'args': str(join_point.args)[:100],
                'error': error
            }
            self.alerts.append(alert)
            
            # Keep only recent alerts
            if len(self.alerts) > 100:
                self.alerts.pop(0)
                
        # Track memory if enabled
        if self.track_memory and 'perf_start_memory' in join_point.metadata:
            import psutil
            process = psutil.Process()
            memory_delta = process.memory_info().rss - join_point.metadata['perf_start_memory']
            join_point.metadata['memory_delta'] = memory_delta
            
    def get_metrics(self, method_pattern: Optional[str] = None) -> Dict[str, Dict[str, float]]:
        """
        Get performance metrics
        
        Args:
            method_pattern: Filter methods by pattern (None = all)
            
        Returns:
            Dictionary of method signatures to metrics
        """
        result = {}
        
        for method_sig, metrics in self.metrics.items():
            if method_pattern is None or method_pattern in method_sig:
                result[method_sig] = metrics.to_dict()
                
        return result
        
    def get_slow_methods(self, threshold_ms: Optional[float] = None) -> List[Tuple[str, float]]:
        """
        Get methods slower than threshold
        
        Args:
            threshold_ms: Threshold in milliseconds (uses alert threshold if None)
            
        Returns:
            List of (method_signature, average_time_ms) tuples
        """
        threshold = threshold_ms or self.alert_threshold_ms
        threshold_sec = threshold / 1000.0
        
        slow_methods = []
        
        for method_sig, metrics in self.metrics.items():
            if metrics.average_time > threshold_sec:
                slow_methods.append((
                    method_sig,
                    metrics.average_time * 1000  # Convert to ms
                ))
                
        # Sort by slowest first
        slow_methods.sort(key=lambda x: x[1], reverse=True)
        
        return slow_methods
        
    def get_hot_methods(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Get most frequently called methods
        
        Args:
            top_n: Number of methods to return
            
        Returns:
            List of (method_signature, call_count) tuples
        """
        hot_methods = [
            (method_sig, metrics.call_count)
            for method_sig, metrics in self.metrics.items()
        ]
        
        # Sort by call count
        hot_methods.sort(key=lambda x: x[1], reverse=True)
        
        return hot_methods[:top_n]
        
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent performance alerts"""
        return self.alerts[-limit:]
        
    def reset_metrics(self):
        """Reset all performance metrics"""
        self.metrics.clear()
        self.alerts.clear()
        
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        total_calls = sum(m.call_count for m in self.metrics.values())
        total_time = sum(m.total_time for m in self.metrics.values())
        total_errors = sum(m.error_count for m in self.metrics.values())
        
        return {
            'total_methods_tracked': len(self.metrics),
            'total_calls': total_calls,
            'total_time_seconds': total_time,
            'total_errors': total_errors,
            'overall_success_rate': 1.0 - (total_errors / max(1, total_calls)),
            'alert_count': len(self.alerts),
            'hot_methods': self.get_hot_methods(5),
            'slow_methods': self.get_slow_methods()[:5]
        }