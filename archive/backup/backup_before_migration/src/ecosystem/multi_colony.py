"""
BioCode Multi-Colony Ecosystem - Inter-project agent migration and collaboration
"""
import os
import json
import pickle
import shutil
import asyncio
import threading
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class ColonyInfo:
    """Information about a colony"""
    colony_id: str
    project_path: str
    created_at: datetime
    population: int = 0
    generation_max: int = 0
    knowledge_entries: int = 0
    health_average: float = 0.0
    specializations: List[str] = field(default_factory=list)
    allied_colonies: Set[str] = field(default_factory=set)
    
    
@dataclass
class MigrationPacket:
    """Data packet for agent migration"""
    agent_id: str
    source_colony: str
    target_colony: str
    dna: 'AgentDNA'
    memory_snapshot: Dict[str, Any]
    knowledge: List[Dict[str, Any]]
    timestamp: datetime
    reason: str = "exploration"
    

@dataclass 
class GeneTransfer:
    """Genetic material transfer between colonies"""
    source_agent: str
    target_agent: str
    traits: Dict[str, Any]
    timestamp: datetime
    success: bool = False
    

class EcosystemCoordinator:
    """Manages multiple colonies and inter-colony operations"""
    
    def __init__(self, ecosystem_name: str = "default"):
        self.ecosystem_name = ecosystem_name
        self.colonies: Dict[str, ColonyInfo] = {}
        self.migration_history: List[MigrationPacket] = []
        self.gene_transfers: List[GeneTransfer] = []
        self.ecosystem_knowledge = deque(maxlen=5000)
        
        # Communication channels
        self.migration_queue = asyncio.Queue()
        self.broadcast_queue = asyncio.Queue()
        
        # Ecosystem rules
        self.migration_rules = {
            'min_health': 70.0,
            'max_migrations_per_hour': 10,
            'quarantine_period': 60,  # seconds
            'max_population_imbalance': 0.5
        }
        
        # Thread safety
        self._lock = threading.RLock()
        self._running = False
        self._coordinator_thread = None
        
        # Persistence
        self.data_dir = Path.home() / '.biocode_ecosystem' / ecosystem_name
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self._load_ecosystem_state()
        
    def _load_ecosystem_state(self):
        """Load ecosystem state from disk"""
        state_file = self.data_dir / 'ecosystem_state.json'
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    # Restore colonies
                    for colony_data in state.get('colonies', []):
                        colony = ColonyInfo(**colony_data)
                        colony.created_at = datetime.fromisoformat(colony.created_at)
                        self.colonies[colony.colony_id] = colony
                logger.info(f"Loaded ecosystem with {len(self.colonies)} colonies")
            except Exception as e:
                logger.error(f"Failed to load ecosystem state: {e}")
                
    def _save_ecosystem_state(self):
        """Save ecosystem state to disk"""
        state_file = self.data_dir / 'ecosystem_state.json'
        try:
            state = {
                'ecosystem_name': self.ecosystem_name,
                'colonies': [
                    {
                        'colony_id': c.colony_id,
                        'project_path': c.project_path,
                        'created_at': c.created_at.isoformat(),
                        'population': c.population,
                        'generation_max': c.generation_max,
                        'knowledge_entries': c.knowledge_entries,
                        'health_average': c.health_average,
                        'specializations': c.specializations,
                        'allied_colonies': list(c.allied_colonies)
                    }
                    for c in self.colonies.values()
                ],
                'total_migrations': len(self.migration_history),
                'total_gene_transfers': len(self.gene_transfers)
            }
            
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save ecosystem state: {e}")
            
    def register_colony(self, colony_id: str, project_path: str) -> ColonyInfo:
        """Register a new colony in the ecosystem"""
        with self._lock:
            if colony_id not in self.colonies:
                colony = ColonyInfo(
                    colony_id=colony_id,
                    project_path=project_path,
                    created_at=datetime.now()
                )
                self.colonies[colony_id] = colony
                self._save_ecosystem_state()
                logger.info(f"Registered colony: {colony_id}")
                
            return self.colonies[colony_id]
            
    def update_colony_stats(
        self, 
        colony_id: str,
        population: int,
        generation_max: int,
        knowledge_entries: int,
        health_average: float
    ):
        """Update colony statistics"""
        with self._lock:
            if colony_id in self.colonies:
                colony = self.colonies[colony_id]
                colony.population = population
                colony.generation_max = generation_max
                colony.knowledge_entries = knowledge_entries
                colony.health_average = health_average
                
    def establish_alliance(self, colony1: str, colony2: str):
        """Establish alliance between colonies"""
        with self._lock:
            if colony1 in self.colonies and colony2 in self.colonies:
                self.colonies[colony1].allied_colonies.add(colony2)
                self.colonies[colony2].allied_colonies.add(colony1)
                logger.info(f"Alliance established: {colony1} <-> {colony2}")
                
    def check_migration_allowed(
        self,
        source_colony: str,
        target_colony: str,
        agent_health: float
    ) -> Tuple[bool, str]:
        """Check if migration is allowed"""
        # Health check
        if agent_health < self.migration_rules['min_health']:
            return False, f"Agent health too low: {agent_health}"
            
        # Alliance check (optional)
        source = self.colonies.get(source_colony)
        target = self.colonies.get(target_colony)
        
        if not source or not target:
            return False, "Invalid colony"
            
        # Population balance check
        if target.population > 0:
            imbalance = abs(source.population - target.population) / max(source.population, target.population)
            if imbalance > self.migration_rules['max_population_imbalance']:
                return False, "Population imbalance too high"
                
        # Rate limiting
        recent_migrations = [
            m for m in self.migration_history[-50:]
            if (datetime.now() - m.timestamp).seconds < 3600
        ]
        if len(recent_migrations) >= self.migration_rules['max_migrations_per_hour']:
            return False, "Migration rate limit reached"
            
        return True, "Migration allowed"
        
    async def initiate_migration(
        self,
        agent: 'BioCodeAgent',
        target_colony_id: str,
        reason: str = "exploration"
    ) -> bool:
        """Initiate agent migration to another colony"""
        source_colony_id = f"{agent.project_path.name}_{id(agent.project_path)}"
        
        # Check if allowed
        allowed, message = self.check_migration_allowed(
            source_colony_id,
            target_colony_id,
            agent.health
        )
        
        if not allowed:
            logger.warning(f"Migration denied: {message}")
            return False
            
        # Prepare migration packet
        packet = MigrationPacket(
            agent_id=agent.dna.agent_id,
            source_colony=source_colony_id,
            target_colony=target_colony_id,
            dna=agent.dna,
            memory_snapshot={
                'files_scanned': list(agent.memory.files_scanned),
                'learned_patterns': dict(agent.memory.learned_patterns),
                'errors_detected': agent.memory.errors_detected[-10:],  # Recent errors
                'performance_metrics': agent.memory.performance_metrics[-10:]
            },
            knowledge=list(agent._colony_knowledge)[-20:],  # Recent knowledge
            timestamp=datetime.now(),
            reason=reason
        )
        
        # Queue for processing
        await self.migration_queue.put(packet)
        
        # Record migration
        self.migration_history.append(packet)
        
        # Agent enters dormant state
        agent._log_to_terminal(f"🚀 Migrating to colony {target_colony_id}", "info")
        agent.apoptosis(f"migration_to_{target_colony_id}")
        
        return True
        
    async def receive_migrant(
        self,
        packet: MigrationPacket,
        target_project_path: str
    ) -> Optional['BioCodeAgent']:
        """Receive and integrate migrant agent"""
        try:
            # Import after to avoid circular import
            from agent.biocode_agent import BioCodeAgent
            
            # Quarantine period
            await asyncio.sleep(self.migration_rules['quarantine_period'])
            
            # Create new agent with migrated DNA
            migrant_dna = packet.dna
            migrant_dna.agent_id = f"{packet.agent_id}_migrant"
            migrant_dna.generation += 1  # New generation in new colony
            
            # Create agent
            migrant = BioCodeAgent(
                project_path=target_project_path,
                dna=migrant_dna,
                sandbox_mode=True
            )
            
            # Restore memory
            migrant.memory.files_scanned.update(packet.memory_snapshot['files_scanned'])
            migrant.memory.learned_patterns.update(packet.memory_snapshot['learned_patterns'])
            
            # Share knowledge with new colony
            for knowledge in packet.knowledge:
                migrant._colony_knowledge.append({
                    **knowledge,
                    'migrant_source': packet.source_colony
                })
                
            # Log migration
            migrant._log_to_terminal(
                f"🌍 Migrated from {packet.source_colony}: {packet.reason}",
                "success"
            )
            
            # Start in new environment
            migrant.start()
            
            logger.info(f"Migrant {migrant_dna.agent_id} integrated successfully")
            return migrant
            
        except Exception as e:
            logger.error(f"Failed to receive migrant: {e}")
            return None
            
    def initiate_gene_transfer(
        self,
        source_agent: 'BioCodeAgent',
        target_colony_id: str,
        traits: List[str]
    ) -> bool:
        """Transfer genetic traits between colonies"""
        # Prepare genetic material
        gene_packet = {
            'mutation_rate': source_agent.dna.mutation_rate,
            'adaptation_speed': source_agent.dna.adaptation_speed,
            'scan_frequency': source_agent.dna.scan_frequency,
            'error_tolerance': source_agent.dna.error_tolerance
        }
        
        # Filter requested traits
        transferred_traits = {
            trait: gene_packet[trait]
            for trait in traits
            if trait in gene_packet
        }
        
        if not transferred_traits:
            return False
            
        # Record transfer
        transfer = GeneTransfer(
            source_agent=source_agent.dna.agent_id,
            target_agent=f"{target_colony_id}_recipient",
            traits=transferred_traits,
            timestamp=datetime.now()
        )
        
        self.gene_transfers.append(transfer)
        
        # Broadcast to target colony
        asyncio.create_task(
            self.broadcast_queue.put({
                'type': 'gene_transfer',
                'target_colony': target_colony_id,
                'transfer': transfer
            })
        )
        
        return True
        
    def apply_gene_transfer(
        self,
        recipient_agent: 'BioCodeAgent',
        transfer: GeneTransfer
    ) -> bool:
        """Apply received genetic traits"""
        try:
            # Apply traits with some mutation
            import random
            
            for trait, value in transfer.traits.items():
                if hasattr(recipient_agent.dna, trait):
                    # Apply with slight mutation
                    mutation_factor = random.uniform(0.9, 1.1)
                    
                    if isinstance(value, (int, float)):
                        new_value = value * mutation_factor
                    else:
                        new_value = value
                        
                    setattr(recipient_agent.dna, trait, new_value)
                    
            recipient_agent._log_to_terminal(
                f"🧬 Received genes from {transfer.source_agent}",
                "info"
            )
            
            transfer.success = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply gene transfer: {e}")
            return False
            
    def analyze_ecosystem_health(self) -> Dict[str, Any]:
        """Analyze overall ecosystem health"""
        with self._lock:
            if not self.colonies:
                return {'status': 'empty', 'health': 0}
                
            total_population = sum(c.population for c in self.colonies.values())
            avg_health = sum(c.health_average * c.population for c in self.colonies.values()) / total_population if total_population > 0 else 0
            
            # Genetic diversity (based on specializations)
            all_specializations = set()
            for colony in self.colonies.values():
                all_specializations.update(colony.specializations)
                
            diversity_score = len(all_specializations) / max(len(self.colonies), 1)
            
            # Migration flow
            recent_migrations = [
                m for m in self.migration_history[-100:]
                if (datetime.now() - m.timestamp).days < 7
            ]
            
            migration_matrix = defaultdict(lambda: defaultdict(int))
            for migration in recent_migrations:
                migration_matrix[migration.source_colony][migration.target_colony] += 1
                
            # Knowledge distribution
            knowledge_distribution = defaultdict(int)
            for entry in self.ecosystem_knowledge:
                if isinstance(entry, dict):
                    knowledge_distribution[entry.get('type', 'unknown')] += 1
                    
            return {
                'status': 'healthy' if avg_health > 70 else 'struggling',
                'total_colonies': len(self.colonies),
                'total_population': total_population,
                'average_health': avg_health,
                'max_generation': max(c.generation_max for c in self.colonies.values()) if self.colonies else 0,
                'genetic_diversity': diversity_score,
                'specializations': list(all_specializations),
                'migration_flow': dict(migration_matrix),
                'knowledge_types': dict(knowledge_distribution),
                'recent_migrations': len(recent_migrations),
                'total_gene_transfers': len(self.gene_transfers)
            }
            
    def find_optimal_migration_target(
        self,
        source_agent: 'BioCodeAgent',
        criteria: Dict[str, Any]
    ) -> Optional[str]:
        """Find optimal colony for migration based on criteria"""
        source_colony_id = f"{source_agent.project_path.name}_{id(source_agent.project_path)}"
        candidates = []
        
        with self._lock:
            for colony_id, colony in self.colonies.items():
                if colony_id == source_colony_id:
                    continue
                    
                score = 0
                
                # Population balance
                if criteria.get('balance_population'):
                    pop_diff = abs(colony.population - self.colonies[source_colony_id].population)
                    score += 100 / (1 + pop_diff)
                    
                # Specialization match
                if criteria.get('specialization'):
                    if criteria['specialization'] in colony.specializations:
                        score += 50
                        
                # Health factor
                score += colony.health_average
                
                # Alliance bonus
                if colony_id in self.colonies[source_colony_id].allied_colonies:
                    score += 30
                    
                candidates.append((colony_id, score))
                
        if not candidates:
            return None
            
        # Return highest scoring colony
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
        
    def start_coordinator(self):
        """Start ecosystem coordinator thread"""
        if self._running:
            return
            
        self._running = True
        self._coordinator_thread = threading.Thread(
            target=self._coordinator_loop,
            daemon=True
        )
        self._coordinator_thread.start()
        logger.info(f"Ecosystem coordinator started for {self.ecosystem_name}")
        
    def stop_coordinator(self):
        """Stop ecosystem coordinator"""
        self._running = False
        if self._coordinator_thread:
            self._coordinator_thread.join()
        self._save_ecosystem_state()
        logger.info("Ecosystem coordinator stopped")
        
    def _coordinator_loop(self):
        """Main coordinator loop"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        
        try:
            loop.run_until_complete(self._async_coordinator_loop())
        except Exception as e:
            logger.error(f"Coordinator loop error: {e}")
        finally:
            loop.close()
            
    async def _async_coordinator_loop(self):
        """Async coordinator operations"""
        while self._running:
            try:
                # Process migrations
                if not self.migration_queue.empty():
                    packet = await self.migration_queue.get()
                    logger.info(f"Processing migration: {packet.agent_id}")
                    # Migration handling would be done by target colony
                    
                # Process broadcasts
                if not self.broadcast_queue.empty():
                    broadcast = await self.broadcast_queue.get()
                    logger.info(f"Broadcasting: {broadcast['type']}")
                    # Broadcast handling
                    
                # Periodic ecosystem analysis
                if len(self.colonies) > 1:
                    health = self.analyze_ecosystem_health()
                    if health['average_health'] < 50:
                        logger.warning("Ecosystem health is low!")
                        
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Coordinator error: {e}")
                await asyncio.sleep(5)


# Global ecosystem instance
_global_ecosystem = None


def get_ecosystem(name: str = "default") -> EcosystemCoordinator:
    """Get or create ecosystem coordinator"""
    global _global_ecosystem
    if _global_ecosystem is None or _global_ecosystem.ecosystem_name != name:
        _global_ecosystem = EcosystemCoordinator(name)
        _global_ecosystem.start_coordinator()
    return _global_ecosystem


# Extension for BioCodeAgent
class MultiColonyMixin:
    """Mixin for multi-colony capabilities"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ecosystem = get_ecosystem()
        self.colony_id = f"{self.project_path.name}_{id(self.project_path)}"
        
        # Register with ecosystem
        self.ecosystem.register_colony(self.colony_id, str(self.project_path))
        
    def consider_migration(self) -> Optional[str]:
        """Consider migrating to another colony"""
        # Migration triggers
        if self.health < 30:
            # Poor health - seek better environment
            return self.ecosystem.find_optimal_migration_target(
                self,
                {'balance_population': True}
            )
            
        if len(self.memory.files_scanned) > 1000:
            # Experienced agent - share knowledge
            return self.ecosystem.find_optimal_migration_target(
                self,
                {'specialization': 'knowledge_sharing'}
            )
            
        if self.dna.generation > 5:
            # High generation - genetic diversity
            import random
            colonies = list(self.ecosystem.colonies.keys())
            colonies.remove(self.colony_id)
            if colonies:
                return random.choice(colonies)
                
        return None
        
    async def attempt_migration(self, target_colony: str):
        """Attempt to migrate to target colony"""
        success = await self.ecosystem.initiate_migration(
            self,
            target_colony,
            reason=f"gen_{self.dna.generation}_exploration"
        )
        
        if success:
            self._log_to_terminal(f"🌍 Migrating to {target_colony}", "info")
            
    def share_genes(self, traits: List[str], target_colony: Optional[str] = None):
        """Share genetic traits with other colonies"""
        if not target_colony:
            # Find allied colony
            colony_info = self.ecosystem.colonies.get(self.colony_id)
            if colony_info and colony_info.allied_colonies:
                target_colony = next(iter(colony_info.allied_colonies))
                
        if target_colony:
            success = self.ecosystem.initiate_gene_transfer(
                self,
                target_colony,
                traits
            )
            
            if success:
                self._log_to_terminal(
                    f"🧬 Shared genes with {target_colony}",
                    "info"
                )