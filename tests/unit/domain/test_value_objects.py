"""Tests for domain value objects"""
import pytest
from biocode.domain.value_objects.dna import DNA


class TestDNA:
    """Test DNA value object"""
    
    def test_dna_creation(self):
        """Test creating DNA with valid sequence"""
        dna = DNA("ACGTACGT")
        assert dna.sequence == "ACGTACGT"
        assert len(dna) == 8
    
    def test_dna_validation(self):
        """Test DNA validation"""
        # Valid sequences
        assert DNA("ACGT").sequence == "ACGT"
        assert DNA("acgt").sequence == "acgt"  # Lowercase should work
        
        # Invalid sequences
        with pytest.raises(ValueError, match="invalid nucleotides"):
            DNA("ACGTX")  # X is not valid
        
        with pytest.raises(ValueError, match="cannot be empty"):
            DNA("")
    
    def test_dna_random(self):
        """Test random DNA generation"""
        dna1 = DNA.random(100)
        dna2 = DNA.random(100)
        
        assert len(dna1) == 100
        assert len(dna2) == 100
        assert dna1.sequence != dna2.sequence  # Should be different
        
        # Check all nucleotides are valid
        for nucleotide in dna1.sequence:
            assert nucleotide in "ACGT"
    
    def test_dna_from_template(self):
        """Test creating DNA from template"""
        template = "  acgtACGT  "
        dna = DNA.from_template(template)
        assert dna.sequence == "ACGTACGT"  # Should be uppercase and stripped
    
    def test_dna_mutate(self):
        """Test DNA mutation"""
        original = DNA("AAAA")
        
        # No mutation
        mutated = original.mutate(0.0)
        assert mutated.sequence == original.sequence
        
        # High mutation rate
        mutated = original.mutate(1.0)
        assert mutated.sequence != original.sequence
        assert len(mutated) == len(original)
        
        # Check mutation rate bounds
        with pytest.raises(ValueError):
            original.mutate(-0.1)
        with pytest.raises(ValueError):
            original.mutate(1.1)
    
    def test_dna_replicate(self):
        """Test DNA replication"""
        original = DNA("ACGT")
        copy = original.replicate()
        
        assert copy.sequence == original.sequence
        assert copy is not original  # Should be different object
    
    def test_dna_hash(self):
        """Test DNA hashing"""
        dna = DNA("ACGT")
        hash1 = dna.get_hash()
        
        assert isinstance(hash1, str)
        assert len(hash1) == 16
        
        # Same sequence should give same hash
        dna2 = DNA("ACGT")
        assert dna2.get_hash() == hash1
        
        # Different sequence should give different hash
        dna3 = DNA("TGCA")
        assert dna3.get_hash() != hash1
    
    def test_gc_content(self):
        """Test GC content calculation"""
        assert DNA("AAAA").get_gc_content() == 0.0
        assert DNA("GGGG").get_gc_content() == 100.0
        assert DNA("CCCC").get_gc_content() == 100.0
        assert DNA("ACGT").get_gc_content() == 50.0
        assert DNA("AATT").get_gc_content() == 0.0
        assert DNA("GGCC").get_gc_content() == 100.0
    
    def test_find_motif(self):
        """Test motif finding"""
        dna = DNA("ACGTACGTACGT")
        
        # Find existing motif
        positions = dna.find_motif("ACGT")
        assert positions == [0, 4, 8]
        
        # Find non-existing motif
        positions = dna.find_motif("TTTT")
        assert positions == []
        
        # Case insensitive
        positions = dna.find_motif("acgt")
        assert positions == [0, 4, 8]
    
    def test_to_rna(self):
        """Test DNA to RNA transcription"""
        dna = DNA("ACGT")
        rna = dna.to_rna()
        assert rna == "ACGU"
        
        dna2 = DNA("TTTT")
        rna2 = dna2.to_rna()
        assert rna2 == "UUUU"
    
    def test_dna_string_representation(self):
        """Test string representations"""
        # Short sequence
        short_dna = DNA("ACGT")
        assert str(short_dna) == "DNA(ACGT)"
        assert repr(short_dna) == "DNA(sequence='ACGT')"
        
        # Long sequence
        long_sequence = "A" * 60
        long_dna = DNA(long_sequence)
        assert str(long_dna) == f"DNA({'A' * 25}...{'A' * 25})"