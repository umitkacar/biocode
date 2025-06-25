# BioCode Evolution Tutorial

This tutorial will guide you through creating your first digital life simulation using BioCode's evolution features.

## Prerequisites

```python
import sys
sys.path.append('path/to/biocode')

from src.evolution.digital_life import *
from src.evolution.sensory_system import *
from src.evolution.evolutionary_scenarios import *
from src.evolution.digital_ecosystem import *
from src.evolution.horizontal_gene_transfer import *
```

## Tutorial 1: Basic Digital Life

### Step 1: Create Your First Cell

```python
# Create a cell with default DNA
cell = SelfReplicatingCell()
print(f"Cell ID: {cell.id}")
print(f"Behavior: {cell.dna.genes['behavior']}")
print(f"Metabolism: {cell.dna.genes['metabolism']}")
```

### Step 2: Cell Reproduction

```python
# Cell divides
child = cell.mitosis()
print(f"Parent cell now has {cell.offspring_count} offspring")
print(f"Child generation: {child.dna.generation}")

# Check for mutations
if child.dna.genes != cell.dna.genes:
    print("Mutation occurred!")
```

### Step 3: Simple Evolution

```python
# Create a small population
population = [SelfReplicatingCell() for _ in range(10)]

# Simulate 5 generations
for generation in range(5):
    new_cells = []
    
    for cell in population:
        # Each cell tries to reproduce
        if cell.energy > 50:
            child = cell.mitosis()
            if child:
                new_cells.append(child)
    
    # Add new cells to population
    population.extend(new_cells)
    
    # Natural selection (keep only 20 fittest)
    population.sort(key=lambda c: c.fitness_score, reverse=True)
    population = population[:20]
    
    print(f"Generation {generation + 1}: {len(population)} cells")
```

## Tutorial 2: Sensory Perception

### Step 1: Create a Sensory Cell

```python
# Define sensory capabilities
genome_traits = {
    'vision': 0.8,         # Good eyesight
    'chemoreception': 0.6, # Moderate smell
    'touch': 0.7,         # Good touch
    'neural_complexity': 0.7  # Good processing
}

# Create sensory system
sensory = IntegratedSensorySystem(genome_traits)

print(f"Active organs: {[organ.value for organ in sensory.organs.keys()]}")
print(f"Attention capacity: {sensory.attention_capacity}")
```

### Step 2: Perceive Environment

```python
# Create environment
environment = {
    'light_level': 0.8,
    'temperature': 22.0,
    'entities': [
        {
            'id': 'food_1',
            'type': 'food',
            'position': (10, 5),
            'color': 'green',
            'size': 2.0
        },
        {
            'id': 'predator_1',
            'type': 'predator',
            'position': (3, 3),
            'color': 'red',
            'size': 5.0
        }
    ],
    'chemical_gradients': {
        'food': {(10, 5): 0.9, (9, 5): 0.7, (8, 5): 0.5},
        'danger': {(3, 3): 1.0, (4, 3): 0.8}
    },
    'cell_state': {
        'energy': 75,
        'health': 90
    }
}

# Cell at position (7, 5) perceives environment
signals = sensory.perceive_environment(environment, (7, 5))

# Display what the cell senses
for signal in signals:
    print(f"\n{signal.signal_type.value} signal:")
    print(f"  Intensity: {signal.intensity:.2f}")
    print(f"  Data: {signal.data}")
```

### Step 3: Make Decisions

```python
# Process signals into action
perception = sensory.process_integrated_perception(signals)

print(f"\nPerception summary:")
print(f"  Threat level: {perception['threat_level']:.2f}")
print(f"  Opportunity level: {perception['opportunity_level']:.2f}")
print(f"  Primary focus: {perception['primary_focus']}")
print(f"  Suggested movement: {perception['movement_suggestion']}")

# Make decision based on perception
if perception['primary_focus'] == 'escape':
    print("Cell decides to flee!")
elif perception['primary_focus'] == 'approach':
    print("Cell moves toward food!")
```

## Tutorial 3: Evolutionary Scenarios

### Step 1: Create a Disaster

```python
# Create a meteor impact
meteor = Disaster(
    disaster_type=DisasterType.METEOR_IMPACT,
    severity=0.7,  # Severe but not total extinction
    duration=5,    # Lasts 5 time steps
    epicenter=(50, 50),
    radius=75
)

print("Meteor impact effects:")
for effect, value in meteor.effects.items():
    print(f"  {effect}: {value}")
```

### Step 2: Apply Selection Pressure

```python
# Create selection pressure for heat resistance
heat_resistance = SelectionPressure(
    name="heat_adaptation",
    trait_preferences={
        'heat_tolerance': 0.9,
        'metabolism': 0.3,  # Slower metabolism better for heat
        'water_retention': 0.8
    },
    strength=2.0  # Strong pressure
)

# Test how different organisms fare
hot_adapted = {'heat_tolerance': 0.85, 'metabolism': 0.35, 'water_retention': 0.75}
cold_adapted = {'heat_tolerance': 0.2, 'metabolism': 0.8, 'water_retention': 0.3}

print(f"Hot-adapted fitness: {heat_resistance.calculate_fitness_modifier(hot_adapted):.2f}")
print(f"Cold-adapted fitness: {heat_resistance.calculate_fitness_modifier(cold_adapted):.2f}")
```

### Step 3: Run Scenario

```python
# Use pre-built scenario
scenario = ScenarioLibrary.create_ice_age()

# Create population
population = [AdaptiveCell() for _ in range(100)]

# Track survival through scenario
initial_count = len(population)
survivors = []

# Simulate ice age effects
for step in range(100):
    # Get environmental modifiers
    env_mods = scenario.get_environmental_modifiers(step)
    
    # Apply to population
    for cell in population[:]:
        # Cold kills cells without adaptation
        if env_mods['temperature_change'] < -10:
            if cell.genome.express_trait('metabolism') > 0.5:
                # High metabolism = death in cold
                population.remove(cell)
            else:
                survivors.append(cell)

print(f"Survival rate: {len(survivors)/initial_count:.1%}")
```

## Tutorial 4: Digital Ecosystem

### Step 1: Create Food Web

```python
# Create ecosystem
ecosystem = Ecosystem(world_size=(100, 100))

# Add primary producer (plants)
grass = Species(
    species_id="grass",
    name="Grass",
    trophic_level=TrophicLevel.PRIMARY_PRODUCER,
    base_traits={
        'growth_rate': 0.8,
        'nutrient_efficiency': 0.7
    },
    carrying_capacity=5000,
    growth_rate=0.2
)

# Add herbivore
rabbit = Species(
    species_id="rabbit",
    name="Rabbit",
    trophic_level=TrophicLevel.PRIMARY_CONSUMER,
    base_traits={
        'speed': 0.7,
        'reproduction_rate': 0.8,
        'vigilance': 0.6
    },
    diet_preferences={"grass": 1.0},
    social_structure="warren",
    carrying_capacity=1000
)

# Add carnivore
fox = Species(
    species_id="fox",
    name="Fox",
    trophic_level=TrophicLevel.SECONDARY_CONSUMER,
    base_traits={
        'speed': 0.8,
        'intelligence': 0.8,
        'hunting_skill': 0.7
    },
    diet_preferences={"rabbit": 0.9},
    social_structure="solitary",
    territorial=True,
    carrying_capacity=100
)

# Add to ecosystem
ecosystem.add_species(grass, initial_population=500)
ecosystem.add_species(rabbit, initial_population=50)
ecosystem.add_species(fox, initial_population=5)

# Establish relationships
ecosystem.establish_food_web()
```

### Step 2: Simulate Ecosystem

```python
# Run simulation
history = []

for step in range(100):
    ecosystem.simulate_step()
    
    # Record population sizes
    stats = ecosystem.get_ecosystem_stats()
    history.append({
        'step': step,
        'grass': stats['species_populations'].get('grass', 0),
        'rabbit': stats['species_populations'].get('rabbit', 0),
        'fox': stats['species_populations'].get('fox', 0)
    })
    
    # Print every 20 steps
    if step % 20 == 0:
        print(f"Step {step}:")
        for species, count in stats['species_populations'].items():
            print(f"  {species}: {count}")
```

### Step 3: Add Symbiosis

```python
# Add decomposer
fungi = Species(
    species_id="fungi",
    name="Fungi",
    trophic_level=TrophicLevel.DECOMPOSER,
    base_traits={
        'decomposition_rate': 0.8,
        'nutrient_conversion': 0.9
    }
)

ecosystem.add_species(fungi, 100)

# Create mutualistic relationship with plants
ecosystem.symbiotic_network.add_relationship(
    "grass", "fungi",
    InteractionType.MUTUALISM,
    benefit1=0.15,  # Grass gets nutrients
    benefit2=0.20   # Fungi gets sugars
)
```

## Tutorial 5: Horizontal Gene Transfer

### Step 1: Create Transferable Genes

```python
# Create beneficial genes
speed_gene = GeneticElement(
    element_id="fast_movement",
    element_type="trait",
    source_species="cheetah_bacteria",
    code=json.dumps({"speed": 0.9, "energy_efficiency": 0.6}),
    metadata={"mobile": True},
    fitness_impact=0.2
)

resistance_gene = GeneticElement(
    element_id="toxin_resistance",
    element_type="trait",
    source_species="extremophile",
    code=json.dumps({"toxin_resistance": 0.8}),
    metadata={"mobile": True},
    fitness_impact=0.3
)
```

### Step 2: Create Gene Transfer Network

```python
# Initialize HGT network
hgt_network = HGTNetwork()

# Create organisms
organisms = []
for i in range(10):
    org = LivingCodeOrganism(f"bacterium_{i}", "E.coli")
    org.position = (i * 5, i * 5)  # Spatial distribution
    org.transformation_competence = 0.3  # Can take up DNA
    organisms.append(org)

# Give speed gene to first organism
organisms[0].genome["speed"] = speed_gene
hgt_network.register_gene(speed_gene)
```

### Step 3: Simulate Gene Spread

```python
# Track gene spread
generations = 10
gene_spread = []

for gen in range(generations):
    # Count organisms with speed gene
    count = sum(1 for org in organisms if "speed" in org.genome)
    gene_spread.append(count)
    
    print(f"Generation {gen}: {count} organisms have speed gene")
    
    # Simulate HGT events
    events = hgt_network.simulate_hgt_event(organisms)
    print(f"  HGT events: {events}")
    
    # Environmental DNA from dead cells
    if gen % 3 == 0:
        # Some organisms die and release DNA
        env_dna = [speed_gene, resistance_gene]
        for org in organisms[5:8]:
            hgt_network.transformation(org, env_dna)
```

### Step 4: Create Viral Transfer

```python
# Create virus that can carry genes
phage = ViralVector(
    virus_id="phage_lambda",
    host_range=["E.coli", "Salmonella"]
)

# Virus picks up resistance gene
phage.genome["resistance"] = resistance_gene

# Infect and spread
for i in range(0, len(organisms), 3):
    if phage.infect(organisms[i]):
        print(f"Infected organism {i}")
        
        # Virus replicates and spreads
        progeny = phage.replicate(organisms[i])
        
        # Progeny infect neighbors
        for j, virus in enumerate(progeny[:3]):
            if i+j+1 < len(organisms):
                virus.infect(organisms[i+j+1])
```

## Tutorial 6: Complete Integration

### Putting It All Together

```python
# Create integrated simulation
class IntegratedSimulation:
    def __init__(self):
        # Create ecosystem
        self.ecosystem = Ecosystem()
        
        # Add HGT network
        self.hgt_network = HGTNetwork()
        
        # Create scenario
        self.scenario = ScenarioLibrary.create_pandemic_scenario()
        
        # Initialize species with sensory systems
        self.setup_species()
        
    def setup_species(self):
        # Create bacteria with senses
        bacteria = Species(
            "bacteria",
            "Sensing Bacteria",
            TrophicLevel.DECOMPOSER,
            base_traits={
                'vision': 0.3,
                'chemoreception': 0.9,  # Good chemical sensing
                'reproduction_rate': 0.8
            }
        )
        
        self.ecosystem.add_species(bacteria, 100)
        
        # Give them antibiotic resistance gene
        resistance = GeneticElement(
            "antibiotic_res",
            "trait",
            "bacteria",
            json.dumps({"antibiotic_resistance": 0.7}),
            {"mobile": True}
        )
        
        # Add to some bacteria
        for org in self.ecosystem.populations["bacteria"][:10]:
            org.genome = {"resistance": resistance}
    
    def run_simulation(self, steps=100):
        for step in range(steps):
            # Environmental phase
            self.ecosystem.simulate_step()
            
            # Sensory phase
            for species_id, organisms in self.ecosystem.populations.items():
                for org in organisms:
                    if hasattr(org, 'sensory_system'):
                        signals = org.sensory_system.perceive_environment(
                            self.ecosystem.environment,
                            org.position
                        )
                        # React to signals
                        self.process_sensory_response(org, signals)
            
            # HGT phase
            all_organisms = []
            for orgs in self.ecosystem.populations.values():
                all_organisms.extend(orgs)
            
            hgt_events = self.hgt_network.simulate_hgt_event(all_organisms)
            
            # Disaster phase
            if step in [30, 60, 90]:
                self.apply_disaster(step)
            
            # Report
            if step % 10 == 0:
                self.report_status(step)
    
    def process_sensory_response(self, organism, signals):
        # Implement behavioral responses to sensory input
        for signal in signals:
            if signal.signal_type == SensoryType.CHEMORECEPTION:
                if signal.data.get('chemical') == 'antibiotic':
                    # Flee from antibiotic
                    organism.position = (
                        organism.position[0] - signal.direction[0],
                        organism.position[1] - signal.direction[1]
                    )
    
    def apply_disaster(self, step):
        disasters = self.scenario.get_active_disasters(step)
        for disaster in disasters:
            print(f"Disaster strikes: {disaster.disaster_type.value}")
    
    def report_status(self, step):
        stats = self.ecosystem.get_ecosystem_stats()
        print(f"\nStep {step}:")
        print(f"  Total organisms: {stats['total_organisms']}")
        print(f"  Species: {list(stats['species_populations'].keys())}")

# Run integrated simulation
sim = IntegratedSimulation()
sim.run_simulation(100)
```

## Best Practices

1. **Start Small**: Begin with <100 organisms to understand dynamics
2. **Balance Parameters**: Extreme values lead to extinction or explosion
3. **Monitor Resources**: Track memory usage with large populations
4. **Save Checkpoints**: Periodically save simulation state
5. **Visualize Results**: Use matplotlib to plot population dynamics

## Common Patterns

### Pattern 1: Predator-Prey Cycles
```python
# Classic Lotka-Volterra dynamics emerge naturally
# Prey increases → Predators increase → Prey decreases → Predators decrease
```

### Pattern 2: Evolutionary Arms Race
```python
# Prey evolve better escape → Predators evolve better hunting
# Track trait changes over generations
```

### Pattern 3: Niche Specialization
```python
# Generalist species splits into specialists
# Each exploits different resources
```

### Pattern 4: Symbiotic Networks
```python
# Mutualistic relationships stabilize ecosystems
# Loss of one partner affects the other
```

## Debugging Tips

1. **Enable Logging**:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

2. **Check Population Crashes**:
```python
if len(population) == 0:
    print("Extinction! Check:")
    print("- Resource levels")
    print("- Predation pressure")
    print("- Environmental conditions")
```

3. **Monitor Gene Flow**:
```python
analysis = hgt_network.analyze_gene_flow()
print(f"Most transferred: {analysis['most_transferred_genes']}")
```

4. **Track Lineages**:
```python
for cell in population:
    print(f"Cell {cell.id}: Generation {cell.generation}, Lineage {cell.dna.lineage_id}")
```

## Next Steps

1. **Extend Behaviors**: Add custom behaviors to your organisms
2. **Create Scenarios**: Design your own evolutionary pressures
3. **Analyze Results**: Use data science tools to find patterns
4. **Share Findings**: Document interesting emergent behaviors

Happy evolving! 🧬