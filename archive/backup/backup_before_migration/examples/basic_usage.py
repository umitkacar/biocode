#!/usr/bin/env python3
"""Basic usage example of the Code-Snippet biological code organization system."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from src.core import CodeCell, AdvancedCodeTissue, CodeOrgan, CodeSystem
from src.core import OrganType, CompatibilityType, ConsciousnessLevel

async def main():
    """Demonstrate basic usage of the biological code system."""
    
    # 1. Create a simple cell
    print("1. Creating a basic CodeCell...")
    cell = CodeCell("example_cell")
    print(f"   Cell: {cell.name}, State: {cell.state.value}, Health: {cell.health_score}")
    
    # 2. Create a tissue and add cells
    print("\n2. Creating an AdvancedCodeTissue...")
    tissue = AdvancedCodeTissue("auth_tissue")
    
    # Register cell types
    tissue.register_cell_type(CodeCell)
    
    # Grow cells
    login_cell = tissue.grow_cell("login_cell", "CodeCell")
    session_cell = tissue.grow_cell("session_cell", "CodeCell")
    
    # Connect cells
    tissue.connect_cells("login_cell", "session_cell")
    
    print(f"   Tissue: {tissue.name}, Cells: {list(tissue.cells.keys())}")
    
    # 3. Create an organ
    print("\n3. Creating a CodeOrgan...")
    organ = CodeOrgan(
        "authentication_organ",
        OrganType.PROCESSING,
        CompatibilityType.TYPE_A
    )
    
    # Add tissue to organ
    organ.add_tissue(tissue, role="authentication")
    
    print(f"   Organ: {organ.organ_name}, Type: {organ.organ_type.value}")
    print(f"   Health: {organ.calculate_health():.2f}%")
    
    # 4. Create a system
    print("\n4. Creating a CodeSystem...")
    system = CodeSystem("MyApp")
    
    # Add organ to system
    system.add_organ(organ)
    
    # Boot the system
    print("   Booting system...")
    await system.boot()
    
    print(f"   System: {system.system_name}")
    print(f"   Consciousness: {system.consciousness_level.value}")
    print(f"   Health: {system.get_system_health():.2f}%")
    
    # 5. Demonstrate some operations
    print("\n5. Performing operations...")
    
    # Process a request
    request = {
        'type': 'authentication',
        'operation': 'login',
        'data': {'user': 'test_user'}
    }
    
    result = await organ.process_request(request)
    print(f"   Request processed: {result}")
    
    # Get diagnostics
    print("\n6. System Diagnostics:")
    diagnostics = system.get_full_diagnostics()
    print(f"   - Organs: {len(diagnostics['organs'])}")
    print(f"   - Total Cells: {diagnostics['statistics']['total_cells']}")
    print(f"   - System Uptime: {diagnostics['uptime']:.2f} seconds")
    
    # Shutdown
    print("\n7. Shutting down system...")
    await system.shutdown()
    print("   System shutdown complete.")

if __name__ == "__main__":
    asyncio.run(main())