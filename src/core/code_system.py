from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
from collections import deque, defaultdict
import logging
from concurrent.futures import ThreadPoolExecutor

from .code_organ import CodeOrgan, CompatibilityType
from ..monitoring.performance_metrics import MetricsCollector, MetricDefinition, MetricType


class ConsciousnessLevel(Enum):
    """System consciousness levels"""
    DORMANT = "dormant"          # System sleeping
    AWAKENING = "awakening"      # Boot sequence
    AWARE = "aware"             # Basic operations
    FOCUSED = "focused"         # Active processing
    HYPERAWARE = "hyperaware"   # Full monitoring & optimization
    DREAMING = "dreaming"       # Background maintenance


@dataclass 
class SystemMemory:
    """System-wide memory consolidation"""
    short_term: deque = field(default_factory=lambda: deque(maxlen=1000))
    long_term: Dict[str, Any] = field(default_factory=dict)
    working_memory: Dict[str, Any] = field(default_factory=dict)
    muscle_memory: Dict[str, Callable] = field(default_factory=dict)  # Cached operations
    
    
@dataclass
class NeuralPathway:
    """System learning pathway"""
    input_pattern: str
    output_action: str
    strength: float = 1.0
    usage_count: int = 0
    last_used: datetime = field(default_factory=datetime.now)
    success_rate: float = 1.0


class SystemAI:
    """Neural learning system for code organism"""
    
    def __init__(self):
        self.pathways: Dict[str, NeuralPathway] = {}
        self.pattern_history = deque(maxlen=10000)
        self.learning_rate = 0.1
        self.threshold = 0.5
        
    def observe_pattern(self, input_data: Dict[str, Any], 
                       action_taken: str, success: bool):
        """Pattern gözlemle ve öğren"""
        pattern_key = self._generate_pattern_key(input_data)
        
        if pattern_key in self.pathways:
            pathway = self.pathways[pattern_key]
            pathway.usage_count += 1
            pathway.last_used = datetime.now()
            
            # Update success rate
            pathway.success_rate = (
                pathway.success_rate * 0.9 + (1.0 if success else 0.0) * 0.1
            )
            
            # Strengthen or weaken based on success
            if success:
                pathway.strength = min(1.0, pathway.strength + self.learning_rate)
            else:
                pathway.strength = max(0.0, pathway.strength - self.learning_rate)
        else:
            # Create new pathway
            self.pathways[pattern_key] = NeuralPathway(
                input_pattern=pattern_key,
                output_action=action_taken,
                success_rate=1.0 if success else 0.0
            )
            
        self.pattern_history.append({
            'pattern': pattern_key,
            'action': action_taken,
            'success': success,
            'timestamp': datetime.now()
        })
        
    def predict_action(self, input_data: Dict[str, Any]) -> Optional[str]:
        """Input'a göre action tahmini"""
        pattern_key = self._generate_pattern_key(input_data)
        
        if pattern_key in self.pathways:
            pathway = self.pathways[pattern_key]
            if pathway.strength > self.threshold and pathway.success_rate > 0.7:
                return pathway.output_action
                
        # Check similar patterns
        similar = self._find_similar_patterns(pattern_key)
        if similar:
            return similar[0].output_action
            
        return None
        
    def _generate_pattern_key(self, input_data: Dict[str, Any]) -> str:
        """Generate unique pattern key from input"""
        # Simplified - in reality would use more sophisticated hashing
        key_parts = []
        for k, v in sorted(input_data.items()):
            if isinstance(v, (str, int, float, bool)):
                key_parts.append(f"{k}:{v}")
        return "|".join(key_parts)
        
    def _find_similar_patterns(self, pattern_key: str) -> List[NeuralPathway]:
        """Benzer pattern'leri bul"""
        # Simplified similarity check
        similar = []
        key_parts = set(pattern_key.split("|"))
        
        for pathway in self.pathways.values():
            pathway_parts = set(pathway.input_pattern.split("|"))
            similarity = len(key_parts & pathway_parts) / len(key_parts | pathway_parts)
            
            if similarity > 0.7:
                similar.append(pathway)
                
        return sorted(similar, key=lambda p: p.strength * p.success_rate, reverse=True)
        
    def consolidate_memory(self):
        """Consolidate learning (move to long-term memory)"""
        # Remove weak pathways
        self.pathways = {
            k: v for k, v in self.pathways.items()
            if v.strength > 0.1 or v.usage_count > 10
        }
        
        # Boost frequently used pathways
        for pathway in self.pathways.values():
            if pathway.usage_count > 100:
                pathway.strength = min(1.0, pathway.strength * 1.1)


class CircadianScheduler:
    """System circadian rhythm for maintenance"""
    
    def __init__(self):
        self.schedules: Dict[str, List[Callable]] = {
            'peak': [],      # High load operations
            'normal': [],    # Regular operations
            'off_peak': [],  # Maintenance tasks
            'sleep': []      # Deep maintenance
        }
        self.current_phase = 'normal'
        self.phase_history = deque(maxlen=24)  # 24 hour history
        
    def get_current_phase(self) -> str:
        """Get current circadian phase based on time and load"""
        hour = datetime.now().hour
        
        # Simple phase determination
        if 9 <= hour <= 17:  # Business hours
            return 'peak'
        elif 6 <= hour <= 22:  # Normal hours
            return 'normal'
        elif 2 <= hour <= 5:  # Deep night
            return 'sleep'
        else:  # Off-peak
            return 'off_peak'
            
    def schedule_task(self, phase: str, task: Callable):
        """Schedule task for specific phase"""
        if phase in self.schedules:
            self.schedules[phase].append(task)
            
    async def execute_phase_tasks(self):
        """Execute tasks for current phase"""
        self.current_phase = self.get_current_phase()
        tasks = self.schedules.get(self.current_phase, [])
        
        results = []
        for task in tasks:
            try:
                if asyncio.iscoroutinefunction(task):
                    result = await task()
                else:
                    result = task()
                results.append(result)
            except Exception as e:
                logging.error(f"Phase task error: {e}")
                
        self.phase_history.append({
            'phase': self.current_phase,
            'task_count': len(tasks),
            'timestamp': datetime.now()
        })
        
        return results


class CodeSystem:
    """The complete code organism system"""
    
    def __init__(self, system_name: str):
        self.system_name = system_name
        self.creation_time = datetime.now()
        self.consciousness_level = ConsciousnessLevel.DORMANT
        
        # Organs
        self.organs: Dict[str, CodeOrgan] = {}
        self.organ_connections: Dict[tuple, float] = {}  # (organ1, organ2) -> strength
        
        # System components
        self.memory = SystemMemory()
        self.neural_ai = SystemAI()
        self.circadian = CircadianScheduler()
        
        # Communication
        self.event_bus = asyncio.Queue()
        self.broadcast_channels: Dict[str, List[str]] = defaultdict(list)
        
        # Monitoring
        self.metrics = MetricsCollector(f"system_{system_name}")
        self._register_metrics()
        self.alert_handlers: List[Callable] = []
        
        # Background tasks
        self.maintenance_task = None
        self.dream_state_task = None
        
        # Thread pool for CPU-bound operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize
        asyncio.create_task(self._boot_sequence())
        
    def _register_metrics(self):
        """System-level metrics"""
        self.metrics.register_metric(MetricDefinition(
            name="consciousness_level",
            type=MetricType.GAUGE,
            unit="level",
            description="System consciousness level"
        ))
        
        self.metrics.register_metric(MetricDefinition(
            name="organ_count",
            type=MetricType.GAUGE,
            unit="count",
            description="Number of active organs"
        ))
        
        self.metrics.register_metric(MetricDefinition(
            name="neural_pathways",
            type=MetricType.GAUGE,
            unit="count",
            description="Number of learned pathways"
        ))
        
        self.metrics.register_metric(MetricDefinition(
            name="memory_usage",
            type=MetricType.GAUGE,
            unit="items",
            description="Memory usage"
        ))
        
    async def _boot_sequence(self):
        """System boot sequence"""
        self.consciousness_level = ConsciousnessLevel.AWAKENING
        
        # Initialize core systems
        await asyncio.sleep(0.1)  # Simulate boot time
        
        # Start background tasks
        self.maintenance_task = asyncio.create_task(self._maintenance_loop())
        self.dream_state_task = asyncio.create_task(self._dream_state_loop())
        
        # Set to aware
        self.consciousness_level = ConsciousnessLevel.AWARE
        self.metrics.record("consciousness_level", 3)  # AWARE = 3
        
        logging.info(f"System {self.system_name} booted successfully")
        
    def add_organ(self, organ: CodeOrgan) -> bool:
        """Add organ to system"""
        if organ.organ_name in self.organs:
            return False
            
        # Check compatibility with existing organs
        compatible = True
        for existing_organ in self.organs.values():
            score = CompatibilityType.compatibility_score(
                organ.compatibility_type,
                existing_organ.compatibility_type
            )
            if score < 0.3:
                logging.warning(
                    f"Low compatibility between {organ.organ_name} "
                    f"and {existing_organ.organ_name}: {score}"
                )
                compatible = False
                
        if not compatible and len(self.organs) > 0:
            return False
            
        self.organs[organ.organ_name] = organ
        self.metrics.record("organ_count", len(self.organs))
        
        # Subscribe organ to event bus
        self.broadcast_channels['all_organs'].append(organ.organ_name)
        
        # Neural pathway for new organ
        self.neural_ai.observe_pattern(
            {'event': 'organ_added', 'type': organ.organ_type.value},
            'integrate_organ',
            True
        )
        
        return True
        
    def connect_organs(self, organ1: str, organ2: str, strength: float = 1.0):
        """Connect two organs"""
        if organ1 not in self.organs or organ2 not in self.organs:
            raise ValueError("Both organs must exist")
            
        self.organ_connections[(organ1, organ2)] = strength
        self.organ_connections[(organ2, organ1)] = strength  # Bidirectional
        
    async def broadcast(self, event: Dict[str, Any], target_channel: str = 'all_organs'):
        """Broadcast event to organs"""
        event['timestamp'] = datetime.now()
        event['source'] = 'system'
        
        # Learn from broadcast
        self.neural_ai.observe_pattern(
            {'event_type': event.get('type', 'unknown')},
            'broadcast',
            True
        )
        
        # Send to targets
        targets = self.broadcast_channels.get(target_channel, [])
        
        tasks = []
        for organ_name in targets:
            if organ_name in self.organs:
                organ = self.organs[organ_name]
                # Simplified - organs would have event handlers
                tasks.append(self._send_to_organ(organ, event))
                
        await asyncio.gather(*tasks, return_exceptions=True)
        
    async def _send_to_organ(self, organ: CodeOrgan, event: Dict[str, Any]):
        """Send event to specific organ"""
        # Simplified implementation
        await organ.process_request({
            'type': 'system_event',
            'event': event
        })
        
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process system-level request"""
        start_time = datetime.now()
        
        # Check if we can predict the best action
        # predicted_action = self.neural_ai.predict_action(request)
        
        # Route to appropriate organ(s)
        request_type = request.get('type', 'general')
        
        # Find best organ for request
        best_organ = None
        for organ in self.organs.values():
            if organ.organ_type.value == request_type:
                best_organ = organ
                break
                
        if not best_organ and self.organs:
            # Use any available organ
            best_organ = list(self.organs.values())[0]
            
        if not best_organ:
            return {'error': 'No organs available'}
            
        # Elevate consciousness if needed
        if self.consciousness_level == ConsciousnessLevel.AWARE:
            self.consciousness_level = ConsciousnessLevel.FOCUSED
            
        # Process through organ
        try:
            result = await best_organ.process_request(request)
            success = 'error' not in result
            
            # Learn from result
            self.neural_ai.observe_pattern(request, best_organ.organ_name, success)
            
            # Store in memory
            self.memory.short_term.append({
                'request': request,
                'organ': best_organ.organ_name,
                'result': result,
                'duration': (datetime.now() - start_time).total_seconds()
            })
            
            return result
            
        finally:
            # Return to normal consciousness
            if self.consciousness_level == ConsciousnessLevel.FOCUSED:
                self.consciousness_level = ConsciousnessLevel.AWARE
                
    def self_diagnose(self) -> Dict[str, Any]:
        """Complete system diagnosis"""
        diagnosis = {
            'system_name': self.system_name,
            'consciousness': self.consciousness_level.value,
            'uptime': (datetime.now() - self.creation_time).total_seconds(),
            'organs': {},
            'memory': {
                'short_term_size': len(self.memory.short_term),
                'long_term_size': len(self.memory.long_term),
                'working_memory_size': len(self.memory.working_memory)
            },
            'neural': {
                'pathways': len(self.neural_ai.pathways),
                'learning_rate': self.neural_ai.learning_rate
            },
            'circadian': {
                'current_phase': self.circadian.current_phase,
                'scheduled_tasks': {
                    phase: len(tasks) 
                    for phase, tasks in self.circadian.schedules.items()
                }
            }
        }
        
        # Organ diagnostics
        for name, organ in self.organs.items():
            diagnosis['organs'][name] = organ.get_diagnostics()
            
        # System health score
        organ_healths = [
            org_diag['health']['overall'] 
            for org_diag in diagnosis['organs'].values()
        ]
        
        diagnosis['overall_health'] = (
            sum(organ_healths) / len(organ_healths) if organ_healths else 100.0
        )
        
        return diagnosis
        
    async def optimize(self):
        """System-wide optimization"""
        self.consciousness_level = ConsciousnessLevel.HYPERAWARE
        
        try:
            # Memory consolidation
            self.neural_ai.consolidate_memory()
            
            # Move short-term to long-term memory
            important_memories = [
                mem for mem in self.memory.short_term
                if mem.get('duration', 0) > 1.0  # Slow operations
            ]
            
            for memory in important_memories:
                key = f"{memory['request'].get('type', 'unknown')}_{len(self.memory.long_term)}"
                self.memory.long_term[key] = memory
                
            # Clear old working memory
            self.memory.working_memory = {
                k: v for k, v in self.memory.working_memory.items()
                if k in self.memory.muscle_memory  # Keep only cached operations
            }
            
            # Optimize organs
            optimization_tasks = []
            for organ in self.organs.values():
                if hasattr(organ, 'optimize'):
                    optimization_tasks.append(organ.optimize())
                    
            await asyncio.gather(*optimization_tasks, return_exceptions=True)
            
        finally:
            self.consciousness_level = ConsciousnessLevel.AWARE
            
    async def _maintenance_loop(self):
        """Background maintenance loop"""
        while True:
            try:
                await asyncio.sleep(60)  # Every minute
                
                # Execute circadian tasks
                await self.circadian.execute_phase_tasks()
                
                # Update metrics
                self.metrics.record("neural_pathways", len(self.neural_ai.pathways))
                self.metrics.record("memory_usage", 
                                  len(self.memory.short_term) + len(self.memory.long_term))
                
                # Check if optimization needed
                if len(self.memory.short_term) > 800:  # 80% full
                    await self.optimize()
                    
            except Exception as e:
                logging.error(f"Maintenance error: {e}")
                
    async def _dream_state_loop(self):
        """Dream state for deep optimization"""
        while True:
            try:
                # Wait for off-peak hours
                await asyncio.sleep(3600)  # Check every hour
                
                if self.circadian.current_phase == 'sleep':
                    self.consciousness_level = ConsciousnessLevel.DREAMING
                    
                    # Deep optimization
                    await self.optimize()
                    
                    # Cleanup
                    self.memory.short_term.clear()
                    
                    # Defragmentation (metaphorical)
                    await self._defragment_memory()
                    
                    self.consciousness_level = ConsciousnessLevel.AWARE
                    
            except Exception as e:
                logging.error(f"Dream state error: {e}")
                
    async def _defragment_memory(self):
        """Memory defragmentation during dream state"""
        # Reorganize long-term memory by access patterns
        access_counts = defaultdict(int)
        
        # Count accesses from neural pathways
        for pathway in self.neural_ai.pathways.values():
            memory_refs = [
                k for k in self.memory.long_term.keys()
                if k in pathway.input_pattern
            ]
            for ref in memory_refs:
                access_counts[ref] += pathway.usage_count
                
        # Keep only frequently accessed memories
        self.memory.long_term = {
            k: v for k, v in self.memory.long_term.items()
            if access_counts[k] > 5 or (datetime.now() - v.get('timestamp', datetime.now())).days < 7
        }
        
    def schedule_maintenance(self, task: Callable, phase: str = 'off_peak'):
        """Schedule maintenance task"""
        self.circadian.schedule_task(phase, task)
        
    async def shutdown(self):
        """Graceful system shutdown"""
        logging.info(f"Shutting down system {self.system_name}")
        
        # Set to dormant
        self.consciousness_level = ConsciousnessLevel.DORMANT
        
        # Cancel background tasks
        if self.maintenance_task:
            self.maintenance_task.cancel()
        if self.dream_state_task:
            self.dream_state_task.cancel()
            
        # Shutdown organs
        shutdown_tasks = []
        for organ in self.organs.values():
            if hasattr(organ, 'shutdown'):
                shutdown_tasks.append(organ.shutdown())
                
        await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logging.info(f"System {self.system_name} shutdown complete")