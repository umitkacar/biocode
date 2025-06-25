import asyncio
import os
import sys
from datetime import datetime

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.code_organ import CodeOrgan, CompatibilityType, OrganHealth, DataFlowController
from src.core.advanced_codetissue import AdvancedCodeTissue
from src.core.enhanced_codecell import EnhancedCodeCell


class TestCodeOrgan:
    """Test suite for CodeOrgan"""

    def test_organ_creation(self):
        """Test basic organ creation"""
        organ = CodeOrgan("liver", compatibility=CompatibilityType.TYPE_O)
        
        assert organ.name == "liver"
        assert organ.compatibility_type == CompatibilityType.TYPE_O
        assert len(organ.tissues) == 0
        assert organ.health is not None
        assert organ.data_flow_controller is not None

    def test_compatibility_types(self):
        """Test blood type compatibility"""
        # Type O can donate to all
        o_organ = CodeOrgan("kidney_o", compatibility=CompatibilityType.TYPE_O)
        assert o_organ.is_compatible_with(CompatibilityType.TYPE_A)
        assert o_organ.is_compatible_with(CompatibilityType.TYPE_B)
        assert o_organ.is_compatible_with(CompatibilityType.TYPE_AB)
        assert o_organ.is_compatible_with(CompatibilityType.TYPE_O)
        
        # Type A can donate to A and AB
        a_organ = CodeOrgan("kidney_a", compatibility=CompatibilityType.TYPE_A)
        assert a_organ.is_compatible_with(CompatibilityType.TYPE_A)
        assert not a_organ.is_compatible_with(CompatibilityType.TYPE_B)
        assert a_organ.is_compatible_with(CompatibilityType.TYPE_AB)
        assert not a_organ.is_compatible_with(CompatibilityType.TYPE_O)

    def test_add_tissue(self):
        """Test adding tissue to organ"""
        organ = CodeOrgan("brain")
        tissue = AdvancedCodeTissue("cortex")
        
        organ.add_tissue(tissue, role="thinking")
        
        assert "cortex" in organ.tissues
        assert organ.tissues["cortex"] == tissue
        assert organ.tissue_roles["cortex"] == "thinking"

    def test_add_duplicate_tissue(self):
        """Test adding duplicate tissue"""
        organ = CodeOrgan("brain")
        tissue = AdvancedCodeTissue("cortex")
        
        organ.add_tissue(tissue)
        
        with pytest.raises(ValueError, match="already exists"):
            organ.add_tissue(tissue)

    def test_remove_tissue(self):
        """Test removing tissue from organ"""
        organ = CodeOrgan("liver")
        tissue = AdvancedCodeTissue("hepatic")
        
        organ.add_tissue(tissue)
        removed = organ.remove_tissue("hepatic")
        
        assert removed == tissue
        assert "hepatic" not in organ.tissues
        assert "hepatic" not in organ.tissue_roles

    def test_organ_health_monitoring(self):
        """Test organ health metrics"""
        organ = CodeOrgan("heart")
        health = organ.health
        
        assert isinstance(health, OrganHealth)
        assert health.blood_flow == 100.0
        assert health.oxygen_level == 98.0
        assert health.toxin_level == 0.0
        assert health.inflammation == 0.0
        assert health.scar_tissue == 0.0

    def test_update_health(self):
        """Test health updates"""
        organ = CodeOrgan("liver")
        
        # Simulate stress
        organ.health.toxin_level = 20.0
        organ.health.inflammation = 15.0
        organ.update_health()
        
        # Check if health degraded
        assert organ.health.blood_flow < 100.0
        assert organ.health.oxygen_level < 98.0

    @pytest.mark.asyncio
    async def test_process_data_simple(self):
        """Test simple data processing through organ"""
        organ = CodeOrgan("processor")
        tissue = AdvancedCodeTissue("compute_tissue")
        tissue.register_cell_type(EnhancedCodeCell)
        
        # Add a processing cell
        cell = tissue.grow_cell("processor_1", "EnhancedCodeCell")
        organ.add_tissue(tissue)
        
        # Process data
        result = await organ.process_data({"value": 42}, "compute_tissue")
        
        assert result is not None

    def test_data_flow_controller(self):
        """Test data flow controller"""
        controller = DataFlowController("test_organ")
        
        # Create channel
        channel = controller.create_channel("main", capacity=100)
        assert channel.capacity == 100
        assert channel.current_load == 0
        
        # Test flow rate
        controller.set_flow_rate("main", 2.0)
        assert controller.channels["main"].flow_rate == 2.0

    @pytest.mark.asyncio
    async def test_backpressure_management(self):
        """Test backpressure in data flow"""
        controller = DataFlowController("test_organ")
        channel = controller.create_channel("test", capacity=10)
        
        # Fill channel to capacity
        for i in range(10):
            await controller.send_data("test", {"item": i})
        
        # Channel should be at capacity
        assert channel.current_load == 10
        assert channel.pressure >= 1.0

    def test_predict_failure(self):
        """Test failure prediction"""
        organ = CodeOrgan("kidney")
        
        # Degrade health
        organ.health.blood_flow = 40.0
        organ.health.oxygen_level = 60.0
        organ.health.toxin_level = 50.0
        
        failure_risk = organ.predict_failure()
        
        assert failure_risk > 0.5  # High risk
        assert "blood_flow" in organ.failure_patterns
        assert "toxins" in organ.failure_patterns

    def test_transplant_preparation(self):
        """Test organ transplant preparation"""
        organ = CodeOrgan("heart", compatibility=CompatibilityType.TYPE_A)
        tissue = AdvancedCodeTissue("cardiac_tissue")
        organ.add_tissue(tissue)
        
        # Prepare for transplant
        transplant_data = organ.prepare_for_transplant()
        
        assert transplant_data["organ_name"] == "heart"
        assert transplant_data["compatibility_type"] == CompatibilityType.TYPE_A
        assert transplant_data["health_status"] is not None
        assert "tissues" in transplant_data

    def test_hot_swap_tissue(self):
        """Test hot swapping tissue"""
        organ = CodeOrgan("liver")
        
        # Add original tissue
        old_tissue = AdvancedCodeTissue("old_hepatic")
        organ.add_tissue(old_tissue)
        
        # Create new tissue
        new_tissue = AdvancedCodeTissue("new_hepatic")
        
        # Hot swap
        success = organ.hot_swap_tissue("old_hepatic", new_tissue)
        
        assert success
        assert "old_hepatic" not in organ.tissues
        assert "new_hepatic" in organ.tissues

    def test_get_diagnostics(self):
        """Test organ diagnostics"""
        organ = CodeOrgan("brain")
        tissue1 = AdvancedCodeTissue("cortex")
        tissue2 = AdvancedCodeTissue("hippocampus")
        
        organ.add_tissue(tissue1)
        organ.add_tissue(tissue2)
        
        diagnostics = organ.get_diagnostics()
        
        assert diagnostics["organ_name"] == "brain"
        assert len(diagnostics["tissues"]) == 2
        assert "health" in diagnostics
        assert "data_flow" in diagnostics
        assert "failure_risk" in diagnostics