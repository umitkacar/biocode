"""
Horizontal Gene Transfer - Living code that exchanges genetic material
"""
import random
import ast
import inspect
import types
import math
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from dataclasses import dataclass
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class GeneticElement:
    """A transferable genetic element (code fragment)"""
    element_id: str
    element_type: str  # 'method', 'attribute', 'trait', 'behavior'
    source_species: str
    code: str  # Actual code or value
    metadata: Dict[str, Any]
    transfer_count: int = 0
    fitness_impact: float = 0.0
    
    def __post_init__(self):
        if not self.element_id:
            # Generate ID from code hash
            self.element_id = hashlib.md5(self.code.encode()).hexdigest()[:8]
    
    def is_compatible(self, target_class: type) -> bool:
        """Check if this element can be integrated into target class"""
        if self.element_type == 'method':
            # Check method signature compatibility
            try:
                # Parse method to check parameters
                tree = ast.parse(self.code)
                if isinstance(tree.body[0], ast.FunctionDef):
                    method_name = tree.body[0].name
                    # Don't override critical methods
                    if method_name in ['__init__', '__del__', '__new__']:
                        return False
                    return True
            except:
                return False
                
        elif self.element_type == 'attribute':
            # Attributes are generally compatible
            return True
            
        elif self.element_type == 'trait':
            # Check if target has trait system
            return hasattr(target_class, 'traits') or hasattr(target_class, 'base_traits')
            
        return True


class PlasmidVector:
    """Carrier for horizontal gene transfer (like bacterial plasmids)"""
    
    def __init__(self, vector_id: str, capacity: int = 5):
        self.vector_id = vector_id
        self.capacity = capacity
        self.genetic_elements: List[GeneticElement] = []
        self.host_history: List[str] = []
        self.resistance_markers: Set[str] = set()  # What this plasmid resists
        self.transfer_rate: float = 0.1
        self.stability: float = 0.9  # Chance of successful integration
        
    def add_element(self, element: GeneticElement) -> bool:
        """Add genetic element to plasmid"""
        if len(self.genetic_elements) >= self.capacity:
            # Remove least fit element
            if self.genetic_elements:
                self.genetic_elements.sort(key=lambda e: e.fitness_impact)
                self.genetic_elements.pop(0)
        
        self.genetic_elements.append(element)
        return True
    
    def can_transfer_to(self, host: Any) -> bool:
        """Check if plasmid can transfer to host"""
        # Check host compatibility
        if hasattr(host, 'plasmid_compatibility'):
            return host.plasmid_compatibility
            
        # Check resistance
        if hasattr(host, 'resistances'):
            for marker in self.resistance_markers:
                if marker in host.resistances:
                    return False
                    
        return random.random() < self.transfer_rate
    
    def integrate_into_host(self, host: Any) -> List[str]:
        """Integrate genetic elements into host"""
        integrated = []
        
        for element in self.genetic_elements:
            if random.random() < self.stability:
                success = self._integrate_element(host, element)
                if success:
                    integrated.append(element.element_id)
                    element.transfer_count += 1
        
        if integrated:
            self.host_history.append(getattr(host, 'id', str(host)))
            
        return integrated
    
    def _integrate_element(self, host: Any, element: GeneticElement) -> bool:
        """Actually integrate genetic element into host"""
        try:
            if element.element_type == 'method':
                # Dynamic method addition
                exec(element.code)
                method_name = element.code.split('def ')[1].split('(')[0]
                method = locals()[method_name]
                setattr(host.__class__, method_name, method)
                logger.info(f"Integrated method {method_name} into {host.__class__.__name__}")
                return True
                
            elif element.element_type == 'attribute':
                # Add attribute
                attr_data = json.loads(element.code)
                for key, value in attr_data.items():
                    setattr(host, key, value)
                return True
                
            elif element.element_type == 'trait':
                # Modify traits
                if hasattr(host, 'traits'):
                    trait_data = json.loads(element.code)
                    for trait, value in trait_data.items():
                        if trait in host.traits:
                            # Average with existing
                            host.traits[trait] = (host.traits[trait] + value) / 2
                        else:
                            host.traits[trait] = value
                return True
                
        except Exception as e:
            logger.error(f"Failed to integrate element {element.element_id}: {e}")
            
        return False


class TransposableElement:
    """Jumping genes that can move within and between genomes"""
    
    def __init__(self, element_id: str, sequence: str, element_class: str = "DNA"):
        self.element_id = element_id
        self.sequence = sequence  # The actual code/function
        self.element_class = element_class  # DNA or RNA transposon
        self.copy_number = 1
        self.activity_level = 0.5
        self.target_sites: List[str] = []  # Preferred integration sites
        
    def transpose(self, source_genome: Dict, target_genome: Dict, 
                 cut_and_paste: bool = False) -> bool:
        """Move or copy element between genomes"""
        if random.random() > self.activity_level:
            return False
            
        try:
            # Find insertion site
            if self.target_sites:
                site = random.choice(self.target_sites)
            else:
                # Random insertion
                site = random.choice(list(target_genome.keys()))
            
            # Insert element
            if site not in target_genome:
                target_genome[site] = []
                
            target_genome[site].append({
                'element': self.element_id,
                'sequence': self.sequence,
                'source': source_genome.get('organism_id', 'unknown')
            })
            
            # Remove from source if cut-and-paste
            if cut_and_paste and site in source_genome:
                source_genome[site] = [
                    e for e in source_genome[site] 
                    if e.get('element') != self.element_id
                ]
                
            self.copy_number += 0 if cut_and_paste else 1
            return True
            
        except Exception as e:
            logger.error(f"Transposition failed: {e}")
            return False


class ViralVector:
    """Virus-like agent for gene transfer"""
    
    def __init__(self, virus_id: str, host_range: List[str]):
        self.virus_id = virus_id
        self.host_range = host_range  # Species that can be infected
        self.genome: Dict[str, GeneticElement] = {}
        self.infection_rate = 0.3
        self.integration_rate = 0.1  # Rate of genome integration
        self.lytic = False  # If True, kills host after replication
        self.latent = True   # Can remain dormant
        self.burst_size = 10  # Copies produced in lytic cycle
        
    def infect(self, host: Any) -> bool:
        """Attempt to infect host"""
        # Check host range
        host_species = getattr(host, 'species', getattr(host, '__class__.__name__', 'unknown'))
        
        if host_species not in self.host_range and 'universal' not in self.host_range:
            return False
            
        if random.random() > self.infection_rate:
            return False
            
        # Successful infection
        if hasattr(host, 'viral_infections'):
            host.viral_infections.append(self.virus_id)
        else:
            host.viral_infections = [self.virus_id]
            
        # Integrate genes
        if random.random() < self.integration_rate:
            self._integrate_viral_genes(host)
            
        return True
    
    def _integrate_viral_genes(self, host: Any):
        """Integrate viral genes into host genome"""
        for gene_id, element in self.genome.items():
            if element.is_compatible(host.__class__):
                # Add with viral marker
                modified_element = GeneticElement(
                    element_id=f"viral_{element.element_id}",
                    element_type=element.element_type,
                    source_species=f"virus_{self.virus_id}",
                    code=element.code,
                    metadata={**element.metadata, 'viral_origin': True}
                )
                
                # Attempt integration
                if hasattr(host, 'genome'):
                    host.genome[gene_id] = modified_element
                elif hasattr(host, 'genetic_elements'):
                    host.genetic_elements.append(modified_element)
    
    def replicate(self, host: Any) -> List['ViralVector']:
        """Replicate within host"""
        if self.virus_id not in getattr(host, 'viral_infections', []):
            return []
            
        progeny = []
        
        for _ in range(self.burst_size):
            # Create progeny with possible mutations
            new_virus = ViralVector(
                f"{self.virus_id}_prog_{random.randint(1000, 9999)}",
                self.host_range.copy()
            )
            
            # Copy genome with mutations
            for gene_id, element in self.genome.items():
                if random.random() < 0.95:  # 5% mutation rate
                    new_virus.genome[gene_id] = element
                else:
                    # Mutate
                    mutated = self._mutate_element(element)
                    new_virus.genome[gene_id] = mutated
                    
            new_virus.infection_rate = self.infection_rate * random.uniform(0.9, 1.1)
            progeny.append(new_virus)
            
        # Kill host if lytic
        if self.lytic and hasattr(host, 'alive'):
            host.alive = False
            
        return progeny
    
    def _mutate_element(self, element: GeneticElement) -> GeneticElement:
        """Create mutated version of genetic element"""
        mutated_code = element.code
        
        if element.element_type == 'trait':
            # Mutate trait values
            try:
                traits = json.loads(element.code)
                for trait in traits:
                    if isinstance(traits[trait], (int, float)):
                        traits[trait] *= random.uniform(0.8, 1.2)
                mutated_code = json.dumps(traits)
            except:
                pass
                
        return GeneticElement(
            element_id=f"{element.element_id}_mut",
            element_type=element.element_type,
            source_species=element.source_species,
            code=mutated_code,
            metadata={**element.metadata, 'mutated': True}
        )


class HGTNetwork:
    """Network for horizontal gene transfer between organisms"""
    
    def __init__(self):
        self.plasmids: Dict[str, PlasmidVector] = {}
        self.transposons: Dict[str, TransposableElement] = {}
        self.viruses: Dict[str, ViralVector] = {}
        self.transfer_history: List[Dict[str, Any]] = []
        self.gene_pool: Dict[str, GeneticElement] = {}  # All known genes
        
    def register_gene(self, element: GeneticElement):
        """Add gene to the pool"""
        self.gene_pool[element.element_id] = element
        
    def create_plasmid(self, source_organism: Any) -> PlasmidVector:
        """Create plasmid from organism's genes"""
        plasmid_id = f"plasmid_{len(self.plasmids)}"
        plasmid = PlasmidVector(plasmid_id)
        
        # Extract transferable elements
        if hasattr(source_organism, 'get_transferable_genes'):
            genes = source_organism.get_transferable_genes()
            for gene in genes[:plasmid.capacity]:
                plasmid.add_element(gene)
        
        self.plasmids[plasmid_id] = plasmid
        return plasmid
    
    def conjugation(self, donor: Any, recipient: Any) -> bool:
        """Transfer genes via conjugation (direct contact)"""
        if not self._can_conjugate(donor, recipient):
            return False
            
        # Check for plasmids in donor
        donor_plasmids = getattr(donor, 'plasmids', [])
        if not donor_plasmids:
            # Create one from donor's genes
            plasmid = self.create_plasmid(donor)
            donor_plasmids = [plasmid.vector_id]
            
        transferred = False
        
        for plasmid_id in donor_plasmids:
            if plasmid_id in self.plasmids:
                plasmid = self.plasmids[plasmid_id]
                
                if plasmid.can_transfer_to(recipient):
                    integrated = plasmid.integrate_into_host(recipient)
                    
                    if integrated:
                        # Add plasmid to recipient
                        if hasattr(recipient, 'plasmids'):
                            recipient.plasmids.append(plasmid_id)
                        else:
                            recipient.plasmids = [plasmid_id]
                            
                        # Record transfer
                        self.transfer_history.append({
                            'type': 'conjugation',
                            'donor': getattr(donor, 'id', str(donor)),
                            'recipient': getattr(recipient, 'id', str(recipient)),
                            'plasmid': plasmid_id,
                            'genes': integrated,
                            'timestamp': len(self.transfer_history)
                        })
                        
                        transferred = True
                        logger.info(f"Conjugation transferred {len(integrated)} genes")
                        
        return transferred
    
    def transformation(self, organism: Any, environmental_dna: List[GeneticElement]) -> bool:
        """Uptake of DNA from environment"""
        if not hasattr(organism, 'transformation_competence'):
            return False
            
        competence = organism.transformation_competence
        if random.random() > competence:
            return False
            
        # Attempt to integrate environmental DNA
        integrated = []
        
        for element in environmental_dna:
            if element.is_compatible(organism.__class__):
                if random.random() < competence * 0.5:  # Lower rate than plasmid
                    # Direct integration attempt
                    plasmid = PlasmidVector(f"temp_{element.element_id}", capacity=1)
                    plasmid.add_element(element)
                    
                    result = plasmid.integrate_into_host(organism)
                    if result:
                        integrated.extend(result)
                        
        if integrated:
            self.transfer_history.append({
                'type': 'transformation',
                'recipient': getattr(organism, 'id', str(organism)),
                'genes': integrated,
                'source': 'environmental',
                'timestamp': len(self.transfer_history)
            })
            
        return len(integrated) > 0
    
    def transduction(self, virus: ViralVector, donor: Any, recipient: Any) -> bool:
        """Virus-mediated gene transfer"""
        # Virus picks up genes from donor
        if hasattr(donor, 'genome'):
            # Sample some genes
            donor_genes = list(donor.genome.values())
            if donor_genes:
                picked_genes = random.sample(
                    donor_genes, 
                    min(3, len(donor_genes))
                )
                
                for gene in picked_genes:
                    if isinstance(gene, GeneticElement):
                        virus.genome[gene.element_id] = gene
        
        # Infect recipient
        if virus.infect(recipient):
            # Genes are transferred during infection
            self.transfer_history.append({
                'type': 'transduction',
                'donor': getattr(donor, 'id', str(donor)),
                'recipient': getattr(recipient, 'id', str(recipient)),
                'virus': virus.virus_id,
                'genes': list(virus.genome.keys()),
                'timestamp': len(self.transfer_history)
            })
            
            return True
            
        return False
    
    def _can_conjugate(self, donor: Any, recipient: Any) -> bool:
        """Check if conjugation is possible"""
        # Check physical proximity
        if hasattr(donor, 'position') and hasattr(recipient, 'position'):
            distance = math.sqrt(
                (donor.position[0] - recipient.position[0])**2 +
                (donor.position[1] - recipient.position[1])**2
            )
            if distance > 5:  # Too far
                return False
                
        # Check species compatibility
        if hasattr(donor, 'species') and hasattr(recipient, 'species'):
            # More likely between same species
            if donor.species == recipient.species:
                return random.random() < 0.8
            else:
                # Cross-species is rarer
                return random.random() < 0.2
                
        return True
    
    def simulate_hgt_event(self, population: List[Any]) -> Dict[str, int]:
        """Simulate random HGT events in population"""
        events = {
            'conjugation': 0,
            'transformation': 0,
            'transduction': 0
        }
        
        if len(population) < 2:
            return events
            
        # Conjugation events
        for _ in range(min(10, len(population) // 2)):
            donor = random.choice(population)
            recipient = random.choice(population)
            
            if donor != recipient:
                if self.conjugation(donor, recipient):
                    events['conjugation'] += 1
        
        # Transformation events
        # Create environmental DNA pool
        env_dna = []
        for org in random.sample(population, min(5, len(population))):
            if hasattr(org, 'genome'):
                env_dna.extend(list(org.genome.values())[:2])
        
        if env_dna:
            for _ in range(min(5, len(population) // 4)):
                recipient = random.choice(population)
                if self.transformation(recipient, random.sample(env_dna, min(3, len(env_dna)))):
                    events['transformation'] += 1
        
        # Transduction events
        if self.viruses:
            for _ in range(min(3, len(population) // 10)):
                virus = random.choice(list(self.viruses.values()))
                donor = random.choice(population)
                recipient = random.choice(population)
                
                if donor != recipient:
                    if self.transduction(virus, donor, recipient):
                        events['transduction'] += 1
        
        return events
    
    def analyze_gene_flow(self) -> Dict[str, Any]:
        """Analyze patterns in gene transfer"""
        analysis = {
            'total_transfers': len(self.transfer_history),
            'transfer_types': {},
            'most_transferred_genes': {},
            'species_connectivity': {}
        }
        
        # Count by type
        for transfer in self.transfer_history:
            t_type = transfer['type']
            analysis['transfer_types'][t_type] = analysis['transfer_types'].get(t_type, 0) + 1
            
            # Track gene popularity
            for gene_id in transfer.get('genes', []):
                analysis['most_transferred_genes'][gene_id] = \
                    analysis['most_transferred_genes'].get(gene_id, 0) + 1
        
        return analysis


class LivingCodeOrganism:
    """Organism capable of horizontal gene transfer"""
    
    def __init__(self, organism_id: str, species: str):
        self.id = organism_id
        self.species = species
        self.genome: Dict[str, GeneticElement] = {}
        self.plasmids: List[str] = []
        self.viral_infections: List[str] = []
        self.position = (0, 0)
        self.transformation_competence = 0.1
        self.conjugation_ability = True
        self.acquired_traits: Dict[str, Any] = {}
        
    def get_transferable_genes(self) -> List[GeneticElement]:
        """Get genes that can be transferred"""
        transferable = []
        
        for gene_id, element in self.genome.items():
            # Some genes are more mobile
            if element.metadata.get('mobile', True):
                transferable.append(element)
                
        return transferable
    
    def integrate_foreign_dna(self, element: GeneticElement) -> bool:
        """Integrate foreign genetic element"""
        # Check compatibility
        if not element.is_compatible(self.__class__):
            return False
            
        # Integration with possible modification
        if element.element_type == 'trait':
            # Merge with existing traits
            try:
                new_traits = json.loads(element.code)
                self.acquired_traits.update(new_traits)
                logger.info(f"{self.id} acquired traits: {new_traits}")
                return True
            except:
                return False
                
        # Add to genome
        self.genome[element.element_id] = element
        return True


# Example usage
if __name__ == "__main__":
    # Create HGT network
    hgt_network = HGTNetwork()
    
    # Create some organisms
    organisms = []
    for i in range(5):
        org = LivingCodeOrganism(f"org_{i}", "bacteria_A")
        
        # Add some genes
        gene1 = GeneticElement(
            element_id=f"gene_resistance_{i}",
            element_type="trait",
            source_species="bacteria_A",
            code=json.dumps({"antibiotic_resistance": 0.8}),
            metadata={"mobile": True}
        )
        
        gene2 = GeneticElement(
            element_id=f"gene_metabolism_{i}",
            element_type="trait", 
            source_species="bacteria_A",
            code=json.dumps({"metabolic_efficiency": 0.6}),
            metadata={"mobile": True}
        )
        
        org.genome[gene1.element_id] = gene1
        org.genome[gene2.element_id] = gene2
        
        organisms.append(org)
        
        # Register genes
        hgt_network.register_gene(gene1)
        hgt_network.register_gene(gene2)
    
    # Create a beneficial gene
    super_gene = GeneticElement(
        element_id="super_metabolism",
        element_type="trait",
        source_species="bacteria_B",
        code=json.dumps({"metabolic_efficiency": 0.95, "growth_rate": 1.5}),
        metadata={"mobile": True},
        fitness_impact=0.3
    )
    
    organisms[0].genome[super_gene.element_id] = super_gene
    hgt_network.register_gene(super_gene)
    
    # Simulate HGT
    print("Initial population:")
    for org in organisms:
        print(f"{org.id}: {list(org.genome.keys())}")
    
    print("\nSimulating HGT events...")
    for generation in range(5):
        events = hgt_network.simulate_hgt_event(organisms)
        print(f"Generation {generation + 1}: {events}")
    
    print("\nFinal population:")
    for org in organisms:
        print(f"{org.id}: {list(org.genome.keys())}")
        if org.acquired_traits:
            print(f"  Acquired traits: {org.acquired_traits}")
    
    # Analyze gene flow
    analysis = hgt_network.analyze_gene_flow()
    print(f"\nGene flow analysis: {analysis}")