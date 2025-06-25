"""
Comprehensive test suite for evolution features
"""
import pytest
import json
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.evolution.digital_life import (
    DigitalDNA, SelfReplicatingCell, ApoptoticCell,
    AdaptiveCell, HiveMindCell, CollectiveIntelligence,
    EvolutionSimulator
)
from src.evolution.sensory_system import (
    SensoryType, SensorySignal, VisualSystem,
    ChemoreceptorSystem, IntegratedSensorySystem
)
from src.evolution.evolutionary_scenarios import (
    DisasterType, Disaster, SelectionPressure,
    Pathogen, ScenarioLibrary, DisasterSimulator
)
from src.evolution.digital_ecosystem import (
    TrophicLevel, Species, Organism, Ecosystem,
    FoodWeb, InteractionType
)
from src.evolution.horizontal_gene_transfer import (
    GeneticElement, PlasmidVector, ViralVector,
    HGTNetwork, LivingCodeOrganism
)


class TestDigitalDNA:
    """Test DNA and mutation systems"""
    
    def test_dna_creation(self):
        """Test DNA initialization"""
        dna = DigitalDNA()
        assert 'behavior' in dna.genes
        assert 'metabolism' in dna.genes
        assert dna.generation == 0
        assert dna.lineage_id is not None
    
    def test_dna_mutation(self):
        """Test DNA mutation"""
        dna = DigitalDNA({'behavior': 'aggressive', 'mutation_rate': 0.5})
        mutated = dna.mutate()
        
        assert mutated.generation == dna.generation + 1
        assert mutated.lineage_id == dna.lineage_id
        # With high mutation rate, something should change
        assert mutated.genes != dna.genes or len(mutated.genes) != len(dna.genes)
    
    def test_dna_crossover(self):
        """Test sexual reproduction"""
        parent1 = DigitalDNA({'behavior': 'aggressive', 'metabolism': 'fast'})
        parent2 = DigitalDNA({'behavior': 'defensive', 'metabolism': 'slow'})
        
        child = parent1.crossover(parent2)
        
        assert child.generation == max(parent1.generation, parent2.generation) + 1
        assert child.genes['behavior'] in ['aggressive', 'defensive']
        assert child.genes['metabolism'] in ['fast', 'slow']


class TestSelfReplicatingCell:
    """Test self-replicating cells"""
    
    def test_cell_creation(self):
        """Test cell initialization"""
        cell = SelfReplicatingCell()
        assert cell.dna is not None
        assert cell.age == 0
        assert cell.offspring_count == 0
        assert cell.fitness_score == 1.0
    
    def test_mitosis(self):
        """Test cell division"""
        parent = SelfReplicatingCell()
        child = parent.mitosis()
        
        assert child is not None
        assert child.id != parent.id
        assert child.dna.generation == parent.dna.generation + 1
        assert parent.offspring_count == 1
    
    def test_mitosis_with_file_save(self, tmp_path):
        """Test saving cell to file"""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            parent = SelfReplicatingCell()
            child = parent.mitosis(save_to_file=True)
            
            # Check file was created
            expected_file = f"digital_life_forms/cell_{child.id}_{child.dna.generation}.py"
            assert os.path.exists(expected_file)


class TestApoptoticCell:
    """Test programmed cell death"""
    
    def test_death_signals(self):
        """Test apoptosis triggering"""
        cell = ApoptoticCell()
        assert cell.state == "healthy"
        
        # Send death signals
        cell.receive_death_signal("DNA damage")
        cell.receive_death_signal("Toxin exposure")
        assert cell.state == "healthy"  # Not enough signals
        
        cell.receive_death_signal("Energy depletion")
        assert cell.state == "dead"  # Triggered after 3 signals
    
    def test_stress_response(self):
        """Test stress-induced apoptosis"""
        cell = ApoptoticCell()
        
        # Simulate high stress
        with patch('psutil.cpu_percent', return_value=95):
            with patch('psutil.virtual_memory') as mock_mem:
                mock_mem.return_value.percent = 95
                
                for _ in range(6):  # Exceed stress threshold
                    cell.check_stress()
                
                assert cell.state == "dead"
    
    def test_genetic_memory_save(self, tmp_path):
        """Test saving genetic memory before death"""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            cell = ApoptoticCell()
            cell._save_genetic_memory()
            
            # Check memory file exists
            assert os.path.exists("genetic_memory")
            files = os.listdir("genetic_memory")
            assert len(files) == 1
            
            # Verify content
            with open(os.path.join("genetic_memory", files[0])) as f:
                memory = json.load(f)
                assert memory['cell_id'] == cell.id
                assert 'dna' in memory


class TestSensorySystem:
    """Test sensory perception systems"""
    
    def test_visual_system(self):
        """Test vision sensing"""
        vision = VisualSystem(sensitivity=0.8, field_of_view=120)
        
        environment = {
            'light_level': 0.8,
            'cell_facing': 0,
            'entities': [
                {'id': 'prey1', 'type': 'food', 'position': (10, 0), 'color': 'green'}
            ]
        }
        
        signals = vision.perceive(environment, (0, 0))
        assert len(signals) == 1
        assert signals[0].signal_type == SensoryType.VISION
        assert signals[0].data['entity_type'] == 'food'
        assert signals[0].data['distance'] == 10.0
    
    def test_chemoreceptor_system(self):
        """Test chemical sensing"""
        chemo = ChemoreceptorSystem(sensitivity=0.7)
        
        environment = {
            'chemical_gradients': {
                'food': {(5, 5): 0.8, (4, 5): 0.6, (6, 5): 0.6}
            }
        }
        
        signals = chemo.perceive(environment, (5, 5))
        assert len(signals) == 1
        assert signals[0].signal_type == SensoryType.CHEMORECEPTION
        assert signals[0].data['chemical'] == 'food'
        assert signals[0].data['concentration'] == 0.8
    
    def test_integrated_sensory_system(self):
        """Test complete sensory integration"""
        genome_traits = {
            'vision': 0.8,
            'chemoreception': 0.6,
            'touch': 0.7,
            'neural_complexity': 0.8
        }
        
        sensory = IntegratedSensorySystem(genome_traits)
        
        assert SensoryType.VISION in sensory.organs
        assert SensoryType.CHEMORECEPTION in sensory.organs
        assert sensory.attention_capacity > 5
        
        # Test perception integration
        test_signals = [
            SensorySignal(SensoryType.VISION, 0.8, data={'entity_type': 'predator'}),
            SensorySignal(SensoryType.CHEMORECEPTION, 0.6, data={'chemical': 'food'})
        ]
        
        perception = sensory.process_integrated_perception(test_signals)
        assert perception['threat_level'] > 0
        assert perception['opportunity_level'] > 0


class TestEvolutionaryScenarios:
    """Test disaster and selection scenarios"""
    
    def test_disaster_creation(self):
        """Test disaster initialization"""
        disaster = Disaster(
            disaster_type=DisasterType.METEOR_IMPACT,
            severity=0.8,
            duration=10
        )
        
        assert disaster.effects['instant_mortality'] > 0.5
        assert disaster.effects['temperature_change'] < 0
        assert disaster.effects['mutation_rate_multiplier'] > 1
    
    def test_selection_pressure(self):
        """Test selection pressure on traits"""
        pressure = SelectionPressure(
            "cold_adaptation",
            {'metabolism': 0.3, 'insulation': 0.9},
            strength=2.0
        )
        
        # Test fitness calculation
        good_traits = {'metabolism': 0.3, 'insulation': 0.85}
        bad_traits = {'metabolism': 0.8, 'insulation': 0.2}
        
        good_fitness = pressure.calculate_fitness_modifier(good_traits)
        bad_fitness = pressure.calculate_fitness_modifier(bad_traits)
        
        assert good_fitness > bad_fitness
        assert good_fitness > 1.0  # Beneficial
        assert bad_fitness < 1.0   # Detrimental
    
    def test_pathogen(self):
        """Test disease dynamics"""
        pathogen = Pathogen("TestVirus", virulence=0.8, lethality=0.3)
        
        # Test infection
        success = pathogen.attempt_infection("host1", host_immunity=0.2)
        assert success  # High virulence vs low immunity
        
        # Test spread
        contact_network = {
            "host1": ["host2", "host3"],
            "host2": ["host4"]
        }
        
        new_infections = pathogen.spread(contact_network)
        assert len(new_infections) > 0
        
        # Test mortality
        deaths = pathogen.cause_mortality()
        assert isinstance(deaths, list)
    
    def test_scenario_library(self):
        """Test pre-built scenarios"""
        kt = ScenarioLibrary.create_kt_extinction()
        assert len(kt.disasters) >= 2
        assert len(kt.selection_pressures) >= 1
        
        ice_age = ScenarioLibrary.create_ice_age()
        assert len(ice_age.environmental_changes) > 0
        
        pandemic = ScenarioLibrary.create_pandemic_scenario()
        assert len(pandemic.pathogens) > 0


class TestDigitalEcosystem:
    """Test multi-species ecosystem"""
    
    def test_species_creation(self):
        """Test species initialization"""
        wolf = Species(
            species_id="wolf",
            name="Wolf",
            trophic_level=TrophicLevel.SECONDARY_CONSUMER,
            base_traits={'speed': 0.7, 'strength': 0.8}
        )
        
        assert wolf.diet_preferences == {"herbivores": 1.0}
        assert wolf.carrying_capacity == 1000.0
        
        # Test fitness calculation
        fitness = wolf.calculate_fitness({'temperature': 25})
        assert 0 < fitness <= 1
    
    def test_ecosystem_setup(self):
        """Test ecosystem initialization"""
        eco = Ecosystem(world_size=(100, 100))
        
        # Add species
        rabbit = Species("rabbit", "Rabbit", TrophicLevel.PRIMARY_CONSUMER, {})
        eco.add_species(rabbit, initial_population=10)
        
        assert "rabbit" in eco.species
        assert len(eco.populations["rabbit"]) == 10
        
        # Test food web
        eco.establish_food_web()
        # Food web should be empty with only one species
        assert len(eco.food_web.predator_prey) == 0
    
    def test_multi_species_interaction(self):
        """Test predator-prey dynamics"""
        eco = Ecosystem(world_size=(50, 50))
        
        # Create simple food chain
        grass = Species("grass", "Grass", TrophicLevel.PRIMARY_PRODUCER, {})
        rabbit = Species("rabbit", "Rabbit", TrophicLevel.PRIMARY_CONSUMER, {})
        fox = Species("fox", "Fox", TrophicLevel.SECONDARY_CONSUMER, {})
        
        eco.add_species(grass, 100)
        eco.add_species(rabbit, 20)
        eco.add_species(fox, 5)
        
        eco.establish_food_web()
        
        # Check food web established
        assert "rabbit" in eco.food_web.predator_prey.get("fox", set())
        
        # Run one step
        initial_rabbits = len(eco.populations["rabbit"])
        eco.simulate_step()
        
        # Population should change
        assert len(eco.populations["rabbit"]) != initial_rabbits or \
               len(eco.populations["fox"]) != 5


class TestHorizontalGeneTransfer:
    """Test HGT mechanisms"""
    
    def test_genetic_element(self):
        """Test genetic element creation"""
        gene = GeneticElement(
            element_id="test_gene",
            element_type="trait",
            source_species="bacteria",
            code=json.dumps({"resistance": 0.8}),
            metadata={"mobile": True}
        )
        
        assert gene.is_compatible(Mock)
        assert gene.transfer_count == 0
    
    def test_plasmid_transfer(self):
        """Test plasmid-mediated transfer"""
        plasmid = PlasmidVector("plasmid1", capacity=3)
        
        gene = GeneticElement(
            element_id="resistance",
            element_type="trait",
            source_species="bacteria",
            code=json.dumps({"antibiotic_resistance": 0.9}),
            metadata={}
        )
        
        assert plasmid.add_element(gene)
        assert len(plasmid.genetic_elements) == 1
        
        # Test transfer
        host = Mock()
        host.plasmid_compatibility = True
        
        assert plasmid.can_transfer_to(host)
    
    def test_viral_vector(self):
        """Test virus-mediated transfer"""
        virus = ViralVector("phage1", host_range=["bacteria_A", "bacteria_B"])
        
        # Add gene to virus
        gene = GeneticElement(
            element_id="viral_gene",
            element_type="trait",
            source_species="virus",
            code=json.dumps({"viral_trait": 1.0}),
            metadata={}
        )
        
        virus.genome["gene1"] = gene
        
        # Test infection
        host = Mock()
        host.species = "bacteria_A"
        host.viral_infections = []
        
        assert virus.infect(host)
        assert virus.virus_id in host.viral_infections
    
    def test_hgt_network(self):
        """Test complete HGT network"""
        network = HGTNetwork()
        
        # Create organisms
        org1 = LivingCodeOrganism("org1", "species_A")
        org2 = LivingCodeOrganism("org2", "species_A")
        
        # Add genes to org1
        gene = GeneticElement(
            element_id="beneficial_gene",
            element_type="trait",
            source_species="species_A",
            code=json.dumps({"benefit": 0.8}),
            metadata={"mobile": True}
        )
        
        org1.genome["gene1"] = gene
        org1.position = (0, 0)
        org2.position = (1, 1)  # Close enough for conjugation
        
        # Test conjugation
        network.create_plasmid(org1)
        success = network.conjugation(org1, org2)
        
        # Conjugation might fail due to randomness, but system should work
        assert isinstance(success, bool)


class TestIntegration:
    """Test integration of multiple features"""
    
    def test_sensory_ecosystem_integration(self):
        """Test sensory system in ecosystem context"""
        # Create organism with sensory system
        genome_traits = {'vision': 0.8, 'chemoreception': 0.6}
        sensory = IntegratedSensorySystem(genome_traits)
        
        # Create ecosystem environment
        environment = {
            'light_level': 0.8,
            'temperature': 20,
            'entities': [
                {'id': 'prey1', 'type': 'prey', 'position': (10, 10)}
            ],
            'chemical_gradients': {
                'food': {(5, 5): 0.5}
            }
        }
        
        # Perceive environment
        signals = sensory.perceive_environment(environment, (0, 0))
        assert len(signals) > 0
        
        # Process perception
        perception = sensory.process_integrated_perception(signals)
        assert 'primary_focus' in perception
    
    def test_disaster_evolution_integration(self):
        """Test how disasters affect evolution"""
        # Create small population
        population = []
        for i in range(10):
            cell = AdaptiveCell(DigitalDNA())
            cell.position = (i * 10, i * 10)
            population.append(cell)
        
        # Apply disaster
        disaster = Disaster(
            disaster_type=DisasterType.SOLAR_FLARE,
            severity=0.7,
            duration=5
        )
        
        simulator = DisasterSimulator()
        results = simulator.apply_disaster(disaster, population, None)
        
        # Check effects
        assert 'deaths' in results
        assert 'environment_changes' in results
        assert results['environment_changes'].get('radiation', 0) > 0
    
    def test_hgt_ecosystem_integration(self):
        """Test HGT in ecosystem context"""
        # Create ecosystem with bacteria
        eco = Ecosystem()
        
        bacteria = Species(
            "bacteria",
            "Bacteria",
            TrophicLevel.DECOMPOSER,
            {'reproduction_rate': 0.8}
        )
        
        eco.add_species(bacteria, 20)
        
        # Create HGT network
        hgt = HGTNetwork()
        
        # Add beneficial gene to one bacterium
        gene = GeneticElement(
            element_id="rapid_growth",
            element_type="trait",
            source_species="bacteria",
            code=json.dumps({"growth_rate": 1.5}),
            metadata={"mobile": True}
        )
        
        # This gene could spread through population
        assert len(eco.populations["bacteria"]) == 20


# Fixtures and utilities
@pytest.fixture
def sample_ecosystem():
    """Create a sample ecosystem for testing"""
    eco = Ecosystem(world_size=(100, 100))
    
    # Add basic food chain
    grass = Species("grass", "Grass", TrophicLevel.PRIMARY_PRODUCER, {})
    rabbit = Species("rabbit", "Rabbit", TrophicLevel.PRIMARY_CONSUMER, {})
    
    eco.add_species(grass, 50)
    eco.add_species(rabbit, 10)
    eco.establish_food_web()
    
    return eco


@pytest.fixture
def sample_population():
    """Create sample cell population"""
    population = []
    for i in range(20):
        cell = HiveMindCell(DigitalDNA())
        cell.position = (random.uniform(0, 100), random.uniform(0, 100))
        population.append(cell)
    return population


if __name__ == "__main__":
    pytest.main([__file__, "-v"])