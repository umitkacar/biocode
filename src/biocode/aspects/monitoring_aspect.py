"""
Monitoring Aspect - System health and metrics monitoring
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import time
import psutil
import os
from typing import Dict, Any, List, Optional, Deque, Callable
from collections import deque, defaultdict
from datetime import datetime
from .base import Aspect, JoinPoint


class MetricType:
    """Types of metrics to collect"""
    COUNTER = "counter"      # Incremental count
    GAUGE = "gauge"          # Current value
    HISTOGRAM = "histogram"  # Distribution of values
    RATE = "rate"           # Rate per time unit


class Metric:
    """Base metric class"""
    
    def __init__(self, name: str, metric_type: str, unit: str = ""):
        self.name = name
        self.type = metric_type
        self.unit = unit
        self.timestamp = time.time()
        
    def record(self, value: float):
        """Record a value"""
        raise NotImplementedError


class CounterMetric(Metric):
    """Counter metric - only increases"""
    
    def __init__(self, name: str, unit: str = ""):
        super().__init__(name, MetricType.COUNTER, unit)
        self.value = 0
        
    def record(self, value: float = 1):
        """Increment counter"""
        self.value += value
        
    def get_value(self) -> float:
        """Get current count"""
        return self.value


class GaugeMetric(Metric):
    """Gauge metric - can go up or down"""
    
    def __init__(self, name: str, unit: str = ""):
        super().__init__(name, MetricType.GAUGE, unit)
        self.value = 0
        
    def record(self, value: float):
        """Set gauge value"""
        self.value = value
        
    def get_value(self) -> float:
        """Get current value"""
        return self.value


class HistogramMetric(Metric):
    """Histogram metric - tracks distribution"""
    
    def __init__(self, name: str, unit: str = "", max_samples: int = 1000):
        super().__init__(name, MetricType.HISTOGRAM, unit)
        self.samples: Deque[float] = deque(maxlen=max_samples)
        
    def record(self, value: float):
        """Add sample to histogram"""
        self.samples.append(value)
        
    def get_percentile(self, percentile: float) -> float:
        """Get percentile value"""
        if not self.samples:
            return 0.0
            
        sorted_samples = sorted(self.samples)
        index = int(len(sorted_samples) * percentile / 100)
        return sorted_samples[min(index, len(sorted_samples) - 1)]
        
    def get_stats(self) -> Dict[str, float]:
        """Get histogram statistics"""
        if not self.samples:
            return {
                'count': 0,
                'min': 0,
                'max': 0,
                'avg': 0,
                'p50': 0,
                'p95': 0,
                'p99': 0
            }
            
        return {
            'count': len(self.samples),
            'min': min(self.samples),
            'max': max(self.samples),
            'avg': sum(self.samples) / len(self.samples),
            'p50': self.get_percentile(50),
            'p95': self.get_percentile(95),
            'p99': self.get_percentile(99)
        }


class MonitoringAspect(Aspect):
    """
    Monitoring aspect for system health and metrics
    
    Collects metrics, monitors resource usage, and tracks system health.
    """
    
    def __init__(self, collect_interval: float = 1.0):
        """
        Initialize monitoring aspect
        
        Args:
            collect_interval: How often to collect system metrics (seconds)
        """
        super().__init__()
        
        self.collect_interval = collect_interval
        self.last_collect_time = time.time()
        
        # Metrics storage
        self.metrics: Dict[str, Metric] = {}
        
        # Health checks
        self.health_checks: Dict[str, Callable] = {}
        self.health_status: Dict[str, bool] = {}
        
        # Resource monitoring
        self.resource_history: Deque[Dict[str, float]] = deque(maxlen=60)
        
        # Alerts
        self.alerts: List[Dict[str, Any]] = []
        self.alert_thresholds: Dict[str, Dict[str, float]] = {}
        
        # Initialize default metrics
        self._init_default_metrics()
        
    def _init_default_metrics(self):
        """Initialize default metrics"""
        # Method metrics
        self.register_metric("method_calls", MetricType.COUNTER)
        self.register_metric("method_errors", MetricType.COUNTER)
        self.register_metric("method_duration", MetricType.HISTOGRAM, "ms")
        
        # System metrics
        self.register_metric("active_entities", MetricType.GAUGE)
        self.register_metric("active_systems", MetricType.GAUGE)
        
        # Resource metrics
        self.register_metric("cpu_usage", MetricType.GAUGE, "%")
        self.register_metric("memory_usage", MetricType.GAUGE, "MB")
        
        # Set default alert thresholds
        self.set_alert_threshold("cpu_usage", high=80.0)
        self.set_alert_threshold("memory_usage", high=1000.0)  # 1GB
        
    def get_pointcut(self) -> str:
        """Monitor all System and World methods"""
        return "*"
        
    def before(self, join_point: JoinPoint):
        """Record method call"""
        # Increment call counter
        self.record_metric("method_calls", 1)
        
        # Store start time
        join_point.metadata['monitor_start_time'] = time.perf_counter()
        
        # Collect system metrics if needed
        self._collect_system_metrics_if_needed()
        
    def after(self, join_point: JoinPoint):
        """Record method completion"""
        # Calculate duration
        start_time = join_point.metadata.get('monitor_start_time')
        if start_time:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.record_metric("method_duration", duration_ms)
            
    def after_throwing(self, join_point: JoinPoint):
        """Record method error"""
        self.record_metric("method_errors", 1)
        
        # Create alert for critical errors
        if isinstance(join_point.exception, (MemoryError, SystemError)):
            self._create_alert(
                "critical_error",
                f"Critical error in {join_point.method_name}: {join_point.exception}",
                severity="critical"
            )
            
    def register_metric(self, name: str, metric_type: str, unit: str = ""):
        """
        Register a new metric
        
        Args:
            name: Metric name
            metric_type: Type of metric (counter, gauge, histogram)
            unit: Unit of measurement
        """
        if metric_type == MetricType.COUNTER:
            self.metrics[name] = CounterMetric(name, unit)
        elif metric_type == MetricType.GAUGE:
            self.metrics[name] = GaugeMetric(name, unit)
        elif metric_type == MetricType.HISTOGRAM:
            self.metrics[name] = HistogramMetric(name, unit)
        else:
            raise ValueError(f"Unknown metric type: {metric_type}")
            
    def record_metric(self, name: str, value: float):
        """
        Record a metric value
        
        Args:
            name: Metric name
            value: Value to record
        """
        if name in self.metrics:
            self.metrics[name].record(value)
            
            # Check alerts
            self._check_metric_alerts(name, value)
            
    def add_health_check(self, name: str, check_func: Callable[[], bool]):
        """
        Add a health check
        
        Args:
            name: Health check name
            check_func: Function that returns True if healthy
        """
        self.health_checks[name] = check_func
        
    def set_alert_threshold(self, metric_name: str, 
                          low: Optional[float] = None,
                          high: Optional[float] = None):
        """
        Set alert thresholds for a metric
        
        Args:
            metric_name: Metric to monitor
            low: Low threshold (alert if below)
            high: High threshold (alert if above)
        """
        self.alert_thresholds[metric_name] = {}
        if low is not None:
            self.alert_thresholds[metric_name]['low'] = low
        if high is not None:
            self.alert_thresholds[metric_name]['high'] = high
            
    def _collect_system_metrics_if_needed(self):
        """Collect system metrics periodically"""
        current_time = time.time()
        if current_time - self.last_collect_time < self.collect_interval:
            return
            
        self.last_collect_time = current_time
        
        # Collect resource usage
        try:
            process = psutil.Process(os.getpid())
            
            # CPU usage
            cpu_percent = process.cpu_percent(interval=0.1)
            self.record_metric("cpu_usage", cpu_percent)
            
            # Memory usage
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.record_metric("memory_usage", memory_mb)
            
            # Store in history
            self.resource_history.append({
                'timestamp': current_time,
                'cpu': cpu_percent,
                'memory': memory_mb
            })
            
        except Exception as e:
            print(f"Failed to collect system metrics: {e}")
            
        # Run health checks
        self._run_health_checks()
        
    def _run_health_checks(self):
        """Run all registered health checks"""
        for name, check_func in self.health_checks.items():
            try:
                is_healthy = check_func()
                
                # Check if status changed
                if name in self.health_status and self.health_status[name] != is_healthy:
                    if not is_healthy:
                        self._create_alert(
                            "health_check_failed",
                            f"Health check '{name}' failed",
                            severity="warning"
                        )
                        
                self.health_status[name] = is_healthy
                
            except Exception as e:
                self.health_status[name] = False
                self._create_alert(
                    "health_check_error",
                    f"Health check '{name}' error: {e}",
                    severity="error"
                )
                
    def _check_metric_alerts(self, metric_name: str, value: float):
        """Check if metric value triggers an alert"""
        if metric_name not in self.alert_thresholds:
            return
            
        thresholds = self.alert_thresholds[metric_name]
        
        if 'low' in thresholds and value < thresholds['low']:
            self._create_alert(
                "metric_threshold",
                f"Metric '{metric_name}' below threshold: {value} < {thresholds['low']}",
                severity="warning"
            )
            
        if 'high' in thresholds and value > thresholds['high']:
            self._create_alert(
                "metric_threshold",
                f"Metric '{metric_name}' above threshold: {value} > {thresholds['high']}",
                severity="warning"
            )
            
    def _create_alert(self, alert_type: str, message: str, severity: str = "info"):
        """Create an alert"""
        alert = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'type': alert_type,
            'message': message,
            'severity': severity
        }
        
        self.alerts.append(alert)
        
        # Keep only recent alerts
        if len(self.alerts) > 100:
            self.alerts.pop(0)
            
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {}
        
        for name, metric in self.metrics.items():
            if isinstance(metric, CounterMetric):
                summary[name] = metric.get_value()
            elif isinstance(metric, GaugeMetric):
                summary[name] = metric.get_value()
            elif isinstance(metric, HistogramMetric):
                summary[name] = metric.get_stats()
                
        return summary
        
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        return {
            'healthy': all(self.health_status.values()) if self.health_status else True,
            'checks': self.health_status.copy(),
            'resource_usage': self.resource_history[-1] if self.resource_history else {},
            'recent_alerts': self.alerts[-10:]  # Last 10 alerts
        }
        
    def get_resource_trends(self) -> Dict[str, List[float]]:
        """Get resource usage trends"""
        if not self.resource_history:
            return {'cpu': [], 'memory': []}
            
        return {
            'cpu': [r['cpu'] for r in self.resource_history],
            'memory': [r['memory'] for r in self.resource_history]
        }