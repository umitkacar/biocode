"""DNA Value Object"""
import random
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import hashlib


@dataclass(frozen=True)
class DNA:
    """Immutable DNA sequence value object"""
    sequence: str
    
    def __post_init__(self):
        """Validate DNA sequence"""
        if not self.sequence:
            raise ValueError("DNA sequence cannot be empty")
            
        # Validate nucleotides
        valid_nucleotides = set("ACGT")
        if not all(n in valid_nucleotides for n in self.sequence.upper()):
            raise ValueError("DNA sequence contains invalid nucleotides")
            
    @classmethod
    def random(cls, length: int = 100) -> "DNA":
        """Generate random DNA sequence"""
        nucleotides = "ACGT"
        sequence = "".join(random.choice(nucleotides) for _ in range(length))
        return cls(sequence)
        
    @classmethod
    def from_template(cls, template: str) -> "DNA":
        """Create DNA from template"""
        # Clean and validate template
        cleaned = template.upper().strip()
        return cls(cleaned)
        
    def mutate(self, mutation_rate: float = 0.01) -> "DNA":
        """Create mutated copy of DNA"""
        if not 0 <= mutation_rate <= 1:
            raise ValueError("Mutation rate must be between 0 and 1")
            
        nucleotides = "ACGT"
        mutated_sequence = []
        
        for nucleotide in self.sequence:
            if random.random() < mutation_rate:
                # Mutation occurs
                new_nucleotide = random.choice([n for n in nucleotides if n != nucleotide])
                mutated_sequence.append(new_nucleotide)
            else:
                mutated_sequence.append(nucleotide)
                
        return DNA("".join(mutated_sequence))
        
    def replicate(self) -> "DNA":
        """Create exact copy of DNA"""
        return DNA(self.sequence)
        
    def get_hash(self) -> str:
        """Get unique hash of DNA sequence"""
        return hashlib.sha256(self.sequence.encode()).hexdigest()[:16]
        
    def get_gc_content(self) -> float:
        """Calculate GC content percentage"""
        gc_count = self.sequence.count('G') + self.sequence.count('C')
        return (gc_count / len(self.sequence)) * 100
        
    def find_motif(self, motif: str) -> List[int]:
        """Find all occurrences of a motif"""
        positions = []
        motif = motif.upper()
        
        for i in range(len(self.sequence) - len(motif) + 1):
            if self.sequence[i:i + len(motif)] == motif:
                positions.append(i)
                
        return positions
        
    def to_rna(self) -> str:
        """Transcribe DNA to RNA"""
        return self.sequence.replace('T', 'U')
        
    def __len__(self) -> int:
        return len(self.sequence)
        
    def __str__(self) -> str:
        if len(self.sequence) > 50:
            return f"DNA({self.sequence[:25]}...{self.sequence[-25:]})"
        return f"DNA({self.sequence})"
        
    def __repr__(self) -> str:
        return f"DNA(sequence='{self.sequence}')"