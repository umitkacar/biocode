"""
Digital Ecosystem - Multiple Species Interactions
"""
import numpy as np
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import random
import math
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class TrophicLevel(Enum):
    """Trophic levels in the ecosystem"""
    PRIMARY_PRODUCER = 1    # Autotrophs (plants)
    PRIMARY_CONSUMER = 2    # Herbivores
    SECONDARY_CONSUMER = 3  # Carnivores
    TERTIARY_CONSUMER = 4   # Apex predators
    DECOMPOSER = 0         # Decomposers
    OMNIVORE = 2.5        # Can eat from multiple levels


class InteractionType(Enum):
    """Types of species interactions"""
    PREDATION = "predation"          # One eats the other
    COMPETITION = "competition"      # Compete for resources
    MUTUALISM = "mutualism"         # Both benefit
    COMMENSALISM = "commensalism"   # One benefits, other unaffected
    PARASITISM = "parasitism"       # One benefits at other's expense
    NEUTRALISM = "neutralism"       # No interaction


@dataclass
class Species:
    """A species in the ecosystem"""
    species_id: str
    name: str
    trophic_level: TrophicLevel
    base_traits: Dict[str, float]
    
    # Ecological characteristics
    diet_preferences: Dict[str, float] = field(default_factory=dict)  # prey_species -> preference
    habitat_preferences: Dict[str, float] = field(default_factory=dict)  # habitat_type -> preference
    resource_requirements: Dict[str, float] = field(default_factory=dict)  # resource -> amount
    
    # Population dynamics
    carrying_capacity: float = 1000.0
    growth_rate: float = 0.1
    mortality_rate: float = 0.05
    
    # Behavioral traits
    social_structure: str = "solitary"  # solitary, pack, herd, colony
    territorial: bool = False
    migration_tendency: float = 0.0
    
    # Evolutionary traits
    mutation_rate: float = 0.01
    generation_time: int = 10
    reproductive_strategy: str = "r-selected"  # r-selected or K-selected
    
    def __post_init__(self):
        # Set default diet based on trophic level
        if not self.diet_preferences:
            if self.trophic_level == TrophicLevel.PRIMARY_PRODUCER:
                self.diet_preferences = {"sunlight": 1.0, "nutrients": 0.5}
            elif self.trophic_level == TrophicLevel.PRIMARY_CONSUMER:
                self.diet_preferences = {"plants": 1.0}
            elif self.trophic_level == TrophicLevel.SECONDARY_CONSUMER:
                self.diet_preferences = {"herbivores": 1.0}
            elif self.trophic_level == TrophicLevel.DECOMPOSER:
                self.diet_preferences = {"dead_matter": 1.0}
    
    def calculate_fitness(self, environment: Dict[str, Any]) -> float:
        """Calculate species fitness in given environment"""
        fitness = 1.0
        
        # Temperature adaptation
        optimal_temp = self.base_traits.get('optimal_temperature', 20)
        temp_tolerance = self.base_traits.get('temperature_tolerance', 10)
        current_temp = environment.get('temperature', 20)
        
        temp_deviation = abs(current_temp - optimal_temp)
        if temp_deviation > temp_tolerance:
            fitness *= 0.5 ** ((temp_deviation - temp_tolerance) / 5)
        
        # Resource availability
        for resource, requirement in self.resource_requirements.items():
            available = environment.get(f'{resource}_availability', 1.0)
            fitness *= min(1.0, available / requirement)
        
        # Habitat suitability
        habitat_type = environment.get('habitat_type', 'mixed')
        habitat_preference = self.habitat_preferences.get(habitat_type, 0.5)
        fitness *= habitat_preference
        
        return max(0.01, fitness)  # Minimum fitness


@dataclass
class Organism:
    """Individual organism of a species"""
    organism_id: str
    species: Species
    position: Tuple[float, float]
    age: int = 0
    energy: float = 100.0
    health: float = 100.0
    size: float = 1.0
    
    # Genetic variation from species baseline
    trait_variations: Dict[str, float] = field(default_factory=dict)
    
    # Social connections
    pack_members: Set[str] = field(default_factory=set)
    territory: Optional[Tuple[Tuple[float, float], float]] = None  # (center, radius)
    
    # Memory and learning
    memory: List[Dict[str, Any]] = field(default_factory=list)
    learned_behaviors: Set[str] = field(default_factory=set)
    
    def get_trait(self, trait_name: str) -> float:
        """Get trait value including variations"""
        base_value = self.species.base_traits.get(trait_name, 0.5)
        variation = self.trait_variations.get(trait_name, 0)
        return max(0, min(1, base_value + variation))


class EcologicalNiche:
    """Represents an ecological niche in the ecosystem"""
    
    def __init__(self, niche_id: str, characteristics: Dict[str, Any]):
        self.niche_id = niche_id
        self.characteristics = characteristics
        self.occupied_by: Set[str] = set()  # Species IDs
        self.resource_pool: Dict[str, float] = {}
        self.capacity: float = characteristics.get('capacity', 100.0)
        
    def calculate_niche_overlap(self, species1: Species, species2: Species) -> float:
        """Calculate how much two species overlap in this niche"""
        overlap = 0.0
        factors = 0
        
        # Diet overlap
        common_prey = set(species1.diet_preferences.keys()) & set(species2.diet_preferences.keys())
        if common_prey:
            diet_overlap = sum(
                min(species1.diet_preferences[prey], species2.diet_preferences[prey])
                for prey in common_prey
            ) / len(common_prey)
            overlap += diet_overlap
            factors += 1
        
        # Habitat overlap
        common_habitats = set(species1.habitat_preferences.keys()) & set(species2.habitat_preferences.keys())
        if common_habitats:
            habitat_overlap = sum(
                min(species1.habitat_preferences[hab], species2.habitat_preferences[hab])
                for hab in common_habitats
            ) / len(common_habitats)
            overlap += habitat_overlap
            factors += 1
        
        # Resource overlap
        common_resources = set(species1.resource_requirements.keys()) & set(species2.resource_requirements.keys())
        if common_resources:
            resource_overlap = len(common_resources) / max(
                len(species1.resource_requirements),
                len(species2.resource_requirements)
            )
            overlap += resource_overlap
            factors += 1
        
        return overlap / factors if factors > 0 else 0.0
    
    def available_capacity(self) -> float:
        """Calculate remaining capacity in niche"""
        used = len(self.occupied_by) / 10.0  # Rough estimate
        return max(0, self.capacity - used)


class FoodWeb:
    """Manages predator-prey relationships"""
    
    def __init__(self):
        self.predator_prey: Dict[str, Set[str]] = defaultdict(set)  # predator -> prey species
        self.prey_predator: Dict[str, Set[str]] = defaultdict(set)  # prey -> predator species
        self.interaction_strengths: Dict[Tuple[str, str], float] = {}
        
    def add_predation(self, predator: str, prey: str, strength: float = 1.0):
        """Add predator-prey relationship"""
        self.predator_prey[predator].add(prey)
        self.prey_predator[prey].add(predator)
        self.interaction_strengths[(predator, prey)] = strength
        
    def get_prey_options(self, predator: str) -> List[Tuple[str, float]]:
        """Get available prey with interaction strengths"""
        prey_list = []
        for prey in self.predator_prey.get(predator, []):
            strength = self.interaction_strengths.get((predator, prey), 1.0)
            prey_list.append((prey, strength))
        return prey_list
    
    def get_predator_pressure(self, prey: str) -> float:
        """Calculate total predation pressure on species"""
        total_pressure = 0.0
        for predator in self.prey_predator.get(prey, []):
            strength = self.interaction_strengths.get((predator, prey), 1.0)
            total_pressure += strength
        return total_pressure
    
    def calculate_trophic_position(self, species_id: str, 
                                 species_trophic_levels: Dict[str, TrophicLevel]) -> float:
        """Calculate actual trophic position based on diet"""
        if species_id not in self.predator_prey:
            # No prey, must be primary producer
            return 1.0
            
        prey_positions = []
        for prey in self.predator_prey[species_id]:
            if prey in species_trophic_levels:
                prey_level = species_trophic_levels[prey].value
                prey_positions.append(prey_level)
        
        if prey_positions:
            return 1 + np.mean(prey_positions)
        return species_trophic_levels.get(species_id, TrophicLevel.PRIMARY_CONSUMER).value


class SymbioticNetwork:
    """Manages mutualistic and parasitic relationships"""
    
    def __init__(self):
        self.relationships: Dict[Tuple[str, str], InteractionType] = {}
        self.relationship_benefits: Dict[Tuple[str, str], Tuple[float, float]] = {}
        
    def add_relationship(self, species1: str, species2: str, 
                        interaction_type: InteractionType,
                        benefit1: float = 0.0, benefit2: float = 0.0):
        """Add symbiotic relationship"""
        key = tuple(sorted([species1, species2]))
        self.relationships[key] = interaction_type
        
        # Store benefits in consistent order
        if key[0] == species1:
            self.relationship_benefits[key] = (benefit1, benefit2)
        else:
            self.relationship_benefits[key] = (benefit2, benefit1)
    
    def get_symbiotic_fitness(self, species: str, partners: Set[str]) -> float:
        """Calculate fitness modification from symbiotic relationships"""
        total_benefit = 0.0
        
        for partner in partners:
            key = tuple(sorted([species, partner]))
            if key in self.relationships:
                benefits = self.relationship_benefits[key]
                if key[0] == species:
                    total_benefit += benefits[0]
                else:
                    total_benefit += benefits[1]
        
        return 1.0 + total_benefit


class Ecosystem:
    """Complete digital ecosystem with multiple species"""
    
    def __init__(self, world_size: Tuple[float, float] = (200, 200)):
        self.world_size = world_size
        self.species: Dict[str, Species] = {}
        self.populations: Dict[str, List[Organism]] = defaultdict(list)
        self.food_web = FoodWeb()
        self.symbiotic_network = SymbioticNetwork()
        self.niches: Dict[str, EcologicalNiche] = {}
        
        # Environmental state
        self.environment = {
            'temperature': 20.0,
            'humidity': 0.5,
            'light_level': 0.8,
            'nutrient_density': 1.0,
            'habitat_types': self._initialize_habitats()
        }
        
        # Ecosystem metrics
        self.time_step = 0
        self.extinction_events: List[Dict[str, Any]] = []
        self.invasion_events: List[Dict[str, Any]] = []
        self.species_history: Dict[str, List[int]] = defaultdict(list)
        
        # Resource pools
        self.resources = {
            'sunlight': np.ones(world_size) * 100,
            'nutrients': np.ones(world_size) * 50,
            'water': np.ones(world_size) * 75,
            'dead_matter': np.zeros(world_size)
        }
        
        logger.info(f"Initialized ecosystem with world size {world_size}")
    
    def _initialize_habitats(self) -> np.ndarray:
        """Create habitat type map"""
        habitat_map = np.zeros(self.world_size)
        
        # Create different habitat patches
        habitat_types = ['forest', 'grassland', 'wetland', 'desert', 'mountain']
        
        # Generate random habitat centers
        n_patches = 10
        for _ in range(n_patches):
            center_x = random.uniform(0, self.world_size[0])
            center_y = random.uniform(0, self.world_size[1])
            radius = random.uniform(20, 50)
            habitat_type = random.choice(range(len(habitat_types)))
            
            # Fill patch
            for x in range(int(max(0, center_x - radius)), 
                          int(min(self.world_size[0], center_x + radius))):
                for y in range(int(max(0, center_y - radius)),
                             int(min(self.world_size[1], center_y + radius))):
                    if (x - center_x)**2 + (y - center_y)**2 <= radius**2:
                        habitat_map[x, y] = habitat_type
        
        return habitat_map
    
    def add_species(self, species: Species, initial_population: int = 10):
        """Add a new species to the ecosystem"""
        self.species[species.species_id] = species
        
        # Create initial population
        for i in range(initial_population):
            organism = Organism(
                organism_id=f"{species.species_id}_{i}",
                species=species,
                position=(
                    random.uniform(0, self.world_size[0]),
                    random.uniform(0, self.world_size[1])
                ),
                trait_variations={
                    trait: random.gauss(0, 0.1)
                    for trait in species.base_traits
                }
            )
            self.populations[species.species_id].append(organism)
        
        logger.info(f"Added species {species.name} with {initial_population} individuals")
    
    def establish_food_web(self):
        """Automatically establish predator-prey relationships based on trophic levels"""
        for pred_id, predator in self.species.items():
            for prey_id, prey in self.species.items():
                if pred_id == prey_id:
                    continue
                    
                # Check if predation is possible based on trophic levels
                if predator.trophic_level.value > prey.trophic_level.value:
                    # Higher trophic level can eat lower
                    level_diff = predator.trophic_level.value - prey.trophic_level.value
                    
                    # Predation more likely between adjacent levels
                    if level_diff <= 2:
                        strength = 1.0 / level_diff
                        self.food_web.add_predation(pred_id, prey_id, strength)
    
    def simulate_step(self):
        """Simulate one time step of ecosystem dynamics"""
        self.time_step += 1
        
        # Update environment
        self._update_environment()
        
        # Process each species
        for species_id, organisms in list(self.populations.items()):
            if not organisms:
                continue
                
            species = self.species[species_id]
            
            # Species-level processes
            self._process_population_dynamics(species_id)
            self._process_resource_consumption(species_id)
            self._process_interactions(species_id)
            self._process_movement(species_id)
            self._process_reproduction(species_id)
            self._process_mortality(species_id)
        
        # Ecosystem-level processes
        self._process_resource_regeneration()
        self._check_extinctions()
        self._process_decomposition()
        self._update_metrics()
    
    def _update_environment(self):
        """Update environmental conditions"""
        # Seasonal variation
        season_phase = (self.time_step % 100) / 100 * 2 * np.pi
        self.environment['temperature'] = 20 + 10 * np.sin(season_phase)
        self.environment['light_level'] = 0.8 + 0.2 * np.sin(season_phase)
        
        # Random weather events
        if random.random() < 0.05:
            # Storm
            self.environment['humidity'] += random.uniform(0.1, 0.3)
            self.resources['water'] += np.random.uniform(10, 30, self.world_size)
    
    def _process_population_dynamics(self, species_id: str):
        """Handle population growth and regulation"""
        species = self.species[species_id]
        population = self.populations[species_id]
        current_size = len(population)
        
        if current_size == 0:
            return
        
        # Calculate effective carrying capacity
        fitness = species.calculate_fitness(self.environment)
        effective_capacity = species.carrying_capacity * fitness
        
        # Logistic growth
        growth = species.growth_rate * current_size * (1 - current_size / effective_capacity)
        
        # Competition effects
        total_competition = 0
        for other_id, other_pop in self.populations.items():
            if other_id != species_id:
                overlap = self._calculate_competition(species_id, other_id)
                total_competition += overlap * len(other_pop) / 100
        
        growth *= (1 - total_competition * 0.5)
        
        # Store growth for reproduction phase
        species._pending_growth = max(0, growth)
    
    def _calculate_competition(self, species1_id: str, species2_id: str) -> float:
        """Calculate competition coefficient between species"""
        species1 = self.species[species1_id]
        species2 = self.species[species2_id]
        
        # Competition based on niche overlap
        total_overlap = 0
        overlap_count = 0
        
        for niche in self.niches.values():
            if species1_id in niche.occupied_by and species2_id in niche.occupied_by:
                overlap = niche.calculate_niche_overlap(species1, species2)
                total_overlap += overlap
                overlap_count += 1
        
        if overlap_count > 0:
            return total_overlap / overlap_count
        
        # Default competition based on trophic level
        if species1.trophic_level == species2.trophic_level:
            return 0.5
        return 0.1
    
    def _process_resource_consumption(self, species_id: str):
        """Handle resource consumption by species"""
        species = self.species[species_id]
        organisms = self.populations[species_id]
        
        for organism in organisms:
            x, y = int(organism.position[0]), int(organism.position[1])
            
            # Consume based on trophic level
            if species.trophic_level == TrophicLevel.PRIMARY_PRODUCER:
                # Photosynthesize
                light = self.environment['light_level']
                nutrients = self.resources['nutrients'][x, y]
                
                energy_gain = min(light * 10, nutrients * 2)
                organism.energy += energy_gain
                self.resources['nutrients'][x, y] -= energy_gain * 0.1
                
            elif species.trophic_level == TrophicLevel.DECOMPOSER:
                # Consume dead matter
                dead_matter = self.resources['dead_matter'][x, y]
                consumption = min(dead_matter, 5)
                
                organism.energy += consumption * 2
                self.resources['dead_matter'][x, y] -= consumption
                self.resources['nutrients'][x, y] += consumption * 0.5
    
    def _process_interactions(self, species_id: str):
        """Process species interactions (predation, symbiosis)"""
        species = self.species[species_id]
        organisms = self.populations[species_id]
        
        for predator in organisms:
            if predator.energy < 50:  # Hungry
                # Look for prey
                prey_options = self.food_web.get_prey_options(species_id)
                
                for prey_species_id, strength in prey_options:
                    if prey_species_id not in self.populations:
                        continue
                        
                    prey_organisms = self.populations[prey_species_id]
                    
                    # Find nearby prey
                    for prey in prey_organisms:
                        distance = np.sqrt(
                            (predator.position[0] - prey.position[0])**2 +
                            (predator.position[1] - prey.position[1])**2
                        )
                        
                        # Hunting range based on size and speed
                        hunt_range = 5 + 5 * predator.get_trait('speed')
                        
                        if distance <= hunt_range:
                            # Attempt predation
                            hunt_success = self._attempt_predation(predator, prey)
                            
                            if hunt_success:
                                # Consume prey
                                predator.energy += prey.energy * 0.7
                                predator.memory.append({
                                    'event': 'successful_hunt',
                                    'prey': prey_species_id,
                                    'location': prey.position
                                })
                                
                                # Remove prey
                                prey_organisms.remove(prey)
                                
                                # Add to dead matter
                                x, y = int(prey.position[0]), int(prey.position[1])
                                self.resources['dead_matter'][x, y] += prey.size * 10
                                
                                break  # One kill per step
    
    def _attempt_predation(self, predator: Organism, prey: Organism) -> bool:
        """Determine if predation attempt succeeds"""
        # Success based on relative traits
        predator_score = (
            predator.get_trait('speed') * 0.3 +
            predator.get_trait('strength') * 0.3 +
            predator.get_trait('intelligence') * 0.2 +
            predator.size * 0.2
        )
        
        prey_score = (
            prey.get_trait('speed') * 0.4 +
            prey.get_trait('agility') * 0.3 +
            prey.get_trait('camouflage') * 0.2 +
            prey.get_trait('vigilance') * 0.1
        )
        
        # Random factor
        predator_score += random.uniform(-0.2, 0.2)
        prey_score += random.uniform(-0.2, 0.2)
        
        return predator_score > prey_score
    
    def _process_movement(self, species_id: str):
        """Handle organism movement"""
        species = self.species[species_id]
        organisms = self.populations[species_id]
        
        for organism in organisms:
            # Movement based on various factors
            move_vector = np.array([0.0, 0.0])
            
            # Random walk
            move_vector += np.random.randn(2) * 0.5
            
            # Territorial species stay near territory
            if species.territorial and organism.territory:
                center, radius = organism.territory
                to_center = np.array(center) - np.array(organism.position)
                if np.linalg.norm(to_center) > radius * 0.8:
                    move_vector += to_center * 0.1
            
            # Social species move towards pack
            if species.social_structure in ['pack', 'herd'] and organism.pack_members:
                pack_center = self._get_pack_center(species_id, organism.pack_members)
                if pack_center:
                    to_pack = np.array(pack_center) - np.array(organism.position)
                    move_vector += to_pack * 0.05
            
            # Apply movement
            speed = organism.get_trait('speed') * 2
            new_position = np.array(organism.position) + move_vector * speed
            
            # Keep in bounds
            new_position[0] = max(0, min(self.world_size[0], new_position[0]))
            new_position[1] = max(0, min(self.world_size[1], new_position[1]))
            
            organism.position = tuple(new_position)
    
    def _get_pack_center(self, species_id: str, pack_members: Set[str]) -> Optional[Tuple[float, float]]:
        """Get center position of pack members"""
        positions = []
        for member_id in pack_members:
            for organism in self.populations[species_id]:
                if organism.organism_id == member_id:
                    positions.append(organism.position)
                    break
        
        if positions:
            center_x = np.mean([p[0] for p in positions])
            center_y = np.mean([p[1] for p in positions])
            return (center_x, center_y)
        return None
    
    def _process_reproduction(self, species_id: str):
        """Handle reproduction"""
        species = self.species[species_id]
        organisms = self.populations[species_id]
        
        # Use pending growth from population dynamics
        growth = getattr(species, '_pending_growth', 0)
        offspring_count = int(growth)
        
        if offspring_count <= 0 or not organisms:
            return
        
        # Select parents based on fitness
        parent_weights = [o.energy * o.health / 10000 for o in organisms]
        if sum(parent_weights) == 0:
            return
            
        for _ in range(offspring_count):
            # Select parents
            parent1 = random.choices(organisms, weights=parent_weights)[0]
            parent2 = random.choices(organisms, weights=parent_weights)[0]
            
            # Create offspring
            offspring_id = f"{species_id}_{self.time_step}_{len(organisms) + _}"
            
            # Inherit traits with variation
            trait_variations = {}
            for trait in species.base_traits:
                parent_avg = (parent1.get_trait(trait) + parent2.get_trait(trait)) / 2
                variation = random.gauss(0, species.mutation_rate)
                trait_variations[trait] = parent_avg - species.base_traits[trait] + variation
            
            # Position near parents
            position = (
                (parent1.position[0] + parent2.position[0]) / 2 + random.uniform(-5, 5),
                (parent1.position[1] + parent2.position[1]) / 2 + random.uniform(-5, 5)
            )
            
            offspring = Organism(
                organism_id=offspring_id,
                species=species,
                position=position,
                trait_variations=trait_variations,
                energy=50,  # Start with half energy
                size=0.5   # Start small
            )
            
            # Inherit pack membership
            if species.social_structure in ['pack', 'herd']:
                offspring.pack_members = parent1.pack_members.copy()
                offspring.pack_members.add(parent1.organism_id)
                offspring.pack_members.add(parent2.organism_id)
            
            self.populations[species_id].append(offspring)
    
    def _process_mortality(self, species_id: str):
        """Handle death and removal of organisms"""
        species = self.species[species_id]
        organisms = self.populations[species_id]
        dead = []
        
        for organism in organisms:
            # Age-based mortality
            age_mortality = species.mortality_rate * (1 + organism.age / 100)
            
            # Energy depletion
            if organism.energy <= 0:
                dead.append(organism)
                continue
            
            # Health-based mortality
            if organism.health <= 0:
                dead.append(organism)
                continue
            
            # Stochastic mortality
            if random.random() < age_mortality:
                dead.append(organism)
                continue
            
            # Update age and energy
            organism.age += 1
            organism.energy -= 1 + organism.size  # Metabolic cost
            
            # Growth
            if organism.size < 1.0:
                organism.size = min(1.0, organism.size + 0.05)
        
        # Remove dead organisms
        for organism in dead:
            organisms.remove(organism)
            # Add to dead matter
            x, y = int(organism.position[0]), int(organism.position[1])
            self.resources['dead_matter'][x, y] += organism.size * organism.energy * 0.1
    
    def _process_resource_regeneration(self):
        """Regenerate renewable resources"""
        # Sunlight regenerates fully each step
        self.resources['sunlight'].fill(100 * self.environment['light_level'])
        
        # Nutrients regenerate slowly
        self.resources['nutrients'] += 0.1
        self.resources['nutrients'] = np.minimum(self.resources['nutrients'], 100)
        
        # Water from humidity
        self.resources['water'] += self.environment['humidity'] * 0.5
        self.resources['water'] = np.minimum(self.resources['water'], 100)
    
    def _process_decomposition(self):
        """Convert dead matter to nutrients"""
        # Decomposition rate depends on decomposer population
        decomposer_count = sum(
            len(pop) for sp_id, pop in self.populations.items()
            if self.species[sp_id].trophic_level == TrophicLevel.DECOMPOSER
        )
        
        decomp_rate = 0.01 + 0.001 * decomposer_count
        
        # Convert dead matter to nutrients
        converted = self.resources['dead_matter'] * decomp_rate
        self.resources['nutrients'] += converted * 0.8
        self.resources['dead_matter'] -= converted
    
    def _check_extinctions(self):
        """Check for species extinctions"""
        for species_id, organisms in list(self.populations.items()):
            if len(organisms) == 0:
                # Species extinct
                self.extinction_events.append({
                    'species': species_id,
                    'time': self.time_step,
                    'last_population': self.species_history[species_id][-1] if species_id in self.species_history else 0
                })
                
                del self.populations[species_id]
                logger.info(f"Species {self.species[species_id].name} went extinct at step {self.time_step}")
    
    def _update_metrics(self):
        """Update ecosystem metrics"""
        # Population sizes
        for species_id, organisms in self.populations.items():
            self.species_history[species_id].append(len(organisms))
    
    def get_ecosystem_stats(self) -> Dict[str, Any]:
        """Get current ecosystem statistics"""
        stats = {
            'time_step': self.time_step,
            'num_species': len(self.populations),
            'total_organisms': sum(len(pop) for pop in self.populations.values()),
            'extinctions': len(self.extinction_events),
            'species_populations': {
                sp_id: len(pop) for sp_id, pop in self.populations.items()
            },
            'trophic_distribution': self._get_trophic_distribution(),
            'total_biomass': sum(
                sum(org.size * org.energy for org in pop)
                for pop in self.populations.values()
            ),
            'resource_levels': {
                res: np.mean(values) for res, values in self.resources.items()
            }
        }
        
        return stats
    
    def _get_trophic_distribution(self) -> Dict[str, int]:
        """Get organism count by trophic level"""
        distribution = defaultdict(int)
        
        for species_id, organisms in self.populations.items():
            trophic = self.species[species_id].trophic_level.name
            distribution[trophic] += len(organisms)
        
        return dict(distribution)
    
    def visualize_ecosystem(self) -> Dict[str, np.ndarray]:
        """Generate visualization data for ecosystem state"""
        # Species distribution maps
        species_maps = {}
        
        for species_id, organisms in self.populations.items():
            species_map = np.zeros(self.world_size)
            
            for organism in organisms:
                x, y = int(organism.position[0]), int(organism.position[1])
                if 0 <= x < self.world_size[0] and 0 <= y < self.world_size[1]:
                    species_map[x, y] += 1
            
            species_maps[self.species[species_id].name] = species_map
        
        return {
            'species_distributions': species_maps,
            'resource_maps': self.resources,
            'habitat_map': self.environment['habitat_types']
        }


# Example species definitions
def create_example_ecosystem():
    """Create example ecosystem with multiple species"""
    ecosystem = Ecosystem()
    
    # Primary producers
    grass = Species(
        species_id="grass",
        name="Grass",
        trophic_level=TrophicLevel.PRIMARY_PRODUCER,
        base_traits={
            'growth_rate': 0.8,
            'drought_tolerance': 0.6,
            'nutrient_efficiency': 0.7
        },
        carrying_capacity=5000,
        growth_rate=0.2
    )
    
    tree = Species(
        species_id="tree",
        name="Tree",
        trophic_level=TrophicLevel.PRIMARY_PRODUCER,
        base_traits={
            'growth_rate': 0.3,
            'drought_tolerance': 0.8,
            'height': 0.9
        },
        carrying_capacity=1000,
        growth_rate=0.05
    )
    
    # Primary consumers
    rabbit = Species(
        species_id="rabbit",
        name="Rabbit",
        trophic_level=TrophicLevel.PRIMARY_CONSUMER,
        base_traits={
            'speed': 0.7,
            'reproduction_rate': 0.9,
            'vigilance': 0.6,
            'agility': 0.8
        },
        diet_preferences={"grass": 1.0},
        social_structure="warren",
        carrying_capacity=2000,
        growth_rate=0.3
    )
    
    deer = Species(
        species_id="deer",
        name="Deer",
        trophic_level=TrophicLevel.PRIMARY_CONSUMER,
        base_traits={
            'speed': 0.8,
            'strength': 0.6,
            'vigilance': 0.7,
            'size': 0.7
        },
        diet_preferences={"grass": 0.7, "tree": 0.3},
        social_structure="herd",
        carrying_capacity=500,
        growth_rate=0.1
    )
    
    # Secondary consumers
    fox = Species(
        species_id="fox",
        name="Fox",
        trophic_level=TrophicLevel.SECONDARY_CONSUMER,
        base_traits={
            'speed': 0.8,
            'intelligence': 0.9,
            'stealth': 0.8,
            'strength': 0.5
        },
        diet_preferences={"rabbit": 0.9, "deer": 0.1},
        social_structure="solitary",
        territorial=True,
        carrying_capacity=200,
        growth_rate=0.05
    )
    
    wolf = Species(
        species_id="wolf",
        name="Wolf",
        trophic_level=TrophicLevel.SECONDARY_CONSUMER,
        base_traits={
            'speed': 0.7,
            'strength': 0.8,
            'intelligence': 0.8,
            'pack_coordination': 0.9
        },
        diet_preferences={"deer": 0.8, "rabbit": 0.2},
        social_structure="pack",
        territorial=True,
        carrying_capacity=100,
        growth_rate=0.03
    )
    
    # Decomposer
    fungi = Species(
        species_id="fungi",
        name="Fungi",
        trophic_level=TrophicLevel.DECOMPOSER,
        base_traits={
            'decomposition_rate': 0.8,
            'nutrient_conversion': 0.9,
            'growth_rate': 0.7
        },
        carrying_capacity=10000,
        growth_rate=0.4
    )
    
    # Add species to ecosystem
    ecosystem.add_species(grass, 1000)
    ecosystem.add_species(tree, 200)
    ecosystem.add_species(rabbit, 300)
    ecosystem.add_species(deer, 100)
    ecosystem.add_species(fox, 20)
    ecosystem.add_species(wolf, 10)
    ecosystem.add_species(fungi, 2000)
    
    # Establish food web
    ecosystem.establish_food_web()
    
    # Add some symbiotic relationships
    ecosystem.symbiotic_network.add_relationship(
        "tree", "fungi",
        InteractionType.MUTUALISM,
        benefit1=0.1,  # Trees benefit from nutrient exchange
        benefit2=0.2   # Fungi benefit from tree sugars
    )
    
    return ecosystem


if __name__ == "__main__":
    # Create and test ecosystem
    eco = create_example_ecosystem()
    
    print("Initial Ecosystem State:")
    stats = eco.get_ecosystem_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Run simulation
    print("\nRunning simulation...")
    for i in range(10):
        eco.simulate_step()
        
        if i % 5 == 0:
            stats = eco.get_ecosystem_stats()
            print(f"\nStep {i}:")
            print(f"Species populations: {stats['species_populations']}")
            print(f"Total biomass: {stats['total_biomass']:.0f}")