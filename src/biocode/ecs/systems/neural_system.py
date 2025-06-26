"""
Neural System - Processes neural activity
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from typing import Tuple, Type, Dict, List
from ..system import System
from ..entity import Entity
from ..components.specialized import NeuralComponent
from ..components.communication import CommunicationComponent, Signal, SignalType
import time


class NeuralSystem(System):
    """
    Sinir sistemi
    
    - Neural integration
    - Spike generation
    - Synaptic transmission
    """
    
    def __init__(self, priority: int = 4):
        super().__init__(priority)
        self.total_spikes = 0
        self.network_activity = 0.0
        
    def required_components(self) -> Tuple[Type, ...]:
        return (NeuralComponent,)
        
    def process_batch(self, entities: List[Entity], delta_time: float):
        """Process neural network as a whole"""
        current_time = time.time()
        
        # Build network map for efficient lookup
        neuron_map: Dict[str, Entity] = {
            e.id: e for e in entities if self.matches_entity(e)
        }
        
        # Process each neuron
        for entity in entities:
            if not self.matches_entity(entity):
                continue
                
            neural = entity.get_component(NeuralComponent)
            
            # Collect input from connected neurons
            total_input = 0.0
            
            for input_id in neural.dendrite_connections:
                if input_id in neuron_map:
                    input_entity = neuron_map[input_id]
                    input_neural = input_entity.get_component(NeuralComponent)
                    
                    # Check if input neuron spiked recently
                    if (input_neural.last_spike_time > 0 and 
                        current_time - input_neural.last_spike_time < 0.01):  # 10ms window
                        
                        # Apply synaptic weight
                        weight = neural.synaptic_weights.get(input_id, 1.0)
                        total_input += weight * 20.0  # Spike current
                        
            # Add any external input from communication
            if entity.has_component(CommunicationComponent):
                comm = entity.get_component(CommunicationComponent)
                signals = comm.process_incoming()
                
                for signal in signals:
                    if signal.type == SignalType.ELECTRICAL:
                        total_input += signal.strength * 10.0
                        
            # Integrate input
            neural.integrate_input(total_input, delta_time)
            
            # Check for spike
            if neural.check_spike(current_time):
                self.total_spikes += 1
                
                # Send spike to connected neurons
                if entity.has_component(CommunicationComponent):
                    comm = entity.get_component(CommunicationComponent)
                    
                    # Send to all axon connections
                    for target_id in neural.axon_connections:
                        comm.emit_signal(
                            signal_type=SignalType.ELECTRICAL,
                            strength=1.0,
                            source_id=entity.id,
                            target_id=target_id,
                            payload={"spike_time": current_time},
                            timestamp=current_time
                        )
                        
            # Reset after spike
            if neural.membrane_potential > 0:
                neural.reset_after_spike()
                
        # Update network activity
        self._update_network_activity(entities)
        
    def process(self, entity: Entity, delta_time: float):
        """Single neuron processing - handled in batch"""
        pass
        
    def _update_network_activity(self, entities: List[Entity]):
        """Calculate overall network activity"""
        total_rate = 0.0
        neuron_count = 0
        
        for entity in entities:
            if self.matches_entity(entity):
                neural = entity.get_component(NeuralComponent)
                total_rate += neural.get_firing_rate()
                neuron_count += 1
                
        self.network_activity = total_rate / max(1, neuron_count)
        
    def get_stats(self) -> dict:
        """Get system statistics"""
        stats = super().get_stats()
        stats.update({
            "total_spikes": self.total_spikes,
            "network_activity": self.network_activity,
            "avg_firing_rate": self.network_activity
        })
        return stats