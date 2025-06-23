from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import asyncio
import logging

from ..core.code_organ import CodeOrgan
from ..monitoring.performance_metrics import MetricsCollector


class SystemBootManager:
    """System boot sequence management"""
    
    def __init__(self, system_name: str):
        self.system_name = system_name
        self.boot_stages = [
            self._initialize_core,
            self._load_configuration,
            self._start_services,
            self._verify_health
        ]
        self.boot_log = []
        self.boot_time = None
        
    async def boot_system(self, system) -> bool:
        """Execute boot sequence"""
        start_time = datetime.now()
        self.boot_log.clear()
        
        try:
            for stage in self.boot_stages:
                stage_name = stage.__name__
                self.boot_log.append({
                    'stage': stage_name,
                    'start': datetime.now(),
                    'status': 'starting'
                })
                
                await stage(system)
                
                self.boot_log[-1]['end'] = datetime.now()
                self.boot_log[-1]['status'] = 'completed'
                
            self.boot_time = datetime.now() - start_time
            logging.info(f"System {self.system_name} booted in {self.boot_time.total_seconds():.2f}s")
            return True
            
        except Exception as e:
            self.boot_log[-1]['status'] = 'failed'
            self.boot_log[-1]['error'] = str(e)
            logging.error(f"Boot failed at stage {self.boot_log[-1]['stage']}: {e}")
            return False
            
    async def _initialize_core(self, system):
        """Initialize core components"""
        # Set initial consciousness
        from code_system import ConsciousnessLevel
        system.consciousness_level = ConsciousnessLevel.AWAKENING
        
        # Initialize metrics
        system.metrics.record("consciousness_level", 2)  # AWAKENING = 2
        
        await asyncio.sleep(0.1)  # Simulate initialization
        
    async def _load_configuration(self, system):
        """Load system configuration"""
        # In real implementation, would load from config file
        system.config = {
            'max_organs': 10,
            'default_phase': 'normal',
            'optimization_interval': 3600
        }
        
    async def _start_services(self, system):
        """Start background services"""
        # Start maintenance task
        system.maintenance_task = asyncio.create_task(
            system._maintenance_loop()
        )
        
        # Start dream state task
        system.dream_state_task = asyncio.create_task(
            system._dream_state_loop()
        )
        
    async def _verify_health(self, system):
        """Verify system health after boot"""
        from code_system import ConsciousnessLevel
        
        # Basic health check
        if len(system.organs) == 0:
            logging.warning("No organs loaded during boot")
            
        # Set to aware
        system.consciousness_level = ConsciousnessLevel.AWARE
        system.metrics.record("consciousness_level", 3)  # AWARE = 3
        
    def get_boot_report(self) -> Dict[str, Any]:
        """Get detailed boot report"""
        return {
            'system': self.system_name,
            'boot_time': self.boot_time.total_seconds() if self.boot_time else None,
            'stages': self.boot_log
        }


class MaintenanceManager:
    """System maintenance operations management"""
    
    def __init__(self, system_name: str):
        self.system_name = system_name
        self.maintenance_tasks = {
            'memory_cleanup': self._memory_cleanup,
            'metrics_rotation': self._rotate_metrics,
            'connection_health': self._check_connections,
            'organ_optimization': self._optimize_organs
        }
        self.maintenance_log = []
        self.last_maintenance = datetime.now()
        
    async def run_maintenance(self, system, tasks: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run maintenance tasks"""
        if tasks is None:
            tasks = list(self.maintenance_tasks.keys())
            
        results = {}
        for task_name in tasks:
            if task_name in self.maintenance_tasks:
                try:
                    result = await self.maintenance_tasks[task_name](system)
                    results[task_name] = {
                        'status': 'success',
                        'result': result
                    }
                    self._log_maintenance(task_name, 'success', result)
                except Exception as e:
                    results[task_name] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                    self._log_maintenance(task_name, 'failed', str(e))
                    
        self.last_maintenance = datetime.now()
        return results
        
    async def _memory_cleanup(self, system) -> Dict[str, int]:
        """Clean up system memory"""
        # Clear old short-term memory
        old_size = len(system.memory.short_term)
        
        # Keep only recent items
        cutoff_time = datetime.now()
        recent_items = [
            item for item in system.memory.short_term
            if isinstance(item, dict) and 
            'timestamp' in item and 
            (cutoff_time - item['timestamp']).seconds < 3600
        ]
        
        system.memory.short_term.clear()
        system.memory.short_term.extend(recent_items)
        
        # Clear unused working memory
        working_cleared = 0
        for key in list(system.memory.working_memory.keys()):
            if key not in system.memory.muscle_memory:
                del system.memory.working_memory[key]
                working_cleared += 1
                
        return {
            'short_term_cleared': old_size - len(system.memory.short_term),
            'working_memory_cleared': working_cleared
        }
        
    async def _rotate_metrics(self, system) -> Dict[str, Any]:
        """Rotate old metrics data"""
        # In real implementation, would archive old metrics
        return {'status': 'metrics rotated'}
        
    async def _check_connections(self, system) -> Dict[str, Any]:
        """Check organ connections health"""
        unhealthy_connections = []
        
        for (organ1, organ2), strength in system.organ_connections.items():
            if strength < 0.3:
                unhealthy_connections.append({
                    'organs': (organ1, organ2),
                    'strength': strength
                })
                
        return {
            'total_connections': len(system.organ_connections),
            'unhealthy_count': len(unhealthy_connections),
            'unhealthy_connections': unhealthy_connections
        }
        
    async def _optimize_organs(self, system) -> Dict[str, Any]:
        """Optimize individual organs"""
        optimization_results = {}
        
        for organ_name, organ in system.organs.items():
            if hasattr(organ, 'calculate_health'):
                health = organ.calculate_health()
                if health < 70:
                    # Organ needs optimization
                    if hasattr(organ, 'optimize'):
                        await organ.optimize()
                    optimization_results[organ_name] = 'optimized'
                    
        return optimization_results
        
    def _log_maintenance(self, task: str, status: str, details: Any):
        """Log maintenance activity"""
        self.maintenance_log.append({
            'task': task,
            'status': status,
            'details': details,
            'timestamp': datetime.now()
        })
        
        # Keep only recent logs
        if len(self.maintenance_log) > 1000:
            self.maintenance_log = self.maintenance_log[-1000:]
            
    def get_maintenance_report(self) -> Dict[str, Any]:
        """Get maintenance report"""
        return {
            'last_maintenance': self.last_maintenance.isoformat(),
            'total_tasks': len(self.maintenance_tasks),
            'recent_logs': self.maintenance_log[-10:],
            'task_stats': self._calculate_task_stats()
        }
        
    def _calculate_task_stats(self) -> Dict[str, Dict[str, int]]:
        """Calculate task statistics"""
        stats = {}
        
        for log_entry in self.maintenance_log:
            task = log_entry['task']
            status = log_entry['status']
            
            if task not in stats:
                stats[task] = {'success': 0, 'failed': 0}
                
            stats[task][status] += 1
            
        return stats


class SystemMemoryManager:
    """System memory consolidation and management"""
    
    def __init__(self):
        self.consolidation_rules = {
            'frequency': self._consolidate_by_frequency,
            'importance': self._consolidate_by_importance,
            'age': self._consolidate_by_age
        }
        
    async def consolidate_memory(self, system, strategy: str = 'frequency') -> Dict[str, Any]:
        """Consolidate memory using specified strategy"""
        if strategy not in self.consolidation_rules:
            strategy = 'frequency'
            
        consolidator = self.consolidation_rules[strategy]
        return await consolidator(system)
        
    async def _consolidate_by_frequency(self, system) -> Dict[str, Any]:
        """Consolidate based on access frequency"""
        # Move frequently accessed short-term to long-term
        frequency_map = {}
        
        for item in system.memory.short_term:
            if isinstance(item, dict) and 'request' in item:
                req_type = item['request'].get('type', 'unknown')
                frequency_map[req_type] = frequency_map.get(req_type, 0) + 1
                
        # Move high-frequency patterns to long-term
        moved = 0
        for req_type, count in frequency_map.items():
            if count > 10:
                key = f"pattern_{req_type}_{len(system.memory.long_term)}"
                system.memory.long_term[key] = {
                    'type': req_type,
                    'frequency': count,
                    'consolidated_at': datetime.now()
                }
                moved += 1
                
        return {'moved_to_long_term': moved, 'strategy': 'frequency'}
        
    async def _consolidate_by_importance(self, system) -> Dict[str, Any]:
        """Consolidate based on importance metrics"""
        # Move slow operations (important to optimize)
        important_items = [
            item for item in system.memory.short_term
            if isinstance(item, dict) and 
            item.get('duration', 0) > 1.0  # Slow operations
        ]
        
        moved = 0
        for item in important_items:
            key = f"important_{len(system.memory.long_term)}"
            system.memory.long_term[key] = item
            moved += 1
            
        return {'moved_to_long_term': moved, 'strategy': 'importance'}
        
    async def _consolidate_by_age(self, system) -> Dict[str, Any]:
        """Consolidate based on age"""
        # Simply remove old items
        cutoff = datetime.now()
        
        old_count = len(system.memory.short_term)
        system.memory.short_term = deque(
            [item for item in system.memory.short_term
             if isinstance(item, dict) and 
             'timestamp' in item and
             (cutoff - item['timestamp']).seconds < 7200],  # 2 hours
            maxlen=system.memory.short_term.maxlen
        )
        
        return {
            'removed': old_count - len(system.memory.short_term),
            'strategy': 'age'
        }


class SystemShutdownManager:
    """Graceful system shutdown management"""
    
    def __init__(self):
        self.shutdown_stages = [
            self._notify_organs,
            self._save_state,
            self._stop_services,
            self._cleanup_resources
        ]
        self.shutdown_log = []
        
    async def shutdown_system(self, system) -> bool:
        """Execute graceful shutdown"""
        from code_system import ConsciousnessLevel
        
        logging.info(f"Starting shutdown for system {system.system_name}")
        system.consciousness_level = ConsciousnessLevel.DORMANT
        
        try:
            for stage in self.shutdown_stages:
                stage_name = stage.__name__
                self.shutdown_log.append({
                    'stage': stage_name,
                    'start': datetime.now()
                })
                
                await stage(system)
                
                self.shutdown_log[-1]['completed'] = datetime.now()
                
            logging.info(f"System {system.system_name} shutdown complete")
            return True
            
        except Exception as e:
            logging.error(f"Shutdown error at stage {stage.__name__}: {e}")
            return False
            
    async def _notify_organs(self, system):
        """Notify all organs of shutdown"""
        shutdown_event = {
            'type': 'system_shutdown',
            'timestamp': datetime.now()
        }
        
        await system.broadcast(shutdown_event)
        
    async def _save_state(self, system):
        """Save system state for recovery"""
        # In real implementation, would persist to disk
        state = {
            'organs': list(system.organs.keys()),
            'connections': list(system.organ_connections.keys()),
            'memory_stats': {
                'short_term': len(system.memory.short_term),
                'long_term': len(system.memory.long_term)
            }
        }
        logging.info(f"State saved: {state}")
        
    async def _stop_services(self, system):
        """Stop background services"""
        if system.maintenance_task:
            system.maintenance_task.cancel()
            
        if system.dream_state_task:
            system.dream_state_task.cancel()
            
        # Give tasks time to cancel
        await asyncio.sleep(0.1)
        
    async def _cleanup_resources(self, system):
        """Clean up system resources"""
        # Shutdown organs
        shutdown_tasks = []
        for organ in system.organs.values():
            if hasattr(organ, 'shutdown'):
                shutdown_tasks.append(organ.shutdown())
                
        await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        # Shutdown executor
        system.executor.shutdown(wait=True)