# BioCode Evolution Module Documentation

## Overview

The Evolution module provides advanced digital life simulation capabilities, including:

- **Digital DNA and Mutations**: Genetic system with crossover and mutations
- **Sensory Perception**: Multi-modal sensory systems for digital organisms
- **Evolutionary Scenarios**: Disasters, selection pressures, and environmental changes
- **Digital Ecosystems**: Multi-species interactions with food webs
- **Horizontal Gene Transfer**: Gene sharing between organisms

## Table of Contents

1. [Digital Life System](#digital-life-system)
2. [Sensory Perception](#sensory-perception)
3. [Evolutionary Scenarios](#evolutionary-scenarios)
4. [Digital Ecosystem](#digital-ecosystem)
5. [Horizontal Gene Transfer](#horizontal-gene-transfer)
6. [Integration Examples](#integration-examples)

## Digital Life System

### Core Components

#### DigitalDNA
Represents genetic information for digital organisms.

```python
from src.evolution.digital_life import DigitalDNA

# Create DNA with specific genes
dna = DigitalDNA({
    'behavior': 'aggressive',
    'metabolism': 'fast',
    'mutation_rate': 0.05
})

# Mutate DNA
mutated_dna = dna.mutate()

# Sexual reproduction
child_dna = parent1_dna.crossover(parent2_dna)
```

#### Cell Types

**SelfReplicatingCell**: Basic cell capable of reproduction
```python
cell = SelfReplicatingCell(dna)
child = cell.mitosis(save_to_file=True)  # Can save to actual file
```

**ApoptoticCell**: Cell with programmed death
```python
cell = ApoptoticCell()
cell.receive_death_signal("DNA damage")
cell.receive_death_signal("Toxin")
cell.receive_death_signal("Energy depletion")  # Triggers apoptosis
```

**AdaptiveCell**: Environmentally responsive cell
```python
cell = AdaptiveCell()
cell.adapt_to_environment()  # Adjusts traits based on conditions
```

**HiveMindCell**: Collectively intelligent cell
```python
cell = HiveMindCell()
cell.share_discovery('food_source', {'location': 'north'})
cell.learn_from_others()  # Learns from colony
```

### Evolution Simulator

```python
from src.evolution.digital_life import EvolutionSimulator

sim = EvolutionSimulator(initial_population=50)
history = sim.run_simulation(generations=100)
```

## Sensory Perception

### Sensory Types

The system supports 8 sensory modalities:

1. **Vision**: Detect entities, colors, movement
2. **Chemoreception**: Smell/taste chemicals and pheromones
3. **Mechanoreception**: Touch, pressure, vibrations
4. **Thermoreception**: Temperature sensing
5. **Electroreception**: Electric field detection
6. **Proprioception**: Self-awareness, body position
7. **Nociception**: Pain/damage detection
8. **Audition**: Sound/vibration detection

### Usage Example

```python
from src.evolution.sensory_system import IntegratedSensorySystem

# Create sensory system based on genetic traits
genome_traits = {
    'vision': 0.8,          # Good vision
    'chemoreception': 0.6,  # Moderate smell
    'touch': 0.7,          # Good touch
    'neural_complexity': 0.8  # High processing power
}

sensory_system = IntegratedSensorySystem(genome_traits)

# Perceive environment
environment = {
    'light_level': 0.8,
    'temperature': 25.0,
    'entities': [
        {'id': 'food_1', 'type': 'food', 'position': (10, 10)},
        {'id': 'predator_1', 'type': 'predator', 'position': (5, 5)}
    ],
    'chemical_gradients': {
        'food': {(10, 10): 0.8},
        'danger': {(5, 5): 0.9}
    }
}

signals = sensory_system.perceive_environment(environment, cell_position=(8, 8))

# Process perception into action
perception = sensory_system.process_integrated_perception(signals)
# Returns: threat_level, opportunity_level, movement_suggestion, etc.
```

### Sensory Adaptation

The system includes habituation to repeated stimuli:

```python
# Repeated exposure reduces signal intensity
# First exposure: intensity = 0.8
# After habituation: intensity = 0.4
```

## Evolutionary Scenarios

### Disaster Types

Ten disaster types are available:
- **METEOR_IMPACT**: Mass extinction event
- **VOLCANIC_ERUPTION**: Climate change, toxins
- **ICE_AGE**: Gradual cooling
- **DROUGHT**: Resource scarcity
- **FLOOD**: Habitat destruction
- **SOLAR_FLARE**: Radiation burst
- **EARTHQUAKE**: Physical disruption
- **PANDEMIC**: Disease outbreak
- **TOXIC_BLOOM**: Chemical poisoning
- **INVASIVE_SPECIES**: New competitors

### Creating Custom Scenarios

```python
from src.evolution.evolutionary_scenarios import (
    EvolutionaryScenario, Disaster, DisasterType, 
    SelectionPressure, Pathogen
)

# Create scenario
scenario = EvolutionaryScenario(
    "Custom Apocalypse",
    "Multiple disasters strike simultaneously"
)

# Add disasters
meteor = Disaster(
    disaster_type=DisasterType.METEOR_IMPACT,
    severity=0.8,  # 0-1 scale
    duration=10,   # Time steps
    epicenter=(50, 50),
    radius=100
)
scenario.add_disaster(generation=50, disaster=meteor)

# Add selection pressures
cold_adaptation = SelectionPressure(
    "cold_survival",
    trait_preferences={'metabolism': 0.3, 'fur_thickness': 0.9},
    strength=2.0
)
scenario.add_selection_pressure(cold_adaptation)

# Add pathogen
plague = Pathogen(
    name="SuperBug",
    virulence=0.8,
    transmissibility=0.6,
    lethality=0.4
)
scenario.add_pathogen(plague, introduction_gen=30)
```

### Pre-built Scenarios

```python
from src.evolution.evolutionary_scenarios import ScenarioLibrary

# Available scenarios
kt_extinction = ScenarioLibrary.create_kt_extinction()
ice_age = ScenarioLibrary.create_ice_age()
pandemic = ScenarioLibrary.create_pandemic_scenario()
cambrian = ScenarioLibrary.create_cambrian_explosion()
anthropocene = ScenarioLibrary.create_anthropocene()
```

## Digital Ecosystem

### Trophic Levels

```python
from src.evolution.digital_ecosystem import TrophicLevel, Species

# Define species at different trophic levels
grass = Species(
    species_id="grass",
    name="Grass",
    trophic_level=TrophicLevel.PRIMARY_PRODUCER,
    base_traits={'growth_rate': 0.8},
    carrying_capacity=5000
)

rabbit = Species(
    species_id="rabbit", 
    name="Rabbit",
    trophic_level=TrophicLevel.PRIMARY_CONSUMER,
    base_traits={'speed': 0.7, 'reproduction_rate': 0.9},
    diet_preferences={"grass": 1.0},
    social_structure="warren"
)

wolf = Species(
    species_id="wolf",
    name="Wolf", 
    trophic_level=TrophicLevel.SECONDARY_CONSUMER,
    base_traits={'strength': 0.8, 'pack_coordination': 0.9},
    diet_preferences={"rabbit": 0.7, "deer": 0.3},
    social_structure="pack"
)
```

### Creating Ecosystems

```python
from src.evolution.digital_ecosystem import Ecosystem

# Initialize ecosystem
ecosystem = Ecosystem(world_size=(200, 200))

# Add species
ecosystem.add_species(grass, initial_population=1000)
ecosystem.add_species(rabbit, initial_population=100)
ecosystem.add_species(wolf, initial_population=10)

# Establish food web automatically
ecosystem.establish_food_web()

# Add symbiotic relationships
ecosystem.symbiotic_network.add_relationship(
    "tree", "fungi",
    InteractionType.MUTUALISM,
    benefit1=0.1,  # Tree benefit
    benefit2=0.2   # Fungi benefit
)

# Run simulation
for _ in range(100):
    ecosystem.simulate_step()
    
# Get statistics
stats = ecosystem.get_ecosystem_stats()
```

### Interaction Types

- **PREDATION**: Hunter-prey relationships
- **COMPETITION**: Resource competition
- **MUTUALISM**: Both species benefit
- **COMMENSALISM**: One benefits, other unaffected
- **PARASITISM**: One benefits at other's expense

## Horizontal Gene Transfer

### Transfer Mechanisms

#### 1. Conjugation (Direct Transfer)
```python
from src.evolution.horizontal_gene_transfer import HGTNetwork, GeneticElement

network = HGTNetwork()

# Create transferable gene
antibiotic_resistance = GeneticElement(
    element_id="abr1",
    element_type="trait",
    source_species="bacteria_A",
    code=json.dumps({"antibiotic_resistance": 0.9}),
    metadata={"mobile": True}
)

# Transfer between organisms
success = network.conjugation(donor_organism, recipient_organism)
```

#### 2. Transformation (Environmental DNA)
```python
# Organisms can pick up DNA from environment
environmental_dna = [antibiotic_resistance, metabolic_gene]
network.transformation(organism, environmental_dna)
```

#### 3. Transduction (Virus-Mediated)
```python
from src.evolution.horizontal_gene_transfer import ViralVector

virus = ViralVector("phage1", host_range=["bacteria_A", "bacteria_B"])
virus.genome["resistance"] = antibiotic_resistance

# Virus transfers genes during infection
network.transduction(virus, donor, recipient)
```

### Plasmid System

```python
from src.evolution.horizontal_gene_transfer import PlasmidVector

# Create plasmid
plasmid = PlasmidVector("pBR322", capacity=5)
plasmid.add_element(antibiotic_resistance)
plasmid.add_element(metabolic_gene)

# Check transfer compatibility
if plasmid.can_transfer_to(host):
    integrated_genes = plasmid.integrate_into_host(host)
```

## Integration Examples

### Example 1: Sensory-Guided Evolution

```python
# Organisms with better vision survive predation
for organism in population:
    # Perceive threats
    signals = organism.sensory_system.perceive_environment(env, organism.position)
    perception = organism.sensory_system.process_integrated_perception(signals)
    
    if perception['threat_level'] > 0.7:
        if organism.get_trait('vision') < 0.5:
            # Poor vision = higher mortality
            organism.health -= 50
```

### Example 2: Pandemic with HGT

```python
# Disease spreads, but resistance genes can transfer
pathogen = Pathogen("SuperBug", virulence=0.8)

# Some organisms have resistance
resistance_gene = GeneticElement(
    element_id="bug_resistance",
    element_type="trait",
    source_species="resistant_strain",
    code=json.dumps({"pathogen_resistance": 0.9})
)

# Resistance spreads via HGT
for generation in range(50):
    # Disease spreads
    pathogen.spread(contact_network)
    
    # But resistance also spreads
    hgt_events = network.simulate_hgt_event(population)
```

### Example 3: Ecosystem Collapse and Recovery

```python
# Asteroid impact affects entire ecosystem
asteroid = Disaster(DisasterType.METEOR_IMPACT, severity=0.9, duration=5)

# Apply to ecosystem
results = disaster_simulator.apply_disaster(asteroid, all_organisms, ecosystem.environment)

# Track recovery
recovery_generations = 0
while ecosystem.get_ecosystem_stats()['total_organisms'] < initial_count * 0.5:
    ecosystem.simulate_step()
    recovery_generations += 1

print(f"Ecosystem recovered in {recovery_generations} generations")
```

### Example 4: Adaptive Radiation

```python
# Single species colonizes diverse habitats
founder_species = Species("founder", "Founder", TrophicLevel.PRIMARY_CONSUMER, {})

# Different selection pressures in each habitat
for habitat_type in ['forest', 'grassland', 'mountain', 'wetland']:
    # Create habitat-specific pressure
    pressure = SelectionPressure(
        f"{habitat_type}_adaptation",
        trait_preferences=habitat_specific_traits[habitat_type],
        strength=2.0
    )
    
    # Populations diverge over time
    subpopulation = [org for org in population if org.habitat == habitat_type]
    for gen in range(100):
        apply_selection_pressure(subpopulation, pressure)
```

## Performance Considerations

### Memory Usage
- Large populations (>10,000 organisms) require significant RAM
- Use `PopulationTracker` for statistics instead of storing all history

### Optimization Tips
1. Limit sensory perception radius
2. Use spatial indexing for neighbor searches
3. Batch HGT events
4. Periodically clean up extinct lineages

### Scaling Recommendations
- **Small simulations**: <100 organisms, full features
- **Medium simulations**: 100-1000 organisms, selective features
- **Large simulations**: >1000 organisms, optimize critical paths

## API Reference

### Key Classes

| Module | Class | Description |
|--------|-------|-------------|
| digital_life | DigitalDNA | Genetic information storage |
| digital_life | EvolutionSimulator | Main simulation controller |
| sensory_system | IntegratedSensorySystem | Multi-modal perception |
| evolutionary_scenarios | EvolutionaryScenario | Disaster and pressure manager |
| digital_ecosystem | Ecosystem | Multi-species environment |
| horizontal_gene_transfer | HGTNetwork | Gene transfer network |

### Common Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| mutation_rate | float | 0.01 | Probability of mutation |
| carrying_capacity | int | 1000 | Maximum population |
| sensitivity | float | 0.5 | Sensory organ sensitivity |
| severity | float | 0.5 | Disaster severity (0-1) |
| transfer_rate | float | 0.1 | HGT success rate |

## Troubleshooting

### Common Issues

**Issue**: Organisms dying too quickly
- **Solution**: Adjust metabolic rates, increase resources, or reduce environmental harshness

**Issue**: No evolution occurring  
- **Solution**: Increase mutation rate, add selection pressures, ensure reproduction

**Issue**: Memory errors with large populations
- **Solution**: Reduce population size, disable file saving, limit history tracking

**Issue**: HGT not occurring
- **Solution**: Check organism proximity, increase transformation competence, verify gene compatibility

## Future Extensions

Planned features:
- Neural network integration for behavior
- 3D spatial simulation
- Real-time visualization dashboard
- Cloud-based distributed simulation
- Machine learning pattern analysis