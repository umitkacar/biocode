import os
import sys
from datetime import datetime, timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.stem_cell_system import (
    StemCell, StemCellBank, CellTemplate,
    NeuronCell, MuscleCell, ImmuneCell
)
from biocode.domain.entities.cell import EnhancedCodeCell, CellState


class TestStemCell:
    """Test suite for StemCell"""

    def test_stem_cell_creation(self):
        """Test basic stem cell creation"""
        stem_cell = StemCell("stem_1")
        
        assert stem_cell.name == "stem_1"
        assert stem_cell.potency == "pluripotent"
        assert stem_cell.differentiation_potential == 1.0
        assert stem_cell.cell_type == "stem"

    def test_stem_cell_properties(self):
        """Test stem cell properties"""
        stem_cell = StemCell("test_stem")
        
        # Check basic properties
        assert stem_cell.potency == "pluripotent"
        assert stem_cell.differentiation_potential == 1.0
        assert stem_cell.health_score == 100

    def test_differentiation(self):
        """Test stem cell differentiation"""
        stem_cell = StemCell("stem_diff")
        
        # Activate the cell first
        stem_cell.state = CellState.HEALTHY
        
        # Differentiate to neuron
        neuron = stem_cell.differentiate(NeuronCell)
        
        assert isinstance(neuron, NeuronCell)
        assert neuron.name == "stem_diff_diff"
        assert neuron.cell_type == "neuron"
        
        # Stem cell loses some potential
        assert stem_cell.differentiation_potential < 1.0

    def test_failed_differentiation(self):
        """Test differentiation failure conditions"""
        stem_cell = StemCell("stem_fail")
        
        # Low differentiation potential
        stem_cell.differentiation_potential = 0.2
        
        with pytest.raises(Exception, match="lost differentiation potential"):
            stem_cell.differentiate(MuscleCell)

    def test_unhealthy_differentiation(self):
        """Test unhealthy cells cannot differentiate"""
        stem_cell = StemCell("sick_stem")
        stem_cell.state = CellState.INFECTED
        
        with pytest.raises(Exception, match="Only healthy cells"):
            stem_cell.differentiate(ImmuneCell)

    def test_self_renewal(self):
        """Test stem cell self-renewal"""
        stem_cell = StemCell("renewable")
        initial_divisions = stem_cell.division_count
        
        # Activate the cell
        stem_cell.state = CellState.HEALTHY
        
        # Self-renew (use divide method from parent)
        daughter = stem_cell.divide()
        
        assert daughter is not None
        assert stem_cell.division_count == initial_divisions + 1


class TestStemCellBank:
    """Test suite for StemCellBank"""

    def test_bank_creation(self):
        """Test stem cell bank creation"""
        bank = StemCellBank("test_bank")
        
        assert bank.name == "test_bank"
        assert len(bank.stored_cells) == 0
        assert bank.capacity == 1000
        assert len(bank.templates) == 0

    def test_store_cell(self):
        """Test storing cells in bank"""
        bank = StemCellBank("storage_bank")
        stem_cell = StemCell("store_me")
        
        cell_id = bank.store_cell(stem_cell)
        
        assert cell_id in bank.stored_cells
        assert bank.stored_cells[cell_id] == stem_cell

    def test_retrieve_cell(self):
        """Test retrieving cells from bank"""
        bank = StemCellBank("retrieval_bank")
        stem_cell = StemCell("retrieve_me")
        
        # Store and retrieve
        cell_id = bank.store_cell(stem_cell)
        retrieved = bank.retrieve_cell(cell_id)
        
        assert retrieved == stem_cell
        assert cell_id not in bank.stored_cells  # Should be removed

    def test_bank_capacity(self):
        """Test bank capacity limits"""
        bank = StemCellBank("capacity_bank", capacity=5)
        
        # Fill bank
        for i in range(5):
            stem_cell = StemCell(f"cell_{i}")
            bank.store_cell(stem_cell)
        
        # Bank should be full
        assert len(bank.stored_cells) == 5

    def test_cell_templates(self):
        """Test cell template system"""
        bank = StemCellBank("template_bank")
        
        # Register templates
        bank.register_template("neuron", NeuronCell)
        bank.register_template("muscle", MuscleCell)
        
        assert "neuron" in bank.templates
        assert "muscle" in bank.templates
        
        # Create from template
        neuron = bank.create_from_template("neuron", "new_neuron")
        assert isinstance(neuron, NeuronCell)
        assert neuron.name == "new_neuron"


class TestCellTemplate:
    """Test suite for CellTemplate"""

    def test_template_creation(self):
        """Test cell template creation"""
        template = CellTemplate("neuron_template", NeuronCell)
        
        assert template.template_name == "neuron_template"
        assert template.base_class == NeuronCell
        assert template.usage_count == 0
        assert template.success_rate == 1.0

    def test_template_instantiation(self):
        """Test creating cells from template"""
        template = CellTemplate("muscle_template", MuscleCell)
        
        # Create cell from template
        muscle = template.instantiate("bicep")
        
        assert isinstance(muscle, MuscleCell)
        assert muscle.name == "bicep"
        assert template.usage_count == 1


class TestSpecializedCells:
    """Test suite for specialized cell types"""

    def test_neuron_cell(self):
        """Test neuron cell creation"""
        neuron = NeuronCell("brain_neuron")
        
        assert neuron.cell_type == "neuron"
        assert hasattr(neuron, 'neurotransmitter_types')
        assert hasattr(neuron, 'synaptic_strength')

    def test_muscle_cell(self):
        """Test muscle cell creation"""
        muscle = MuscleCell("bicep_cell")
        
        assert muscle.cell_type == "muscle"
        assert hasattr(muscle, 'contraction_strength')
        assert hasattr(muscle, 'fiber_type')

    def test_immune_cell(self):
        """Test immune cell creation"""
        immune = ImmuneCell("tcell")
        
        assert immune.cell_type == "immune"
        assert hasattr(immune, 'recognized_antigens')
        assert hasattr(immune, 'activation_threshold')