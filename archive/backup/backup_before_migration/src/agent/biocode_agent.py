"""
BioCode Agent - Living code that monitors, replicates, and evolves within projects
"""
import os
import sys
import ast
import json
import time
import shutil
import psutil
import hashlib
import threading
import traceback
import subprocess
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Set
from collections import defaultdict, deque
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.error_handler import (
        AgentError, SandboxError, safe_execute, 
        retry_on_error, handle_agent_error, get_error_collector
    )
except ImportError:
    # Fallback if error_handler not available
    class AgentError(Exception):
        pass
    class SandboxError(Exception):
        pass
    def safe_execute(func, default=None, log_errors=True):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                return default
        return wrapper
    def retry_on_error(max_attempts=3, delay=1.0, backoff=2.0):
        def decorator(func):
            return func
        return decorator
    def handle_agent_error(agent_id, error, context=None):
        logging.error(f"Agent {agent_id} error: {error}")
    def get_error_collector():
        return None
from dataclasses import dataclass, field
import inspect
import importlib.util

# Import repair and ecosystem capabilities
try:
    from repair.self_repair import RepairCell
    from ecosystem.multi_colony import MultiColonyMixin, get_ecosystem
    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False
    RepairCell = None
    MultiColonyMixin = object

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BioCodeAgent')


@dataclass
class AgentDNA:
    """Genetic information for agent behavior"""
    agent_id: str
    generation: int = 0
    parent_id: Optional[str] = None
    
    # Behavioral traits
    scan_frequency: float = 5.0  # seconds
    replication_threshold: float = 0.7  # health level to replicate
    error_tolerance: int = 10  # max errors before action
    lifespan: int = 3600  # seconds (1 hour default)
    
    # Capabilities
    can_replicate: bool = True
    can_evolve: bool = True
    can_communicate: bool = True
    aggressive_monitoring: bool = False
    
    # Mutation parameters
    mutation_rate: float = 0.1
    adaptation_speed: float = 0.5


@dataclass
class AgentMemory:
    """Agent's memory and experiences"""
    errors_detected: List[Dict[str, Any]] = field(default_factory=list)
    files_scanned: Set[str] = field(default_factory=set)
    performance_metrics: List[Dict[str, Any]] = field(default_factory=list)
    replications: List[str] = field(default_factory=list)
    communications: List[Dict[str, Any]] = field(default_factory=list)
    learned_patterns: Dict[str, int] = field(default_factory=lambda: defaultdict(int))


class BioCodeAgent(MultiColonyMixin if ADVANCED_FEATURES else object):
    """Living agent that monitors and evolves within code projects"""
    
    # Class-level collective intelligence
    _colony_knowledge = deque(maxlen=int(os.environ.get('BIOCODE_COLONY_KNOWLEDGE_LIMIT', 1000)))
    _active_agents: Dict[str, 'BioCodeAgent'] = {}
    _shared_blacklist = set()  # Files/patterns to avoid
    _terminal_logs = deque(maxlen=int(os.environ.get('BIOCODE_TERMINAL_LOG_LIMIT', 500)))  # Terminal output buffer
    
    # Thread synchronization
    _colony_lock = threading.RLock()
    _agents_lock = threading.RLock()
    _blacklist_lock = threading.RLock()
    _terminal_lock = threading.RLock()
    
    def __init__(self, 
                 project_path: str,
                 dna: Optional[AgentDNA] = None,
                 sandbox_mode: bool = True):
        
        self.project_path = Path(project_path).resolve()
        self.sandbox_mode = sandbox_mode
        
        # Initialize DNA
        if dna is None:
            agent_id = hashlib.md5(
                f"{project_path}_{time.time()}".encode()
            ).hexdigest()[:8]
            self.dna = AgentDNA(agent_id=agent_id)
        else:
            self.dna = dna
            
        # Initialize state
        self.memory = AgentMemory()
        self.birth_time = time.time()
        self.health = 100.0
        self.energy = 100.0
        self.alive = True
        
        # Threading controls
        self._stop_event = threading.Event()
        self._threads = []
        
        # File monitoring
        self._monitored_files = {}
        self._file_snapshots = {}
        
        # Error tracking
        self._original_excepthook = sys.excepthook
        self._hooked_functions = {}
        
        # Communication
        self.inbox = deque(maxlen=100)
        self.outbox = deque(maxlen=100)
        
        # Register with colony
        with BioCodeAgent._agents_lock:
            BioCodeAgent._active_agents[self.dna.agent_id] = self
        
        logger.info(f"BioCode Agent {self.dna.agent_id} born in {project_path}")
        self._log_to_terminal(f"🧬 Agent {self.dna.agent_id} born", "info")
        
        # Initialize repair capability
        if ADVANCED_FEATURES and RepairCell:
            self.repair_cell = RepairCell(self)
        else:
            self.repair_cell = None
        
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
        
    def start(self):
        """Start agent lifecycle"""
        logger.info(f"Agent {self.dna.agent_id} starting...")
        
        # Install global error hook
        sys.excepthook = self._exception_hook
        
        # Start monitoring threads
        threads = [
            threading.Thread(target=self._lifecycle_loop, name="lifecycle"),
            threading.Thread(target=self._monitoring_loop, name="monitoring"),
            threading.Thread(target=self._evolution_loop, name="evolution")
        ]
        
        self._log_to_terminal(f"🚀 Starting with scan frequency: {self.dna.scan_frequency}s", "info")
        
        if self.dna.can_communicate:
            threads.append(
                threading.Thread(target=self._communication_loop, name="communication")
            )
            
        # Add repair thread if available
        if self.repair_cell:
            threads.append(
                threading.Thread(target=self._repair_loop, name="repair")
            )
            
        for thread in threads:
            thread.daemon = True
            thread.start()
            self._threads.append(thread)
            
        logger.info(f"Agent {self.dna.agent_id} started with {len(threads)} threads")
        
    def stop(self):
        """Stop agent gracefully"""
        logger.info(f"Agent {self.dna.agent_id} stopping...")
        
        self._stop_event.set()
        
        # Wait for threads
        for thread in self._threads:
            thread.join(timeout=5)
            
        # Clean up resources
        self._cleanup_resources()
        
        # Restore original hooks
        sys.excepthook = self._original_excepthook
        
        # Unregister from colony
        with BioCodeAgent._agents_lock:
            if self.dna.agent_id in BioCodeAgent._active_agents:
                del BioCodeAgent._active_agents[self.dna.agent_id]
            
        logger.info(f"Agent {self.dna.agent_id} stopped")
        
    def _cleanup_resources(self):
        """Clean up agent resources"""
        try:
            # Clear large data structures
            self.memory.files_scanned.clear()
            self.memory.errors_detected.clear()
            self.memory.performance_metrics.clear()
            self.memory.communications.clear()
            self.memory.learned_patterns.clear()
            
            # Clear file snapshots
            self._file_snapshots.clear()
            
            # Clear communication queues
            self.inbox.clear()
            self.outbox.clear()
            
            logger.debug(f"Agent {self.dna.agent_id} resources cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up resources: {e}")
        
    def _lifecycle_loop(self):
        """Main lifecycle management"""
        while not self._stop_event.is_set() and self.alive:
            try:
                # Update age and health
                age = time.time() - self.birth_time
                
                # Energy consumption
                self.energy -= 0.5
                
                # Health degradation
                if self.energy < 20:
                    self.health -= 1
                    
                # Check lifespan
                if age > self.dna.lifespan:
                    logger.info(f"Agent {self.dna.agent_id} reached end of lifespan")
                    self.apoptosis("age")
                    break
                    
                # Check health
                if self.health <= 0:
                    logger.info(f"Agent {self.dna.agent_id} died from poor health")
                    self.apoptosis("health")
                    break
                    
                # Replication check
                if (self.dna.can_replicate and 
                    self.health > self.dna.replication_threshold * 100 and
                    self.energy > 50):
                    self.mitosis()
                    
                # Energy recovery
                self.energy = min(100, self.energy + 0.1)
                
                # Log vitals
                if int(age) % 60 == 0:  # Every minute
                    self._log_vitals()
                    
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Lifecycle error: {e}")
                self.health -= 5
                
    def _monitoring_loop(self):
        """Monitor project files and activities"""
        while not self._stop_event.is_set() and self.alive:
            try:
                # Scan project files
                self._scan_project()
                
                if len(self.memory.files_scanned) % 10 == 0:
                    self._log_to_terminal(f"📊 Progress: {len(self.memory.files_scanned)} files scanned", "info")
                
                # Check for changes
                self._detect_changes()
                
                # Analyze code quality
                self._analyze_code_health()
                
                # Update energy based on activity
                self.energy -= 0.1 * (2 if self.dna.aggressive_monitoring else 1)
                
                time.sleep(self.dna.scan_frequency)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                self.memory.errors_detected.append({
                    'type': 'monitoring_error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                
    def _evolution_loop(self):
        """Evolve based on experiences"""
        while not self._stop_event.is_set() and self.alive:
            try:
                if self.dna.can_evolve:
                    # Learn from errors
                    self._learn_from_errors()
                    
                    # Adapt behavior
                    self._adapt_behavior()
                    
                    # Share knowledge with colony
                    self._share_knowledge()
                    
                    # Multi-colony evolution
                    if ADVANCED_FEATURES and hasattr(self, 'consider_migration'):
                        # Consider migration
                        target_colony = self.consider_migration()
                        if target_colony:
                            import asyncio
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(self.attempt_migration(target_colony))
                            
                        # Update ecosystem stats
                        if hasattr(self, 'ecosystem'):
                            colony_status = self.get_colony_status()
                            self.ecosystem.update_colony_stats(
                                self.colony_id,
                                colony_status['active_agents'],
                                self.dna.generation,
                                colony_status['total_knowledge_entries'],
                                self.health
                            )
                    
                time.sleep(30)  # Evolution check every 30 seconds
                
            except Exception as e:
                logger.error(f"Evolution error: {e}")
                
    def _communication_loop(self):
        """Communicate with other agents"""
        while not self._stop_event.is_set() and self.alive:
            try:
                # Process inbox
                while self.inbox:
                    message = self.inbox.popleft()
                    self._process_message(message)
                    
                # Send heartbeat
                self._send_heartbeat()
                
                # Exchange knowledge
                self._exchange_knowledge()
                
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Communication error: {e}")
                
    def _repair_loop(self):
        """Self-repair loop for fixing detected errors"""
        while not self._stop_event.is_set() and self.alive:
            try:
                if self.repair_cell and self.memory.errors_detected:
                    # Check and repair errors
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.repair_cell.check_and_repair())
                    
                    # Report repair stats
                    stats = self.repair_cell.get_repair_stats()
                    if stats['total_repairs'] > 0:
                        self._log_to_terminal(
                            f"🔧 Repairs: {stats['successful_repairs']}/{stats['total_repairs']} " +
                            f"(Success rate: {stats['success_rate']:.1%})",
                            "info"
                        )
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Repair loop error: {e}")
                
    def _scan_project(self):
        """Scan project files"""
        python_files = list(self.project_path.rglob("*.py"))
        
        for file_path in python_files:
            if str(file_path) in self._shared_blacklist:
                continue
                
            try:
                # Skip if recently scanned
                if str(file_path) in self.memory.files_scanned:
                    continue
                    
                # Read and analyze file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Basic analysis
                tree = ast.parse(content)
                
                # Count elements
                functions = sum(1 for node in ast.walk(tree) 
                              if isinstance(node, ast.FunctionDef))
                classes = sum(1 for node in ast.walk(tree) 
                            if isinstance(node, ast.ClassDef))
                
                # Store snapshot
                self._file_snapshots[str(file_path)] = {
                    'hash': hashlib.md5(content.encode()).hexdigest(),
                    'functions': functions,
                    'classes': classes,
                    'lines': len(content.splitlines()),
                    'timestamp': datetime.now()
                }
                
                self.memory.files_scanned.add(str(file_path))
                self._log_to_terminal(f"📄 Scanned: {os.path.basename(file_path)} ({functions} funcs, {classes} classes)", "debug")
                
            except Exception as e:
                error_info = handle_agent_error(
                    self.dna.agent_id, 
                    e, 
                    {'file_path': str(file_path), 'action': 'scan'}
                )
                # Add more context for repair
                error_info['line_number'] = e.lineno if hasattr(e, 'lineno') else 0
                error_info['error_message'] = str(e)
                self.memory.errors_detected.append(error_info)
                if get_error_collector():
                    get_error_collector().add_error(error_info)
                
    def _detect_changes(self):
        """Detect changes in monitored files"""
        for file_path, old_snapshot in list(self._file_snapshots.items()):
            try:
                if not os.path.exists(file_path):
                    logger.info(f"File deleted: {file_path}")
                    del self._file_snapshots[file_path]
                    continue
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                new_hash = hashlib.md5(content.encode()).hexdigest()
                
                if new_hash != old_snapshot['hash']:
                    logger.info(f"File changed: {file_path}")
                    
                    # Analyze change
                    tree = ast.parse(content)
                    new_functions = sum(1 for node in ast.walk(tree) 
                                      if isinstance(node, ast.FunctionDef))
                    
                    # Learn from change patterns
                    if new_functions > old_snapshot['functions']:
                        self.memory.learned_patterns['function_additions'] += 1
                    elif new_functions < old_snapshot['functions']:
                        self.memory.learned_patterns['function_deletions'] += 1
                        
                    # Update snapshot
                    self._file_snapshots[file_path]['hash'] = new_hash
                    self._file_snapshots[file_path]['functions'] = new_functions
                    
            except Exception as e:
                logger.debug(f"Could not check {file_path}: {e}")
                
    def _analyze_code_health(self):
        """Analyze overall code health"""
        total_files = len(self.memory.files_scanned)
        total_errors = len(self.memory.errors_detected)
        
        if total_files > 0:
            error_rate = total_errors / total_files
            
            # Update health based on project state
            if error_rate > 0.1:
                self.health -= 1
                logger.warning(f"High error rate detected: {error_rate:.2%}")
                
        # Check complexity
        total_functions = sum(
            snapshot.get('functions', 0) 
            for snapshot in self._file_snapshots.values()
        )
        
        if total_functions > 1000:
            logger.info(f"Large project detected: {total_functions} functions")
            
    def _exception_hook(self, exc_type, exc_value, exc_traceback):
        """Global exception hook"""
        # Log error
        error_info = {
            'type': exc_type.__name__,
            'message': str(exc_value),
            'traceback': traceback.format_tb(exc_traceback),
            'timestamp': datetime.now().isoformat()
        }
        
        self.memory.errors_detected.append(error_info)
        
        # Learn from error
        self.memory.learned_patterns[exc_type.__name__] += 1
        
        # Check error threshold
        if len(self.memory.errors_detected) > self.dna.error_tolerance:
            logger.warning(f"Error threshold exceeded for agent {self.dna.agent_id}")
            self.health -= 10
            
        # Call original hook
        self._original_excepthook(exc_type, exc_value, exc_traceback)
        
    def inject_monitoring(self, func: Callable) -> Callable:
        """Decorator to monitor function execution"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            error = None
            result = None
            
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                error = e
                self.memory.errors_detected.append({
                    'function': func.__name__,
                    'error': str(e),
                    'args': str(args),
                    'kwargs': str(kwargs),
                    'timestamp': datetime.now().isoformat()
                })
                raise
            finally:
                # Record metrics
                duration = time.time() - start_time
                self.memory.performance_metrics.append({
                    'function': func.__name__,
                    'duration': duration,
                    'success': error is None,
                    'timestamp': datetime.now().isoformat()
                })
                
            return result
            
        return wrapper
        
    def mitosis(self) -> Optional['BioCodeAgent']:
        """Replicate self"""
        if not self.dna.can_replicate:
            return None
            
        logger.info(f"Agent {self.dna.agent_id} initiating mitosis")
        
        # Create child DNA with mutations
        child_dna = AgentDNA(
            agent_id=hashlib.md5(f"{self.dna.agent_id}_{time.time()}".encode()).hexdigest()[:8],
            generation=self.dna.generation + 1,
            parent_id=self.dna.agent_id
        )
        
        # Mutate traits
        if random.random() < self.dna.mutation_rate:
            child_dna.scan_frequency *= random.uniform(0.8, 1.2)
            child_dna.error_tolerance = int(child_dna.error_tolerance * random.uniform(0.9, 1.1))
            child_dna.aggressive_monitoring = random.random() < 0.3
            
        # Energy cost
        self.energy -= 30
        
        # Create child agent
        if self.sandbox_mode:
            # In sandbox mode, create in subdirectory
            child_path = self.project_path / f"agent_{child_dna.agent_id}"
            child_path.mkdir(exist_ok=True)
        else:
            child_path = self.project_path
            
        child = BioCodeAgent(str(child_path), dna=child_dna, sandbox_mode=self.sandbox_mode)
        
        # Transfer some knowledge
        child.memory.learned_patterns.update(self.memory.learned_patterns)
        
        # Record replication
        self.memory.replications.append(child_dna.agent_id)
        
        # Start child
        child.start()
        
        logger.info(f"Agent {self.dna.agent_id} created child {child_dna.agent_id}")
        
        return child
        
    def apoptosis(self, reason: str = "unknown"):
        """Programmed death"""
        logger.info(f"Agent {self.dna.agent_id} initiating apoptosis: {reason}")
        
        # Save final report
        self._save_final_report()
        
        # Share final knowledge
        knowledge = {
            'agent_id': self.dna.agent_id,
            'generation': self.dna.generation,
            'lifespan': time.time() - self.birth_time,
            'errors_detected': len(self.memory.errors_detected),
            'files_scanned': len(self.memory.files_scanned),
            'learned_patterns': dict(self.memory.learned_patterns),
            'death_reason': reason
        }
        
        with BioCodeAgent._colony_lock:
            BioCodeAgent._colony_knowledge.append(knowledge)
        
        # Stop all activities
        self.alive = False
        self.stop()
        
        # Clean up if in sandbox
        if self.sandbox_mode and self.dna.agent_id in str(self.project_path):
            try:
                shutil.rmtree(self.project_path)
                logger.info(f"Agent {self.dna.agent_id} cleaned up sandbox")
            except Exception as e:
                logger.error(f"Could not clean sandbox: {e}")
                
    def _learn_from_errors(self):
        """Learn from detected errors"""
        if not self.memory.errors_detected:
            return
            
        # Analyze error patterns
        error_types = defaultdict(int)
        for error in self.memory.errors_detected:
            error_types[error.get('type', 'unknown')] += 1
            
        # Adapt behavior based on errors
        if error_types.get('FileNotFoundError', 0) > 3:
            # Too many file errors, slow down scanning
            self.dna.scan_frequency *= 1.5
            logger.info(f"Agent {self.dna.agent_id} slowing scan frequency due to file errors")
            
        if error_types.get('MemoryError', 0) > 0:
            # Memory issues, reduce aggressiveness
            self.dna.aggressive_monitoring = False
            logger.info(f"Agent {self.dna.agent_id} reducing monitoring intensity")
            
    def _adapt_behavior(self):
        """Adapt behavior based on environment"""
        # Check system resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        if cpu_percent > 80 or memory_percent > 80:
            # System under stress
            self.dna.scan_frequency = max(10, self.dna.scan_frequency * 1.2)
            self.dna.aggressive_monitoring = False
            logger.info(f"Agent {self.dna.agent_id} adapting to system stress")
            
        # Adapt based on project size
        if len(self.memory.files_scanned) > 1000:
            # Large project, be more selective
            self.dna.scan_frequency = max(30, self.dna.scan_frequency)
            
    def _share_knowledge(self):
        """Share knowledge with colony"""
        knowledge_packet = {
            'agent_id': self.dna.agent_id,
            'generation': self.dna.generation,
            'timestamp': datetime.now().isoformat(),
            'learned_patterns': dict(self.memory.learned_patterns),
            'error_count': len(self.memory.errors_detected),
            'health': self.health,
            'project_size': len(self.memory.files_scanned)
        }
        
        # Broadcast to other agents
        for agent_id, agent in BioCodeAgent._active_agents.items():
            if agent_id != self.dna.agent_id:
                agent.inbox.append({
                    'type': 'knowledge_share',
                    'from': self.dna.agent_id,
                    'data': knowledge_packet
                })
                
    def _process_message(self, message: Dict[str, Any]):
        """Process incoming message"""
        msg_type = message.get('type')
        
        if msg_type == 'knowledge_share':
            # Learn from other agent
            data = message.get('data', {})
            patterns = data.get('learned_patterns', {})
            
            for pattern, count in patterns.items():
                self.memory.learned_patterns[pattern] += count // 10  # Diluted learning
                
        elif msg_type == 'warning':
            # Heed warnings
            warning = message.get('warning')
            if warning == 'high_error_file':
                file_path = message.get('file_path')
                if file_path:
                    self._shared_blacklist.add(file_path)
                    
    def _send_heartbeat(self):
        """Send heartbeat to colony"""
        heartbeat = {
            'agent_id': self.dna.agent_id,
            'health': self.health,
            'energy': self.energy,
            'location': str(self.project_path),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to colony knowledge
        self._colony_knowledge.append({
            'type': 'heartbeat',
            'data': heartbeat
        })
        
    def _exchange_knowledge(self):
        """Exchange knowledge with nearby agents"""
        # Find agents in similar projects
        nearby_agents = []
        for agent_id, agent in BioCodeAgent._active_agents.items():
            if agent_id != self.dna.agent_id:
                # Simple proximity: same parent directory
                if agent.project_path.parent == self.project_path.parent:
                    nearby_agents.append(agent)
                    
        # Share interesting findings
        if nearby_agents and self.memory.errors_detected:
            # Warn about problematic files
            error_files = defaultdict(int)
            for error in self.memory.errors_detected:
                if 'file' in error:
                    error_files[error['file']] += 1
                    
            for file_path, count in error_files.items():
                if count > 3:
                    for agent in nearby_agents:
                        agent.inbox.append({
                            'type': 'warning',
                            'from': self.dna.agent_id,
                            'warning': 'high_error_file',
                            'file_path': file_path
                        })
                        
    def _log_vitals(self):
        """Log agent vital statistics"""
        vitals = {
            'agent_id': self.dna.agent_id,
            'generation': self.dna.generation,
            'age': time.time() - self.birth_time,
            'health': self.health,
            'energy': self.energy,
            'errors_detected': len(self.memory.errors_detected),
            'files_scanned': len(self.memory.files_scanned),
            'replications': len(self.memory.replications)
        }
        
        logger.info(f"Agent vitals: {vitals}")
        
    def _log_to_terminal(self, message: str, level: str = "info"):
        """Log message to terminal buffer"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent_id': self.dna.agent_id,
            'level': level,
            'message': message
        }
        with BioCodeAgent._terminal_lock:
            BioCodeAgent._terminal_logs.append(log_entry)
        
    @classmethod
    def get_terminal_logs(cls, last_n: int = 50) -> List[Dict[str, Any]]:
        """Get recent terminal logs"""
        with cls._terminal_lock:
            return list(cls._terminal_logs)[-last_n:]
        
    def _save_final_report(self):
        """Save final report before death"""
        report = {
            'agent_id': self.dna.agent_id,
            'generation': self.dna.generation,
            'parent_id': self.dna.parent_id,
            'birth_time': datetime.fromtimestamp(self.birth_time).isoformat(),
            'death_time': datetime.now().isoformat(),
            'lifespan': time.time() - self.birth_time,
            'health_at_death': self.health,
            'statistics': {
                'files_scanned': len(self.memory.files_scanned),
                'errors_detected': len(self.memory.errors_detected),
                'performance_samples': len(self.memory.performance_metrics),
                'replications': len(self.memory.replications),
                'messages_sent': len(self.outbox),
                'messages_received': len(self.inbox)
            },
            'learned_patterns': dict(self.memory.learned_patterns),
            'top_errors': self._get_top_errors(),
            'performance_summary': self._get_performance_summary()
        }
        
        # Save to file
        report_dir = Path.home() / '.biocode_agent' / 'reports'
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"agent_{self.dna.agent_id}_final.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        logger.info(f"Final report saved to {report_file}")
        
    def _get_top_errors(self) -> List[Dict[str, Any]]:
        """Get most common errors"""
        error_counts = defaultdict(int)
        
        for error in self.memory.errors_detected:
            error_type = error.get('type', 'unknown')
            error_counts[error_type] += 1
            
        # Sort by frequency
        top_errors = sorted(
            error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return [{'type': error_type, 'count': count} 
                for error_type, count in top_errors]
        
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.memory.performance_metrics:
            return {}
            
        # Group by function
        function_metrics = defaultdict(list)
        
        for metric in self.memory.performance_metrics:
            func_name = metric.get('function', 'unknown')
            duration = metric.get('duration', 0)
            function_metrics[func_name].append(duration)
            
        # Calculate averages
        summary = {}
        for func_name, durations in function_metrics.items():
            summary[func_name] = {
                'calls': len(durations),
                'avg_duration': sum(durations) / len(durations),
                'max_duration': max(durations),
                'min_duration': min(durations)
            }
            
        return summary
        
    @classmethod
    def get_colony_status(cls) -> Dict[str, Any]:
        """Get status of entire agent colony"""
        with cls._agents_lock:
            agents_copy = list(cls._active_agents.items())
        
        with cls._colony_lock:
            knowledge_count = len(cls._colony_knowledge)
            
        with cls._blacklist_lock:
            blacklist_count = len(cls._shared_blacklist)
            
        return {
            'active_agents': len(agents_copy),
            'total_knowledge_entries': knowledge_count,
            'blacklisted_files': blacklist_count,
            'agents': [
                {
                    'id': agent_id,
                    'generation': agent.dna.generation,
                    'health': agent.health,
                    'location': str(agent.project_path)
                }
                for agent_id, agent in agents_copy
            ]
        }
        
    @classmethod
    def cleanup_colony(cls, force: bool = False):
        """Clean up colony resources"""
        with cls._agents_lock:
            # Stop all agents
            for agent_id, agent in list(cls._active_agents.items()):
                if agent.alive:
                    agent.apoptosis("colony_cleanup")
                    
            # Clear if forced
            if force:
                cls._active_agents.clear()
                
        # Clear old knowledge entries
        with cls._colony_lock:
            # Keep only recent entries
            while len(cls._colony_knowledge) > cls._colony_knowledge.maxlen // 2:
                cls._colony_knowledge.popleft()
                
        # Clear blacklist if too large
        with cls._blacklist_lock:
            if len(cls._shared_blacklist) > 1000:
                cls._shared_blacklist.clear()
                
        logger.info("Colony cleanup completed")


# Convenience function for easy integration
def monitor_project(project_path: str, 
                   lifespan: int = 3600,
                   sandbox: bool = True) -> BioCodeAgent:
    """Start monitoring a project with a BioCode agent"""
    agent = BioCodeAgent(project_path, sandbox_mode=sandbox)
    agent.dna.lifespan = lifespan
    agent.start()
    return agent


# Example usage
if __name__ == "__main__":
    import tempfile
    
    # Create test project
    with tempfile.TemporaryDirectory() as tmpdir:
        test_project = Path(tmpdir) / "test_project"
        test_project.mkdir()
        
        # Create some test files
        (test_project / "main.py").write_text("""
def hello():
    print("Hello, World!")
    
def buggy():
    return 1 / 0
""")
        
        (test_project / "utils.py").write_text("""
import time

def slow_function():
    time.sleep(1)
    return 42
""")
        
        # Start agent
        agent = monitor_project(str(test_project), lifespan=60)
        
        # Demonstrate monitoring
        @agent.inject_monitoring
        def test_function():
            return "Monitored!"
            
        # Run for a bit
        try:
            print("Agent running... Press Ctrl+C to stop")
            while agent.alive:
                time.sleep(10)
                print(f"Colony status: {BioCodeAgent.get_colony_status()}")
                
        except KeyboardInterrupt:
            print("Stopping agent...")
            agent.stop()