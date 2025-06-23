from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
import time
import statistics
import json
from enum import Enum


class MetricType(Enum):
    """Metrik tipleri"""
    COUNTER = "counter"          # Artan sayaç
    GAUGE = "gauge"              # Anlık değer
    HISTOGRAM = "histogram"      # Dağılım
    RATE = "rate"               # Oran (ops/sec)
    LATENCY = "latency"         # Gecikme süresi


@dataclass
class MetricPoint:
    """Tek bir metrik noktası"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricDefinition:
    """Metrik tanımı"""
    name: str
    type: MetricType
    unit: str
    description: str
    retention_period: timedelta = timedelta(hours=24)
    alert_thresholds: Dict[str, float] = field(default_factory=dict)


class MetricsCollector:
    """Merkezi metrik toplama sistemi"""
    
    def __init__(self, collector_name: str):
        self.collector_name = collector_name
        self.metrics: Dict[str, MetricDefinition] = {}
        self.data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.aggregations: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.alert_callbacks: List[Callable] = []
        
    def register_metric(self, metric_def: MetricDefinition):
        """Yeni metrik tanımla"""
        self.metrics[metric_def.name] = metric_def
        
    def record(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Metrik kaydet"""
        if metric_name not in self.metrics:
            raise ValueError(f"Unknown metric: {metric_name}")
            
        metric_def = self.metrics[metric_name]
        point = MetricPoint(datetime.now(), value, labels or {})
        
        self.data[metric_name].append(point)
        
        # Update aggregations
        self._update_aggregations(metric_name, value)
        
        # Check alerts
        self._check_alerts(metric_name, value)
        
    def _update_aggregations(self, metric_name: str, value: float):
        """Aggregation'ları güncelle"""
        metric_type = self.metrics[metric_name].type
        
        if metric_type == MetricType.COUNTER:
            self.aggregations[metric_name]['total'] = \
                self.aggregations[metric_name].get('total', 0) + value
                
        elif metric_type == MetricType.GAUGE:
            self.aggregations[metric_name]['current'] = value
            self.aggregations[metric_name]['min'] = \
                min(value, self.aggregations[metric_name].get('min', float('inf')))
            self.aggregations[metric_name]['max'] = \
                max(value, self.aggregations[metric_name].get('max', float('-inf')))
                
        elif metric_type == MetricType.LATENCY:
            if 'latencies' not in self.aggregations[metric_name]:
                self.aggregations[metric_name]['latencies'] = deque(maxlen=1000)
            self.aggregations[metric_name]['latencies'].append(value)
            
    def _check_alerts(self, metric_name: str, value: float):
        """Alert kontrolü"""
        metric_def = self.metrics[metric_name]
        
        for threshold_name, threshold_value in metric_def.alert_thresholds.items():
            if value > threshold_value:
                for callback in self.alert_callbacks:
                    callback(metric_name, threshold_name, value, threshold_value)
                    
    def get_statistics(self, metric_name: str, time_window: Optional[timedelta] = None) -> Dict[str, float]:
        """İstatistik hesapla"""
        if metric_name not in self.data:
            return {}
            
        points = list(self.data[metric_name])
        
        if time_window:
            cutoff = datetime.now() - time_window
            points = [p for p in points if p.timestamp > cutoff]
            
        if not points:
            return {}
            
        values = [p.value for p in points]
        
        return {
            'count': len(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values),
            'p95': self._percentile(values, 95),
            'p99': self._percentile(values, 99)
        }
        
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Percentile hesapla"""
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
        
    def get_rate(self, metric_name: str, time_window: timedelta = timedelta(minutes=1)) -> float:
        """Rate hesapla (ops/sec)"""
        if metric_name not in self.data:
            return 0.0
            
        cutoff = datetime.now() - time_window
        recent_points = [p for p in self.data[metric_name] if p.timestamp > cutoff]
        
        if not recent_points:
            return 0.0
            
        return len(recent_points) / time_window.total_seconds()


class CellMetrics:
    """Cell-level metrikler"""
    
    def __init__(self, cell_name: str):
        self.cell_name = cell_name
        self.collector = MetricsCollector(f"cell_{cell_name}")
        
        # Define cell metrics
        self._define_metrics()
        
    def _define_metrics(self):
        """Cell metrikleri tanımla"""
        # Health metrics
        self.collector.register_metric(MetricDefinition(
            name="health_score",
            type=MetricType.GAUGE,
            unit="score",
            description="Cell health score (0-100)",
            alert_thresholds={"critical": 30, "warning": 50}
        ))
        
        # Performance metrics
        self.collector.register_metric(MetricDefinition(
            name="operation_latency",
            type=MetricType.LATENCY,
            unit="ms",
            description="Operation execution latency",
            alert_thresholds={"slow": 100, "critical": 500}
        ))
        
        # Error metrics
        self.collector.register_metric(MetricDefinition(
            name="error_count",
            type=MetricType.COUNTER,
            unit="errors",
            description="Total error count"
        ))
        
        # Resource metrics
        self.collector.register_metric(MetricDefinition(
            name="energy_level",
            type=MetricType.GAUGE,
            unit="ATP",
            description="Cell energy level",
            alert_thresholds={"low": 20}
        ))
        
        # Throughput metrics
        self.collector.register_metric(MetricDefinition(
            name="operations_completed",
            type=MetricType.COUNTER,
            unit="ops",
            description="Total operations completed"
        ))
        
    def record_operation(self, operation_name: str, duration_ms: float, success: bool):
        """Operasyon metriği kaydet"""
        self.collector.record("operation_latency", duration_ms, 
                            {"operation": operation_name})
        
        if success:
            self.collector.record("operations_completed", 1, 
                                {"operation": operation_name})
        else:
            self.collector.record("error_count", 1, 
                                {"operation": operation_name})
            
    def update_health(self, health_score: float, energy_level: float):
        """Sağlık metrikleri güncelle"""
        self.collector.record("health_score", health_score)
        self.collector.record("energy_level", energy_level)
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Performans özeti"""
        return {
            'cell_name': self.cell_name,
            'health': self.collector.get_statistics("health_score"),
            'latency': self.collector.get_statistics("operation_latency"),
            'error_rate': self.collector.get_rate("error_count"),
            'throughput': self.collector.get_rate("operations_completed"),
            'energy': self.collector.aggregations.get("energy_level", {})
        }


class TissueMetrics:
    """Tissue-level metrikler"""
    
    def __init__(self, tissue_name: str):
        self.tissue_name = tissue_name
        self.collector = MetricsCollector(f"tissue_{tissue_name}")
        self.cell_metrics: Dict[str, CellMetrics] = {}
        
        self._define_metrics()
        
    def _define_metrics(self):
        """Tissue metrikleri tanımla"""
        # Tissue health
        self.collector.register_metric(MetricDefinition(
            name="tissue_health",
            type=MetricType.GAUGE,
            unit="score",
            description="Overall tissue health",
            alert_thresholds={"critical": 40, "warning": 60}
        ))
        
        # Cell coordination
        self.collector.register_metric(MetricDefinition(
            name="inter_cell_latency",
            type=MetricType.LATENCY,
            unit="ms",
            description="Communication latency between cells"
        ))
        
        # Quarantine metrics
        self.collector.register_metric(MetricDefinition(
            name="quarantined_cells",
            type=MetricType.GAUGE,
            unit="cells",
            description="Number of quarantined cells",
            alert_thresholds={"high": 5}
        ))
        
        # Transaction metrics
        self.collector.register_metric(MetricDefinition(
            name="transaction_success_rate",
            type=MetricType.GAUGE,
            unit="percent",
            description="Transaction success rate"
        ))
        
    def add_cell_metrics(self, cell_name: str, cell_metrics: CellMetrics):
        """Cell metriklerini ekle"""
        self.cell_metrics[cell_name] = cell_metrics
        
    def calculate_tissue_health(self) -> float:
        """Tissue sağlığını hesapla"""
        if not self.cell_metrics:
            return 100.0
            
        cell_healths = []
        for cell_metric in self.cell_metrics.values():
            health_stats = cell_metric.collector.get_statistics("health_score")
            if health_stats:
                cell_healths.append(health_stats.get('mean', 0))
                
        if cell_healths:
            tissue_health = statistics.mean(cell_healths)
            self.collector.record("tissue_health", tissue_health)
            return tissue_health
            
        return 0.0
        
    def record_communication(self, from_cell: str, to_cell: str, latency_ms: float):
        """Cell arası iletişim metriği"""
        self.collector.record("inter_cell_latency", latency_ms,
                            {"from": from_cell, "to": to_cell})
                            
    def get_tissue_dashboard(self) -> Dict[str, Any]:
        """Tissue dashboard verisi"""
        return {
            'tissue_name': self.tissue_name,
            'overall_health': self.calculate_tissue_health(),
            'cell_count': len(self.cell_metrics),
            'quarantine_count': self.collector.aggregations.get("quarantined_cells", {}).get("current", 0),
            'communication_latency': self.collector.get_statistics("inter_cell_latency"),
            'transaction_success': self.collector.aggregations.get("transaction_success_rate", {}).get("current", 100),
            'cell_summaries': {
                name: metrics.get_performance_summary()
                for name, metrics in self.cell_metrics.items()
            }
        }


class MetricsDashboard:
    """Merkezi dashboard"""
    
    def __init__(self):
        self.tissue_metrics: Dict[str, TissueMetrics] = {}
        self.update_interval = timedelta(seconds=5)
        self.last_update = datetime.now()
        
    def add_tissue(self, tissue_name: str, tissue_metrics: TissueMetrics):
        """Tissue ekle"""
        self.tissue_metrics[tissue_name] = tissue_metrics
        
    def get_dashboard_json(self) -> str:
        """JSON formatında dashboard verisi"""
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'tissues': {}
        }
        
        for tissue_name, metrics in self.tissue_metrics.items():
            dashboard_data['tissues'][tissue_name] = metrics.get_tissue_dashboard()
            
        return json.dumps(dashboard_data, indent=2)
        
    def get_health_summary(self) -> Dict[str, Any]:
        """Sağlık özeti"""
        summary = {
            'total_tissues': len(self.tissue_metrics),
            'healthy_tissues': 0,
            'warning_tissues': 0,
            'critical_tissues': 0
        }
        
        for tissue_metrics in self.tissue_metrics.values():
            health = tissue_metrics.calculate_tissue_health()
            
            if health > 70:
                summary['healthy_tissues'] += 1
            elif health > 40:
                summary['warning_tissues'] += 1
            else:
                summary['critical_tissues'] += 1
                
        return summary
        
    def print_dashboard(self):
        """Terminal dashboard"""
        print("\n" + "="*60)
        print(f"🏥 CODE ORGANISM HEALTH DASHBOARD - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        summary = self.get_health_summary()
        print(f"\n📊 Overall Status:")
        print(f"   Tissues: {summary['total_tissues']} total")
        print(f"   ✅ Healthy: {summary['healthy_tissues']}")
        print(f"   ⚠️  Warning: {summary['warning_tissues']}")
        print(f"   🚨 Critical: {summary['critical_tissues']}")
        
        for tissue_name, metrics in self.tissue_metrics.items():
            data = metrics.get_tissue_dashboard()
            print(f"\n🧬 Tissue: {tissue_name}")
            print(f"   Health: {data['overall_health']:.1f}%")
            print(f"   Cells: {data['cell_count']} active, {data['quarantine_count']} quarantined")
            print(f"   Transaction Success: {data['transaction_success']:.1f}%")
            
            # Communication stats
            comm_stats = data.get('communication_latency', {})
            if comm_stats:
                print(f"   Inter-cell Latency: {comm_stats.get('mean', 0):.2f}ms (p95: {comm_stats.get('p95', 0):.2f}ms)")


# Performance monitoring decorator
def monitor_performance(metrics: CellMetrics, operation_name: str):
    """Performans monitoring decorator"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                metrics.record_operation(operation_name, duration_ms, success)
                
        return wrapper
    return decorator