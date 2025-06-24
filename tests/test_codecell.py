import os
import sys

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.enhanced_codecell import CellState, EnhancedCodeCell


class TestEnhancedCodeCell:
    """Test suite for EnhancedCodeCell"""

    def test_cell_creation(self):
        """Test basic cell creation"""
        cell = EnhancedCodeCell("test_cell", cell_type="test")

        assert cell.name == "test_cell"
        assert cell.cell_type == "test"
        assert cell.state == CellState.HEALTHY
        assert cell.health_score == 100
        assert cell.energy_level == 100
        assert cell.stress_level == 0

    def test_cell_dna_generation(self):
        """Test that cells have unique DNA"""
        cell1 = EnhancedCodeCell("cell1")
        cell2 = EnhancedCodeCell("cell2")

        assert cell1.dna != cell2.dna
        assert len(cell1.dna) == 64  # SHA256 hex length

    def test_cell_infection(self):
        """Test cell infection mechanism"""
        cell = EnhancedCodeCell("test_cell")
        error = Exception("Test error")

        cell.infect(error)

        assert cell.state == CellState.INFECTED
        assert cell.error_count == 1
        assert cell.health_score < 100

    def test_cell_healing(self):
        """Test cell healing mechanism"""
        cell = EnhancedCodeCell("test_cell")
        cell.health_score = 50

        cell.heal()

        assert cell.health_score > 50
        assert cell.health_score <= 100

    def test_cell_division(self):
        """Test cell division (mitosis)"""
        parent_cell = EnhancedCodeCell("parent")
        parent_cell.energy_level = 80

        daughter_cell = parent_cell.divide()

        assert daughter_cell is not None
        assert daughter_cell.name == "parent_d1"
        assert parent_cell.division_count == 1
        assert parent_cell.energy_level == 40  # Energy split
        assert daughter_cell.energy_level == 40

    def test_hayflick_limit(self):
        """Test that cells can't divide beyond Hayflick limit"""
        cell = EnhancedCodeCell("test_cell")
        cell.division_count = cell.max_divisions

        daughter = cell.divide()

        assert daughter is None

    def test_apoptosis(self):
        """Test programmed cell death"""
        cell = EnhancedCodeCell("test_cell")

        cell.trigger_apoptosis()

        assert cell.state == CellState.DEAD
        assert cell.apoptosis_triggered is True
        assert len(cell.connected_cells) == 0

    def test_epigenetic_changes(self):
        """Test epigenetic modifications"""
        cell = EnhancedCodeCell("test_cell")
        original_metabolism = cell.metabolism_rate

        cell.apply_epigenetic_change("high_performance", True)

        assert cell.epigenetic_markers["high_performance"] is True
        assert cell.metabolism_rate > original_metabolism

    @pytest.mark.asyncio
    async def test_perform_operation(self):
        """Test cell operation execution"""
        cell = EnhancedCodeCell("test_cell")

        result = await cell.perform_operation("test_op", energy_cost=10)

        assert result == "Executed test_op"
        # Energy might recover due to metabolism
        assert cell.operations_count == 1

    @pytest.mark.asyncio
    async def test_insufficient_energy(self):
        """Test operation failure with insufficient energy"""
        cell = EnhancedCodeCell("test_cell")
        cell.energy_level = 5

        with pytest.raises(Exception, match="Insufficient energy"):
            await cell.perform_operation("test_op", energy_cost=10)

        assert cell.error_count == 1
        assert cell.stress_level > 0

    def test_cell_membrane_receptors(self):
        """Test cell membrane receptor functionality"""
        cell = EnhancedCodeCell("test_cell")

        # Check default receptor exists
        assert "stress_signal" in cell.membrane.receptors

        # Test signal reception
        result = cell.membrane.receive_signal("dict", {"amount": 30})

        assert result is True
        assert cell.stress_level == 30

    def test_health_report(self):
        """Test health report generation"""
        cell = EnhancedCodeCell("test_cell")
        cell.operations_count = 10
        cell.error_count = 2

        report = cell.get_health_report()

        assert report["name"] == "test_cell"
        assert report["type"] == "generic"
        assert report["state"] == "healthy"
        assert report["operations"] == 10
        assert report["errors"] == 2
        assert "organelle_status" in report
