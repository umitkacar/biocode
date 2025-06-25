import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from .enhanced_codecell import CellState, EnhancedCodeCell


class CellTemplate:
    """Cell template for stem cell differentiation"""

    def __init__(self, template_name: str, base_class: Type[EnhancedCodeCell]):
        self.template_name = template_name
        self.base_class = base_class
        self.creation_time = datetime.now()
        self.usage_count = 0
        self.success_rate = 1.0
        self.metadata: Dict[str, Any] = {}

    def instantiate(self, cell_name: str, **kwargs) -> EnhancedCodeCell:
        """Template'den yeni cell oluştur"""
        self.usage_count += 1
        cell = self.base_class(cell_name, **kwargs)
        return cell


class StemCell(EnhancedCodeCell):
    """Pluripotent stem cell - can differentiate into any cell type"""

    def __init__(self, name: str):
        super().__init__(name, cell_type="stem")
        self.potency = "pluripotent"  # pluripotent, multipotent, unipotent
        self.differentiation_potential = 1.0

    def differentiate(
        self, target_type: Type[EnhancedCodeCell], **kwargs
    ) -> EnhancedCodeCell:
        """Stem cell'i başka cell tipine dönüştür"""
        if self.differentiation_potential < 0.3:
            raise Exception("Cell has lost differentiation potential")

        if self.state != CellState.HEALTHY:
            raise Exception("Only healthy cells can differentiate")

        # Create new specialized cell
        new_cell = target_type(f"{self.name}_diff", **kwargs)

        # Transfer some properties
        new_cell.energy_level = self.energy_level * 0.8
        new_cell.epigenetic_markers = self.epigenetic_markers.copy()

        # Reduce differentiation potential
        self.differentiation_potential *= 0.9

        return new_cell


class StemCellBank:
    """Stem cell ve template storage facility"""

    def __init__(self, bank_name: str):
        self.bank_name = bank_name
        self.stem_cells: Dict[str, StemCell] = {}
        self.templates: Dict[str, CellTemplate] = {}
        self.storage_path = Path(f"./cell_banks/{bank_name}")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Bank statistics
        self.total_stored = 0
        self.total_retrieved = 0
        self.success_rate = 1.0

    def store_stem_cell(self, stem_cell: StemCell, preserve_state: bool = True):
        """Stem cell'i bankaya kaydet"""
        cell_id = f"{stem_cell.name}_{datetime.now().isoformat()}"

        if preserve_state:
            # Cryopreservation - freeze current state
            self._cryopreserve(stem_cell, cell_id)

        self.stem_cells[cell_id] = stem_cell
        self.total_stored += 1

        return cell_id

    def retrieve_stem_cell(self, cell_id: str) -> Optional[StemCell]:
        """Bankadan stem cell al"""
        if cell_id not in self.stem_cells:
            return None

        cell = self.stem_cells.pop(cell_id)

        # Thaw process
        self._thaw_cell(cell)

        self.total_retrieved += 1
        return cell

    def store_template(self, template: CellTemplate):
        """Cell template'i kaydet"""
        self.templates[template.template_name] = template

        # Persist to disk
        template_path = self.storage_path / f"{template.template_name}.template"
        with open(template_path, "w") as f:
            json.dump(
                {
                    "name": template.template_name,
                    "base_class": template.base_class.__name__,
                    "metadata": template.metadata,
                    "creation_time": template.creation_time.isoformat(),
                },
                f,
                indent=2,
            )

    def get_template(self, template_name: str) -> Optional[CellTemplate]:
        """Template'i getir"""
        return self.templates.get(template_name)

    def create_from_template(
        self, template_name: str, cell_name: str, **kwargs
    ) -> Optional[EnhancedCodeCell]:
        """Template'den yeni cell oluştur"""
        template = self.get_template(template_name)
        if not template:
            return None

        try:
            cell = template.instantiate(cell_name, **kwargs)
            return cell
        except Exception:
            self.success_rate *= 0.95  # Reduce success rate on failure
            raise

    def _cryopreserve(self, cell: StemCell, cell_id: str):
        """Cell'i dondur (state preservation)"""
        # Simplified - gerçekte state serialization olurdu
        state_file = self.storage_path / f"{cell_id}.state"

        state_data = {
            "health": cell.health_score,
            "energy": cell.energy_level,
            "mutations": cell.mutations,
            "epigenetic": cell.epigenetic_markers,
            "division_count": cell.division_count,
        }

        with open(state_file, "w") as f:
            json.dump(state_data, f)

    def _thaw_cell(self, cell: StemCell):
        """Cell'i çöz (state restoration)"""
        # Post-thaw recovery period
        cell.state = CellState.STRESSED
        cell.energy_level *= 0.7  # Some energy loss during thaw

    def get_bank_statistics(self) -> Dict[str, Any]:
        """Banka istatistikleri"""
        return {
            "bank_name": self.bank_name,
            "stem_cells_stored": len(self.stem_cells),
            "templates_available": len(self.templates),
            "total_stored": self.total_stored,
            "total_retrieved": self.total_retrieved,
            "success_rate": self.success_rate,
            "storage_efficiency": len(self.stem_cells) / max(self.total_stored, 1),
        }

    def quality_check(self) -> List[str]:
        """Kalite kontrol - bozuk cell'leri tespit et"""
        issues = []

        for cell_id, cell in list(self.stem_cells.items()):
            # Check cell viability
            if cell.state == CellState.DEAD:
                issues.append(f"Dead cell found: {cell_id}")
                del self.stem_cells[cell_id]

            elif cell.differentiation_potential < 0.1:
                issues.append(f"Low differentiation potential: {cell_id}")

            elif cell.division_count > 40:
                issues.append(f"High division count: {cell_id}")

        return issues


# Specialized cell types for differentiation
class NeuronCell(EnhancedCodeCell):
    """Sinir hücresi - Logic processing"""

    def __init__(self, name: str):
        super().__init__(name, cell_type="neuron")
        self.dendrites: List[str] = []  # Input connections
        self.axon_terminals: List[str] = []  # Output connections
        self.neurotransmitters = {"dopamine": 1.0, "serotonin": 1.0, "gaba": 1.0}

    def fire_signal(self, signal_strength: float) -> Dict[str, Any]:
        """Sinyal gönder"""
        if signal_strength < 0.3:  # Threshold
            return {"fired": False}

        return {
            "fired": True,
            "strength": signal_strength * self.neurotransmitters["dopamine"],
            "targets": self.axon_terminals,
        }


class MuscleCell(EnhancedCodeCell):
    """Kas hücresi - High performance operations"""

    def __init__(self, name: str):
        super().__init__(name, cell_type="muscle")
        self.contraction_strength = 1.0
        self.fiber_type = "fast-twitch"  # fast-twitch or slow-twitch
        self.fatigue_level = 0

        # Boost metabolism for muscle cells
        self.metabolism_rate = 1.5

    def contract(self, intensity: float) -> float:
        """Kas kasılması - intensive operation"""
        energy_cost = intensity * 20

        if self.energy_level < energy_cost:
            return 0  # Can't contract without energy

        self.energy_level -= energy_cost
        self.fatigue_level += intensity * 0.1

        actual_strength = self.contraction_strength * (1 - self.fatigue_level)
        return actual_strength * intensity


class ImmuneCell(EnhancedCodeCell):
    """Bağışıklık hücresi - Security and error handling"""

    def __init__(self, name: str):
        super().__init__(name, cell_type="immune")
        self.antibodies: Dict[str, str] = {}  # Pattern -> Response
        self.memory_cells: List[Dict[str, Any]] = []  # Learned threats
        self.phagocytosis_capacity = 10

    def detect_pathogen(self, pattern: Any) -> bool:
        """Tehdit tespiti"""
        pattern_hash = str(hash(str(pattern)))

        # Check if we've seen this before
        if pattern_hash in self.antibodies:
            return True

        # Check against known threat patterns
        threat_patterns = ["sql_injection", "xss", "buffer_overflow"]
        for threat in threat_patterns:
            if threat in str(pattern).lower():
                self.create_antibody(pattern_hash, threat)
                return True

        return False

    def create_antibody(self, pattern_hash: str, threat_type: str):
        """Yeni antibody oluştur"""
        self.antibodies[pattern_hash] = threat_type
        self.memory_cells.append(
            {
                "pattern": pattern_hash,
                "threat": threat_type,
                "timestamp": datetime.now(),
            }
        )

    def phagocytose(self, target: Any) -> bool:
        """Hedefi yok et (cleanup malicious code)"""
        if self.phagocytosis_capacity <= 0:
            return False

        self.phagocytosis_capacity -= 1
        # Cleanup logic here
        return True


# Example usage
if __name__ == "__main__":
    # Create stem cell bank
    bank = StemCellBank("primary_bank")

    # Create and store stem cells
    stem1 = StemCell("stem_001")
    stem2 = StemCell("stem_002")

    id1 = bank.store_stem_cell(stem1)
    id2 = bank.store_stem_cell(stem2)

    # Create cell templates
    neuron_template = CellTemplate("standard_neuron", NeuronCell)
    muscle_template = CellTemplate("fast_muscle", MuscleCell)
    immune_template = CellTemplate("t_cell", ImmuneCell)

    bank.store_template(neuron_template)
    bank.store_template(muscle_template)
    bank.store_template(immune_template)

    # Differentiate stem cell
    stem3 = StemCell("stem_003")
    neuron = stem3.differentiate(NeuronCell)
    print(f"Created neuron: {neuron.get_health_report()}")

    # Create from template
    muscle = bank.create_from_template("fast_muscle", "bicep_001")
    print(f"Created muscle: {muscle.get_health_report()}")

    # Bank statistics
    print(f"Bank stats: {bank.get_bank_statistics()}")
