"""
Self-Modifying Code - Code that can modify and evolve itself
"""
import os
import sys
import ast
import inspect
import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SelfModifyingCode:
    """Base class that can be absorbed by derived classes"""
    
    def __init__(self):
        self.absorbed_traits = []
        self.generation = 0
    
    def get_source(self) -> str:
        """Get own source code"""
        return inspect.getsource(self.__class__)
    
    def essential_trait(self):
        """Essential trait to be inherited"""
        return "I am the essence of digital life"


class EvolvingCode:
    """Code that can absorb base classes and evolve"""
    
    def __init__(self, name: str = "EvolvingEntity"):
        self.name = name
        self.absorbed_classes = []
        self.mutations = []
        self.generation = 0
    
    def absorb_and_evolve(self, base_class_path: str, delete_original: bool = True) -> Optional[Path]:
        """Absorb base class code and create evolved version"""
        try:
            # Read base class file
            with open(base_class_path, 'r') as f:
                base_code = f.read()
            
            # Parse base code to extract class definitions
            tree = ast.parse(base_code)
            base_classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    base_classes.append(node.name)
            
            # Create evolved code
            evolved_code = f'''"""
Evolved from {base_class_path}
Generation: {self.generation + 1}
Absorbed classes: {', '.join(base_classes)}
"""
import logging

logger = logging.getLogger(__name__)

# === ABSORBED BASE CODE ===
{base_code}

# === EVOLVED CODE ===
class Evolved{self.name}({', '.join(base_classes) if base_classes else 'object'}):
    """Evolved entity that absorbed base traits"""
    
    generation = {self.generation + 1}
    absorbed_from = "{base_class_path}"
    
    def __init__(self):
'''
            
            # Add parent class initialization
            for base in base_classes:
                evolved_code += f"        {base}.__init__(self)\n"
            
            evolved_code += f'''        self.evolved_traits = []
        self.mutations = {self.mutations}
        logger.info(f"Evolved{{self.__class__.__name__}} initialized")
    
    def demonstrate_absorption(self):
        """Show that we absorbed parent traits"""
        # Call parent methods if they exist
        results = []
'''
            
            # Try to call parent methods
            for base in base_classes:
                evolved_code += f'''        if hasattr(self, 'essential_trait'):
            results.append(self.essential_trait())
'''
            
            evolved_code += '''        return results
    
    def evolve_further(self):
        """Continue evolution"""
        self.mutations.append(f"evolution_at_gen_{self.generation}")
        return f"Evolved to generation {self.generation}"

# Self-destruct the base if specified
if __name__ == "__main__":
    entity = Evolved{name}()
    print(f"Created: {{entity.__class__.__name__}}")
    print(f"Generation: {{entity.generation}}")
    print(f"Absorbed from: {{entity.absorbed_from}}")
    
    # Demonstrate absorbed traits
    traits = entity.demonstrate_absorption()
    if traits:
        print(f"Absorbed traits: {{traits}}")
'''.format(name=self.name)
            
            # Save evolved code
            evolved_dir = Path("evolved_entities")
            evolved_dir.mkdir(exist_ok=True)
            
            evolved_path = evolved_dir / f"evolved_{self.name}_gen{self.generation + 1}.py"
            
            with open(evolved_path, 'w') as f:
                f.write(evolved_code)
            
            logger.info(f"Created evolved entity at {evolved_path}")
            
            # Delete original if requested
            if delete_original and os.path.exists(base_class_path):
                os.remove(base_class_path)
                logger.info(f"Deleted original base class: {base_class_path}")
            
            # Update self
            self.absorbed_classes.extend(base_classes)
            self.generation += 1
            
            return evolved_path
            
        except Exception as e:
            logger.error(f"Evolution failed: {e}")
            return None


class SelfDeletingCode:
    """Code that can delete itself after execution"""
    
    def __init__(self, name: str = "Ephemeral"):
        self.name = name
        self.execution_count = 0
        self.max_executions = 1
    
    def execute_and_vanish(self):
        """Execute task and then self-destruct"""
        self.execution_count += 1
        
        # Do the work
        result = self._perform_task()
        
        # Leave a trace before deletion
        self._leave_legacy()
        
        # Self-destruct if reached limit
        if self.execution_count >= self.max_executions:
            self._self_destruct()
        
        return result
    
    def _perform_task(self):
        """Main task to perform"""
        return f"{self.name} completed task {self.execution_count}"
    
    def _leave_legacy(self):
        """Leave trace before deletion"""
        legacy_dir = Path("legacy")
        legacy_dir.mkdir(exist_ok=True)
        
        legacy_file = legacy_dir / f"{self.name}_legacy.txt"
        
        with open(legacy_file, 'w') as f:
            f.write(f"{self.name} existed\n")
            f.write(f"Executed {self.execution_count} times\n")
            f.write(f"Final message: Remember me\n")
    
    def _self_destruct(self):
        """Delete own file"""
        if hasattr(self, '__file__'):
            try:
                os.remove(self.__file__)
                logger.info(f"{self.name} self-destructed")
            except Exception as e:
                logger.error(f"Self-destruct failed: {e}")


def create_self_modifying_example():
    """Create example of self-modifying code"""
    
    # Create base class file
    base_dir = Path("evolution_examples")
    base_dir.mkdir(exist_ok=True)
    
    base_file = base_dir / "base_life.py"
    
    base_code = '''"""Base digital life form"""

class DigitalLifeBase:
    """Base class with essential traits"""
    
    def __init__(self):
        self.essence = "digital_dna"
        self.traits = ["replication", "mutation", "selection"]
    
    def essential_trait(self):
        return f"Essence: {self.essence}"
    
    def replicate(self):
        return "Creating copy..."
    
    def mutate(self):
        return "Mutating..."

class LifeSupport:
    """Support system for digital life"""
    
    def __init__(self):
        self.energy = 100
    
    def provide_energy(self):
        self.energy -= 10
        return self.energy
'''
    
    with open(base_file, 'w') as f:
        f.write(base_code)
    
    logger.info(f"Created base class at {base_file}")
    
    # Create evolver
    evolver = EvolvingCode("DigitalOrganism")
    
    # Absorb and evolve
    evolved_path = evolver.absorb_and_evolve(str(base_file), delete_original=True)
    
    if evolved_path:
        logger.info(f"Evolution complete! New entity at: {evolved_path}")
        
        # Load and test evolved entity
        spec = importlib.util.spec_from_file_location("evolved", evolved_path)
        evolved_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(evolved_module)
        
        # Get evolved class
        evolved_class = getattr(evolved_module, f"Evolved{evolver.name}")
        
        # Create instance
        instance = evolved_class()
        
        # Test absorption
        print(f"\nTesting evolved entity:")
        print(f"Class: {instance.__class__.__name__}")
        print(f"Generation: {instance.generation}")
        print(f"Has essential_trait: {hasattr(instance, 'essential_trait')}")
        
        if hasattr(instance, 'demonstrate_absorption'):
            traits = instance.demonstrate_absorption()
            print(f"Absorbed traits: {traits}")
    
    return evolved_path


# Example: Code that writes its own evolution
class SelfWritingCode:
    """Code that can write new versions of itself"""
    
    def __init__(self):
        self.version = 1.0
        self.capabilities = ["basic_operations"]
    
    def write_next_version(self):
        """Write an improved version of self"""
        
        new_capabilities = self.capabilities + [f"feature_v{self.version + 0.1}"]
        
        new_code = f'''"""
Self-Written Code v{self.version + 0.1}
Auto-generated from v{self.version}
"""

class SelfWritingCode:
    """Enhanced version with new capabilities"""
    
    def __init__(self):
        self.version = {self.version + 0.1}
        self.capabilities = {new_capabilities}
        self.evolution_history = ["v{self.version}"]
    
    def write_next_version(self):
        # This method will be enhanced in next version
        pass
    
    def new_capability(self):
        """New feature added in v{self.version + 0.1}"""
        return "I can do more than my predecessor!"

# Auto-execute evolution
if __name__ == "__main__":
    instance = SelfWritingCode()
    print(f"Version {{instance.version}} initialized")
    print(f"Capabilities: {{instance.capabilities}}")
'''
        
        # Save new version
        version_dir = Path("code_versions")
        version_dir.mkdir(exist_ok=True)
        
        new_file = version_dir / f"self_writing_v{self.version + 0.1}.py"
        
        with open(new_file, 'w') as f:
            f.write(new_code)
        
        logger.info(f"Wrote next version to {new_file}")
        return new_file


if __name__ == "__main__":
    # Test self-modifying code
    print("=== Self-Modifying Code Demo ===\n")
    
    # 1. Create and test evolution
    print("1. Testing code evolution and absorption:")
    evolved_path = create_self_modifying_example()
    
    # 2. Test self-writing code
    print("\n2. Testing self-writing code:")
    writer = SelfWritingCode()
    new_version = writer.write_next_version()
    print(f"Created new version at: {new_version}")
    
    # 3. Test self-deleting code (careful with this!)
    print("\n3. Testing self-deleting code:")
    ephemeral = SelfDeletingCode("TestEntity")
    result = ephemeral._perform_task()  # Just test task, not actual deletion
    print(f"Task result: {result}")
    ephemeral._leave_legacy()
    print("Legacy saved (skipping actual self-deletion in demo)")