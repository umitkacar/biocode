"""
Sensory Perception System for Digital Cells
"""
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import math
from collections import defaultdict, deque


class SensoryType(Enum):
    """Types of sensory perception"""
    VISION = "vision"           # See other cells and objects
    CHEMORECEPTION = "smell"    # Detect chemicals/pheromones
    MECHANORECEPTION = "touch"  # Physical contact
    THERMORECEPTION = "heat"    # Temperature sensing
    ELECTRORECEPTION = "electric"  # Electric fields
    PROPRIOCEPTION = "position" # Self body awareness
    NOCICEPTION = "pain"       # Damage detection
    AUDITION = "hearing"       # Sound/vibration detection


@dataclass
class SensorySignal:
    """A sensory signal received by a cell"""
    signal_type: SensoryType
    intensity: float  # 0.0 to 1.0
    direction: Optional[Tuple[float, float]] = None  # Vector to source
    source_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: float = 0.0


class SensoryOrgan:
    """Base class for sensory organs"""
    
    def __init__(self, organ_type: SensoryType, sensitivity: float = 0.5):
        self.organ_type = organ_type
        self.sensitivity = sensitivity  # 0-1, affects detection range/threshold
        self.energy_cost = 0.1  # Energy per sensing action
        self.damage = 0.0  # Organ can be damaged
        
    def perceive(self, environment_state: Dict, cell_position: Tuple[float, float]) -> List[SensorySignal]:
        """Process environmental stimuli into sensory signals"""
        raise NotImplementedError
        
    def process_signal(self, raw_signal: float) -> float:
        """Process raw signal through organ sensitivity"""
        if self.damage > 0.8:
            return 0.0  # Organ too damaged
            
        # Apply sensitivity and damage
        processed = raw_signal * self.sensitivity * (1 - self.damage)
        
        # Add noise based on organ quality
        noise = np.random.normal(0, 0.05 * (1 - self.sensitivity))
        
        return max(0, min(1, processed + noise))


class VisualSystem(SensoryOrgan):
    """Vision - detect light, colors, shapes, movement"""
    
    def __init__(self, sensitivity: float = 0.5, field_of_view: float = 120):
        super().__init__(SensoryType.VISION, sensitivity)
        self.field_of_view = field_of_view  # Degrees
        self.color_perception = sensitivity > 0.7  # Can see colors if sensitive enough
        self.motion_detection = True
        self.max_range = 20 + 30 * sensitivity  # Vision range
        
    def perceive(self, environment_state: Dict, cell_position: Tuple[float, float]) -> List[SensorySignal]:
        signals = []
        
        # Detect light level
        light_level = environment_state.get('light_level', 0.5)
        if light_level < 0.1:  # Too dark to see
            return signals
            
        # Detect nearby entities
        for entity in environment_state.get('entities', []):
            if entity.get('id') == cell_position:  # Don't see self
                continue
                
            # Calculate distance and direction
            entity_pos = entity.get('position', (0, 0))
            dx = entity_pos[0] - cell_position[0]
            dy = entity_pos[1] - cell_position[1]
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > self.max_range:
                continue
                
            # Check if in field of view
            angle = math.degrees(math.atan2(dy, dx))
            cell_facing = environment_state.get('cell_facing', 0)
            angle_diff = abs((angle - cell_facing + 180) % 360 - 180)
            
            if angle_diff > self.field_of_view / 2:
                continue
                
            # Create visual signal
            intensity = self.process_signal((1 - distance / self.max_range) * light_level)
            
            signal_data = {
                'entity_type': entity.get('type', 'unknown'),
                'size': entity.get('size', 1.0),
                'distance': distance
            }
            
            if self.color_perception:
                signal_data['color'] = entity.get('color', 'gray')
                
            if self.motion_detection and 'velocity' in entity:
                signal_data['movement'] = entity['velocity']
                
            signals.append(SensorySignal(
                signal_type=SensoryType.VISION,
                intensity=intensity,
                direction=(dx, dy),
                source_id=entity.get('id'),
                data=signal_data
            ))
            
        return signals


class ChemoreceptorSystem(SensoryOrgan):
    """Smell/Taste - detect chemical gradients"""
    
    def __init__(self, sensitivity: float = 0.5):
        super().__init__(SensoryType.CHEMORECEPTION, sensitivity)
        self.chemical_types = ['food', 'toxin', 'pheromone', 'warning']
        self.detection_threshold = 0.1 * (1 - sensitivity)
        
    def perceive(self, environment_state: Dict, cell_position: Tuple[float, float]) -> List[SensorySignal]:
        signals = []
        
        # Check chemical gradients
        chemical_map = environment_state.get('chemical_gradients', {})
        
        for chemical_type, gradient in chemical_map.items():
            if chemical_type not in self.chemical_types:
                continue
                
            # Sample chemical concentration at position
            x, y = int(cell_position[0]), int(cell_position[1])
            if hasattr(gradient, 'shape') and 0 <= x < gradient.shape[0] and 0 <= y < gradient.shape[1]:
                concentration = gradient[x, y]
            else:
                concentration = gradient.get((x, y), 0) if isinstance(gradient, dict) else 0
                
            if concentration < self.detection_threshold:
                continue
                
            # Calculate gradient direction
            dx, dy = self._calculate_gradient_direction(gradient, cell_position)
            
            intensity = self.process_signal(concentration)
            
            signals.append(SensorySignal(
                signal_type=SensoryType.CHEMORECEPTION,
                intensity=intensity,
                direction=(dx, dy) if (dx != 0 or dy != 0) else None,
                data={
                    'chemical': chemical_type,
                    'concentration': concentration,
                    'gradient_strength': math.sqrt(dx**2 + dy**2)
                }
            ))
            
        return signals
    
    def _calculate_gradient_direction(self, gradient, position):
        """Calculate direction of strongest increase"""
        x, y = int(position[0]), int(position[1])
        dx, dy = 0, 0
        
        # Sample neighboring positions
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                    
                nx, ny = x + i, y + j
                
                if hasattr(gradient, 'shape'):
                    if 0 <= nx < gradient.shape[0] and 0 <= ny < gradient.shape[1]:
                        diff = gradient[nx, ny] - gradient[x, y]
                        dx += i * diff
                        dy += j * diff
                elif isinstance(gradient, dict):
                    current = gradient.get((x, y), 0)
                    neighbor = gradient.get((nx, ny), 0)
                    diff = neighbor - current
                    dx += i * diff
                    dy += j * diff
                    
        return dx, dy


class MechanoreceptorSystem(SensoryOrgan):
    """Touch/Pressure - detect physical contact and pressure"""
    
    def __init__(self, sensitivity: float = 0.5):
        super().__init__(SensoryType.MECHANORECEPTION, sensitivity)
        self.pressure_threshold = 0.2 * (1 - sensitivity)
        self.vibration_detection = sensitivity > 0.6
        
    def perceive(self, environment_state: Dict, cell_position: Tuple[float, float]) -> List[SensorySignal]:
        signals = []
        
        # Check collisions
        collisions = environment_state.get('collisions', [])
        for collision in collisions:
            if collision.get('position') == cell_position:
                force = collision.get('force', 0.5)
                if force < self.pressure_threshold:
                    continue
                    
                intensity = self.process_signal(force)
                
                signals.append(SensorySignal(
                    signal_type=SensoryType.MECHANORECEPTION,
                    intensity=intensity,
                    direction=collision.get('direction'),
                    source_id=collision.get('other_id'),
                    data={
                        'force': force,
                        'contact_type': collision.get('type', 'touch')
                    }
                ))
        
        # Detect vibrations if capable
        if self.vibration_detection:
            vibrations = environment_state.get('vibrations', [])
            for vib in vibrations:
                distance = math.sqrt((vib['source'][0] - cell_position[0])**2 + 
                                   (vib['source'][1] - cell_position[1])**2)
                
                # Vibration intensity decreases with distance
                vib_intensity = vib['intensity'] / (1 + distance * 0.1)
                
                if vib_intensity > self.pressure_threshold:
                    intensity = self.process_signal(vib_intensity)
                    
                    signals.append(SensorySignal(
                        signal_type=SensoryType.MECHANORECEPTION,
                        intensity=intensity,
                        direction=(vib['source'][0] - cell_position[0], 
                                 vib['source'][1] - cell_position[1]),
                        data={
                            'vibration_frequency': vib.get('frequency', 1.0),
                            'vibration_pattern': vib.get('pattern', 'continuous')
                        }
                    ))
                    
        return signals


class ThermoreceptorSystem(SensoryOrgan):
    """Temperature sensing"""
    
    def __init__(self, sensitivity: float = 0.5):
        super().__init__(SensoryType.THERMORECEPTION, sensitivity)
        self.optimal_temp = 20.0
        self.temp_range = 40.0  # Can sense ±20°C from optimal
        
    def perceive(self, environment_state: Dict, cell_position: Tuple[float, float]) -> List[SensorySignal]:
        signals = []
        
        # Get temperature at position
        temperature = environment_state.get('temperature', self.optimal_temp)
        
        # Check for local temperature variations
        temp_map = environment_state.get('temperature_map')
        if temp_map:
            x, y = int(cell_position[0]), int(cell_position[1])
            if hasattr(temp_map, 'shape') and 0 <= x < temp_map.shape[0] and 0 <= y < temp_map.shape[1]:
                temperature = temp_map[x, y]
        
        # Calculate deviation from optimal
        temp_diff = abs(temperature - self.optimal_temp)
        if temp_diff > self.temp_range:
            intensity = 1.0  # Extreme temperature
        else:
            intensity = temp_diff / self.temp_range
            
        intensity = self.process_signal(intensity)
        
        # Determine if hot or cold
        sensation = 'hot' if temperature > self.optimal_temp else 'cold'
        
        signals.append(SensorySignal(
            signal_type=SensoryType.THERMORECEPTION,
            intensity=intensity,
            data={
                'temperature': temperature,
                'sensation': sensation,
                'deviation': temperature - self.optimal_temp
            }
        ))
        
        return signals


class ProprioceptorSystem(SensoryOrgan):
    """Self-awareness - body position, energy levels, internal state"""
    
    def __init__(self, sensitivity: float = 0.5):
        super().__init__(SensoryType.PROPRIOCEPTION, sensitivity)
        
    def perceive(self, environment_state: Dict, cell_position: Tuple[float, float]) -> List[SensorySignal]:
        signals = []
        
        # Get cell's internal state
        cell_state = environment_state.get('cell_state', {})
        
        # Energy awareness
        energy = cell_state.get('energy', 100)
        energy_signal = SensorySignal(
            signal_type=SensoryType.PROPRIOCEPTION,
            intensity=self.process_signal(1 - energy / 100),
            data={'state': 'energy', 'level': energy, 'critical': energy < 20}
        )
        signals.append(energy_signal)
        
        # Health awareness
        health = cell_state.get('health', 100)
        if health < 100:
            health_signal = SensorySignal(
                signal_type=SensoryType.PROPRIOCEPTION,
                intensity=self.process_signal(1 - health / 100),
                data={'state': 'health', 'level': health, 'damaged': health < 50}
            )
            signals.append(health_signal)
        
        # Movement awareness
        velocity = cell_state.get('velocity', (0, 0))
        if velocity[0] != 0 or velocity[1] != 0:
            speed = math.sqrt(velocity[0]**2 + velocity[1]**2)
            movement_signal = SensorySignal(
                signal_type=SensoryType.PROPRIOCEPTION,
                intensity=self.process_signal(min(1, speed / 5)),
                data={'state': 'movement', 'velocity': velocity, 'speed': speed}
            )
            signals.append(movement_signal)
            
        return signals


class NociceptorSystem(SensoryOrgan):
    """Pain/Damage detection"""
    
    def __init__(self, sensitivity: float = 0.5):
        super().__init__(SensoryType.NOCICEPTION, sensitivity)
        self.pain_threshold = 0.3 * (1 - sensitivity)
        self.pain_memory = []  # Remember recent pain
        
    def perceive(self, environment_state: Dict, cell_position: Tuple[float, float]) -> List[SensorySignal]:
        signals = []
        
        # Check for damage sources
        damage_events = environment_state.get('damage_events', [])
        
        for event in damage_events:
            if event.get('target') == cell_position:
                damage = event.get('amount', 0)
                if damage < self.pain_threshold:
                    continue
                    
                intensity = self.process_signal(min(1, damage))
                
                # Remember this pain
                self.pain_memory.append({
                    'damage': damage,
                    'source': event.get('source'),
                    'type': event.get('damage_type', 'physical')
                })
                
                # Keep only recent pain memories
                if len(self.pain_memory) > 10:
                    self.pain_memory.pop(0)
                
                signals.append(SensorySignal(
                    signal_type=SensoryType.NOCICEPTION,
                    intensity=intensity,
                    source_id=event.get('source'),
                    data={
                        'damage': damage,
                        'damage_type': event.get('damage_type', 'physical'),
                        'continuous': len([p for p in self.pain_memory 
                                         if p['source'] == event.get('source')]) > 1
                    }
                ))
                
        return signals


class IntegratedSensorySystem:
    """Complete sensory system integrating all organs"""
    
    def __init__(self, genome_traits: Dict[str, float]):
        """Initialize sensory system based on genetic traits"""
        self.organs = {}
        
        # Create organs based on genetic predisposition
        if genome_traits.get('vision', 0) > 0.3:
            self.organs[SensoryType.VISION] = VisualSystem(
                sensitivity=genome_traits.get('vision', 0.5)
            )
            
        if genome_traits.get('chemoreception', 0) > 0.3:
            self.organs[SensoryType.CHEMORECEPTION] = ChemoreceptorSystem(
                sensitivity=genome_traits.get('chemoreception', 0.5)
            )
            
        if genome_traits.get('touch', 0) > 0.3:
            self.organs[SensoryType.MECHANORECEPTION] = MechanoreceptorSystem(
                sensitivity=genome_traits.get('touch', 0.5)
            )
            
        if genome_traits.get('temperature', 0) > 0.3:
            self.organs[SensoryType.THERMORECEPTION] = ThermoreceptorSystem(
                sensitivity=genome_traits.get('temperature', 0.5)
            )
            
        # All cells have proprioception and nociception
        self.organs[SensoryType.PROPRIOCEPTION] = ProprioceptorSystem(
            sensitivity=genome_traits.get('self_awareness', 0.5)
        )
        self.organs[SensoryType.NOCICEPTION] = NociceptorSystem(
            sensitivity=genome_traits.get('pain_sensitivity', 0.5)
        )
        
        # Sensory integration and processing
        self.attention_capacity = 5 + int(10 * genome_traits.get('neural_complexity', 0.5))
        self.sensory_memory = deque(maxlen=20)
        self.sensory_adaptation = defaultdict(float)  # Habituation to repeated stimuli
        
    def perceive_environment(self, environment_state: Dict, 
                           cell_position: Tuple[float, float]) -> List[SensorySignal]:
        """Gather all sensory information from environment"""
        all_signals = []
        total_energy_cost = 0
        
        # Collect signals from all organs
        for organ_type, organ in self.organs.items():
            try:
                signals = organ.perceive(environment_state, cell_position)
                all_signals.extend(signals)
                total_energy_cost += organ.energy_cost
            except Exception as e:
                # Organ malfunction
                print(f"Sensory organ {organ_type} failed: {e}")
                organ.damage += 0.1
        
        # Apply sensory adaptation (habituation)
        adapted_signals = []
        for signal in all_signals:
            # Create signal signature for adaptation tracking
            sig_key = f"{signal.signal_type}_{signal.source_id}_{signal.data}"
            
            # Check adaptation level
            adaptation = self.sensory_adaptation[sig_key]
            
            # Reduce intensity based on adaptation
            adapted_intensity = signal.intensity * (1 - adaptation * 0.5)
            
            if adapted_intensity > 0.1:  # Threshold for perception
                signal.intensity = adapted_intensity
                adapted_signals.append(signal)
                
                # Increase adaptation for this stimulus
                self.sensory_adaptation[sig_key] = min(1.0, adaptation + 0.1)
        
        # Decay adaptation over time
        for key in list(self.sensory_adaptation.keys()):
            self.sensory_adaptation[key] *= 0.95
            if self.sensory_adaptation[key] < 0.01:
                del self.sensory_adaptation[key]
        
        # Sort by intensity and limit by attention capacity
        adapted_signals.sort(key=lambda s: s.intensity, reverse=True)
        focused_signals = adapted_signals[:self.attention_capacity]
        
        # Store in sensory memory
        self.sensory_memory.extend(focused_signals)
        
        # Return signals and energy cost
        environment_state['sensory_energy_cost'] = total_energy_cost
        
        return focused_signals
    
    def get_sensory_summary(self) -> Dict[str, Any]:
        """Get summary of current sensory state"""
        summary = {
            'active_organs': list(self.organs.keys()),
            'attention_capacity': self.attention_capacity,
            'recent_signals': len(self.sensory_memory),
            'adaptation_count': len(self.sensory_adaptation),
            'organ_status': {}
        }
        
        for organ_type, organ in self.organs.items():
            summary['organ_status'][organ_type.value] = {
                'sensitivity': organ.sensitivity,
                'damage': organ.damage,
                'functional': organ.damage < 0.8
            }
            
        return summary
    
    def process_integrated_perception(self, signals: List[SensorySignal]) -> Dict[str, Any]:
        """Integrate multiple sensory signals into unified perception"""
        perception = {
            'threat_level': 0.0,
            'opportunity_level': 0.0,
            'movement_suggestion': (0, 0),
            'primary_focus': None,
            'emotional_state': 'neutral'
        }
        
        # Analyze signals
        for signal in signals:
            if signal.signal_type == SensoryType.NOCICEPTION:
                perception['threat_level'] += signal.intensity
                perception['emotional_state'] = 'pain'
                
            elif signal.signal_type == SensoryType.VISION:
                if signal.data and signal.data.get('entity_type') == 'predator':
                    perception['threat_level'] += signal.intensity * 0.8
                elif signal.data and signal.data.get('entity_type') == 'food':
                    perception['opportunity_level'] += signal.intensity
                    
            elif signal.signal_type == SensoryType.CHEMORECEPTION:
                if signal.data and signal.data.get('chemical') == 'food':
                    perception['opportunity_level'] += signal.intensity * 0.7
                    if signal.direction:
                        perception['movement_suggestion'] = signal.direction
                elif signal.data and signal.data.get('chemical') == 'toxin':
                    perception['threat_level'] += signal.intensity * 0.6
                    if signal.direction:
                        # Move away from toxin
                        perception['movement_suggestion'] = (-signal.direction[0], 
                                                           -signal.direction[1])
        
        # Determine primary focus
        if perception['threat_level'] > 0.7:
            perception['primary_focus'] = 'escape'
            perception['emotional_state'] = 'fear'
        elif perception['opportunity_level'] > 0.5:
            perception['primary_focus'] = 'approach'
            perception['emotional_state'] = 'interest'
        else:
            perception['primary_focus'] = 'explore'
            
        return perception


# Example usage and testing
if __name__ == "__main__":
    # Test sensory system
    test_genome = {
        'vision': 0.8,
        'chemoreception': 0.6,
        'touch': 0.7,
        'temperature': 0.5,
        'self_awareness': 0.9,
        'pain_sensitivity': 0.4,
        'neural_complexity': 0.7
    }
    
    sensory_system = IntegratedSensorySystem(test_genome)
    
    # Mock environment
    test_environment = {
        'light_level': 0.8,
        'temperature': 25.0,
        'entities': [
            {'id': 'food_1', 'type': 'food', 'position': (10, 10), 'color': 'green'},
            {'id': 'pred_1', 'type': 'predator', 'position': (5, 5), 'color': 'red'}
        ],
        'chemical_gradients': {
            'food': {(10, 10): 0.8, (9, 10): 0.6, (8, 10): 0.4},
            'warning': {(5, 5): 0.9, (6, 5): 0.7}
        },
        'cell_state': {
            'energy': 75,
            'health': 90,
            'velocity': (1, 0)
        }
    }
    
    # Test perception
    signals = sensory_system.perceive_environment(test_environment, (8, 8))
    
    print("Sensory Signals Received:")
    for signal in signals:
        print(f"- {signal.signal_type.value}: intensity={signal.intensity:.2f}, "
              f"data={signal.data}")
    
    # Test integrated perception
    perception = sensory_system.process_integrated_perception(signals)
    print(f"\nIntegrated Perception: {perception}")
    
    # Get summary
    summary = sensory_system.get_sensory_summary()
    print(f"\nSensory System Summary: {summary}")