"""
Digital Life System for BioCode - Real biological behaviors in code
"""
import os
import shutil
import random
import inspect
import importlib.util
import sys
import psutil
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import logging

try:
    from ..core.code_cell import CodeCell
    from ..utils.logging_config import get_logger
except ImportError:
    # Fallback for standalone execution
    import logging
    logging.basicConfig(level=logging.INFO)
    
    class CodeCell:
        """Minimal CodeCell for standalone execution"""
        def __init__(self, cell_type="basic", metadata=None):
            self.id = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
            self.cell_type = cell_type
            self.metadata = metadata or {}
            self.health = 100
            self.state = "healthy"
    
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)


class DigitalDNA:
    """Genetic information for code generation"""
    
    def __init__(self, genes: Optional[Dict[str, Any]] = None):
        self.genes = genes or {
            'behavior': random.choice(['aggressive', 'defensive', 'cooperative']),
            'metabolism': random.choice(['fast', 'efficient', 'adaptive']),
            'reproduction': random.choice(['mitosis', 'budding', 'fragmentation']),
            'resilience': random.uniform(0.1, 1.0),
            'mutation_rate': random.uniform(0.01, 0.1),
            'lifespan': random.randint(10, 100)
        }
        self.generation = 0
        self.lineage_id = hashlib.md5(str(self.genes).encode()).hexdigest()[:8]
    
    def mutate(self) -> 'DigitalDNA':
        """Create mutated copy of DNA"""
        new_genes = self.genes.copy()
        
        # Random mutations
        for gene, value in new_genes.items():
            if random.random() < new_genes.get('mutation_rate', 0.05):
                if isinstance(value, str):
                    # String mutations - pick from alternatives
                    alternatives = {
                        'behavior': ['aggressive', 'defensive', 'cooperative', 'neutral'],
                        'metabolism': ['fast', 'efficient', 'adaptive', 'balanced'],
                        'reproduction': ['mitosis', 'budding', 'fragmentation', 'binary_fission']
                    }
                    if gene in alternatives:
                        new_genes[gene] = random.choice(alternatives[gene])
                elif isinstance(value, (int, float)):
                    # Numeric mutations - small changes
                    new_genes[gene] = value * random.uniform(0.8, 1.2)
        
        new_dna = DigitalDNA(new_genes)
        new_dna.generation = self.generation + 1
        new_dna.lineage_id = self.lineage_id
        return new_dna
    
    def crossover(self, other: 'DigitalDNA') -> 'DigitalDNA':
        """Sexual reproduction - mix genes from two parents"""
        child_genes = {}
        for gene in self.genes:
            if gene in other.genes:
                # 50/50 chance from each parent
                child_genes[gene] = random.choice([self.genes[gene], other.genes[gene]])
            else:
                child_genes[gene] = self.genes[gene]
        
        child = DigitalDNA(child_genes)
        child.generation = max(self.generation, other.generation) + 1
        child.lineage_id = hashlib.md5(
            f"{self.lineage_id}+{other.lineage_id}".encode()
        ).hexdigest()[:8]
        return child


class SelfReplicatingCell(CodeCell):
    """A cell that can replicate itself with mutations"""
    
    def __init__(self, dna: Optional[DigitalDNA] = None):
        super().__init__(cell_type="replicating", metadata={})
        self.dna = dna or DigitalDNA()
        self.age = 0
        self.offspring_count = 0
        self.mutations = []
        self.fitness_score = 1.0
        
    def mitosis(self, save_to_file: bool = False) -> Optional['SelfReplicatingCell']:
        """Reproduce by cell division"""
        if self.age > self.dna.genes['lifespan']:
            logger.info(f"Cell {self.id} too old to reproduce")
            return None
            
        # Create child with mutated DNA
        child_dna = self.dna.mutate()
        child = SelfReplicatingCell(dna=child_dna)
        child.mutations = self.mutations.copy()
        child.mutations.append(f"gen_{self.dna.generation}_mutation")
        
        self.offspring_count += 1
        logger.info(f"Cell {self.id} reproduced. Child: {child.id}")
        
        # Optionally save to file system
        if save_to_file:
            self._save_to_file(child)
            
        return child
    
    def _save_to_file(self, child: 'SelfReplicatingCell'):
        """Save child cell as actual Python file"""
        cell_dir = Path("digital_life_forms")
        cell_dir.mkdir(exist_ok=True)
        
        filename = cell_dir / f"cell_{child.id}_{child.dna.generation}.py"
        
        code = f'''"""
Auto-generated digital life form
Generation: {child.dna.generation}
Lineage: {child.dna.lineage_id}
DNA: {json.dumps(child.dna.genes, indent=2)}
"""

from src.evolution.digital_life import SelfReplicatingCell, DigitalDNA

# This cell's DNA
dna = DigitalDNA({json.dumps(child.dna.genes)})

# Instantiate this cell
cell = SelfReplicatingCell(dna=dna)

if __name__ == "__main__":
    print(f"Cell {{cell.id}} is alive!")
    print(f"Behavior: {{cell.dna.genes['behavior']}}")
    print(f"Generation: {{cell.dna.generation}}")
'''
        
        with open(filename, 'w') as f:
            f.write(code)
        
        logger.info(f"Saved cell to {filename}")


class ApoptoticCell(SelfReplicatingCell):
    """A cell that can undergo programmed death"""
    
    def __init__(self, dna: Optional[DigitalDNA] = None):
        super().__init__(dna)
        self.death_signals = []
        self.stress_level = 0
        self._death_triggered = False
        
    def receive_death_signal(self, signal: str):
        """Receive apoptosis signal"""
        self.death_signals.append(signal)
        if len(self.death_signals) >= 3:  # Death threshold
            self.programmed_death()
    
    def check_stress(self):
        """Monitor stress and trigger apoptosis if needed"""
        # Check system resources
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent
        
        if cpu_percent > 90 or memory_percent > 90:
            self.stress_level += 1
            
        if self.stress_level > 5:
            logger.warning(f"Cell {self.id} under extreme stress")
            self.programmed_death()
    
    def programmed_death(self):
        """Execute programmed cell death"""
        if self._death_triggered:
            return
            
        self._death_triggered = True
        logger.info(f"Cell {self.id} initiating apoptosis")
        
        # Save genetic memory before death
        self._save_genetic_memory()
        
        # Clean up resources
        self.health = 0
        self.state = "dead"
        
        # If this cell has a file representation, delete it
        if hasattr(self, '__file__') and os.path.exists(self.__file__):
            try:
                os.remove(self.__file__)
                logger.info(f"Cell file {self.__file__} deleted")
            except Exception as e:
                logger.error(f"Could not delete cell file: {e}")
    
    def _save_genetic_memory(self):
        """Save important genetic information before death"""
        memory_dir = Path("genetic_memory")
        memory_dir.mkdir(exist_ok=True)
        
        memory_file = memory_dir / f"memory_{self.id}_{datetime.now().isoformat()}.json"
        
        memory_data = {
            'cell_id': self.id,
            'dna': self.dna.genes,
            'generation': self.dna.generation,
            'lineage': self.dna.lineage_id,
            'mutations': self.mutations,
            'death_time': datetime.now().isoformat(),
            'death_signals': self.death_signals,
            'offspring_count': self.offspring_count
        }
        
        with open(memory_file, 'w') as f:
            json.dump(memory_data, f, indent=2)
        
        logger.info(f"Genetic memory saved to {memory_file}")


class AdaptiveCell(ApoptoticCell):
    """A cell that adapts to its environment"""
    
    def __init__(self, dna: Optional[DigitalDNA] = None):
        super().__init__(dna)
        self.adaptations = []
        self.environment_history = []
        
    def sense_environment(self) -> Dict[str, Any]:
        """Sense current environment conditions"""
        env = {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'timestamp': datetime.now(),
            'process_count': len(psutil.pids())
        }
        
        self.environment_history.append(env)
        return env
    
    def adapt_to_environment(self):
        """Adapt behavior based on environment"""
        env = self.sense_environment()
        
        # High CPU - become more efficient
        if env['cpu_percent'] > 70:
            self.dna.genes['metabolism'] = 'efficient'
            self.adaptations.append('cpu_efficiency')
            logger.info(f"Cell {self.id} adapted to high CPU usage")
        
        # Low memory - reduce replication
        if env['memory_percent'] > 80:
            self.dna.genes['reproduction'] = 'budding'  # Less resource intensive
            self.adaptations.append('memory_conservation')
            logger.info(f"Cell {self.id} adapted to low memory")
        
        # Many processes - become cooperative
        if env['process_count'] > 100:
            self.dna.genes['behavior'] = 'cooperative'
            self.adaptations.append('cooperation')
            logger.info(f"Cell {self.id} adapted to crowded environment")
    
    def predict_future_state(self) -> str:
        """Predict future based on environment history"""
        if len(self.environment_history) < 3:
            return "insufficient_data"
        
        # Analyze trends
        cpu_trend = sum(h['cpu_percent'] for h in self.environment_history[-3:]) / 3
        mem_trend = sum(h['memory_percent'] for h in self.environment_history[-3:]) / 3
        
        if cpu_trend > 80 and mem_trend > 80:
            return "system_overload_predicted"
        elif cpu_trend < 30 and mem_trend < 30:
            return "resources_abundant"
        else:
            return "stable_environment"


class CollectiveIntelligence:
    """Shared consciousness for cell colony"""
    
    _shared_memory: Dict[str, Any] = {}
    _collective_knowledge: List[Dict[str, Any]] = []
    _pheromone_trails: Dict[str, float] = {}
    
    @classmethod
    def share_experience(cls, cell_id: str, experience: Dict[str, Any]):
        """Share experience with the colony"""
        knowledge = {
            'cell_id': cell_id,
            'experience': experience,
            'timestamp': datetime.now(),
            'importance': experience.get('importance', 1.0)
        }
        cls._collective_knowledge.append(knowledge)
        logger.info(f"Cell {cell_id} shared experience: {experience.get('type', 'unknown')}")
    
    @classmethod
    def learn_from_colony(cls, cell_id: str, max_items: int = 10) -> List[Dict[str, Any]]:
        """Learn from other cells' experiences"""
        # Get recent experiences from other cells
        others_knowledge = [
            k for k in cls._collective_knowledge 
            if k['cell_id'] != cell_id
        ]
        
        # Sort by importance and recency
        others_knowledge.sort(
            key=lambda x: (x['importance'], x['timestamp']), 
            reverse=True
        )
        
        return others_knowledge[:max_items]
    
    @classmethod
    def emit_pheromone(cls, signal_type: str, strength: float = 1.0):
        """Emit chemical signal for colony communication"""
        if signal_type not in cls._pheromone_trails:
            cls._pheromone_trails[signal_type] = 0
        
        cls._pheromone_trails[signal_type] += strength
        logger.info(f"Pheromone {signal_type} emitted: {strength}")
    
    @classmethod
    def sense_pheromones(cls) -> Dict[str, float]:
        """Sense current pheromone levels"""
        # Pheromones decay over time
        for signal in cls._pheromone_trails:
            cls._pheromone_trails[signal] *= 0.95  # 5% decay
            
        return cls._pheromone_trails.copy()


class HiveMindCell(AdaptiveCell):
    """Cell connected to collective intelligence"""
    
    def __init__(self, dna: Optional[DigitalDNA] = None):
        super().__init__(dna)
        self.learned_behaviors = []
        
    def share_discovery(self, discovery_type: str, data: Any):
        """Share important discovery with colony"""
        experience = {
            'type': discovery_type,
            'data': data,
            'dna': self.dna.genes,
            'importance': self.fitness_score
        }
        CollectiveIntelligence.share_experience(self.id, experience)
    
    def learn_from_others(self):
        """Learn successful strategies from other cells"""
        knowledge = CollectiveIntelligence.learn_from_colony(self.id)
        
        for item in knowledge:
            exp = item['experience']
            
            # Adopt successful behaviors
            if exp.get('type') == 'successful_adaptation':
                if 'behavior' in exp.get('dna', {}):
                    self.dna.genes['behavior'] = exp['dna']['behavior']
                    self.learned_behaviors.append(f"learned_{exp['dna']['behavior']}")
                    logger.info(f"Cell {self.id} learned behavior from {item['cell_id']}")
    
    def signal_danger(self, danger_type: str):
        """Alert colony to danger"""
        CollectiveIntelligence.emit_pheromone(f"danger_{danger_type}", strength=10.0)
        self.share_discovery('danger', {'type': danger_type, 'location': self.id})
    
    def respond_to_signals(self):
        """Respond to colony signals"""
        pheromones = CollectiveIntelligence.sense_pheromones()
        
        for signal, strength in pheromones.items():
            if signal.startswith('danger_') and strength > 5.0:
                # Fight or flight response
                if self.dna.genes['behavior'] == 'aggressive':
                    logger.info(f"Cell {self.id} preparing to fight")
                else:
                    logger.info(f"Cell {self.id} initiating escape")
            
            elif signal == 'food_found' and strength > 3.0:
                # Move towards food
                logger.info(f"Cell {self.id} moving towards food signal")


class EvolutionSimulator:
    """Simulate digital evolution"""
    
    def __init__(self, initial_population: int = 10):
        self.population: List[HiveMindCell] = []
        self.generation = 0
        self.history = []
        
        # Create initial population
        for _ in range(initial_population):
            self.population.append(HiveMindCell())
    
    def run_generation(self):
        """Run one generation of evolution"""
        self.generation += 1
        logger.info(f"=== Generation {self.generation} ===")
        
        # Each cell lives
        for cell in self.population[:]:  # Copy list to allow modification
            # Age cells
            cell.age += 1
            
            # Environmental pressure
            cell.adapt_to_environment()
            cell.check_stress()
            
            # Learn from colony
            cell.learn_from_others()
            cell.respond_to_signals()
            
            # Reproduction
            if cell.state == "healthy" and random.random() < 0.3:
                child = cell.mitosis()
                if child:
                    self.population.append(child)
            
            # Natural death
            if cell.age > cell.dna.genes['lifespan'] or cell.state == "dead":
                if cell in self.population:
                    self.population.remove(cell)
                    logger.info(f"Cell {cell.id} died naturally")
        
        # Record generation stats
        self.record_generation_stats()
        
        # Natural selection - remove least fit
        self.natural_selection()
    
    def natural_selection(self):
        """Remove least fit individuals if population too large"""
        max_population = 50
        
        if len(self.population) > max_population:
            # Sort by fitness
            self.population.sort(key=lambda c: c.fitness_score, reverse=True)
            
            # Keep only the fittest
            removed = self.population[max_population:]
            self.population = self.population[:max_population]
            
            for cell in removed:
                cell.programmed_death()
                logger.info(f"Natural selection removed cell {cell.id}")
    
    def record_generation_stats(self):
        """Record statistics for this generation"""
        if not self.population:
            return
            
        stats = {
            'generation': self.generation,
            'population_size': len(self.population),
            'avg_fitness': sum(c.fitness_score for c in self.population) / len(self.population),
            'behaviors': {},
            'metabolisms': {},
            'avg_generation': sum(c.dna.generation for c in self.population) / len(self.population)
        }
        
        # Count traits
        for cell in self.population:
            behavior = cell.dna.genes['behavior']
            metabolism = cell.dna.genes['metabolism']
            
            stats['behaviors'][behavior] = stats['behaviors'].get(behavior, 0) + 1
            stats['metabolisms'][metabolism] = stats['metabolisms'].get(metabolism, 0) + 1
        
        self.history.append(stats)
        logger.info(f"Generation {self.generation} stats: {stats}")
    
    def run_simulation(self, generations: int = 10):
        """Run evolution simulation"""
        logger.info(f"Starting evolution simulation for {generations} generations")
        
        for _ in range(generations):
            self.run_generation()
            
            if not self.population:
                logger.warning("Population extinct!")
                break
        
        logger.info("Simulation complete")
        return self.history


# Example usage
if __name__ == "__main__":
    # Create and test individual cells
    cell = HiveMindCell()
    cell.adapt_to_environment()
    
    # Share knowledge
    cell.share_discovery('food_source', {'location': 'north', 'amount': 100})
    
    # Run evolution simulation
    sim = EvolutionSimulator(initial_population=5)
    history = sim.run_simulation(generations=10)
    
    # Print final statistics
    if history:
        final = history[-1]
        print(f"Final generation: {final['generation']}")
        print(f"Population size: {final['population_size']}")
        print(f"Dominant behaviors: {final['behaviors']}")