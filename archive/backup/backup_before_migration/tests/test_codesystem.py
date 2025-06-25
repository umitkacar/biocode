import asyncio
import os
import sys
from datetime import datetime

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.code_system import (
    CodeSystem, ConsciousnessLevel, SystemAI, SystemMemory,
    CircadianScheduler
)
from src.core.code_organ import CodeOrgan
from src.core.advanced_codetissue import AdvancedCodeTissue
from src.core.enhanced_codecell import EnhancedCodeCell


class TestCodeSystem:
    """Test suite for CodeSystem"""

    def test_system_creation(self):
        """Test basic system creation"""
        system = CodeSystem("test_organism")
        
        assert system.name == "test_organism"
        assert len(system.organs) == 0
        assert system.consciousness_level == ConsciousnessLevel.DORMANT
        assert system.neural_ai is not None
        assert system.memory is not None
        assert system.circadian is not None

    def test_add_organ(self):
        """Test adding organ to system"""
        system = CodeSystem("human")
        brain = CodeOrgan("brain")
        
        system.add_organ(brain)
        
        assert "brain" in system.organs
        assert system.organs["brain"] == brain

    def test_consciousness_levels(self):
        """Test consciousness level transitions"""
        system = CodeSystem("ai_system")
        
        # Should start dormant
        assert system.consciousness_level == ConsciousnessLevel.DORMANT
        
        # Awaken the system
        system.awaken()
        assert system.consciousness_level == ConsciousnessLevel.AWAKENING
        
        # Progress to aware
        system.consciousness_level = ConsciousnessLevel.AWARE
        assert system.consciousness_level == ConsciousnessLevel.AWARE

    def test_neural_ai_creation(self):
        """Test neural AI component"""
        ai = SystemAI()
        
        assert len(ai.neural_pathways) == 0
        assert len(ai.learned_patterns) == 0
        assert ai.learning_rate == 0.1

    def test_neural_pathway_learning(self):
        """Test neural pathway formation"""
        ai = SystemAI()
        
        # Create pathway
        pathway = ai.create_pathway("visual", "motor", strength=0.8)
        
        assert pathway is not None
        assert pathway.input_pattern == "visual"
        assert pathway.output_action == "motor"
        assert pathway.strength == 0.8

    def test_pattern_recognition(self):
        """Test pattern learning"""
        ai = SystemAI()
        
        # Learn pattern
        pattern_data = {"input": [1, 0, 1], "output": [0, 1, 0]}
        ai.learn_pattern("xor", pattern_data)
        
        assert "xor" in ai.learned_patterns
        assert "xor" in ai.patterns  # Check actual pattern storage

    def test_system_memory(self):
        """Test memory subsystem"""
        memory = SystemMemory()
        
        # Store in short-term memory
        memory.store_short_term("event1", {"data": "test"})
        # Check if event1 is in short term memory (stored as tuple)
        assert any(item[0] == "event1" for item in memory.short_term_memory)
        
        # Store in long-term memory
        memory.store_long_term("fact1", {"info": "permanent"})
        assert "fact1" in memory.long_term_memory
        
        # Working memory
        memory.update_working_memory("task1", {"status": "active"})
        assert "task1" in memory.working_memory

    def test_memory_consolidation(self):
        """Test memory consolidation"""
        memory = SystemMemory()
        
        # Add multiple short-term memories
        # Add same event multiple times to trigger consolidation
        for i in range(5):
            memory.store_short_term("repeated_event", {"count": i})
        
        # Consolidate memories
        memory.consolidate_memories()
        consolidated = memory.get_consolidated()
        
        assert len(consolidated) > 0

    def test_circadian_scheduler(self):
        """Test circadian rhythm scheduler"""
        scheduler = CircadianScheduler()
        
        # Check phase
        phase = scheduler.get_current_phase()
        assert phase in ["peak", "normal", "sleep", "off_peak"]
        
        # Check if should sleep
        scheduler.last_sleep = datetime.now().timestamp() - 20 * 3600  # 20 hours ago
        assert scheduler.should_sleep()

    @pytest.mark.asyncio
    async def test_system_broadcast(self):
        """Test system-wide broadcasting"""
        system = CodeSystem("broadcast_test")
        
        # Add organs
        brain = CodeOrgan("brain")
        heart = CodeOrgan("heart")
        system.add_organ(brain)
        system.add_organ(heart)
        
        # Broadcast message
        responses = await system.broadcast("status_check", {"type": "health"})
        
        assert len(responses) == 2
        assert "brain" in responses
        assert "heart" in responses

    def test_self_diagnose(self):
        """Test system self-diagnosis"""
        system = CodeSystem("diagnostic_test")
        
        # Add organs with different health states
        healthy_organ = CodeOrgan("liver")
        sick_organ = CodeOrgan("kidney")
        sick_organ.health.toxin_level = 80.0
        
        system.add_organ(healthy_organ)
        system.add_organ(sick_organ)
        
        diagnosis = system.self_diagnose()
        
        assert diagnosis["overall_health"] < 100.0
        assert "kidney" in diagnosis["problem_organs"]
        assert len(diagnosis["recommendations"]) > 0

    def test_evolution(self):
        """Test system evolution"""
        system = CodeSystem("evolving_system")
        
        # Add organ
        brain = CodeOrgan("brain")
        system.add_organ(brain)
        
        # Trigger evolution
        system.evolve(selection_pressure="efficiency")
        
        assert system.generation > 0
        assert len(system.evolutionary_history) > 0

    def test_optimize_system(self):
        """Test system optimization"""
        system = CodeSystem("optimize_test")
        
        # Add components
        organ = CodeOrgan("processor")
        system.add_organ(organ)
        
        # Run optimization
        metrics_before = system.get_system_metrics()
        system.optimize()
        metrics_after = system.get_system_metrics()
        
        # System should maintain or improve metrics
        assert metrics_after["total_health"] >= metrics_before["total_health"]

    @pytest.mark.asyncio
    async def test_dream_state(self):
        """Test dream state processing"""
        system = CodeSystem("dreaming_system")
        
        # Set consciousness to sleeping
        system.consciousness_level = ConsciousnessLevel.DREAMING
        
        # Enter dream state (short duration for test)
        await system.dream(duration=0.1)
        
        # Check if memories were processed
        assert system.consciousness_level == ConsciousnessLevel.DREAMING

    def test_get_system_metrics(self):
        """Test system metrics collection"""
        system = CodeSystem("metrics_test")
        
        # Add organs
        brain = CodeOrgan("brain")
        heart = CodeOrgan("heart")
        system.add_organ(brain)
        system.add_organ(heart)
        
        metrics = system.get_system_metrics()
        
        assert "total_organs" in metrics
        assert metrics["total_organs"] == 2
        assert "consciousness_level" in metrics
        assert "total_health" in metrics
        assert "memory_usage" in metrics

    def test_consciousness_progression(self):
        """Test consciousness level progression"""
        system = CodeSystem("conscious_test")
        
        # Progress through levels
        levels = [
            ConsciousnessLevel.DORMANT,
            ConsciousnessLevel.AWAKENING,
            ConsciousnessLevel.AWARE,
            ConsciousnessLevel.FOCUSED,
            ConsciousnessLevel.HYPERAWARE
        ]
        
        for level in levels:
            system.consciousness_level = level
            assert system.consciousness_level == level
            
            # Check consciousness effects
            if level == ConsciousnessLevel.HYPERAWARE:
                assert system.neural_ai.learning_rate > 0.1  # Enhanced learning

    def test_inter_organ_communication(self):
        """Test communication between organs"""
        system = CodeSystem("communication_test")
        
        # Create organs with tissues and cells
        brain = CodeOrgan("brain")
        brain_tissue = AdvancedCodeTissue("neurons")
        brain_tissue.register_cell_type(EnhancedCodeCell)
        brain_tissue.grow_cell("neuron1", "EnhancedCodeCell")
        brain.add_tissue(brain_tissue)
        
        heart = CodeOrgan("heart")
        heart_tissue = AdvancedCodeTissue("cardiac")
        heart_tissue.register_cell_type(EnhancedCodeCell)
        heart_tissue.grow_cell("cardiac1", "EnhancedCodeCell")
        heart.add_tissue(heart_tissue)
        
        system.add_organ(brain)
        system.add_organ(heart)
        
        # System should maintain organ registry
        assert len(system.organs) == 2
        assert system.get_total_cell_count() == 2