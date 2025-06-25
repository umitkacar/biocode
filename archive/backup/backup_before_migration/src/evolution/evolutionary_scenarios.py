"""
Evolutionary Scenarios - Disasters, Epidemics, and Selection Pressures
"""
import random
import numpy as np
from typing import Dict, List, Optional, Callable, Any, Tuple
from enum import Enum
from dataclasses import dataclass
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DisasterType(Enum):
    """Types of environmental disasters"""
    METEOR_IMPACT = "meteor"          # Instant mass extinction
    VOLCANIC_ERUPTION = "volcano"     # Long-term climate change
    ICE_AGE = "ice_age"              # Gradual cooling
    DROUGHT = "drought"               # Resource scarcity
    FLOOD = "flood"                   # Habitat destruction
    SOLAR_FLARE = "solar_flare"       # Radiation burst
    EARTHQUAKE = "earthquake"         # Physical disruption
    PANDEMIC = "pandemic"             # Disease outbreak
    TOXIC_BLOOM = "toxic_bloom"       # Chemical poisoning
    INVASIVE_SPECIES = "invasion"     # New predator/competitor


@dataclass
class Disaster:
    """A disaster event affecting the population"""
    disaster_type: DisasterType
    severity: float  # 0.0 to 1.0
    duration: int    # Time steps
    epicenter: Optional[Tuple[float, float]] = None
    radius: Optional[float] = None
    effects: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.effects is None:
            self.effects = self._default_effects()
    
    def _default_effects(self) -> Dict[str, Any]:
        """Get default effects for disaster type"""
        effects = {
            DisasterType.METEOR_IMPACT: {
                'instant_mortality': 0.5 + 0.4 * self.severity,
                'temperature_change': -20 * self.severity,
                'resource_destruction': 0.8 * self.severity,
                'mutation_rate_multiplier': 5.0
            },
            DisasterType.VOLCANIC_ERUPTION: {
                'instant_mortality': 0.1 + 0.2 * self.severity,
                'temperature_change': -10 * self.severity,
                'toxin_increase': 30 * self.severity,
                'light_reduction': 0.7 * self.severity
            },
            DisasterType.ICE_AGE: {
                'temperature_change': -15 * self.severity,
                'resource_reduction': 0.5 * self.severity,
                'metabolism_pressure': 'efficient'
            },
            DisasterType.DROUGHT: {
                'resource_reduction': 0.7 * self.severity,
                'water_scarcity': 0.9 * self.severity,
                'temperature_increase': 5 * self.severity
            },
            DisasterType.FLOOD: {
                'instant_mortality': 0.2 + 0.3 * self.severity,
                'habitat_destruction': 0.6 * self.severity,
                'movement_requirement': True
            },
            DisasterType.SOLAR_FLARE: {
                'radiation_increase': 50 * self.severity,
                'electronics_damage': 0.8 * self.severity,
                'mutation_rate_multiplier': 10.0
            },
            DisasterType.PANDEMIC: {
                'infection_rate': 0.3 + 0.5 * self.severity,
                'mortality_rate': 0.1 + 0.4 * self.severity,
                'immunity_advantage': True
            },
            DisasterType.TOXIC_BLOOM: {
                'toxin_increase': 40 * self.severity,
                'resource_contamination': 0.6 * self.severity,
                'immunity_pressure': True
            },
            DisasterType.INVASIVE_SPECIES: {
                'predation_pressure': 0.5 * self.severity,
                'competition_increase': 0.7 * self.severity,
                'behavior_pressure': 'defensive'
            }
        }
        
        return effects.get(self.disaster_type, {})


class SelectionPressure:
    """Specific selection pressure favoring certain traits"""
    
    def __init__(self, name: str, trait_preferences: Dict[str, float], 
                 strength: float = 1.0):
        self.name = name
        self.trait_preferences = trait_preferences  # trait -> optimal value
        self.strength = strength  # How strongly it affects fitness
        self.active = True
        self.generations_active = 0
        
    def calculate_fitness_modifier(self, traits: Dict[str, float]) -> float:
        """Calculate fitness modification based on traits"""
        if not self.active:
            return 1.0
            
        total_fitness = 0.0
        count = 0
        
        for trait, optimal in self.trait_preferences.items():
            if trait in traits:
                # Calculate deviation from optimal
                deviation = abs(traits[trait] - optimal)
                # Fitness decreases with deviation
                trait_fitness = 1.0 - deviation
                total_fitness += trait_fitness
                count += 1
        
        if count == 0:
            return 1.0
            
        # Average fitness across all relevant traits
        avg_fitness = total_fitness / count
        
        # Apply strength
        return 1.0 + (avg_fitness - 0.5) * self.strength
    
    def update(self):
        """Update pressure state"""
        if self.active:
            self.generations_active += 1


class Pathogen:
    """Disease agent for pandemic scenarios"""
    
    def __init__(self, name: str, virulence: float = 0.5, 
                 transmissibility: float = 0.5, lethality: float = 0.3):
        self.name = name
        self.virulence = virulence  # How easily it infects
        self.transmissibility = transmissibility  # How easily it spreads
        self.lethality = lethality  # Death rate if infected
        self.mutation_rate = 0.01
        self.infected_hosts = set()
        self.immune_hosts = set()
        self.strain_variants = [self]
        
    def attempt_infection(self, host_id: str, host_immunity: float) -> bool:
        """Try to infect a host"""
        if host_id in self.immune_hosts:
            return False
            
        if host_id in self.infected_hosts:
            return True  # Already infected
            
        # Infection chance based on virulence vs immunity
        infection_chance = self.virulence * (1 - host_immunity)
        
        if random.random() < infection_chance:
            self.infected_hosts.add(host_id)
            return True
            
        # Failed infection might grant immunity
        if random.random() < host_immunity:
            self.immune_hosts.add(host_id)
            
        return False
    
    def spread(self, contact_network: Dict[str, List[str]]) -> List[str]:
        """Spread to connected hosts"""
        new_infections = []
        
        for infected in list(self.infected_hosts):
            if infected in contact_network:
                for contact in contact_network[infected]:
                    if random.random() < self.transmissibility:
                        if contact not in self.infected_hosts and contact not in self.immune_hosts:
                            new_infections.append(contact)
        
        self.infected_hosts.update(new_infections)
        return new_infections
    
    def cause_mortality(self) -> List[str]:
        """Determine which infected hosts die"""
        deaths = []
        survivors = []
        
        for host in list(self.infected_hosts):
            if random.random() < self.lethality:
                deaths.append(host)
            else:
                survivors.append(host)
        
        # Remove dead hosts
        for host in deaths:
            self.infected_hosts.discard(host)
            
        # Some survivors gain immunity
        for host in survivors:
            if random.random() < 0.3:  # 30% chance to gain immunity
                self.infected_hosts.discard(host)
                self.immune_hosts.add(host)
                
        return deaths
    
    def mutate(self) -> Optional['Pathogen']:
        """Create mutated strain"""
        if random.random() < self.mutation_rate:
            new_strain = Pathogen(
                name=f"{self.name}_variant_{len(self.strain_variants)}",
                virulence=max(0, min(1, self.virulence + random.uniform(-0.1, 0.1))),
                transmissibility=max(0, min(1, self.transmissibility + random.uniform(-0.1, 0.1))),
                lethality=max(0, min(1, self.lethality + random.uniform(-0.1, 0.1)))
            )
            new_strain.mutation_rate = self.mutation_rate
            self.strain_variants.append(new_strain)
            return new_strain
        return None


class EvolutionaryScenario:
    """A complete evolutionary scenario with events and pressures"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.disasters: List[Tuple[int, Disaster]] = []  # (time, disaster)
        self.selection_pressures: List[SelectionPressure] = []
        self.pathogens: List[Pathogen] = []
        self.environmental_changes: List[Tuple[int, Dict[str, Any]]] = []
        self.milestone_events: Dict[int, str] = {}  # Generation -> event description
        
    def add_disaster(self, generation: int, disaster: Disaster):
        """Schedule a disaster"""
        self.disasters.append((generation, disaster))
        self.milestone_events[generation] = f"{disaster.disaster_type.value} strikes!"
        
    def add_selection_pressure(self, pressure: SelectionPressure):
        """Add ongoing selection pressure"""
        self.selection_pressures.append(pressure)
        
    def add_pathogen(self, pathogen: Pathogen, introduction_gen: int):
        """Introduce a pathogen"""
        self.pathogens.append(pathogen)
        self.milestone_events[introduction_gen] = f"Pathogen {pathogen.name} emerges"
        
    def add_environmental_change(self, generation: int, changes: Dict[str, Any]):
        """Schedule environmental change"""
        self.environmental_changes.append((generation, changes))
        
    def get_active_disasters(self, current_generation: int) -> List[Disaster]:
        """Get disasters active at current generation"""
        active = []
        for gen, disaster in self.disasters:
            if gen <= current_generation < gen + disaster.duration:
                active.append(disaster)
        return active
    
    def get_environmental_modifiers(self, current_generation: int) -> Dict[str, Any]:
        """Get all environmental modifications for current generation"""
        modifiers = {
            'temperature_change': 0,
            'resource_multiplier': 1.0,
            'toxin_increase': 0,
            'radiation_increase': 0,
            'mutation_rate_multiplier': 1.0
        }
        
        # Apply disaster effects
        for disaster in self.get_active_disasters(current_generation):
            for key, value in disaster.effects.items():
                if key in modifiers:
                    if 'multiplier' in key:
                        modifiers[key] *= value
                    elif 'change' in key or 'increase' in key:
                        modifiers[key] += value
                        
        # Apply scheduled changes
        for gen, changes in self.environmental_changes:
            if gen <= current_generation:
                modifiers.update(changes)
                
        return modifiers


class ScenarioLibrary:
    """Pre-defined evolutionary scenarios"""
    
    @staticmethod
    def create_kt_extinction() -> EvolutionaryScenario:
        """Cretaceous-Paleogene extinction event scenario"""
        scenario = EvolutionaryScenario(
            "K-T Extinction",
            "Asteroid impact causing mass extinction and climate change"
        )
        
        # Major impact
        impact = Disaster(
            disaster_type=DisasterType.METEOR_IMPACT,
            severity=0.9,
            duration=5,
            epicenter=(50, 50),
            radius=100
        )
        scenario.add_disaster(50, impact)
        
        # Following volcanic activity
        volcano = Disaster(
            disaster_type=DisasterType.VOLCANIC_ERUPTION,
            severity=0.7,
            duration=20
        )
        scenario.add_disaster(55, volcano)
        
        # Selection for small, adaptable organisms
        scenario.add_selection_pressure(SelectionPressure(
            "size_reduction",
            {'size': 0.3, 'metabolism': 0.7, 'reproduction': 0.8},
            strength=2.0
        ))
        
        return scenario
    
    @staticmethod
    def create_ice_age() -> EvolutionaryScenario:
        """Ice age with gradual cooling"""
        scenario = EvolutionaryScenario(
            "Ice Age",
            "Gradual global cooling with advancing glaciers"
        )
        
        # Gradual cooling
        for i in range(10):
            scenario.add_environmental_change(
                20 + i * 5,
                {'temperature_change': -2 * i}
            )
        
        # Ice age disaster
        ice_age = Disaster(
            disaster_type=DisasterType.ICE_AGE,
            severity=0.8,
            duration=50
        )
        scenario.add_disaster(70, ice_age)
        
        # Selection for cold adaptation
        scenario.add_selection_pressure(SelectionPressure(
            "cold_adaptation",
            {'metabolism': 0.3, 'insulation': 0.9, 'activity_level': 0.4},
            strength=1.5
        ))
        
        return scenario
    
    @staticmethod
    def create_pandemic_scenario() -> EvolutionaryScenario:
        """Disease outbreak scenario"""
        scenario = EvolutionaryScenario(
            "Great Plague",
            "Deadly pathogen spreads through population"
        )
        
        # Create pathogen
        plague = Pathogen(
            "BlackDeath",
            virulence=0.8,
            transmissibility=0.6,
            lethality=0.5
        )
        
        scenario.add_pathogen(plague, 30)
        
        # Pandemic disaster
        pandemic = Disaster(
            disaster_type=DisasterType.PANDEMIC,
            severity=0.8,
            duration=20
        )
        scenario.add_disaster(30, pandemic)
        
        # Selection for immunity
        scenario.add_selection_pressure(SelectionPressure(
            "disease_resistance",
            {'immunity': 0.9, 'social_tendency': 0.2},  # Less social = less transmission
            strength=3.0
        ))
        
        return scenario
    
    @staticmethod
    def create_cambrian_explosion() -> EvolutionaryScenario:
        """Rapid diversification scenario"""
        scenario = EvolutionaryScenario(
            "Cambrian Explosion",
            "Rapid evolutionary diversification with new ecological niches"
        )
        
        # Increase resources dramatically
        scenario.add_environmental_change(
            10,
            {'resource_multiplier': 3.0, 'temperature_change': 5}
        )
        
        # High mutation rate period
        scenario.add_environmental_change(
            15,
            {'mutation_rate_multiplier': 5.0}
        )
        
        # Multiple selection pressures for diversification
        scenario.add_selection_pressure(SelectionPressure(
            "vision_evolution",
            {'vision': 0.9, 'neural_complexity': 0.8},
            strength=1.0
        ))
        
        scenario.add_selection_pressure(SelectionPressure(
            "predator_evolution", 
            {'aggression': 0.8, 'speed': 0.7, 'vision': 0.8},
            strength=0.8
        ))
        
        scenario.add_selection_pressure(SelectionPressure(
            "armor_evolution",
            {'defense': 0.9, 'size': 0.6},
            strength=0.8
        ))
        
        return scenario
    
    @staticmethod
    def create_anthropocene() -> EvolutionaryScenario:
        """Human-caused environmental changes"""
        scenario = EvolutionaryScenario(
            "Anthropocene",
            "Rapid environmental change due to human activity"
        )
        
        # Gradual warming
        for i in range(20):
            scenario.add_environmental_change(
                10 + i * 2,
                {'temperature_change': 0.5 * i}
            )
        
        # Pollution events
        toxic = Disaster(
            disaster_type=DisasterType.TOXIC_BLOOM,
            severity=0.6,
            duration=30
        )
        scenario.add_disaster(30, toxic)
        
        # Habitat destruction
        scenario.add_environmental_change(
            40,
            {'resource_multiplier': 0.3, 'habitat_fragmentation': True}
        )
        
        # Selection for urban adaptation
        scenario.add_selection_pressure(SelectionPressure(
            "urban_adaptation",
            {'adaptability': 0.9, 'toxin_resistance': 0.8, 'size': 0.3},
            strength=2.0
        ))
        
        return scenario


class DisasterSimulator:
    """Simulates disaster effects on population"""
    
    def __init__(self):
        self.active_disasters: List[Disaster] = []
        self.disaster_history: List[Dict[str, Any]] = []
        
    def apply_disaster(self, disaster: Disaster, population: List[Any], 
                      environment: Any) -> Dict[str, Any]:
        """Apply disaster effects to population and environment"""
        results = {
            'deaths': [],
            'environment_changes': {},
            'population_effects': {}
        }
        
        effects = disaster.effects
        
        # Instant mortality
        if 'instant_mortality' in effects:
            mortality_rate = effects['instant_mortality']
            
            # Distance-based mortality if epicenter exists
            if disaster.epicenter and disaster.radius:
                for individual in population:
                    distance = np.sqrt(
                        (individual.position[0] - disaster.epicenter[0])**2 +
                        (individual.position[1] - disaster.epicenter[1])**2
                    )
                    
                    # Mortality decreases with distance
                    local_mortality = mortality_rate * max(0, 1 - distance / disaster.radius)
                    
                    if random.random() < local_mortality:
                        results['deaths'].append(individual)
            else:
                # Global mortality
                for individual in population:
                    if random.random() < mortality_rate:
                        results['deaths'].append(individual)
        
        # Environmental changes
        if 'temperature_change' in effects:
            results['environment_changes']['temperature'] = effects['temperature_change']
            
        if 'resource_reduction' in effects:
            results['environment_changes']['resources'] = -effects['resource_reduction']
            
        if 'toxin_increase' in effects:
            results['environment_changes']['toxins'] = effects['toxin_increase']
            
        if 'radiation_increase' in effects:
            results['environment_changes']['radiation'] = effects['radiation_increase']
        
        # Population-wide effects
        if 'mutation_rate_multiplier' in effects:
            results['population_effects']['mutation_rate'] = effects['mutation_rate_multiplier']
            
        # Record in history
        self.disaster_history.append({
            'type': disaster.disaster_type,
            'severity': disaster.severity,
            'deaths': len(results['deaths']),
            'timestamp': datetime.now()
        })
        
        logger.info(f"Disaster {disaster.disaster_type.value} caused {len(results['deaths'])} deaths")
        
        return results


# Example usage
if __name__ == "__main__":
    # Test scenarios
    print("Available Scenarios:")
    print("1. K-T Extinction")
    print("2. Ice Age") 
    print("3. Pandemic")
    print("4. Cambrian Explosion")
    print("5. Anthropocene")
    
    # Create K-T scenario
    kt_scenario = ScenarioLibrary.create_kt_extinction()
    print(f"\n{kt_scenario.name}: {kt_scenario.description}")
    print(f"Disasters scheduled: {len(kt_scenario.disasters)}")
    print(f"Selection pressures: {len(kt_scenario.selection_pressures)}")
    
    # Test disaster application
    simulator = DisasterSimulator()
    
    # Mock population
    class MockOrganism:
        def __init__(self):
            self.position = (random.uniform(0, 100), random.uniform(0, 100))
            self.immunity = random.uniform(0, 1)
    
    population = [MockOrganism() for _ in range(100)]
    
    # Apply meteor impact
    impact = kt_scenario.disasters[0][1]
    results = simulator.apply_disaster(impact, population, None)
    
    print(f"\nMeteor impact results:")
    print(f"Deaths: {len(results['deaths'])} / {len(population)}")
    print(f"Environmental changes: {results['environment_changes']}")