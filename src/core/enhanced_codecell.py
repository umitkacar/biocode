from typing import Dict, Any, List, Optional, Callable, Set
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass
import hashlib
import inspect
import weakref
from enum import Enum
import threading
from queue import Queue
import asyncio


class CellState(Enum):
    """Cell'in yaşam durumları"""
    DORMANT = "dormant"          # Uyku hali
    HEALTHY = "healthy"          # Sağlıklı
    STRESSED = "stressed"        # Stresli
    INFECTED = "infected"        # Enfekte
    INFLAMED = "inflamed"        # İltihaplı
    HEALING = "healing"          # İyileşiyor
    APOPTOTIC = "apoptotic"      # Programlı ölüm
    DEAD = "dead"               # Ölü


@dataclass
class Receptor:
    """Cell membrane receptor"""
    name: str
    signal_type: type
    callback: Callable
    sensitivity: float = 1.0


@dataclass
class Transporter:
    """Cell membrane transporter"""
    name: str
    direction: str  # 'import' or 'export'
    data_type: type
    transform_func: Optional[Callable] = None


class CellMembrane:
    """Hücre zarı - Interface control ve boundary management"""
    
    def __init__(self, cell: 'EnhancedCodeCell'):
        self.cell = weakref.ref(cell)
        self.receptors: Dict[str, Receptor] = {}
        self.transporters: Dict[str, Transporter] = {}
        self.permeability = 1.0  # 0-1 arası, 1 = tam geçirgen
        self.channels_open = True
        
    def add_receptor(self, receptor: Receptor):
        """Yeni receptor ekle"""
        self.receptors[receptor.name] = receptor
        
    def add_transporter(self, transporter: Transporter):
        """Yeni transporter ekle"""
        self.transporters[transporter.name] = transporter
        
    def receive_signal(self, signal_type: str, signal_data: Any) -> bool:
        """Dışarıdan gelen sinyali al"""
        if not self.channels_open:
            return False
            
        for receptor in self.receptors.values():
            if receptor.signal_type.__name__ == signal_type:
                # Sensitivity check
                if receptor.sensitivity >= 0.5:
                    receptor.callback(signal_data)
                    return True
        return False
        
    def transport_in(self, transporter_name: str, data: Any) -> Any:
        """Veriyi içeri al"""
        if transporter_name not in self.transporters:
            raise ValueError(f"Unknown transporter: {transporter_name}")
            
        transporter = self.transporters[transporter_name]
        if transporter.direction != 'import':
            raise ValueError(f"Transporter {transporter_name} is not for import")
            
        # Transform data if needed
        if transporter.transform_func:
            data = transporter.transform_func(data)
            
        return data
        
    def transport_out(self, transporter_name: str, data: Any) -> Any:
        """Veriyi dışarı gönder"""
        if transporter_name not in self.transporters:
            raise ValueError(f"Unknown transporter: {transporter_name}")
            
        transporter = self.transporters[transporter_name]
        if transporter.direction != 'export':
            raise ValueError(f"Transporter {transporter_name} is not for export")
            
        # Transform data if needed
        if transporter.transform_func:
            data = transporter.transform_func(data)
            
        return data * self.permeability  # Permeability affects output


class Organelle(ABC):
    """Base organelle class"""
    
    def __init__(self, name: str):
        self.name = name
        self.active = True
        self.efficiency = 1.0
        
    @abstractmethod
    def function(self, *args, **kwargs) -> Any:
        """Organelin ana fonksiyonu"""
        pass


class Mitochondria(Organelle):
    """Enerji üretimi - Performance optimization"""
    
    def __init__(self):
        super().__init__("mitochondria")
        self.atp_production = 100
        self.oxygen_consumption = 1.0
        
    def function(self, workload: float) -> Dict[str, float]:
        """Enerji üret"""
        if not self.active:
            return {'atp': 0, 'heat': 0}
            
        atp = self.atp_production * self.efficiency * workload
        heat = workload * 0.3  # Some energy lost as heat
        
        return {
            'atp': atp,
            'heat': heat,
            'efficiency': self.efficiency
        }


class Nucleus(Organelle):
    """Çekirdek - Core logic ve DNA management"""
    
    def __init__(self):
        super().__init__("nucleus")
        self.dna = ""
        self.transcription_rate = 1.0
        
    def function(self, operation: str, *args) -> Any:
        """Core operations"""
        if operation == "transcribe":
            return self._transcribe_dna()
        elif operation == "mutate":
            return self._apply_mutation(*args)
        elif operation == "repair":
            return self._repair_dna()
            
    def _transcribe_dna(self) -> str:
        """DNA'yı RNA'ya çevir (metaphor: kod dökümantasyonu)"""
        return f"Transcribed at rate {self.transcription_rate}"
        
    def _apply_mutation(self, mutation_type: str) -> bool:
        """DNA mutasyonu uygula"""
        # Simplified mutation logic
        return True
        
    def _repair_dna(self) -> bool:
        """DNA onarımı"""
        return True


class Lysosome(Organelle):
    """Atık temizleme - Garbage collection"""
    
    def __init__(self):
        super().__init__("lysosome")
        self.waste_queue = Queue()
        self.enzyme_level = 1.0
        
    def function(self, waste_item: Any = None) -> int:
        """Atık temizle"""
        if waste_item:
            self.waste_queue.put(waste_item)
            
        cleaned = 0
        while not self.waste_queue.empty() and self.enzyme_level > 0.1:
            self.waste_queue.get()
            cleaned += 1
            self.enzyme_level -= 0.01
            
        return cleaned


class EnhancedCodeCell:
    """Gelişmiş CodeCell - Full biological features"""
    
    def __init__(self, name: str, cell_type: str = "generic"):
        # Temel özellikler
        self.name = name
        self.cell_type = cell_type
        self.state = CellState.DORMANT
        self.birth_time = datetime.now()
        self.age = 0
        
        # Sağlık ve metabolizma
        self.health_score = 100
        self.metabolism_rate = 1.0
        self.stress_level = 0
        self.energy_level = 100
        
        # DNA ve mutasyonlar
        self.dna = self._generate_dna()
        self.mutations: List[Dict[str, Any]] = []
        self.epigenetic_markers: Dict[str, bool] = {}
        
        # Cell membrane
        self.membrane = CellMembrane(self)
        
        # Organeller
        self.organelles = {
            'mitochondria': Mitochondria(),
            'nucleus': Nucleus(),
            'lysosome': Lysosome()
        }
        
        # İletişim
        self.signal_queue = Queue()
        self.connected_cells: Set[str] = set()
        
        # Lifecycle
        self.division_count = 0
        self.max_divisions = 50  # Hayflick limit
        self.apoptosis_triggered = False
        
        # İstatistikler
        self.operations_count = 0
        self.error_count = 0
        self.last_error: Optional[Exception] = None
        
        # Initialize
        self._activate()
        
    def _generate_dna(self) -> str:
        """Cell'in unique genetic code'u"""
        source = f"{self.cell_type}_{self.name}_{datetime.now()}"
        return hashlib.sha256(source.encode()).hexdigest()
        
    def _activate(self):
        """Cell'i aktif hale getir"""
        self.state = CellState.HEALTHY
        # Setup default receptors
        self.membrane.add_receptor(Receptor(
            name="stress_signal",
            signal_type=dict,
            callback=self._handle_stress_signal
        ))
        
    def _handle_stress_signal(self, signal_data: Dict[str, Any]):
        """Stres sinyalini işle"""
        stress_amount = signal_data.get('amount', 10)
        self.stress_level += stress_amount
        if self.stress_level > 50:
            self.state = CellState.STRESSED
            
    def perform_operation(self, operation_name: str, *args, **kwargs) -> Any:
        """Cell operasyonu gerçekleştir"""
        try:
            self.operations_count += 1
            
            # Enerji kontrolü
            energy_cost = kwargs.get('energy_cost', 10)
            if self.energy_level < energy_cost:
                raise Exception("Insufficient energy")
                
            self.energy_level -= energy_cost
            
            # Operasyonu gerçekleştir
            result = self._execute_operation(operation_name, *args, **kwargs)
            
            # Metabolizma
            self._metabolize()
            
            return result
            
        except Exception as e:
            self.error_count += 1
            self.last_error = e
            self._handle_error(e)
            raise
            
    def _execute_operation(self, operation_name: str, *args, **kwargs) -> Any:
        """Actual operation execution"""
        # Simplified - normalde operation mapping olurdu
        return f"Executed {operation_name}"
        
    def _metabolize(self):
        """Metabolik işlemler"""
        # Mitokondri ile enerji üret
        if 'mitochondria' in self.organelles:
            energy_result = self.organelles['mitochondria'].function(
                workload=self.metabolism_rate
            )
            self.energy_level += energy_result['atp'] * 0.1
            
        # Lysosome ile atık temizle
        if 'lysosome' in self.organelles:
            self.organelles['lysosome'].function()
            
    def _handle_error(self, error: Exception):
        """Hata durumunu yönet"""
        self.stress_level += 20
        
        if self.error_count > 3:
            self.state = CellState.INFECTED
            
        if self.error_count > 10:
            self.state = CellState.INFLAMED
            
    def divide(self) -> Optional['EnhancedCodeCell']:
        """Cell division - mitosis"""
        if self.division_count >= self.max_divisions:
            # Hayflick limit reached
            return None
            
        if self.state not in [CellState.HEALTHY, CellState.STRESSED]:
            # Unhealthy cells shouldn't divide
            return None
            
        self.division_count += 1
        
        # Create daughter cell
        daughter = EnhancedCodeCell(
            name=f"{self.name}_d{self.division_count}",
            cell_type=self.cell_type
        )
        
        # Copy some properties
        daughter.mutations = self.mutations.copy()
        daughter.epigenetic_markers = self.epigenetic_markers.copy()
        
        # Enegy split
        self.energy_level /= 2
        daughter.energy_level = self.energy_level
        
        return daughter
        
    def trigger_apoptosis(self):
        """Programlı hücre ölümü başlat"""
        if self.apoptosis_triggered:
            return
            
        self.apoptosis_triggered = True
        self.state = CellState.APOPTOTIC
        
        # Cleanup resources
        self._cleanup_resources()
        
        # Signal neighboring cells
        self._send_death_signal()
        
        # Final state
        self.state = CellState.DEAD
        
    def _cleanup_resources(self):
        """Kaynakları temizle"""
        # Close connections
        self.connected_cells.clear()
        
        # Deactivate organelles
        for organelle in self.organelles.values():
            organelle.active = False
            
    def _send_death_signal(self):
        """Ölüm sinyali gönder"""
        death_signal = {
            'type': 'cell_death',
            'cell_name': self.name,
            'timestamp': datetime.now()
        }
        # Simplified - normally would send to connected cells
        
    def apply_epigenetic_change(self, marker: str, active: bool):
        """Epigenetik değişiklik uygula (runtime behavior change)"""
        self.epigenetic_markers[marker] = active
        
        # Apply changes based on marker
        if marker == "high_performance":
            self.metabolism_rate = 2.0 if active else 1.0
        elif marker == "energy_saving":
            self.metabolism_rate = 0.5 if active else 1.0
            
    def get_health_report(self) -> Dict[str, Any]:
        """Detaylı sağlık raporu"""
        return {
            'name': self.name,
            'type': self.cell_type,
            'state': self.state.value,
            'health': self.health_score,
            'energy': self.energy_level,
            'stress': self.stress_level,
            'age': (datetime.now() - self.birth_time).total_seconds(),
            'divisions': self.division_count,
            'errors': self.error_count,
            'operations': self.operations_count,
            'organelle_status': {
                name: org.efficiency 
                for name, org in self.organelles.items()
            }
        }