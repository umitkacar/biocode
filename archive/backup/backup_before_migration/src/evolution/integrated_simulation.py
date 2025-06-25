"""
Integrated Digital Life Simulation - Advanced BioCode Evolution
"""
import os
import sys
import json
import random
import hashlib
import shutil
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import pickle
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnvironmentalConditions:
    """Dynamic environmental conditions affecting cell survival"""
    
    def __init__(self):
        self.temperature = 20.0  # Optimal around 20
        self.resource_level = 100.0  # Food/energy availability
        self.toxin_level = 0.0  # Environmental hazards
        self.radiation = 0.0  # Mutation inducer
        self.time_of_day = 0  # Affects metabolism (0-23)
        self.season = "spring"  # Affects reproduction
        
    def update(self, time_step: int):
        """Update environmental conditions over time"""
        # Temperature fluctuation
        self.temperature = 20 + 10 * np.sin(time_step * 0.1) + random.uniform(-2, 2)
        
        # Resource depletion and regeneration
        self.resource_level = max(0, min(100, 
            self.resource_level - random.uniform(0, 5) + random.uniform(0, 3)))
        
        # Random environmental events
        if random.random() < 0.05:  # 5% chance of toxin spike
            self.toxin_level = min(50, self.toxin_level + random.uniform(5, 15))
        else:
            self.toxin_level = max(0, self.toxin_level - 1)
        
        # Radiation bursts
        if random.random() < 0.02:  # 2% chance
            self.radiation = random.uniform(10, 30)
        else:
            self.radiation = max(0, self.radiation - 0.5)
        
        # Time progression
        self.time_of_day = (self.time_of_day + 1) % 24
        
        # Season change
        if time_step % 100 == 0:
            seasons = ["spring", "summer", "autumn", "winter"]
            current_idx = seasons.index(self.season)
            self.season = seasons[(current_idx + 1) % 4]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'temperature': self.temperature,
            'resource_level': self.resource_level,
            'toxin_level': self.toxin_level,
            'radiation': self.radiation,
            'time_of_day': self.time_of_day,
            'season': self.season
        }


class AdvancedGenome:
    """Enhanced genome with multiple chromosomes and epigenetics"""
    
    def __init__(self, chromosomes: Optional[Dict[str, List[float]]] = None):
        if chromosomes is None:
            # Initialize random genome
            self.chromosomes = {
                'metabolism': [random.uniform(0, 1) for _ in range(10)],
                'immunity': [random.uniform(0, 1) for _ in range(8)],
                'behavior': [random.uniform(0, 1) for _ in range(12)],
                'reproduction': [random.uniform(0, 1) for _ in range(6)],
                'adaptation': [random.uniform(0, 1) for _ in range(15)]
            }
        else:
            self.chromosomes = chromosomes
            
        self.epigenetic_marks = defaultdict(float)  # Gene expression modifiers
        self.mutation_history = []
        self.lineage_id = hashlib.md5(
            json.dumps(self.chromosomes, sort_keys=True).encode()
        ).hexdigest()[:8]
    
    def express_trait(self, trait: str) -> float:
        """Express a trait considering epigenetic modifications"""
        if trait not in self.chromosomes:
            return 0.5  # Default
            
        base_value = np.mean(self.chromosomes[trait])
        epigenetic_modifier = self.epigenetic_marks.get(trait, 0)
        
        # Epigenetics can modify expression ±50%
        return max(0, min(1, base_value * (1 + epigenetic_modifier * 0.5)))
    
    def mutate(self, radiation_level: float = 0) -> 'AdvancedGenome':
        """Create mutated copy with tracking"""
        new_chromosomes = {}
        mutations = []
        
        # Base mutation rate affected by radiation
        base_rate = 0.01 + (radiation_level / 1000)
        
        for chrom_name, genes in self.chromosomes.items():
            new_genes = []
            for i, gene in enumerate(genes):
                if random.random() < base_rate:
                    # Mutation occurs
                    mutation_size = random.gauss(0, 0.1)
                    new_gene = max(0, min(1, gene + mutation_size))
                    new_genes.append(new_gene)
                    mutations.append({
                        'chromosome': chrom_name,
                        'position': i,
                        'old_value': gene,
                        'new_value': new_gene,
                        'type': 'point_mutation'
                    })
                else:
                    new_genes.append(gene)
            
            # Chromosome-level mutations (duplications, deletions)
            if random.random() < base_rate / 10:
                if random.random() < 0.5 and len(new_genes) > 3:
                    # Deletion
                    del_pos = random.randint(0, len(new_genes) - 1)
                    del new_genes[del_pos]
                    mutations.append({
                        'chromosome': chrom_name,
                        'type': 'deletion',
                        'position': del_pos
                    })
                else:
                    # Duplication
                    dup_pos = random.randint(0, len(new_genes) - 1)
                    new_genes.insert(dup_pos, new_genes[dup_pos])
                    mutations.append({
                        'chromosome': chrom_name,
                        'type': 'duplication',
                        'position': dup_pos
                    })
            
            new_chromosomes[chrom_name] = new_genes
        
        # Create new genome
        child = AdvancedGenome(new_chromosomes)
        child.mutation_history = self.mutation_history.copy()
        child.mutation_history.extend(mutations)
        child.epigenetic_marks = self.epigenetic_marks.copy()
        
        return child
    
    def crossover(self, other: 'AdvancedGenome') -> 'AdvancedGenome':
        """Sexual reproduction with recombination"""
        new_chromosomes = {}
        
        for chrom_name in self.chromosomes:
            if chrom_name in other.chromosomes:
                # Perform crossover
                parent1_genes = self.chromosomes[chrom_name]
                parent2_genes = other.chromosomes[chrom_name]
                
                # Ensure same length
                min_len = min(len(parent1_genes), len(parent2_genes))
                
                # Random crossover points
                crossover_points = sorted([0] + 
                    [random.randint(1, min_len-1) for _ in range(random.randint(1, 3))] + 
                    [min_len])
                
                new_genes = []
                use_parent1 = True
                
                for i in range(len(crossover_points) - 1):
                    start, end = crossover_points[i], crossover_points[i + 1]
                    if use_parent1:
                        new_genes.extend(parent1_genes[start:end])
                    else:
                        new_genes.extend(parent2_genes[start:end])
                    use_parent1 = not use_parent1
                
                new_chromosomes[chrom_name] = new_genes
            else:
                # No matching chromosome in other parent
                new_chromosomes[chrom_name] = self.chromosomes[chrom_name].copy()
        
        child = AdvancedGenome(new_chromosomes)
        child.mutation_history = []  # Fresh start for new individual
        
        # Inherit some epigenetic marks from parents
        for mark, value in self.epigenetic_marks.items():
            if random.random() < 0.5:
                child.epigenetic_marks[mark] = value * 0.8  # Diluted inheritance
        
        for mark, value in other.epigenetic_marks.items():
            if random.random() < 0.5:
                child.epigenetic_marks[mark] = value * 0.8
        
        return child


class AdvancedCell:
    """Enhanced cell with complex behaviors and memory"""
    
    def __init__(self, genome: AdvancedGenome, cell_id: Optional[str] = None):
        self.id = cell_id or hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
        self.genome = genome
        self.age = 0
        self.energy = 100.0
        self.health = 100.0
        self.memory = deque(maxlen=50)  # Remember last 50 experiences
        self.social_network = set()  # Connected cells
        self.position = (random.uniform(0, 100), random.uniform(0, 100))  # Spatial location
        self.alive = True
        self.offspring_count = 0
        self.generation = 0
        
        # Phenotype based on genome
        self._update_phenotype()
        
    def _update_phenotype(self):
        """Update cell characteristics based on genome"""
        self.metabolic_rate = self.genome.express_trait('metabolism')
        self.immunity = self.genome.express_trait('immunity')
        self.social_tendency = self.genome.express_trait('behavior')
        self.reproductive_threshold = 50 + 50 * self.genome.express_trait('reproduction')
        self.adaptation_speed = self.genome.express_trait('adaptation')
        
    def fitness(self, environment: EnvironmentalConditions) -> float:
        """Calculate fitness in current environment"""
        # Temperature tolerance
        optimal_temp = 20.0
        temp_tolerance = 10.0 * (1 + self.genome.express_trait('adaptation'))
        temp_fitness = np.exp(-((environment.temperature - optimal_temp) ** 2) / (2 * temp_tolerance ** 2))
        
        # Toxin resistance
        toxin_resistance = self.immunity
        toxin_fitness = 1.0 - (environment.toxin_level / 100) * (1 - toxin_resistance)
        
        # Energy efficiency
        energy_fitness = self.energy / 100.0
        
        # Social bonus
        social_bonus = 1.0 + 0.1 * len(self.social_network) if self.social_tendency > 0.5 else 1.0
        
        # Time of day adaptation (nocturnal vs diurnal)
        circadian_trait = self.genome.express_trait('behavior')
        if circadian_trait > 0.7:  # Nocturnal
            time_fitness = 1.0 if environment.time_of_day >= 20 or environment.time_of_day <= 4 else 0.8
        elif circadian_trait < 0.3:  # Diurnal
            time_fitness = 1.0 if 6 <= environment.time_of_day <= 18 else 0.8
        else:  # Flexible
            time_fitness = 0.9
        
        # Combine all factors
        total_fitness = temp_fitness * toxin_fitness * energy_fitness * social_bonus * time_fitness
        
        return max(0, min(1, total_fitness))
    
    def metabolize(self, environment: EnvironmentalConditions):
        """Use energy based on metabolic rate and activities"""
        # Base metabolism
        energy_cost = 1 + 2 * self.metabolic_rate
        
        # Environmental stress costs
        if abs(environment.temperature - 20) > 10:
            energy_cost += 0.5
        
        if environment.toxin_level > 20:
            energy_cost += 0.3
            self.health -= environment.toxin_level * 0.01 * (1 - self.immunity)
        
        # Social interaction cost/benefit
        if self.social_network:
            if self.social_tendency > 0.7:
                energy_cost -= 0.2  # Cooperation benefit
            else:
                energy_cost += 0.1  # Competition cost
        
        self.energy -= energy_cost
        
        # Consume resources
        if environment.resource_level > 0:
            consumption = min(5 * self.metabolic_rate, environment.resource_level)
            self.energy += consumption
            environment.resource_level -= consumption * 0.1  # Depletion
        
        # Death conditions
        if self.energy <= 0 or self.health <= 0 or self.age > 100 + 50 * self.genome.express_trait('adaptation'):
            self.alive = False
    
    def interact_with(self, other: 'AdvancedCell', environment: EnvironmentalConditions):
        """Social interaction between cells"""
        distance = np.sqrt((self.position[0] - other.position[0])**2 + 
                          (self.position[1] - other.position[1])**2)
        
        if distance > 10:  # Too far to interact
            return
        
        # Form social connection
        if self.social_tendency > 0.5 and other.social_tendency > 0.5:
            self.social_network.add(other.id)
            other.social_network.add(self.id)
            
            # Share resources if cooperative
            if self.social_tendency > 0.8 and other.social_tendency > 0.8:
                avg_energy = (self.energy + other.energy) / 2
                self.energy = avg_energy
                other.energy = avg_energy
                
                # Share knowledge (epigenetic transfer)
                shared_experience = f"cooperation_at_temp_{environment.temperature:.1f}"
                self.memory.append(shared_experience)
                other.memory.append(shared_experience)
        
        # Competition if aggressive
        elif self.social_tendency < 0.3 or other.social_tendency < 0.3:
            # Fight for resources
            if self.energy > other.energy:
                transfer = min(10, other.energy * 0.2)
                self.energy += transfer
                other.energy -= transfer
                other.health -= 5
    
    def reproduce(self, partner: Optional['AdvancedCell'] = None, 
                  environment: EnvironmentalConditions = None) -> Optional['AdvancedCell']:
        """Reproduction with optional sexual/asexual modes"""
        if not self.alive or self.energy < self.reproductive_threshold:
            return None
        
        # Season affects reproduction success
        season_bonus = {
            'spring': 1.2,
            'summer': 1.0,
            'autumn': 0.8,
            'winter': 0.5
        }
        
        if environment and random.random() > season_bonus.get(environment.season, 1.0):
            return None  # Failed due to season
        
        # Energy cost
        self.energy -= 30
        
        # Create offspring
        if partner and partner.alive:
            # Sexual reproduction
            child_genome = self.genome.crossover(partner.genome)
            partner.energy -= 20
        else:
            # Asexual reproduction
            child_genome = self.genome.mutate(
                environment.radiation if environment else 0
            )
        
        # Environmental effects on mutation
        if environment and environment.radiation > 10:
            child_genome = child_genome.mutate(environment.radiation)
        
        child = AdvancedCell(child_genome)
        child.generation = self.generation + 1
        child.position = (
            self.position[0] + random.uniform(-5, 5),
            self.position[1] + random.uniform(-5, 5)
        )
        
        # Inherit some memories (cultural transmission)
        if self.memory:
            for _ in range(min(5, len(self.memory))):
                child.memory.append(random.choice(list(self.memory)))
        
        self.offspring_count += 1
        
        # Epigenetic changes based on parent's experience
        if environment:
            if environment.temperature > 25:
                child.genome.epigenetic_marks['metabolism'] += 0.1
            elif environment.temperature < 15:
                child.genome.epigenetic_marks['metabolism'] -= 0.1
            
            if environment.toxin_level > 30:
                child.genome.epigenetic_marks['immunity'] += 0.2
        
        return child
    
    def move(self):
        """Cell movement in 2D space"""
        # Movement influenced by social tendency
        if self.social_network and self.social_tendency > 0.5:
            # Move towards social connections (simplified)
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
        else:
            # Random walk
            dx = random.uniform(-2, 2)
            dy = random.uniform(-2, 2)
        
        self.position = (
            max(0, min(100, self.position[0] + dx)),
            max(0, min(100, self.position[1] + dy))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize cell state"""
        return {
            'id': self.id,
            'age': self.age,
            'energy': self.energy,
            'health': self.health,
            'alive': self.alive,
            'generation': self.generation,
            'position': self.position,
            'offspring_count': self.offspring_count,
            'genome_summary': {
                'metabolic_rate': self.metabolic_rate,
                'immunity': self.immunity,
                'social_tendency': self.social_tendency
            },
            'memory_size': len(self.memory),
            'social_connections': len(self.social_network)
        }


class SimulationSandbox:
    """Secure sandbox for running cell code"""
    
    def __init__(self, sandbox_dir: Optional[Path] = None):
        self.sandbox_dir = sandbox_dir or Path(tempfile.mkdtemp(prefix="biocode_sandbox_"))
        self.processes = []
        logger.info(f"Created sandbox at {self.sandbox_dir}")
    
    def execute_cell_code(self, code: str, timeout: int = 5) -> Tuple[bool, str]:
        """Execute cell code in isolated environment"""
        # Create temporary file
        cell_file = self.sandbox_dir / f"cell_{random.randint(1000, 9999)}.py"
        
        try:
            with open(cell_file, 'w') as f:
                f.write(code)
            
            # Execute with timeout and resource limits
            result = subprocess.run(
                [sys.executable, str(cell_file)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.sandbox_dir)
            )
            
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            
            return success, output
            
        except subprocess.TimeoutExpired:
            return False, "Execution timeout"
        except Exception as e:
            return False, str(e)
        finally:
            # Clean up
            if cell_file.exists():
                cell_file.unlink()
    
    def cleanup(self):
        """Remove sandbox directory"""
        if self.sandbox_dir.exists():
            shutil.rmtree(self.sandbox_dir)
            logger.info(f"Cleaned up sandbox at {self.sandbox_dir}")


class PopulationTracker:
    """Track population genetics and history"""
    
    def __init__(self):
        self.genome_history = []
        self.allele_frequencies = defaultdict(lambda: defaultdict(list))
        self.lineages = defaultdict(list)
        self.extinction_events = []
        
    def record_generation(self, population: List[AdvancedCell], generation: int):
        """Record genetic diversity metrics"""
        if not population:
            return
        
        # Genome diversity
        genomes = {}
        for cell in population:
            genome_hash = hashlib.md5(
                json.dumps(cell.genome.chromosomes, sort_keys=True).encode()
            ).hexdigest()
            genomes[genome_hash] = genomes.get(genome_hash, 0) + 1
        
        diversity = len(genomes) / len(population)
        
        # Allele frequencies for each chromosome
        for chrom_name in population[0].genome.chromosomes:
            allele_sums = defaultdict(float)
            allele_counts = defaultdict(int)
            
            for cell in population:
                if chrom_name in cell.genome.chromosomes:
                    for i, gene in enumerate(cell.genome.chromosomes[chrom_name]):
                        allele_sums[i] += gene
                        allele_counts[i] += 1
            
            # Calculate mean allele values
            for position in allele_sums:
                mean_value = allele_sums[position] / allele_counts[position]
                self.allele_frequencies[chrom_name][position].append(mean_value)
        
        # Track lineages
        for cell in population:
            self.lineages[cell.genome.lineage_id].append({
                'generation': generation,
                'cell_id': cell.id,
                'fitness': cell.energy * cell.health / 10000
            })
        
        self.genome_history.append({
            'generation': generation,
            'population_size': len(population),
            'unique_genomes': len(genomes),
            'diversity_index': diversity,
            'dominant_genome': max(genomes, key=genomes.get) if genomes else None
        })
    
    def detect_extinction(self, lineage_id: str, generation: int):
        """Record lineage extinction"""
        self.extinction_events.append({
            'lineage_id': lineage_id,
            'generation': generation,
            'total_individuals': len(self.lineages[lineage_id])
        })


class IntegratedLifeSimulation:
    """Complete integrated simulation with all features"""
    
    def __init__(self, 
                 initial_population: int = 50,
                 world_size: Tuple[float, float] = (100, 100),
                 enable_sandbox: bool = True):
        
        self.world_size = world_size
        self.environment = EnvironmentalConditions()
        self.population: List[AdvancedCell] = []
        self.generation = 0
        self.time_step = 0
        self.tracker = PopulationTracker()
        self.sandbox = SimulationSandbox() if enable_sandbox else None
        
        # Knowledge sharing system
        self.collective_knowledge = deque(maxlen=1000)
        self.pheromone_map = np.zeros(world_size)
        
        # Initialize population
        for _ in range(initial_population):
            cell = AdvancedCell(AdvancedGenome())
            self.population.append(cell)
        
        # Statistics
        self.stats_history = []
        
        logger.info(f"Initialized simulation with {initial_population} cells")
    
    def step(self):
        """Execute one simulation step"""
        self.time_step += 1
        
        # Update environment
        self.environment.update(self.time_step)
        
        # Cell actions
        random.shuffle(self.population)  # Random order
        
        new_cells = []
        dead_cells = []
        
        for cell in self.population:
            if not cell.alive:
                dead_cells.append(cell)
                continue
            
            # Age and metabolize
            cell.age += 1
            cell.metabolize(self.environment)
            
            # Movement
            cell.move()
            
            # Update pheromones
            x, y = int(cell.position[0]), int(cell.position[1])
            if 0 <= x < self.world_size[0] and 0 <= y < self.world_size[1]:
                self.pheromone_map[x, y] += cell.social_tendency
            
            # Social interactions
            nearby_cells = self._find_nearby_cells(cell, radius=10)
            for other in nearby_cells[:3]:  # Interact with up to 3 neighbors
                cell.interact_with(other, self.environment)
            
            # Learning from collective
            if random.random() < 0.1:  # 10% chance to learn
                self._learn_from_collective(cell)
            
            # Reproduction
            if cell.energy > cell.reproductive_threshold:
                if cell.social_tendency > 0.5 and nearby_cells:
                    # Sexual reproduction
                    partner = random.choice(nearby_cells)
                    child = cell.reproduce(partner, self.environment)
                else:
                    # Asexual reproduction
                    child = cell.reproduce(environment=self.environment)
                
                if child:
                    new_cells.append(child)
                    
                    # Share birth experience
                    self.collective_knowledge.append({
                        'type': 'birth',
                        'parent_fitness': cell.fitness(self.environment),
                        'environment': self.environment.to_dict(),
                        'genome_traits': {
                            'metabolism': child.metabolic_rate,
                            'immunity': child.immunity
                        }
                    })
            
            # Death handling
            if not cell.alive:
                dead_cells.append(cell)
                
                # Share death experience
                self.collective_knowledge.append({
                    'type': 'death',
                    'age': cell.age,
                    'cause': 'energy' if cell.energy <= 0 else 'health' if cell.health <= 0 else 'age',
                    'environment': self.environment.to_dict()
                })
        
        # Update population
        for cell in dead_cells:
            if cell in self.population:
                self.population.remove(cell)
                
                # Check for lineage extinction
                lineage_alive = any(c.genome.lineage_id == cell.genome.lineage_id 
                                  for c in self.population)
                if not lineage_alive:
                    self.tracker.detect_extinction(cell.genome.lineage_id, self.generation)
        
        self.population.extend(new_cells)
        
        # Natural selection (population cap)
        if len(self.population) > 200:
            # Keep fittest individuals
            self.population.sort(key=lambda c: c.fitness(self.environment), reverse=True)
            self.population = self.population[:200]
        
        # Decay pheromones
        self.pheromone_map *= 0.95
        
        # Generation tracking
        if self.time_step % 50 == 0:
            self.generation += 1
            self.tracker.record_generation(self.population, self.generation)
            self._record_statistics()
            logger.info(f"Generation {self.generation}: {len(self.population)} cells")
    
    def _find_nearby_cells(self, cell: AdvancedCell, radius: float) -> List[AdvancedCell]:
        """Find cells within radius of given cell"""
        nearby = []
        for other in self.population:
            if other.id != cell.id and other.alive:
                distance = np.sqrt((cell.position[0] - other.position[0])**2 + 
                                 (cell.position[1] - other.position[1])**2)
                if distance <= radius:
                    nearby.append(other)
        return nearby
    
    def _learn_from_collective(self, cell: AdvancedCell):
        """Cell learns from collective knowledge"""
        if not self.collective_knowledge:
            return
        
        # Sample recent knowledge
        recent_knowledge = list(self.collective_knowledge)[-10:]
        
        for knowledge in recent_knowledge:
            if knowledge['type'] == 'death' and knowledge['cause'] == 'energy':
                # Learn to be more efficient
                cell.genome.epigenetic_marks['metabolism'] -= 0.05
            elif knowledge['type'] == 'birth' and knowledge['parent_fitness'] > 0.8:
                # Learn from successful parents
                if 'genome_traits' in knowledge:
                    if knowledge['genome_traits']['metabolism'] < cell.metabolic_rate:
                        cell.genome.epigenetic_marks['metabolism'] -= 0.02
        
        # Update phenotype based on new epigenetic marks
        cell._update_phenotype()
    
    def _record_statistics(self):
        """Record population statistics"""
        if not self.population:
            return
        
        stats = {
            'generation': self.generation,
            'time_step': self.time_step,
            'population_size': len(self.population),
            'avg_age': np.mean([c.age for c in self.population]),
            'avg_energy': np.mean([c.energy for c in self.population]),
            'avg_health': np.mean([c.health for c in self.population]),
            'avg_generation': np.mean([c.generation for c in self.population]),
            'social_connections': sum(len(c.social_network) for c in self.population),
            'total_memory': sum(len(c.memory) for c in self.population),
            'environment': self.environment.to_dict(),
            'traits': {
                'metabolism': np.mean([c.metabolic_rate for c in self.population]),
                'immunity': np.mean([c.immunity for c in self.population]),
                'social': np.mean([c.social_tendency for c in self.population])
            }
        }
        
        self.stats_history.append(stats)
    
    def visualize_population(self, save_path: Optional[str] = None):
        """Create visualization of current population state"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # 1. Spatial distribution
        ax = axes[0, 0]
        positions = np.array([c.position for c in self.population if c.alive])
        if len(positions) > 0:
            colors = [c.metabolic_rate for c in self.population if c.alive]
            scatter = ax.scatter(positions[:, 0], positions[:, 1], 
                               c=colors, cmap='viridis', alpha=0.6)
            ax.set_title('Spatial Distribution (color=metabolism)')
            ax.set_xlim(0, self.world_size[0])
            ax.set_ylim(0, self.world_size[1])
            plt.colorbar(scatter, ax=ax)
        
        # 2. Population over time
        ax = axes[0, 1]
        if self.stats_history:
            generations = [s['generation'] for s in self.stats_history]
            pop_sizes = [s['population_size'] for s in self.stats_history]
            ax.plot(generations, pop_sizes, 'b-', linewidth=2)
            ax.set_xlabel('Generation')
            ax.set_ylabel('Population Size')
            ax.set_title('Population Dynamics')
            ax.grid(True)
        
        # 3. Trait evolution
        ax = axes[0, 2]
        if self.stats_history:
            traits = ['metabolism', 'immunity', 'social']
            for trait in traits:
                values = [s['traits'][trait] for s in self.stats_history]
                ax.plot(generations, values, label=trait, linewidth=2)
            ax.set_xlabel('Generation')
            ax.set_ylabel('Trait Value')
            ax.set_title('Trait Evolution')
            ax.legend()
            ax.grid(True)
        
        # 4. Environmental conditions
        ax = axes[1, 0]
        if self.stats_history:
            temps = [s['environment']['temperature'] for s in self.stats_history]
            resources = [s['environment']['resource_level'] for s in self.stats_history]
            ax2 = ax.twinx()
            ax.plot(generations, temps, 'r-', label='Temperature')
            ax2.plot(generations, resources, 'g-', label='Resources')
            ax.set_xlabel('Generation')
            ax.set_ylabel('Temperature', color='r')
            ax2.set_ylabel('Resources', color='g')
            ax.set_title('Environmental Conditions')
        
        # 5. Age distribution
        ax = axes[1, 1]
        ages = [c.age for c in self.population if c.alive]
        if ages:
            ax.hist(ages, bins=20, alpha=0.7, color='blue')
            ax.axvline(np.mean(ages), color='red', linestyle='--', 
                      label=f'Mean: {np.mean(ages):.1f}')
            ax.set_xlabel('Age')
            ax.set_ylabel('Count')
            ax.set_title('Age Distribution')
            ax.legend()
        
        # 6. Genetic diversity
        ax = axes[1, 2]
        if self.tracker.genome_history:
            diversity = [h['diversity_index'] for h in self.tracker.genome_history]
            gens = [h['generation'] for h in self.tracker.genome_history]
            ax.plot(gens, diversity, 'purple', linewidth=2)
            ax.set_xlabel('Generation')
            ax.set_ylabel('Diversity Index')
            ax.set_title('Genetic Diversity')
            ax.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150)
            logger.info(f"Saved visualization to {save_path}")
        else:
            plt.show()
    
    def save_state(self, filepath: str):
        """Save simulation state to file"""
        state = {
            'generation': self.generation,
            'time_step': self.time_step,
            'environment': self.environment.to_dict(),
            'population': [c.to_dict() for c in self.population],
            'stats_history': self.stats_history,
            'tracker': {
                'genome_history': self.tracker.genome_history,
                'extinction_events': self.tracker.extinction_events
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Saved simulation state to {filepath}")
    
    def generate_report(self) -> str:
        """Generate comprehensive simulation report"""
        if not self.population:
            return "No population data available"
        
        report = f"""
BioCode Integrated Life Simulation Report
========================================

Generation: {self.generation}
Time Steps: {self.time_step}
Current Population: {len(self.population)}

Environmental Conditions:
- Temperature: {self.environment.temperature:.1f}°C
- Resources: {self.environment.resource_level:.1f}%
- Toxins: {self.environment.toxin_level:.1f}%
- Radiation: {self.environment.radiation:.1f}
- Season: {self.environment.season}

Population Statistics:
- Average Age: {np.mean([c.age for c in self.population]):.1f}
- Average Energy: {np.mean([c.energy for c in self.population]):.1f}
- Average Health: {np.mean([c.health for c in self.population]):.1f}
- Total Offspring: {sum(c.offspring_count for c in self.population)}

Trait Averages:
- Metabolism: {np.mean([c.metabolic_rate for c in self.population]):.3f}
- Immunity: {np.mean([c.immunity for c in self.population]):.3f}
- Social Tendency: {np.mean([c.social_tendency for c in self.population]):.3f}

Social Network:
- Total Connections: {sum(len(c.social_network) for c in self.population)}
- Average Connections per Cell: {np.mean([len(c.social_network) for c in self.population]):.1f}

Genetic Diversity:
- Unique Lineages: {len(set(c.genome.lineage_id for c in self.population))}
- Extinction Events: {len(self.tracker.extinction_events)}

Collective Knowledge:
- Total Experiences: {len(self.collective_knowledge)}
- Recent Deaths: {sum(1 for k in list(self.collective_knowledge)[-100:] if k['type'] == 'death')}
- Recent Births: {sum(1 for k in list(self.collective_knowledge)[-100:] if k['type'] == 'birth')}
"""
        
        return report
    
    def run(self, steps: int = 1000, visualize_every: int = 100):
        """Run simulation for specified steps"""
        logger.info(f"Starting simulation for {steps} steps")
        
        for i in range(steps):
            self.step()
            
            # Periodic visualization
            if visualize_every > 0 and (i + 1) % visualize_every == 0:
                self.visualize_population(
                    save_path=f"simulation_gen_{self.generation}.png"
                )
            
            # Check for extinction
            if not self.population:
                logger.warning(f"Population extinct at step {i}")
                break
        
        # Final report
        print(self.generate_report())
        
        # Save final state
        self.save_state(f"simulation_final_gen_{self.generation}.json")
        
        # Cleanup sandbox if used
        if self.sandbox:
            self.sandbox.cleanup()


# Example usage
if __name__ == "__main__":
    # Create and run simulation
    sim = IntegratedLifeSimulation(
        initial_population=50,
        world_size=(100, 100),
        enable_sandbox=True
    )
    
    # Run for 500 steps with visualization every 100 steps
    sim.run(steps=500, visualize_every=100)
    
    # Create final visualization
    sim.visualize_population("final_population_state.png")