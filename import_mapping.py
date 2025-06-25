#!/usr/bin/env python3
"""Import mapping for old to new structure"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Import mappings: old import -> new import
IMPORT_MAPPINGS = {
    # Core components
    "from src.core.codecell_example import": "from biocode.domain.entities.base_cell import",
    "from src.core.code_organ import": "from biocode.domain.entities.organ import",
    "from src.core.code_system import": "from biocode.domain.entities.system import",
    "from src.core.code_tissue import": "from biocode.domain.entities.tissue import",
    
    # Components
    "from src.components.tissue_components import": "from biocode.domain.entities.advanced_tissue import",
    "from src.components.system_managers import": "from biocode.domain.entities.system import",
    "from src.components.specialized_cells import": "from biocode.domain.entities.cell import",
    "from src.components.metabolic_system import": "from biocode.domain.entities.cell import",
    
    # Direct imports
    "import src.core": "import biocode.domain.entities",
    "import src.components": "import biocode.domain.entities",
    
    # Specific class mappings
    "CodeCell": "CodeCell",
    "CellState": "CellState",
    "CodeOrgan": "CodeOrgan",
    "CodeSystem": "CodeSystem",
    "CodeTissue": "AdvancedCodeTissue",
    "CompatibilityType": "CompatibilityType",
}

# Files that might need special handling
SPECIAL_CASES = {
    "test_components.py": [
        ("ExtracellularMatrix", "# TODO: Create ExtracellularMatrix in biocode.domain.entities"),
        ("ResourceType", "# TODO: Create ResourceType in biocode.domain.entities"),
        ("SharedResource", "# TODO: Create SharedResource in biocode.domain.entities"),
        ("HomeostasisController", "# TODO: Create HomeostasisController in biocode.domain.entities"),
        ("VascularizationSystem", "# TODO: Create VascularizationSystem in biocode.domain.entities"),
        ("SystemBootManager", "# TODO: Create SystemBootManager in biocode.domain.entities"),
        ("MaintenanceManager", "# TODO: Create MaintenanceManager in biocode.domain.entities"),
        ("SystemMemoryManager", "# TODO: Create SystemMemoryManager in biocode.domain.entities"),
        ("SystemShutdownManager", "# TODO: Create SystemShutdownManager in biocode.domain.entities"),
    ]
}


def fix_imports_in_file(file_path: Path) -> Tuple[bool, List[str]]:
    """Fix imports in a single file"""
    changes_made = False
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply standard mappings
        for old_import, new_import in IMPORT_MAPPINGS.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                changes_made = True
        
        # Handle special cases for specific files
        if file_path.name in SPECIAL_CASES:
            for class_name, replacement in SPECIAL_CASES[file_path.name]:
                if class_name in content and "# TODO:" not in content:
                    # Add TODO comment after imports
                    import_section_end = content.rfind("import")
                    if import_section_end != -1:
                        line_end = content.find("\n", import_section_end)
                        if line_end != -1:
                            content = content[:line_end] + f"\n{replacement}" + content[line_end:]
                            issues.append(f"Missing class {class_name} - added TODO")
        
        # Write back if changes were made
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
        return changes_made, issues
        
    except Exception as e:
        return False, [f"Error processing {file_path}: {str(e)}"]


def fix_all_test_imports(test_dir: Path) -> Dict[str, List[str]]:
    """Fix imports in all test files"""
    results = {}
    
    for test_file in test_dir.glob("**/*.py"):
        if test_file.name.startswith("test_"):
            changed, issues = fix_imports_in_file(test_file)
            if changed or issues:
                results[str(test_file)] = issues
    
    return results


def main():
    """Main function to fix all imports"""
    project_root = Path(__file__).parent
    test_dir = project_root / "tests"
    
    print("🔧 Fixing imports in test files...")
    results = fix_all_test_imports(test_dir)
    
    if results:
        print("\n📝 Import fix results:")
        for file_path, issues in results.items():
            print(f"\n{file_path}:")
            if issues:
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print("  ✅ Imports fixed successfully")
    else:
        print("✅ No import fixes needed")
    
    # Also fix imports in src files if needed
    src_dir = project_root / "src"
    for py_file in src_dir.glob("**/*.py"):
        changed, issues = fix_imports_in_file(py_file)
        if changed:
            print(f"Fixed imports in {py_file}")


if __name__ == "__main__":
    main()