import os
import sys
from datetime import datetime, timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.stem_cell_system import (
    StemCell, StemCellBank,
    DifferentiationFactors, Potency
)
from src.core.enhanced_codecell import EnhancedCodeCell


class TestStemCell:
    """Test suite for StemCell"""

    def test_stem_cell_creation(self):
        """Test basic stem cell creation"""
        stem_cell = StemCell("stem_1", potency=Potency.PLURIPOTENT)
        
        assert stem_cell.name == "stem_1"
        assert stem_cell.potency == Potency.PLURIPOTENT
        assert stem_cell.differentiation_potential == 100
        assert not stem_cell.is_differentiated
        assert len(stem_cell.markers) > 0

    def test_potency_levels(self):
        """Test different potency levels"""
        totipotent = StemCell("toti", potency=Potency.TOTIPOTENT)
        pluripotent = StemCell("pluri", potency=Potency.PLURIPOTENT)
        multipotent = StemCell("multi", potency=Potency.MULTIPOTENT)
        unipotent = StemCell("uni", potency=Potency.UNIPOTENT)
        
        # Totipotent can become anything
        assert len(totipotent.possible_fates) > len(pluripotent.possible_fates)
        assert len(pluripotent.possible_fates) > len(multipotent.possible_fates)
        assert len(multipotent.possible_fates) > len(unipotent.possible_fates)

    def test_differentiation_check(self):
        """Test checking if differentiation is possible"""
        stem_cell = StemCell("stem_test", potency=Potency.MULTIPOTENT)
        
        # Should be able to differentiate to allowed types
        assert stem_cell.can_differentiate_to("muscle")
        assert stem_cell.can_differentiate_to("bone")
        
        # May not differentiate to all types
        if stem_cell.potency != Potency.TOTIPOTENT:
            # Find a fate not in possible_fates
            impossible_fate = "exotic_type"
            assert not stem_cell.can_differentiate_to(impossible_fate)

    def test_differentiate(self):
        """Test stem cell differentiation"""
        stem_cell = StemCell("stem_diff", potency=Potency.PLURIPOTENT)
        
        # Apply differentiation factors
        factors = DifferentiationFactors(
            growth_factors=["FGF", "BMP"],
            transcription_factors=["MyoD"],
            environment_signals=["mechanical_stress"],
            epigenetic_modifiers=["methylation"]
        )
        
        # Differentiate
        differentiated_cell = stem_cell.differentiate("muscle", factors)
        
        assert differentiated_cell is not None
        assert isinstance(differentiated_cell, EnhancedCodeCell)
        assert differentiated_cell.cell_type == "muscle"
        assert stem_cell.is_differentiated
        assert stem_cell.differentiation_potential < 100

    def test_failed_differentiation(self):
        """Test differentiation failure"""
        stem_cell = StemCell("stem_fail", potency=Potency.UNIPOTENT)
        
        # Try to differentiate to impossible type
        factors = DifferentiationFactors()
        
        # This should fail for unipotent trying exotic type
        result = stem_cell.differentiate("neuron", factors)
        
        if "neuron" not in stem_cell.possible_fates:
            assert result is None or stem_cell.differentiation_potential < 100

    def test_self_renewal(self):
        """Test stem cell self-renewal"""
        stem_cell = StemCell("renewable", potency=Potency.PLURIPOTENT)
        initial_divisions = stem_cell.division_count
        
        # Self-renew
        daughter = stem_cell.self_renew()
        
        assert daughter is not None
        assert isinstance(daughter, StemCell)
        assert daughter.potency == stem_cell.potency
        assert stem_cell.division_count == initial_divisions + 1

    def test_age_effects(self):
        """Test aging effects on stem cells"""
        stem_cell = StemCell("aging_stem", potency=Potency.MULTIPOTENT)
        
        # Simulate aging
        stem_cell.birth_time = datetime.now() - timedelta(days=100)
        stem_cell.division_count = 40
        
        # Old stem cells have reduced potential
        stem_cell.update_differentiation_potential()
        
        assert stem_cell.differentiation_potential < 100


class TestStemCellBank:
    """Test suite for StemCellBank"""

    def test_bank_creation(self):
        """Test stem cell bank creation"""
        bank = StemCellBank("test_bank")
        
        assert bank.name == "test_bank"
        assert len(bank.stored_cells) == 0
        assert bank.total_capacity == 1000
        assert len(bank.lineage_tracking) == 0

    def test_store_stem_cell(self):
        """Test storing stem cells"""
        bank = StemCellBank("storage_bank")
        stem_cell = StemCell("store_me", potency=Potency.PLURIPOTENT)
        
        stored_id = bank.store_stem_cell(stem_cell)
        
        assert stored_id is not None
        assert stored_id in bank.stored_cells
        assert bank.stored_cells[stored_id] == stem_cell

    def test_retrieve_stem_cell(self):
        """Test retrieving stem cells"""
        bank = StemCellBank("retrieval_bank")
        stem_cell = StemCell("retrieve_me", potency=Potency.MULTIPOTENT)
        
        # Store and retrieve
        cell_id = bank.store_stem_cell(stem_cell)
        retrieved = bank.retrieve_stem_cell(cell_id)
        
        assert retrieved == stem_cell
        assert cell_id not in bank.stored_cells  # Should be removed

    def test_find_compatible_cells(self):
        """Test finding compatible stem cells"""
        bank = StemCellBank("compatibility_bank")
        
        # Store various stem cells
        bank.store_stem_cell(StemCell("pluri1", potency=Potency.PLURIPOTENT))
        bank.store_stem_cell(StemCell("pluri2", potency=Potency.PLURIPOTENT))
        bank.store_stem_cell(StemCell("multi1", potency=Potency.MULTIPOTENT))
        
        # Find cells that can become neurons
        compatible = bank.find_compatible_cells("neuron")
        
        assert len(compatible) >= 2  # Pluripotent cells should match

    def test_bank_capacity(self):
        """Test bank capacity limits"""
        bank = StemCellBank("capacity_bank", capacity=5)
        
        # Fill bank
        for i in range(5):
            stem_cell = StemCell(f"cell_{i}", potency=Potency.MULTIPOTENT)
            bank.store_stem_cell(stem_cell)
        
        # Try to store one more
        extra_cell = StemCell("extra", potency=Potency.UNIPOTENT)
        with pytest.raises(Exception, match="Bank is full"):
            bank.store_stem_cell(extra_cell)

    def test_quality_control(self):
        """Test quality control in bank"""
        bank = StemCellBank("quality_bank")
        
        # Create a degraded stem cell
        bad_cell = StemCell("degraded", potency=Potency.PLURIPOTENT)
        bad_cell.health_score = 20  # Very unhealthy
        bad_cell.differentiation_potential = 10  # Very low potential
        
        # Bank should reject or flag unhealthy cells
        result = bank.quality_check(bad_cell)
        assert not result  # Should fail quality check

    def test_lineage_tracking(self):
        """Test cell lineage tracking"""
        bank = StemCellBank("lineage_bank")
        
        # Create parent stem cell
        parent = StemCell("parent", potency=Potency.PLURIPOTENT)
        parent_id = bank.store_stem_cell(parent)
        
        # Track differentiation
        factors = DifferentiationFactors(growth_factors=["NGF"])
        bank.track_differentiation(parent_id, "neuron", factors)
        
        assert parent_id in bank.lineage_tracking
        assert bank.lineage_tracking[parent_id]["fate"] == "neuron"

    def test_get_bank_statistics(self):
        """Test bank statistics"""
        bank = StemCellBank("stats_bank")
        
        # Add various cells
        bank.store_stem_cell(StemCell("t1", potency=Potency.TOTIPOTENT))
        bank.store_stem_cell(StemCell("p1", potency=Potency.PLURIPOTENT))
        bank.store_stem_cell(StemCell("p2", potency=Potency.PLURIPOTENT))
        bank.store_stem_cell(StemCell("m1", potency=Potency.MULTIPOTENT))
        
        stats = bank.get_statistics()
        
        assert stats["total_cells"] == 4
        assert stats["capacity_used"] == 0.4  # 4/1000
        assert stats["potency_distribution"][Potency.PLURIPOTENT] == 2
        assert stats["potency_distribution"][Potency.TOTIPOTENT] == 1


class TestDifferentiationFactors:
    """Test suite for DifferentiationFactors"""

    def test_differentiation_factors(self):
        """Test differentiation factors"""
        factors = DifferentiationFactors(
            growth_factors=["FGF", "EGF"],
            transcription_factors=["Oct4", "Sox2"],
            environment_signals=["hypoxia"],
            epigenetic_modifiers=["acetylation"]
        )
        
        assert len(factors.growth_factors) == 2
        assert "Oct4" in factors.transcription_factors
        assert "hypoxia" in factors.environment_signals