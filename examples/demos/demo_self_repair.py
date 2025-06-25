#!/usr/bin/env python3
"""
Demo: Self-Repair Capability
"""
import sys
import os
import time
import tempfile
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent.biocode_agent import BioCodeAgent, AgentDNA

print("""
🔧 BioCode Self-Repair Demo
==========================

This demo shows:
1. Error detection in code
2. Automatic patch generation
3. Repair application and testing
""")

# Create a test project with intentional errors
test_dir = tempfile.mkdtemp(prefix="biocode_repair_")
print(f"\n📁 Test directory: {test_dir}")

# Create file with errors
buggy_code = '''
import os
import sys

def process_data(data):
    # Missing return statement
    result = data * 2
    
def divide_numbers(a, b):
    # No zero check
    return a / b
    
def read_file(path):
    # No file existence check
    with open(path, 'r') as f:
        return f.read()
        
def access_dict(data):
    # Unsafe dictionary access
    return data['key']
    
# Undefined variable usage
print(undefined_var)

# Missing import
result = np.array([1, 2, 3])
'''

test_file = Path(test_dir) / "buggy_code.py"
test_file.write_text(buggy_code)

print("📝 Created buggy code file")
print("\n🧬 Creating repair-capable agent...")

# Create agent with repair capability
repair_dna = AgentDNA(
    agent_id="repair_specialist",
    scan_frequency=2.0,
    error_tolerance=5,
    lifespan=300,
    can_evolve=True
)

agent = BioCodeAgent(test_dir, dna=repair_dna, sandbox_mode=False)

print(f"✅ Agent {agent.dna.agent_id} created")
print("\n🚀 Starting agent...")

agent.start()

# Monitor repairs
print("\n⏱️  Monitoring repairs for 30 seconds...")
print("=" * 50)

start_time = time.time()
last_error_count = 0

while time.time() - start_time < 30:
    error_count = len(agent.memory.errors_detected)
    
    if error_count > last_error_count:
        print(f"\n🔍 Detected {error_count - last_error_count} new errors")
        last_error_count = error_count
        
    if agent.repair_cell:
        stats = agent.repair_cell.get_repair_stats()
        if stats['total_repairs'] > 0:
            print(f"\n🔧 Repair Stats:")
            print(f"   Total attempts: {stats['total_repairs']}")
            print(f"   Successful: {stats['successful_repairs']}")
            print(f"   Success rate: {stats['success_rate']:.1%}")
            print(f"   Knowledge patterns: {stats['knowledge_patterns']}")
            
    time.sleep(5)

# Show repaired code
print("\n" + "=" * 50)
print("📄 Repaired code:")
print("=" * 50)

if test_file.exists():
    print(test_file.read_text())

# Cleanup
agent.stop()
print("\n✅ Demo complete!")
print(f"🧹 Cleanup: rm -rf {test_dir}")

# Optional: Actually clean up
# import shutil
# shutil.rmtree(test_dir)