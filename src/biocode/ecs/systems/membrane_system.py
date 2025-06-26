"""
Membrane System - Manages cellular membrane and transport
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from typing import Tuple, Type, Dict
from ..system import System
from ..entity import Entity
from ..components.membrane import MembraneComponent, TransportType
from ..components.biological import EnergyComponent, HealthComponent
from ..components.communication import CommunicationComponent, Signal, SignalType
import time


class MembraneSystem(System):
    """
    Hücre zarı yönetim sistemi
    
    - Ion transport and membrane potential
    - Receptor binding and signaling
    - Membrane damage and repair
    - Molecular transport
    """
    
    def __init__(self, priority: int = 7):
        super().__init__(priority)
        self.environment_molecules: Dict[str, float] = {
            "glucose": 5.0,  # mM
            "oxygen": 0.8,   # relative
            "amino_acids": 2.0,
            "lipids": 1.0,
            "ions": 150.0
        }
        self.total_transported = 0.0
        self.total_signals_received = 0
        
    def required_components(self) -> Tuple[Type, ...]:
        return (MembraneComponent,)
        
    def process(self, entity: Entity, delta_time: float):
        """Process membrane functions"""
        membrane = entity.get_component(MembraneComponent)
        
        # Update membrane potential
        membrane.update_membrane_potential()
        
        # Process transport
        self._process_transport(entity, membrane, delta_time)
        
        # Process receptor signaling
        self._process_receptors(entity, membrane, delta_time)
        
        # Membrane maintenance
        self._maintain_membrane(entity, membrane, delta_time)
        
        # Check for membrane damage effects
        if membrane.integrity < 0.5:
            entity.add_tag("membrane_damaged")
            
            # Severe damage causes ion imbalance
            if membrane.integrity < 0.2:
                # Catastrophic ion leakage
                membrane.ion_concentrations["Na+_in"] += 10 * delta_time
                membrane.ion_concentrations["K+_in"] -= 10 * delta_time
                membrane.ion_concentrations["Ca2+_in"] += 0.1 * delta_time
                
                # This can trigger cell death
                if entity.has_component(HealthComponent):
                    health = entity.get_component(HealthComponent)
                    health.current -= 5.0 * delta_time
        else:
            entity.remove_tag("membrane_damaged")
            
    def _process_transport(self, entity: Entity, membrane: MembraneComponent, 
                         delta_time: float):
        """Handle molecular transport across membrane"""
        energy = None
        if entity.has_component(EnergyComponent):
            energy = entity.get_component(EnergyComponent)
            
        for name, transporter in membrane.transporters.items():
            molecule = transporter.molecule_type
            
            # Calculate concentration gradient
            env_conc = self.environment_molecules.get(molecule, 0.0)
            # Simplified: assume internal concentration is inverse of health
            internal_conc = 10.0 - env_conc
            gradient = env_conc - internal_conc
            
            # Calculate transport rate
            atp_available = energy.current if energy else 0.0
            transport_rate = transporter.calculate_transport_rate(gradient, atp_available)
            
            if transport_rate > 0:
                # Apply transport
                amount_transported = transport_rate * delta_time
                self.total_transported += amount_transported
                
                # Update energy for active transport
                if transporter.transport_type == TransportType.ACTIVE_TRANSPORT and energy:
                    energy_cost = transporter.energy_cost * amount_transported
                    energy.current = max(0, energy.current - energy_cost)
                    
                # Special handling for specific molecules
                if molecule == "glucose" and energy:
                    # Glucose provides energy
                    energy.current = min(energy.maximum, energy.current + amount_transported * 2.0)
                    
    def _process_receptors(self, entity: Entity, membrane: MembraneComponent,
                          delta_time: float):
        """Handle receptor binding and signaling"""
        # Check for communication signals
        if entity.has_component(CommunicationComponent):
            comm = entity.get_component(CommunicationComponent)
            
            # Process incoming chemical signals
            signals = [s for s in comm.incoming_signals if s.type == SignalType.CHEMICAL]
            
            for signal in signals:
                # Try to bind signal to matching receptor
                ligand = signal.payload.get("ligand", "unknown")
                
                for receptor_name, receptor in membrane.receptors.items():
                    if receptor.ligand == ligand:
                        # Attempt binding based on signal strength
                        if receptor.bind_ligand(signal.strength):
                            self.total_signals_received += 1
                            membrane.active_receptors.add(receptor_name)
                            
                            # Trigger downstream effects
                            self._trigger_receptor_response(entity, receptor, signal)
                            
            # Clear processed signals
            comm.incoming_signals = [s for s in comm.incoming_signals 
                                   if s.type != SignalType.CHEMICAL]
                                   
        # Update receptor states
        for receptor_name, receptor in membrane.receptors.items():
            if receptor.occupied:
                # Receptors can spontaneously unbind
                if delta_time > 0.1:  # Simple unbinding probability
                    receptor.release_ligand()
                    membrane.active_receptors.discard(receptor_name)
                    
            # Recover sensitivity over time
            receptor.recover_sensitivity(0.05 * delta_time)
            
    def _trigger_receptor_response(self, entity: Entity, receptor, signal: Signal):
        """Trigger cellular response to receptor activation"""
        # Different responses based on receptor type
        if receptor.receptor_type.value == "growth_factor":
            # Promote cell division
            entity.add_tag("growth_signal_received")
            
        elif receptor.receptor_type.value == "cytokine":
            # Immune response
            entity.add_tag("cytokine_activated")
            
        elif receptor.receptor_type.value == "g_protein_coupled":
            # Various cellular responses
            response_type = signal.payload.get("response", "unknown")
            if response_type == "metabolic":
                if entity.has_component(EnergyComponent):
                    energy = entity.get_component(EnergyComponent)
                    energy.production_rate *= 1.5  # Boost metabolism
                    
    def _maintain_membrane(self, entity: Entity, membrane: MembraneComponent,
                          delta_time: float):
        """Maintain and repair membrane"""
        # Natural membrane repair
        if membrane.integrity < 1.0:
            # Repair rate depends on available energy
            repair_rate = 0.05  # Base repair rate
            
            if entity.has_component(EnergyComponent):
                energy = entity.get_component(EnergyComponent)
                # More energy = faster repair
                if energy.percentage() > 50:
                    repair_rate *= 2.0
                elif energy.percentage() < 20:
                    repair_rate *= 0.1
                    
            membrane.repair_membrane(repair_rate * delta_time)
            
        # Adjust fluidity based on temperature (simplified)
        # Optimal fluidity around 0.5
        if membrane.fluidity < 0.4 or membrane.fluidity > 0.6:
            # Cell tries to maintain optimal fluidity
            target_fluidity = 0.5
            adjustment = (target_fluidity - membrane.fluidity) * 0.1 * delta_time
            membrane.fluidity += adjustment
            
    def set_environment_molecule(self, molecule: str, concentration: float):
        """Set environmental molecule concentration"""
        self.environment_molecules[molecule] = concentration
        
    def get_stats(self) -> dict:
        """Get system statistics"""
        stats = super().get_stats()
        stats.update({
            "total_transported": self.total_transported,
            "total_signals_received": self.total_signals_received,
            "environment": self.environment_molecules
        })
        return stats