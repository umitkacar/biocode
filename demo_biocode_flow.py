#!/usr/bin/env python3
"""
BioCode Demo: Cell → Tissue → Organ → System Flow
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

WARNING: This is LIVING CODE that can grow, reproduce, mutate, and die.
Run only in isolated, secure environments. User assumes all risks.
"""
import asyncio
import sys
sys.path.insert(0, 'src')

from biocode.domain.entities.base_cell import CodeCell
from biocode.domain.entities.tissue import AdvancedCodeTissue
from biocode.domain.entities.organ import CodeOrgan, OrganType, CompatibilityType
from biocode.domain.entities.system import CodeSystem, ConsciousnessLevel


async def demo_biocode_flow():
    """Demonstrate the complete BioCode flow"""
    
    print("🧬 BioCode Demo: Building a Living System")
    print("=" * 50)
    
    # Step 1: Create Cells
    print("\n1️⃣ Creating Cells...")
    cells = []
    for i in range(5):
        cell = CodeCell(f"neuron_{i}")
        cells.append(cell)
        print(f"   ✅ Created {cell.name} - Health: {cell.health_score}%")
    
    # Step 2: Create Tissue from Cells
    print("\n2️⃣ Creating Brain Tissue...")
    brain_tissue = AdvancedCodeTissue("cortex")
    
    for i, cell in enumerate(cells):
        brain_tissue.cells[f"neuron_{i}"] = cell
    
    print(f"   ✅ Created tissue '{brain_tissue.name}' with {len(brain_tissue.cells)} cells")
    
    # Test tissue coordination
    print("\n   🔄 Testing tissue coordination...")
    async def think_operation(cell):
        return f"Thinking with {cell.name}"
    
    result = await brain_tissue.execute_coordinated_operation(think_operation)
    print(f"   📊 Coordination result: {len(result)} cells responded")
    
    # Step 3: Create Organ from Tissue
    print("\n3️⃣ Creating Brain Organ...")
    brain = CodeOrgan(
        "brain",
        OrganType.PROCESSING,
        CompatibilityType.TYPE_O  # Universal donor
    )
    
    brain.add_tissue(brain_tissue, role="thinking")
    print(f"   ✅ Created organ '{brain.organ_name}' with {len(brain.tissues)} tissue(s)")
    
    # Check organ health
    brain.update_health()
    print(f"   💚 Organ health: {brain.health.overall_health:.1f}%")
    print(f"   🩸 Blood flow: {brain.health.blood_flow:.1f}%")
    print(f"   💨 Oxygen level: {brain.health.oxygen_level:.1f}%")
    
    # Step 4: Create System and Add Organ
    print("\n4️⃣ Creating Organism System...")
    organism = CodeSystem("demo_organism")
    
    # Boot the system
    await organism.boot()
    print(f"   ✅ System booted - Consciousness: {organism.consciousness_level.value}")
    
    # Add organ to system
    if organism.add_organ(brain):
        print(f"   ✅ Added {brain.organ_name} to system")
    
    # Step 5: Test System Operations
    print("\n5️⃣ Testing System Operations...")
    
    # Awaken the system
    organism.awaken()
    print(f"   👁️ System awakened - Consciousness: {organism.consciousness_level.value}")
    
    # Process a request through the system
    print("\n   📨 Processing request through system...")
    request = {
        "type": "processing",
        "operation": "calculate",
        "data": "2 + 2"
    }
    
    response = await organism.process_request(request)
    print(f"   📤 Response: {response}")
    
    # Get system metrics
    print("\n6️⃣ System Metrics:")
    metrics = organism.get_system_metrics()
    print(f"   📊 Total organs: {metrics['organ_count']}")
    print(f"   🧠 Neural pathways: {metrics['neural_pathways']}")
    print(f"   💾 Memory usage: {metrics['memory_usage']}")
    print(f"   ⏱️ Uptime: {metrics['uptime']:.1f} seconds")
    print(f"   💚 System health: {metrics['total_health']:.1f}%")
    
    # Self diagnosis
    print("\n7️⃣ Self Diagnosis:")
    diagnosis = organism.self_diagnose()
    print(f"   🏥 Overall health: {diagnosis['overall_health']:.1f}%")
    print(f"   ⚠️ Problem organs: {diagnosis['problem_organs']}")
    print(f"   💊 Recommendations: {diagnosis['recommendations']}")
    
    # Evolution
    print("\n8️⃣ System Evolution:")
    print(f"   🧬 Generation: {organism.generation}")
    organism.evolve(selection_pressure="efficiency")
    print(f"   🧬 Evolved to generation: {organism.generation}")
    print(f"   📈 Learning rate: {organism.neural_ai.learning_rate}")
    
    # Shutdown
    print("\n9️⃣ Shutting down system...")
    await organism.shutdown()
    print("   ✅ System shutdown complete")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed successfully!")


if __name__ == "__main__":
    print("\n🚀 Starting BioCode Demo...\n")
    asyncio.run(demo_biocode_flow())