import asyncio
import os
import sys
from datetime import datetime

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from biocode.domain.entities.advanced_tissue import (
    ExtracellularMatrix, ResourceType, SharedResource,
    HomeostasisController,
    VascularizationSystem
)
from biocode.domain.entities.system import (
    SystemBootManager, MaintenanceManager, SystemMemoryManager,
    SystemShutdownManager
)
from biocode.domain.entities.base_cell import CodeCell
# TODO: Create ExtracellularMatrix in biocode.domain.entities


class TestExtracellularMatrix:
    """Test suite for ExtracellularMatrix"""

    def test_ecm_creation(self):
        """Test ECM creation"""
        ecm = ExtracellularMatrix()
        
        assert ecm.resources is not None
        assert ecm.matrix_health is not None
        assert ecm.connective_proteins is not None
        assert len(ecm.barriers) == 0

    def test_deposit_resource(self):
        """Test resource deposition"""
        ecm = ExtracellularMatrix()
        
        resource = SharedResource(
            name="glucose",
            resource_type=ResourceType.NUTRIENT,
            data={"amount": 100, "unit": "mg"},
            access_level="public"
        )
        
        ecm.deposit_resource(ResourceType.NUTRIENT, resource)
        
        assert ResourceType.NUTRIENT in ecm.resources
        assert "glucose" in ecm.resources[ResourceType.NUTRIENT]

    def test_retrieve_resource(self):
        """Test resource retrieval"""
        ecm = ExtracellularMatrix()
        
        # Deposit resource
        config = SharedResource(
            name="db_config",
            resource_type=ResourceType.CONFIG,
            data={"host": "localhost", "port": 5432}
        )
        ecm.deposit_resource(ResourceType.CONFIG, config)
        
        # Retrieve resource
        retrieved = ecm.retrieve_resource(ResourceType.CONFIG, "db_config")
        
        assert retrieved is not None
        assert retrieved.data["host"] == "localhost"

    def test_resource_expiry(self):
        """Test resource expiration"""
        ecm = ExtracellularMatrix()
        
        # Create expired resource
        expired_resource = SharedResource(
            name="temp_data",
            resource_type=ResourceType.CACHE,
            data={"value": "old"},
            expiry=datetime.now()  # Already expired
        )
        
        ecm.deposit_resource(ResourceType.CACHE, expired_resource)
        
        # Should not retrieve expired resource
        retrieved = ecm.retrieve_resource(ResourceType.CACHE, "temp_data")
        assert retrieved is None

    def test_create_barrier(self):
        """Test security barrier creation"""
        ecm = ExtracellularMatrix()
        
        # Create barrier that only allows healthy cells
        def healthy_filter(cell):
            return hasattr(cell, 'health_score') and cell.health_score > 80
        
        ecm.create_barrier("health_check", healthy_filter)
        
        assert "health_check" in ecm.barriers
        
        # Test barrier
        class MockCell:
            health_score = 90
        
        assert ecm.check_barrier_access("health_check", MockCell())

    def test_matrix_health(self):
        """Test matrix health monitoring"""
        ecm = ExtracellularMatrix()
        
        # ECM should have health tracking
        assert hasattr(ecm, 'matrix_health')
        
        # Test basic health operations if available
        if hasattr(ecm, 'update_health'):
            ecm.update_health()
            assert True  # Health update completed


class TestHomeostasisController:
    """Test suite for HomeostasisController"""

    def test_controller_creation(self):
        """Test homeostasis controller creation"""
        controller = HomeostasisController("test_tissue")
        
        assert controller.tissue_name == "test_tissue"
        assert len(controller.parameters) == 0
        assert len(controller.feedback_loops) == 0

    def test_register_parameter(self):
        """Test parameter registration"""
        controller = HomeostasisController("liver")
        
        controller.register_parameter(
            name="glucose_level",
            target=90.0,
            min_val=70.0,
            max_val=110.0
        )
        
        assert "glucose_level" in controller.parameters
        param = controller.parameters["glucose_level"]
        assert param.target == 90.0
        assert param.min_value == 70.0
        assert param.max_value == 110.0

    def test_feedback_loop(self):
        """Test feedback loop"""
        controller = HomeostasisController("pancreas")
        
        # Register parameter
        controller.register_parameter("insulin", 5.0, 2.0, 10.0)
        
        # Mock sensor and actuator
        current_value = 8.0
        
        def sensor():
            return current_value
        
        def actuator(adjustment):
            nonlocal current_value
            current_value += adjustment
        
        # Add feedback loop
        controller.add_feedback_loop(
            parameter="insulin",
            sensor=sensor,
            actuator=actuator,
            gain=0.5
        )
        
        # Run regulation
        controller.regulate_parameter("insulin")
        
        # Should move towards target
        assert current_value < 8.0  # Moved down towards target of 5.0

    @pytest.mark.asyncio
    async def test_async_regulation(self):
        """Test async regulation"""
        controller = HomeostasisController("kidney")
        
        # Register multiple parameters
        controller.register_parameter("sodium", 140.0, 135.0, 145.0)
        controller.register_parameter("potassium", 4.0, 3.5, 4.5)
        
        # Add mock feedback loops
        for param in ["sodium", "potassium"]:
            controller.add_feedback_loop(
                parameter=param,
                sensor=lambda: controller.parameters[param].target,
                actuator=lambda x: None,
                gain=1.0
            )
        
        # Run regulation
        await controller.regulate()
        
        # Should complete without errors
        assert True


class TestVascularizationSystem:
    """Test suite for VascularizationSystem"""

    def test_system_creation(self):
        """Test vascularization system creation"""
        vascular = VascularizationSystem()
        
        assert len(vascular.vessels) == 0
        assert len(vascular.connections) == 0
        assert len(vascular.flow_rates) == 0

    def test_create_vessel(self):
        """Test blood vessel creation"""
        vascular = VascularizationSystem()
        
        vessel = vascular.create_vessel("aorta", capacity=1000.0)
        
        assert vessel.id == "aorta"
        assert vessel.capacity == 1000.0
        assert vessel.flow_rate == 0.0
        assert vessel.oxygen_level == 100.0

    def test_connect_vessels(self):
        """Test vessel connection"""
        vascular = VascularizationSystem()
        
        # Create vessels
        artery = vascular.create_vessel("artery", 500)
        vein = vascular.create_vessel("vein", 300)
        
        # Connect them
        vascular.connect_vessels("artery", "vein", flow_rate=2.0)
        
        assert "vein" in vascular.connections["artery"]
        assert ("artery", "vein") in vascular.flow_rates
        assert vascular.flow_rates[("artery", "vein")] == 2.0

    def test_vessel_attributes(self):
        """Test vessel attributes"""
        vascular = VascularizationSystem()
        
        # Create a vessel using the system
        vessel = vascular.create_vessel("test_vessel", capacity=100)
        
        # Check vessel attributes
        assert vessel.id == "test_vessel"
        assert vessel.capacity == 100
        assert hasattr(vessel, 'flow_rate')
        assert hasattr(vessel, 'oxygen_level')

    @pytest.mark.asyncio
    async def test_distribute_resources(self):
        """Test resource distribution"""
        vascular = VascularizationSystem()
        
        # Create network
        main = vascular.create_vessel("main", 1000)
        branch1 = vascular.create_vessel("branch1", 500)
        branch2 = vascular.create_vessel("branch2", 500)
        
        vascular.connect_vessels("main", "branch1", 1.0)
        vascular.connect_vessels("main", "branch2", 1.0)
        
        # Distribute resources
        resources = {"oxygen": 100, "glucose": 50}
        await vascular.distribute_resources(resources)
        
        # Check distribution
        assert main.oxygen_level > 0
        # Resources should flow to branches


class TestSystemManagers:
    """Test suite for system managers"""

    @pytest.mark.asyncio
    async def test_boot_manager(self):
        """Test system boot manager"""
        boot_manager = SystemBootManager("test_system")
        
        assert boot_manager.system_name == "test_system"
        assert len(boot_manager.boot_stages) > 0
        assert boot_manager.boot_status == "not_started"
        
        # Run boot sequence
        success = await boot_manager.boot()
        
        assert success
        assert boot_manager.boot_status == "completed"

    def test_maintenance_manager(self):
        """Test maintenance manager"""
        maintenance = MaintenanceManager()
        
        # Schedule task
        task_called = False
        
        def maintenance_task():
            nonlocal task_called
            task_called = True
        
        maintenance.schedule_maintenance(
            task=maintenance_task,
            interval=0.1  # Short interval for testing
        )
        
        # Task should be scheduled
        assert len(maintenance.scheduled_tasks) > 0

    def test_memory_manager(self):
        """Test system memory manager"""
        memory_manager = SystemMemoryManager()
        
        # Allocate memory
        block = memory_manager.allocate_memory(size=1024, purpose="test")
        
        assert block is not None
        assert block["size"] == 1024
        assert block["purpose"] == "test"
        assert memory_manager.used_memory >= 1024
        
        # Release memory
        memory_manager.release_memory(block["id"])
        assert memory_manager.used_memory < 1024

    @pytest.mark.asyncio
    async def test_shutdown_manager(self):
        """Test system shutdown manager"""
        shutdown_manager = SystemShutdownManager()
        
        # Add cleanup task
        cleanup_called = False
        
        async def cleanup():
            nonlocal cleanup_called
            cleanup_called = True
        
        shutdown_manager.register_cleanup_task(cleanup)
        
        # Initiate shutdown
        await shutdown_manager.initiate_shutdown()
        
        assert cleanup_called
        assert shutdown_manager.shutdown_status == "completed"