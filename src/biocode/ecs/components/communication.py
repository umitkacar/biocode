"""
Communication Components - Inter-entity messaging
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum


class SignalType(Enum):
    """Types of biological signals"""
    CHEMICAL = "chemical"
    ELECTRICAL = "electrical"
    MECHANICAL = "mechanical"
    OPTICAL = "optical"
    THERMAL = "thermal"


@dataclass
class Signal:
    """Individual signal data"""
    type: SignalType
    strength: float
    source_id: str
    target_id: Optional[str] = None  # None = broadcast
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    ttl: float = 1.0  # Time to live
    
    def is_expired(self, current_time: float) -> bool:
        """Check if signal has expired"""
        return (current_time - self.timestamp) > self.ttl
    
    def attenuate(self, distance: float, decay_rate: float = 0.1) -> float:
        """Calculate signal strength after distance attenuation"""
        return self.strength * (1.0 / (1.0 + decay_rate * distance))


@dataclass
class CommunicationComponent:
    """İletişim verisi"""
    # Signal emission
    emission_range: float = 10.0
    emission_strength: float = 1.0
    emission_types: Set[SignalType] = field(default_factory=lambda: {SignalType.CHEMICAL})
    
    # Signal reception
    reception_range: float = 15.0
    reception_sensitivity: float = 0.1
    reception_types: Set[SignalType] = field(default_factory=lambda: {SignalType.CHEMICAL})
    
    # Signal buffers
    outgoing_signals: List[Signal] = field(default_factory=list)
    incoming_signals: List[Signal] = field(default_factory=list)
    
    # Communication history
    signal_history: List[Signal] = field(default_factory=list)
    max_history_size: int = 100
    
    def emit_signal(self, signal_type: SignalType, strength: float, 
                   source_id: str, payload: Dict[str, Any], 
                   timestamp: float, target_id: Optional[str] = None) -> Signal:
        """Create and queue outgoing signal"""
        if signal_type not in self.emission_types:
            raise ValueError(f"Cannot emit {signal_type} signals")
            
        signal = Signal(
            type=signal_type,
            strength=min(strength, self.emission_strength),
            source_id=source_id,
            target_id=target_id,
            payload=payload,
            timestamp=timestamp
        )
        
        self.outgoing_signals.append(signal)
        return signal
    
    def receive_signal(self, signal: Signal) -> bool:
        """Receive incoming signal if compatible"""
        if signal.type not in self.reception_types:
            return False
            
        if signal.strength < self.reception_sensitivity:
            return False
            
        self.incoming_signals.append(signal)
        
        # Maintain history
        self.signal_history.append(signal)
        if len(self.signal_history) > self.max_history_size:
            self.signal_history.pop(0)
            
        return True
    
    def clear_expired_signals(self, current_time: float):
        """Remove expired signals from buffers"""
        self.incoming_signals = [
            s for s in self.incoming_signals 
            if not s.is_expired(current_time)
        ]
        self.outgoing_signals = [
            s for s in self.outgoing_signals 
            if not s.is_expired(current_time)
        ]
    
    def process_incoming(self) -> List[Signal]:
        """Process and clear incoming signal buffer"""
        signals = self.incoming_signals.copy()
        self.incoming_signals.clear()
        return signals
    
    def process_outgoing(self) -> List[Signal]:
        """Process and clear outgoing signal buffer"""
        signals = self.outgoing_signals.copy()
        self.outgoing_signals.clear()
        return signals


@dataclass
class SignalComponent:
    """Basit sinyal verisi - lightweight alternative"""
    active: bool = False
    signal_type: SignalType = SignalType.CHEMICAL
    intensity: float = 0.0
    frequency: float = 1.0  # Hz for periodic signals
    phase: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def modulate(self, delta_intensity: float):
        """Modulate signal intensity"""
        self.intensity = max(0.0, min(1.0, self.intensity + delta_intensity))
        self.active = self.intensity > 0.0
    
    def oscillate(self, time: float) -> float:
        """Calculate oscillating signal value"""
        if not self.active:
            return 0.0
        import math
        return self.intensity * math.sin(2 * math.pi * self.frequency * time + self.phase)