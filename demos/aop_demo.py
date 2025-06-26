#!/usr/bin/env python3
"""
BioCode AOP (Aspect-Oriented Programming) Demo
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

Demonstrates cross-cutting concerns with AOP.
"""
import time
import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.biocode.ecs import World, LifeSystem, EnergySystem
from src.biocode.factories import CellFactory
from src.biocode.aspects import (
    AspectWeaver,
    LoggingAspect,
    PerformanceAspect,
    SecurityAspect,
    ErrorHandlingAspect,
    MonitoringAspect,
    SecurityContext,
    SecurityLevel,
    get_security_context,
    set_security_context
)


def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("biocode.demo")


def demo_logging_aspect():
    """Demonstrate logging aspect"""
    print("\n📝 Logging Aspect Demo")
    print("=" * 60)
    
    # Create world and systems
    world = World()
    life_system = LifeSystem()
    energy_system = EnergySystem()
    
    # Set up logging aspect
    logger = setup_logging()
    logging_aspect = LoggingAspect(logger=logger)
    
    # Create weaver and apply aspect
    weaver = AspectWeaver()
    weaver.add_aspect(logging_aspect)
    
    # Weave into systems
    print("\n🔗 Applying logging aspect to systems...")
    weaver.weave(life_system)
    weaver.weave(energy_system)
    
    # Add systems to world
    world.add_system(life_system)
    world.add_system(energy_system)
    
    # Create some entities
    factory = CellFactory(world)
    cell1 = factory.create_stem_cell()
    cell2 = factory.create_neuron()
    
    print("\n📊 Running simulation with logging...")
    print("-" * 60)
    
    # Run update - logging will automatically capture method calls
    world.update(delta_time=0.1)
    
    print("-" * 60)
    print("✅ Check the logs above to see automatic method logging!")


def demo_performance_aspect():
    """Demonstrate performance monitoring aspect"""
    print("\n\n⚡ Performance Aspect Demo")
    print("=" * 60)
    
    # Create world
    world = World()
    life_system = LifeSystem()
    
    # Set up performance aspect
    perf_aspect = PerformanceAspect(alert_threshold_ms=10.0)
    
    # Apply aspect
    weaver = AspectWeaver()
    weaver.add_aspect(perf_aspect)
    weaver.weave(life_system)
    
    world.add_system(life_system)
    
    # Create many entities to stress test
    print("\n🔬 Creating 100 cells for performance testing...")
    factory = CellFactory(world)
    for i in range(100):
        factory.create_stem_cell(position=(i, 0, 0))
        
    print("\n⏱️  Running performance monitoring...")
    
    # Run multiple updates
    for i in range(5):
        world.update(delta_time=0.1)
        
    # Show performance metrics
    print("\n📊 Performance Metrics:")
    print("-" * 60)
    
    metrics = perf_aspect.get_metrics()
    for method, stats in metrics.items():
        print(f"\n{method}:")
        print(f"  Calls: {stats['call_count']}")
        print(f"  Avg Time: {stats['average_time']*1000:.2f}ms")
        print(f"  Min Time: {stats['min_time']*1000:.2f}ms")
        print(f"  Max Time: {stats['max_time']*1000:.2f}ms")
        
    # Show slow methods
    slow_methods = perf_aspect.get_slow_methods(threshold_ms=1.0)
    if slow_methods:
        print("\n🐌 Slow Methods (>1ms):")
        for method, avg_time in slow_methods:
            print(f"  {method}: {avg_time:.2f}ms average")


def demo_security_aspect():
    """Demonstrate security aspect"""
    print("\n\n🔒 Security Aspect Demo")
    print("=" * 60)
    
    # Create world
    world = World()
    
    # Set up security aspect
    security_aspect = SecurityAspect()
    
    # Apply aspect
    weaver = AspectWeaver()
    weaver.add_aspect(security_aspect)
    weaver.weave(world)
    
    print("\n🔐 Testing security controls...")
    
    # Test 1: Try to access without proper permissions
    print("\n1️⃣ Attempting to remove entity without permission:")
    
    # Set low security context
    context = SecurityContext()
    context.security_level = SecurityLevel.PUBLIC
    set_security_context(context)
    
    # Create an entity
    factory = CellFactory(world)
    entity = factory.create_stem_cell()
    
    try:
        world.remove_entity(entity.id)
        print("   ❌ Should have been blocked!")
    except PermissionError as e:
        print(f"   ✅ Access denied: {e}")
        
    # Test 2: Access with proper permissions
    print("\n2️⃣ Attempting with proper permissions:")
    
    # Set higher security context
    context.permissions.add("entity:delete")
    
    try:
        world.remove_entity(entity.id)
        print("   ✅ Access granted - entity removed")
    except PermissionError as e:
        print(f"   ❌ Unexpected denial: {e}")
        
    # Show audit log
    print("\n📋 Security Audit Log:")
    audit_log = security_aspect.get_audit_log()
    for entry in audit_log[-5:]:  # Last 5 entries
        print(f"   {entry['event']}: {entry['method']} - {entry.get('reason', 'success')}")


def demo_error_handling_aspect():
    """Demonstrate error handling with retry"""
    print("\n\n🛡️ Error Handling Aspect Demo")
    print("=" * 60)
    
    # Create a flaky system that sometimes fails
    class FlakySystem(LifeSystem):
        def __init__(self):
            super().__init__()
            self.call_count = 0
            
        def process(self, entity, delta_time):
            self.call_count += 1
            # Fail first 2 times, succeed on 3rd
            if self.call_count < 3:
                raise RuntimeError(f"Temporary failure (attempt {self.call_count})")
            super().process(entity, delta_time)
            
    # Create world
    world = World()
    flaky_system = FlakySystem()
    
    # Set up error handling aspect with retry
    error_aspect = ErrorHandlingAspect(max_retries=3, retry_delay=0.1)
    
    # Apply aspect
    weaver = AspectWeaver()
    weaver.add_aspect(error_aspect)
    weaver.weave(flaky_system)
    
    world.add_system(flaky_system)
    
    # Create entity
    factory = CellFactory(world)
    entity = factory.create_stem_cell()
    
    print("\n🔄 Testing automatic retry on failure...")
    
    # This should retry and eventually succeed
    try:
        world.update(delta_time=0.1)
        print("\n✅ Success after automatic retries!")
    except Exception as e:
        print(f"\n❌ Failed even after retries: {e}")
        
    # Show error report
    print("\n📊 Error Report:")
    report = error_aspect.get_error_report()
    print(f"   Total Errors: {report['total_errors']}")
    print(f"   Error Types: {report['error_by_type']}")


def demo_monitoring_aspect():
    """Demonstrate system monitoring"""
    print("\n\n📡 Monitoring Aspect Demo")
    print("=" * 60)
    
    # Create world
    world = World()
    
    # Set up monitoring aspect
    monitor_aspect = MonitoringAspect(collect_interval=0.5)
    
    # Add health check
    def check_entity_count():
        return len(world.entities) < 100  # Healthy if less than 100 entities
        
    monitor_aspect.add_health_check("entity_count", check_entity_count)
    
    # Apply aspect
    weaver = AspectWeaver()
    weaver.add_aspect(monitor_aspect)
    weaver.weave(world)
    
    # Add systems
    world.add_system(LifeSystem())
    world.add_system(EnergySystem())
    
    print("\n📊 Starting system monitoring...")
    
    # Create entities and monitor
    factory = CellFactory(world)
    
    for i in range(5):
        print(f"\n🔄 Cycle {i+1}:")
        
        # Create some entities
        for _ in range(25):
            factory.create_stem_cell()
            
        # Update world
        world.update(delta_time=0.1)
        
        # Show metrics
        metrics = monitor_aspect.get_metrics_summary()
        print(f"   Method Calls: {metrics.get('method_calls', 0)}")
        print(f"   CPU Usage: {metrics.get('cpu_usage', 0):.1f}%")
        print(f"   Memory Usage: {metrics.get('memory_usage', 0):.1f}MB")
        
        # Check health
        health = monitor_aspect.get_health_status()
        print(f"   System Healthy: {health['healthy']}")
        
        time.sleep(0.5)
        
    # Show final monitoring summary
    print("\n📈 Monitoring Summary:")
    print("-" * 60)
    
    health_status = monitor_aspect.get_health_status()
    print(f"Overall Health: {'✅ Healthy' if health_status['healthy'] else '❌ Unhealthy'}")
    
    if health_status['recent_alerts']:
        print("\n⚠️  Recent Alerts:")
        for alert in health_status['recent_alerts']:
            print(f"   [{alert['severity']}] {alert['message']}")


def demo_combined_aspects():
    """Demonstrate multiple aspects working together"""
    print("\n\n🎯 Combined Aspects Demo")
    print("=" * 60)
    print("Combining Logging + Performance + Monitoring")
    
    # Create world
    world = World()
    
    # Create all aspects
    logger = setup_logging()
    aspects = [
        LoggingAspect(logger=logger, log_args=False),  # Simplified logging
        PerformanceAspect(alert_threshold_ms=5.0),
        MonitoringAspect(collect_interval=1.0)
    ]
    
    # Apply all aspects
    weaver = AspectWeaver()
    for aspect in aspects:
        weaver.add_aspect(aspect)
        
    # Weave into world
    weaver.weave(world)
    
    # Add systems
    life_system = LifeSystem()
    energy_system = EnergySystem()
    
    # Weave into systems too
    weaver.weave(life_system)
    weaver.weave(energy_system)
    
    world.add_system(life_system)
    world.add_system(energy_system)
    
    print("\n🚀 Running with all aspects enabled...")
    
    # Create entities
    factory = CellFactory(world)
    for i in range(10):
        factory.create_stem_cell(position=(i, 0, 0))
        
    # Run simulation
    for i in range(3):
        print(f"\n⏱️  Update {i+1}:")
        world.update(delta_time=0.1)
        
    # Show weaver summary
    print("\n📊 Aspect Weaver Summary:")
    summary = weaver.get_woven_summary()
    print(f"   Total Aspects: {summary['total_aspects']}")
    print(f"   Woven Objects: {summary['total_woven_objects']}")
    
    for aspect_info in summary['aspects']:
        print(f"\n   {aspect_info['type']}:")
        print(f"      Pointcut: {aspect_info['pointcut']}")
        print(f"      Applied to {len(aspect_info['applied_to'])} methods")


def main():
    """Run all AOP demos"""
    try:
        print("\n" + "=" * 80)
        print("🎯 BIOCODE AOP (ASPECT-ORIENTED PROGRAMMING) DEMO")
        print("Demonstrating Cross-Cutting Concerns")
        print("=" * 80)
        
        # Run individual demos
        demo_logging_aspect()
        demo_performance_aspect()
        demo_security_aspect()
        demo_error_handling_aspect()
        demo_monitoring_aspect()
        demo_combined_aspects()
        
        print("\n\n" + "=" * 80)
        print("✅ AOP DEMO COMPLETED!")
        print("\nBioCode now supports:")
        print("   ✓ Automatic logging")
        print("   ✓ Performance monitoring")
        print("   ✓ Security enforcement")
        print("   ✓ Error handling & retry")
        print("   ✓ System health monitoring")
        print("   ✓ All without modifying core code!")
        print("\n🚀 Clean separation of concerns achieved!")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()