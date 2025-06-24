# 📊 Dashboard ve JSON Çıktı Örnekleri

## 🎯 JSON Dashboard Çıktısı

```json
{
  "timestamp": "2024-01-15T14:30:45.123456",
  "tissues": {
    "AuthenticationTissue": {
      "tissue_name": "AuthenticationTissue",
      "overall_health": 85.3,
      "cell_count": 3,
      "quarantine_count": 0,
      "communication_latency": {
        "count": 1247,
        "mean": 12.4,
        "median": 10.2,
        "stdev": 5.8,
        "min": 2.1,
        "max": 89.3,
        "p95": 24.7,
        "p99": 45.2
      },
      "transaction_success": 98.5,
      "cell_summaries": {
        "main_login": {
          "cell_name": "main_login",
          "health": {
            "count": 500,
            "mean": 82.4,
            "median": 85.0,
            "stdev": 12.3,
            "min": 45.0,
            "max": 100.0,
            "p95": 95.0,
            "p99": 98.0
          },
          "latency": {
            "count": 1500,
            "mean": 23.5,
            "median": 18.2,
            "stdev": 15.7,
            "min": 5.1,
            "max": 125.3,
            "p95": 52.3,
            "p99": 98.7
          },
          "error_rate": 0.03,
          "throughput": 25.4,
          "energy": {
            "current": 78.5,
            "min": 12.0,
            "max": 100.0
          }
        },
        "jwt_handler": {
          "cell_name": "jwt_handler",
          "health": {
            "count": 500,
            "mean": 92.1,
            "median": 94.0,
            "stdev": 8.2,
            "min": 65.0,
            "max": 100.0,
            "p95": 98.0,
            "p99": 100.0
          },
          "latency": {
            "count": 2000,
            "mean": 8.2,
            "median": 7.1,
            "stdev": 3.4,
            "min": 2.3,
            "max": 45.2,
            "p95": 15.2,
            "p99": 22.3
          },
          "error_rate": 0.01,
          "throughput": 45.2,
          "energy": {
            "current": 92.3,
            "min": 45.0,
            "max": 100.0
          }
        },
        "permission_checker": {
          "cell_name": "permission_checker",
          "health": {
            "count": 500,
            "mean": 96.8,
            "median": 98.0,
            "stdev": 4.2,
            "min": 78.0,
            "max": 100.0,
            "p95": 100.0,
            "p99": 100.0
          },
          "latency": {
            "count": 3000,
            "mean": 4.2,
            "median": 3.8,
            "stdev": 1.8,
            "min": 1.2,
            "max": 15.3,
            "p95": 7.8,
            "p99": 10.2
          },
          "error_rate": 0.001,
          "throughput": 78.9,
          "energy": {
            "current": 95.7,
            "min": 72.0,
            "max": 100.0
          }
        }
      }
    }
  }
}
```

## 🖥️ Terminal Dashboard Görünümü

```
============================================================
🏥 CODE ORGANISM HEALTH DASHBOARD - 2024-01-15 14:30:45
============================================================

📊 Overall Status:
   Tissues: 3 total
   ✅ Healthy: 2
   ⚠️  Warning: 1
   🚨 Critical: 0

🧬 Tissue: AuthenticationTissue
   Health: 85.3%
   Cells: 3 active, 0 quarantined
   Transaction Success: 98.5%
   Inter-cell Latency: 12.40ms (p95: 24.70ms)

🧬 Tissue: DataProcessingTissue
   Health: 72.1%
   Cells: 5 active, 1 quarantined
   Transaction Success: 94.2%
   Inter-cell Latency: 18.75ms (p95: 35.20ms)

🧬 Tissue: CachingTissue
   Health: 91.8%
   Cells: 2 active, 0 quarantined
   Transaction Success: 99.8%
   Inter-cell Latency: 5.23ms (p95: 8.90ms)
```

## 📈 Real-time Metrics Stream

```json
{
  "metric_stream": [
    {
      "timestamp": "2024-01-15T14:30:45.123",
      "metric": "cell.health_score",
      "value": 85.0,
      "labels": {
        "cell": "main_login",
        "tissue": "AuthenticationTissue"
      }
    },
    {
      "timestamp": "2024-01-15T14:30:45.234",
      "metric": "cell.operation_latency",
      "value": 23.5,
      "labels": {
        "cell": "jwt_handler",
        "operation": "generate_token",
        "tissue": "AuthenticationTissue"
      }
    },
    {
      "timestamp": "2024-01-15T14:30:45.345",
      "metric": "tissue.quarantined_cells",
      "value": 1,
      "labels": {
        "tissue": "DataProcessingTissue",
        "reason": "high_error_rate"
      }
    }
  ]
}
```

## 🚨 Alert Examples

```json
{
  "alerts": [
    {
      "timestamp": "2024-01-15T14:25:32.456",
      "severity": "warning",
      "metric": "cell.health_score",
      "current_value": 45.2,
      "threshold": 50.0,
      "message": "Cell health below warning threshold",
      "cell": "data_processor_3",
      "tissue": "DataProcessingTissue",
      "suggested_action": "Check error logs and resource consumption"
    },
    {
      "timestamp": "2024-01-15T14:28:15.789",
      "severity": "critical",
      "metric": "cell.operation_latency",
      "current_value": 523.7,
      "threshold": 500.0,
      "message": "Operation latency exceeded critical threshold",
      "cell": "cache_writer",
      "operation": "bulk_write",
      "tissue": "CachingTissue",
      "suggested_action": "Scale resources or optimize operation"
    }
  ]
}
```

## 📊 Cell Health Report

```json
{
  "cell_report": {
    "name": "main_login",
    "type": "LoginCell",
    "state": "healthy",
    "health": 85,
    "energy": 78.5,
    "stress": 15,
    "age": 3672.5,
    "divisions": 2,
    "errors": 12,
    "operations": 1523,
    "organelle_status": {
      "mitochondria": 0.92,
      "nucleus": 0.98,
      "lysosome": 0.87
    },
    "membrane_status": {
      "permeability": 0.95,
      "receptors_active": 5,
      "transporters_active": 3
    },
    "mutations": [
      {
        "type": "config_change",
        "timestamp": "2024-01-15T12:15:00",
        "details": {
          "parameter": "max_login_attempts",
          "old_value": 3,
          "new_value": 5
        }
      }
    ],
    "epigenetic_markers": {
      "high_performance": false,
      "energy_saving": true,
      "debug_mode": false
    }
  }
}
```

## 🔄 Transaction History

```json
{
  "transactions": [
    {
      "id": "tx_123456",
      "tissue": "AuthenticationTissue",
      "state": "committed",
      "start_time": "2024-01-15T14:30:40.123",
      "end_time": "2024-01-15T14:30:40.456",
      "duration_ms": 333,
      "affected_cells": ["main_login", "jwt_handler", "permission_checker"],
      "operations": [
        {
          "cell": "main_login",
          "operation": "authenticate",
          "status": "success"
        },
        {
          "cell": "jwt_handler",
          "operation": "generate_token",
          "status": "success"
        },
        {
          "cell": "permission_checker",
          "operation": "validate_permissions",
          "status": "success"
        }
      ]
    },
    {
      "id": "tx_123457",
      "tissue": "DataProcessingTissue",
      "state": "rolled_back",
      "start_time": "2024-01-15T14:30:42.789",
      "end_time": "2024-01-15T14:30:43.012",
      "duration_ms": 223,
      "affected_cells": ["data_processor_1", "data_processor_2"],
      "rollback_reason": "Cell data_processor_2 became infected during transaction",
      "operations": [
        {
          "cell": "data_processor_1",
          "operation": "process_batch",
          "status": "success"
        },
        {
          "cell": "data_processor_2",
          "operation": "aggregate_results",
          "status": "failed",
          "error": "OutOfMemoryError"
        }
      ]
    }
  ]
}
```

## 🌡️ Resource Usage Dashboard

```json
{
  "resource_usage": {
    "timestamp": "2024-01-15T14:30:45",
    "tissues": {
      "AuthenticationTissue": {
        "memory_mb": 128.5,
        "cpu_percent": 12.3,
        "thread_count": 8,
        "energy_consumption": 245.7,
        "cells": {
          "main_login": {
            "memory_mb": 45.2,
            "cpu_percent": 5.8,
            "energy_level": 78.5,
            "active_operations": 3
          },
          "jwt_handler": {
            "memory_mb": 38.7,
            "cpu_percent": 3.2,
            "energy_level": 92.3,
            "active_operations": 5
          },
          "permission_checker": {
            "memory_mb": 44.6,
            "cpu_percent": 3.3,
            "energy_level": 95.7,
            "active_operations": 12
          }
        }
      }
    }
  }
}
```

## 📱 Mobile Dashboard View (Simplified)

```json
{
  "mobile_summary": {
    "health_score": 87.5,
    "status": "healthy",
    "active_tissues": 3,
    "total_cells": 10,
    "quarantined": 1,
    "alerts": 2,
    "last_update": "2 seconds ago",
    "quick_stats": {
      "requests_per_second": 145.7,
      "average_latency_ms": 15.3,
      "error_rate_percent": 0.05
    }
  }
}
```

## 🎨 Grafana/Prometheus Export Format

```
# HELP code_organism_health_score Overall health score of the organism
# TYPE code_organism_health_score gauge
code_organism_health_score{tissue="AuthenticationTissue",cell="main_login"} 85.0
code_organism_health_score{tissue="AuthenticationTissue",cell="jwt_handler"} 92.1
code_organism_health_score{tissue="AuthenticationTissue",cell="permission_checker"} 96.8

# HELP code_organism_operation_latency Operation latency in milliseconds
# TYPE code_organism_operation_latency histogram
code_organism_operation_latency_bucket{tissue="AuthenticationTissue",cell="main_login",operation="authenticate",le="10"} 245
code_organism_operation_latency_bucket{tissue="AuthenticationTissue",cell="main_login",operation="authenticate",le="25"} 456
code_organism_operation_latency_bucket{tissue="AuthenticationTissue",cell="main_login",operation="authenticate",le="50"} 489
code_organism_operation_latency_bucket{tissue="AuthenticationTissue",cell="main_login",operation="authenticate",le="+Inf"} 500

# HELP code_organism_energy_level Current energy level of cells
# TYPE code_organism_energy_level gauge
code_organism_energy_level{tissue="AuthenticationTissue",cell="main_login"} 78.5
code_organism_energy_level{tissue="AuthenticationTissue",cell="jwt_handler"} 92.3
code_organism_energy_level{tissue="AuthenticationTissue",cell="permission_checker"} 95.7
```