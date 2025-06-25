# BioCode Evolution API Reference

## Table of Contents
- [Digital Life API](#digital-life-api)
- [Sensory System API](#sensory-system-api)
- [Evolutionary Scenarios API](#evolutionary-scenarios-api)
- [Digital Ecosystem API](#digital-ecosystem-api)
- [Horizontal Gene Transfer API](#horizontal-gene-transfer-api)

---

## Digital Life API

### `class DigitalDNA`

Represents genetic information for digital organisms.

#### Constructor
```python
DigitalDNA(genes: Optional[Dict[str, Any]] = None)
```

**Parameters:**
- `genes` (dict, optional): Initial genetic values. If None, random genes are generated.

**Default genes:**
- `behavior`: 'aggressive', 'defensive', 'cooperative', or 'neutral'
- `metabolism`: 'fast', 'efficient', 'adaptive', or 'balanced'
- `reproduction`: 'mitosis', 'budding', 'fragmentation', or 'binary_fission'
- `resilience`: 0.1 to 1.0
- `mutation_rate`: 0.01 to 0.1
- `lifespan`: 10 to 100

#### Methods

##### `mutate() -> DigitalDNA`
Creates a mutated copy of the DNA.

**Returns:** New DigitalDNA instance with mutations

**Example:**
```python
mutated_dna = original_dna.mutate()
```

##### `crossover(other: DigitalDNA) -> DigitalDNA`
Performs sexual reproduction with another DNA.

**Parameters:**
- `other`: Another DigitalDNA instance

**Returns:** Child DigitalDNA with mixed genes

---

### `class SelfReplicatingCell`

Cell capable of self-replication with mutations.

#### Constructor
```python
SelfReplicatingCell(dna: Optional[DigitalDNA] = None)
```

#### Methods

##### `mitosis(save_to_file: bool = False) -> Optional[SelfReplicatingCell]`
Reproduce by cell division.

**Parameters:**
- `save_to_file`: If True, saves child as Python file

**Returns:** Child cell or None if too old/unhealthy

---

### `class ApoptoticCell`

Cell with programmed death capability.

#### Methods

##### `receive_death_signal(signal: str)`
Receive apoptosis signal. Three signals trigger death.

**Parameters:**
- `signal`: Description of death signal

##### `check_stress()`
Monitor system stress and trigger apoptosis if needed.

##### `programmed_death()`
Execute programmed cell death.

---

### `class EvolutionSimulator`

Main simulation controller for evolution.

#### Constructor
```python
EvolutionSimulator(initial_population: int = 10)
```

#### Methods

##### `run_simulation(generations: int = 10) -> List[Dict]`
Run evolution simulation.

**Parameters:**
- `generations`: Number of generations to simulate

**Returns:** History of generation statistics

---

## Sensory System API

### `class IntegratedSensorySystem`

Complete sensory system with multiple organs.

#### Constructor
```python
IntegratedSensorySystem(genome_traits: Dict[str, float])
```

**Parameters:**
- `genome_traits`: Dictionary of sensory capabilities (0-1 scale)
  - `vision`: Visual acuity
  - `chemoreception`: Chemical sensing
  - `touch`: Mechanoreception
  - `temperature`: Heat sensing
  - `neural_complexity`: Processing power

#### Methods

##### `perceive_environment(environment_state: Dict, cell_position: Tuple[float, float]) -> List[SensorySignal]`
Gather sensory information from environment.

**Parameters:**
- `environment_state`: Dictionary containing environmental data
- `cell_position`: (x, y) coordinates

**Returns:** List of SensorySignal objects

##### `process_integrated_perception(signals: List[SensorySignal]) -> Dict[str, Any]`
Integrate signals into unified perception.

**Returns:** Dictionary with:
- `threat_level`: 0.0 to 1.0
- `opportunity_level`: 0.0 to 1.0
- `movement_suggestion`: (dx, dy) vector
- `primary_focus`: 'escape', 'approach', or 'explore'
- `emotional_state`: Current emotional state

---

### `class SensorySignal`

Data class for sensory information.

#### Attributes
- `signal_type`: SensoryType enum
- `intensity`: Signal strength (0.0 to 1.0)
- `direction`: Optional (x, y) vector to source
- `source_id`: Optional identifier of source
- `data`: Optional dictionary of additional data

---

## Evolutionary Scenarios API

### `class Disaster`

Environmental disaster affecting population.

#### Constructor
```python
Disaster(
    disaster_type: DisasterType,
    severity: float,
    duration: int,
    epicenter: Optional[Tuple[float, float]] = None,
    radius: Optional[float] = None,
    effects: Optional[Dict[str, Any]] = None
)
```

**Parameters:**
- `disaster_type`: Type of disaster (enum)
- `severity`: Intensity (0.0 to 1.0)
- `duration`: Time steps disaster lasts
- `epicenter`: Optional center point
- `radius`: Optional effect radius
- `effects`: Optional custom effects

---

### `class SelectionPressure`

Ongoing selection favoring certain traits.

#### Constructor
```python
SelectionPressure(
    name: str,
    trait_preferences: Dict[str, float],
    strength: float = 1.0
)
```

#### Methods

##### `calculate_fitness_modifier(traits: Dict[str, float]) -> float`
Calculate fitness modification based on traits.

**Returns:** Fitness multiplier (typically 0.5 to 1.5)

---

### `class Pathogen`

Disease agent for pandemic scenarios.

#### Constructor
```python
Pathogen(
    name: str,
    virulence: float = 0.5,
    transmissibility: float = 0.5,
    lethality: float = 0.3
)
```

#### Methods

##### `attempt_infection(host_id: str, host_immunity: float) -> bool`
Try to infect a host.

##### `spread(contact_network: Dict[str, List[str]]) -> List[str]`
Spread to connected hosts.

##### `cause_mortality() -> List[str]`
Determine which infected hosts die.

---

### `class ScenarioLibrary`

Pre-built evolutionary scenarios.

#### Static Methods

##### `create_kt_extinction() -> EvolutionaryScenario`
Cretaceous-Paleogene extinction event.

##### `create_ice_age() -> EvolutionaryScenario`
Gradual global cooling scenario.

##### `create_pandemic_scenario() -> EvolutionaryScenario`
Disease outbreak scenario.

##### `create_cambrian_explosion() -> EvolutionaryScenario`
Rapid diversification scenario.

##### `create_anthropocene() -> EvolutionaryScenario`
Human-caused environmental change.

---

## Digital Ecosystem API

### `class Species`

Species definition in ecosystem.

#### Constructor
```python
Species(
    species_id: str,
    name: str,
    trophic_level: TrophicLevel,
    base_traits: Dict[str, float],
    diet_preferences: Optional[Dict[str, float]] = None,
    habitat_preferences: Optional[Dict[str, float]] = None,
    resource_requirements: Optional[Dict[str, float]] = None,
    carrying_capacity: float = 1000.0,
    growth_rate: float = 0.1,
    mortality_rate: float = 0.05,
    social_structure: str = "solitary",
    territorial: bool = False,
    migration_tendency: float = 0.0
)
```

#### Methods

##### `calculate_fitness(environment: Dict[str, Any]) -> float`
Calculate species fitness in environment.

---

### `class Ecosystem`

Complete ecosystem simulation.

#### Constructor
```python
Ecosystem(world_size: Tuple[float, float] = (200, 200))
```

#### Methods

##### `add_species(species: Species, initial_population: int = 10)`
Add species to ecosystem.

##### `establish_food_web()`
Automatically create predator-prey relationships.

##### `simulate_step()`
Run one time step of ecosystem dynamics.

##### `get_ecosystem_stats() -> Dict[str, Any]`
Get current ecosystem statistics.

**Returns:**
- `time_step`: Current simulation time
- `num_species`: Active species count
- `total_organisms`: Total organism count
- `species_populations`: Dict of populations by species
- `trophic_distribution`: Organisms by trophic level
- `total_biomass`: Combined biomass
- `resource_levels`: Average resource availability

---

### `class FoodWeb`

Manages predator-prey relationships.

#### Methods

##### `add_predation(predator: str, prey: str, strength: float = 1.0)`
Add predator-prey relationship.

##### `get_prey_options(predator: str) -> List[Tuple[str, float]]`
Get available prey with interaction strengths.

##### `get_predator_pressure(prey: str) -> float`
Calculate total predation pressure on species.

---

## Horizontal Gene Transfer API

### `class GeneticElement`

Transferable genetic element.

#### Constructor
```python
GeneticElement(
    element_id: str,
    element_type: str,
    source_species: str,
    code: str,
    metadata: Dict[str, Any],
    transfer_count: int = 0,
    fitness_impact: float = 0.0
)
```

**Parameters:**
- `element_type`: 'method', 'attribute', 'trait', or 'behavior'
- `code`: Actual code or JSON-encoded data

#### Methods

##### `is_compatible(target_class: type) -> bool`
Check if element can integrate into target.

---

### `class PlasmidVector`

Carrier for horizontal gene transfer.

#### Constructor
```python
PlasmidVector(vector_id: str, capacity: int = 5)
```

#### Methods

##### `add_element(element: GeneticElement) -> bool`
Add genetic element to plasmid.

##### `can_transfer_to(host: Any) -> bool`
Check transfer compatibility.

##### `integrate_into_host(host: Any) -> List[str]`
Integrate elements into host.

---

### `class ViralVector`

Virus-like agent for gene transfer.

#### Constructor
```python
ViralVector(virus_id: str, host_range: List[str])
```

#### Methods

##### `infect(host: Any) -> bool`
Attempt to infect host.

##### `replicate(host: Any) -> List[ViralVector]`
Replicate within host.

---

### `class HGTNetwork`

Network managing all gene transfers.

#### Methods

##### `conjugation(donor: Any, recipient: Any) -> bool`
Direct gene transfer via contact.

##### `transformation(organism: Any, environmental_dna: List[GeneticElement]) -> bool`
Uptake DNA from environment.

##### `transduction(virus: ViralVector, donor: Any, recipient: Any) -> bool`
Virus-mediated transfer.

##### `simulate_hgt_event(population: List[Any]) -> Dict[str, int]`
Simulate random HGT events.

**Returns:** Count of each transfer type

---

## Constants and Enums

### `SensoryType`
```python
VISION = "vision"
CHEMORECEPTION = "smell"
MECHANORECEPTION = "touch"
THERMORECEPTION = "heat"
ELECTRORECEPTION = "electric"
PROPRIOCEPTION = "position"
NOCICEPTION = "pain"
AUDITION = "hearing"
```

### `TrophicLevel`
```python
PRIMARY_PRODUCER = 1
PRIMARY_CONSUMER = 2
SECONDARY_CONSUMER = 3
TERTIARY_CONSUMER = 4
DECOMPOSER = 0
OMNIVORE = 2.5
```

### `InteractionType`
```python
PREDATION = "predation"
COMPETITION = "competition"
MUTUALISM = "mutualism"
COMMENSALISM = "commensalism"
PARASITISM = "parasitism"
NEUTRALISM = "neutralism"
```

### `DisasterType`
```python
METEOR_IMPACT = "meteor"
VOLCANIC_ERUPTION = "volcano"
ICE_AGE = "ice_age"
DROUGHT = "drought"
FLOOD = "flood"
SOLAR_FLARE = "solar_flare"
EARTHQUAKE = "earthquake"
PANDEMIC = "pandemic"
TOXIC_BLOOM = "toxic_bloom"
INVASIVE_SPECIES = "invasion"
```

---

## Error Handling

All methods may raise:
- `ValueError`: Invalid parameters
- `KeyError`: Missing required data
- `RuntimeError`: Simulation errors
- `MemoryError`: Population too large

Always wrap simulations in try-except blocks:

```python
try:
    ecosystem.simulate_step()
except RuntimeError as e:
    logger.error(f"Simulation failed: {e}")
```