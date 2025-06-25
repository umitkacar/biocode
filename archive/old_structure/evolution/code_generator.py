"""
Code Generator - Generate actual Python code from DNA
"""
import random
import ast
import textwrap
from typing import Dict, Any, List
from pathlib import Path


class CodeGeneticTemplate:
    """Templates for generating code from genes"""
    
    BEHAVIOR_TEMPLATES = {
        'aggressive': '''
    def attack(self, target):
        """Aggressive behavior - attack target"""
        damage = self.strength * 2
        logger.info(f"{self.id} attacking {target} for {damage} damage")
        return damage
        ''',
        
        'defensive': '''
    def defend(self):
        """Defensive behavior - increase protection"""
        self.armor += 1
        logger.info(f"{self.id} defending, armor now {self.armor}")
        ''',
        
        'cooperative': '''
    def help_neighbor(self, neighbor):
        """Cooperative behavior - help others"""
        if self.energy > 10:
            self.energy -= 5
            neighbor.energy += 5
            logger.info(f"{self.id} helping {neighbor.id}")
        ''',
        
        'neutral': '''
    def observe(self):
        """Neutral behavior - just observe"""
        logger.info(f"{self.id} observing environment")
        '''
    }
    
    METABOLISM_TEMPLATES = {
        'fast': '''
    def metabolize(self):
        """Fast metabolism - quick energy burn"""
        self.energy -= 2
        self.speed = 2.0
        ''',
        
        'efficient': '''
    def metabolize(self):
        """Efficient metabolism - slow and steady"""
        self.energy -= 0.5
        self.efficiency = 1.5
        ''',
        
        'adaptive': '''
    def metabolize(self):
        """Adaptive metabolism - adjust to conditions"""
        if self.energy > 50:
            self.energy -= 1.5
        else:
            self.energy -= 0.3
        ''',
        
        'balanced': '''
    def metabolize(self):
        """Balanced metabolism"""
        self.energy -= 1
        '''
    }
    
    REPRODUCTION_TEMPLATES = {
        'mitosis': '''
    def reproduce(self):
        """Reproduce by mitosis"""
        if self.energy > 30:
            self.energy /= 2
            return self.__class__(dna=self.dna.mutate())
        ''',
        
        'budding': '''
    def reproduce(self):
        """Reproduce by budding"""
        if self.energy > 20:
            self.energy -= 10
            return self.__class__(dna=self.dna.mutate())
        ''',
        
        'fragmentation': '''
    def reproduce(self):
        """Reproduce by fragmentation"""
        if self.energy > 40:
            fragments = []
            for _ in range(3):
                self.energy /= 3
                fragments.append(self.__class__(dna=self.dna.mutate()))
            return fragments
        ''',
        
        'binary_fission': '''
    def reproduce(self):
        """Reproduce by binary fission"""
        if self.energy > 25:
            self.energy /= 2
            child1 = self.__class__(dna=self.dna.mutate())
            child2 = self.__class__(dna=self.dna.mutate())
            return [child1, child2]
        '''
    }


class CodeDNAExpressor:
    """Express DNA as actual Python code"""
    
    def __init__(self):
        self.templates = CodeGeneticTemplate()
    
    def express_phenotype(self, dna: Dict[str, Any], class_name: str = "GeneratedCell") -> str:
        """Generate complete Python class from DNA"""
        
        # Base imports
        code = '''"""
Auto-generated cell from DNA expression
"""
import random
import logging
from src.evolution.digital_life import DigitalDNA, AdaptiveCell

logger = logging.getLogger(__name__)

'''
        
        # Class definition
        code += f"class {class_name}(AdaptiveCell):\n"
        code += f'    """Generated cell with unique traits"""\n'
        
        # Class attributes from DNA
        code += f"    behavior_type = '{dna.get('behavior', 'neutral')}'\n"
        code += f"    metabolism_type = '{dna.get('metabolism', 'balanced')}'\n"
        code += f"    mutation_rate = {dna.get('mutation_rate', 0.05)}\n"
        code += f"    lifespan = {dna.get('lifespan', 50)}\n"
        code += f"    resilience = {dna.get('resilience', 0.5)}\n"
        
        # Constructor
        code += '''
    def __init__(self, dna=None):
        if not dna:
            dna = DigitalDNA({
'''
        # DNA genes
        for key, value in dna.items():
            if isinstance(value, str):
                code += f"                '{key}': '{value}',\n"
            else:
                code += f"                '{key}': {value},\n"
        code += '''            })
        super().__init__(dna)
        self.energy = 100
        self.armor = 0
        self.speed = 1.0
        self.efficiency = 1.0
        self.strength = 10
'''
        
        # Add behavior method
        behavior = dna.get('behavior', 'neutral')
        if behavior in self.templates.BEHAVIOR_TEMPLATES:
            code += self.templates.BEHAVIOR_TEMPLATES[behavior]
        
        # Add metabolism method
        metabolism = dna.get('metabolism', 'balanced')
        if metabolism in self.templates.METABOLISM_TEMPLATES:
            code += self.templates.METABOLISM_TEMPLATES[metabolism]
        
        # Add reproduction method
        reproduction = dna.get('reproduction', 'mitosis')
        if reproduction in self.templates.REPRODUCTION_TEMPLATES:
            code += self.templates.REPRODUCTION_TEMPLATES[reproduction]
        
        # Add unique traits based on random DNA combinations
        code += self._generate_unique_traits(dna)
        
        # Add main execution
        code += '''

if __name__ == "__main__":
    cell = {class_name}()
    print(f"Cell {{cell.id}} created!")
    print(f"Behavior: {{cell.behavior_type}}")
    print(f"Metabolism: {{cell.metabolism_type}}")
    print(f"Lifespan: {{cell.lifespan}}")
'''.format(class_name=class_name)
        
        return code
    
    def _generate_unique_traits(self, dna: Dict[str, Any]) -> str:
        """Generate unique trait methods based on DNA combinations"""
        traits = ""
        
        # High resilience + defensive = regeneration
        if dna.get('resilience', 0) > 0.7 and dna.get('behavior') == 'defensive':
            traits += '''
    def regenerate(self):
        """Special trait: Regeneration"""
        if self.health < 100:
            self.health += 5
            logger.info(f"{self.id} regenerating health")
'''
        
        # Fast metabolism + aggressive = berserker
        if dna.get('metabolism') == 'fast' and dna.get('behavior') == 'aggressive':
            traits += '''
    def berserker_mode(self):
        """Special trait: Berserker mode"""
        self.strength *= 2
        self.energy -= 10
        logger.info(f"{self.id} entering berserker mode!")
'''
        
        # Cooperative + efficient = resource sharing
        if dna.get('behavior') == 'cooperative' and dna.get('metabolism') == 'efficient':
            traits += '''
    def share_resources(self, colony):
        """Special trait: Enhanced resource sharing"""
        total_energy = sum(cell.energy for cell in colony)
        avg_energy = total_energy / len(colony)
        for cell in colony:
            cell.energy = avg_energy
        logger.info(f"{self.id} balanced colony resources")
'''
        
        return traits
    
    def save_generated_cell(self, dna: Dict[str, Any], filename: str = None) -> Path:
        """Generate and save cell code to file"""
        if not filename:
            behavior = dna.get('behavior', 'unknown')
            metabolism = dna.get('metabolism', 'unknown')
            filename = f"cell_{behavior}_{metabolism}_{random.randint(1000, 9999)}.py"
        
        # Create directory
        generated_dir = Path("generated_cells")
        generated_dir.mkdir(exist_ok=True)
        
        filepath = generated_dir / filename
        
        # Generate code
        code = self.express_phenotype(dna)
        
        # Save to file
        with open(filepath, 'w') as f:
            f.write(code)
        
        return filepath


class EvolutionaryCodeFactory:
    """Factory for creating evolving code populations"""
    
    def __init__(self):
        self.expressor = CodeDNAExpressor()
        self.gene_pool = []
    
    def create_random_population(self, size: int = 10) -> List[Path]:
        """Create a population of random cells"""
        created_files = []
        
        behaviors = ['aggressive', 'defensive', 'cooperative', 'neutral']
        metabolisms = ['fast', 'efficient', 'adaptive', 'balanced']
        reproductions = ['mitosis', 'budding', 'fragmentation', 'binary_fission']
        
        for i in range(size):
            dna = {
                'behavior': random.choice(behaviors),
                'metabolism': random.choice(metabolisms),
                'reproduction': random.choice(reproductions),
                'mutation_rate': random.uniform(0.01, 0.15),
                'lifespan': random.randint(20, 100),
                'resilience': random.uniform(0.1, 0.9)
            }
            
            filepath = self.expressor.save_generated_cell(
                dna, 
                filename=f"population_{i:03d}.py"
            )
            created_files.append(filepath)
            self.gene_pool.append(dna)
        
        return created_files
    
    def breed_cells(self, parent1_dna: Dict, parent2_dna: Dict) -> Dict:
        """Crossbreed two cells' DNA"""
        child_dna = {}
        
        # Each gene has 50% chance from each parent
        all_genes = set(parent1_dna.keys()) | set(parent2_dna.keys())
        
        for gene in all_genes:
            if gene in parent1_dna and gene in parent2_dna:
                # Both parents have this gene
                if random.random() < 0.5:
                    child_dna[gene] = parent1_dna[gene]
                else:
                    child_dna[gene] = parent2_dna[gene]
            elif gene in parent1_dna:
                child_dna[gene] = parent1_dna[gene]
            else:
                child_dna[gene] = parent2_dna[gene]
        
        # Chance of mutation
        if random.random() < child_dna.get('mutation_rate', 0.05):
            # Mutate a random gene
            gene_to_mutate = random.choice(list(child_dna.keys()))
            if isinstance(child_dna[gene_to_mutate], (int, float)):
                child_dna[gene_to_mutate] *= random.uniform(0.8, 1.2)
        
        return child_dna


# Example usage
if __name__ == "__main__":
    # Create code expressor
    expressor = CodeDNAExpressor()
    
    # Example DNA
    example_dna = {
        'behavior': 'cooperative',
        'metabolism': 'efficient',
        'reproduction': 'mitosis',
        'mutation_rate': 0.05,
        'lifespan': 75,
        'resilience': 0.8
    }
    
    # Generate code
    code = expressor.express_phenotype(example_dna, "ExampleCell")
    print("Generated Code:")
    print("=" * 50)
    print(code)
    
    # Save to file
    filepath = expressor.save_generated_cell(example_dna)
    print(f"\nSaved to: {filepath}")
    
    # Create a population
    factory = EvolutionaryCodeFactory()
    population_files = factory.create_random_population(5)
    print(f"\nCreated population of {len(population_files)} cells")
    
    # Breed two cells
    if len(factory.gene_pool) >= 2:
        child_dna = factory.breed_cells(factory.gene_pool[0], factory.gene_pool[1])
        child_file = expressor.save_generated_cell(child_dna, "child_cell.py")
        print(f"Bred child saved to: {child_file}")