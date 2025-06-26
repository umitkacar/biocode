"""
Communication System - Manages inter-entity signaling
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from typing import Tuple, Type, List, Dict
from ..system import System
from ..entity import Entity
from ..components.communication import CommunicationComponent, Signal
from ..components.movement import PositionComponent
import time


class CommunicationSystem(System):
    """
    İletişim sistemi
    
    - Signal propagation
    - Range-based communication
    - Signal decay
    """
    
    def __init__(self, priority: int = 3):
        super().__init__(priority)
        self.signal_registry: Dict[str, List[Entity]] = {}  # Target ID -> Entities
        self.broadcast_signals: List[Signal] = []
        self.total_signals_sent = 0
        self.total_signals_received = 0
        
    def required_components(self) -> Tuple[Type, ...]:
        return (CommunicationComponent,)
        
    def process_batch(self, entities: List[Entity], delta_time: float):
        """Process all communication entities together for efficiency"""
        current_time = time.time()
        
        # Clear expired signals and collect outgoing
        all_signals: List[tuple[Entity, Signal]] = []
        
        for entity in entities:
            if not self.matches_entity(entity):
                continue
                
            comm = entity.get_component(CommunicationComponent)
            
            # Clear expired signals
            comm.clear_expired_signals(current_time)
            
            # Collect outgoing signals
            outgoing = comm.process_outgoing()
            for signal in outgoing:
                all_signals.append((entity, signal))
                self.total_signals_sent += 1
                
        # Propagate signals
        for sender, signal in all_signals:
            self._propagate_signal(sender, signal, entities)
            
    def process(self, entity: Entity, delta_time: float):
        """Process single entity - handled in batch for efficiency"""
        pass
        
    def _propagate_signal(self, sender: Entity, signal: Signal, 
                         all_entities: List[Entity]):
        """Propagate signal to valid receivers"""
        sender_pos = None
        if sender.has_component(PositionComponent):
            sender_pos = sender.get_component(PositionComponent)
            
        # Targeted signal
        if signal.target_id:
            for receiver in all_entities:
                if receiver.id == signal.target_id:
                    self._try_deliver_signal(sender, receiver, signal, sender_pos)
                    break
        # Broadcast signal
        else:
            for receiver in all_entities:
                if receiver.id != sender.id:  # Don't send to self
                    self._try_deliver_signal(sender, receiver, signal, sender_pos)
                    
    def _try_deliver_signal(self, sender: Entity, receiver: Entity, 
                           signal: Signal, sender_pos: PositionComponent):
        """Attempt to deliver signal to receiver"""
        if not receiver.has_component(CommunicationComponent):
            return
            
        receiver_comm = receiver.get_component(CommunicationComponent)
        
        # Check signal type compatibility
        if signal.type not in receiver_comm.reception_types:
            return
            
        # Calculate signal strength with distance attenuation
        final_strength = signal.strength
        
        if sender_pos and receiver.has_component(PositionComponent):
            receiver_pos = receiver.get_component(PositionComponent)
            distance = sender_pos.distance_to(receiver_pos)
            
            # Check range
            if distance > receiver_comm.reception_range:
                return
                
            # Attenuate signal
            final_strength = signal.attenuate(distance)
            
        # Check sensitivity threshold
        if final_strength < receiver_comm.reception_sensitivity:
            return
            
        # Deliver signal
        delivered_signal = Signal(
            type=signal.type,
            strength=final_strength,
            source_id=signal.source_id,
            target_id=signal.target_id,
            payload=signal.payload.copy(),
            timestamp=signal.timestamp,
            ttl=signal.ttl
        )
        
        if receiver_comm.receive_signal(delivered_signal):
            self.total_signals_received += 1
            
    def get_stats(self) -> dict:
        """Get system statistics"""
        stats = super().get_stats()
        stats.update({
            "total_signals_sent": self.total_signals_sent,
            "total_signals_received": self.total_signals_received,
            "delivery_rate": (self.total_signals_received / 
                            max(1, self.total_signals_sent))
        })
        return stats