"""
Unit tests for Performance Aspect - Proper Implementation
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import pytest
import time
from src.biocode.aspects import PerformanceAspect, AspectWeaver, JoinPoint


class MockObject:
    """Mock object for testing"""
    
    def fast_method(self):
        return "fast"
        
    def slow_method(self):
        time.sleep(0.01)  # 10ms
        return "slow"
        
    def variable_method(self, delay: float):
        time.sleep(delay)
        return f"delayed {delay}s"
        
    def failing_method(self):
        time.sleep(0.002)
        raise ValueError("Test error")


class TestPerformanceAspect:
    """Test PerformanceAspect functionality - PROPER VERSION"""
    
    def test_aspect_creation(self):
        """Test creating performance aspect"""
        aspect = PerformanceAspect(alert_threshold_ms=100.0)
        
        assert aspect.alert_threshold_ms == 100.0
        assert len(aspect.metrics) == 0
        
    def test_metric_recording(self):
        """Test recording performance metrics"""
        aspect = PerformanceAspect()
        
        # Simulate method execution
        join_point = JoinPoint(
            target=MockObject(),
            method_name="test_method",
            args=(MockObject(),),
            kwargs={}
        )
        join_point.metadata['perf_start_time'] = time.perf_counter() - 0.005  # 5ms ago
        
        aspect.after(join_point)
        
        # Check metrics
        metrics = aspect.get_metrics()
        assert "MockObject.test_method" in metrics
        
        method_metrics = metrics["MockObject.test_method"]
        assert method_metrics["call_count"] == 1
        assert method_metrics["average_time"] > 0.004  # At least 4ms
        assert method_metrics["min_time"] > 0
        assert method_metrics["max_time"] >= method_metrics["min_time"]
        
    def test_multiple_calls(self):
        """Test metrics for multiple method calls"""
        # Create aspect with custom pointcut
        class TestPerformanceAspect(PerformanceAspect):
            def get_pointcut(self) -> str:
                return "MockObject.*"
        
        aspect = TestPerformanceAspect()
        obj = MockObject()
        
        # Create weaver and apply aspect
        weaver = AspectWeaver()
        weaver.add_aspect(aspect)
        weaver.weave(obj)
        
        # Call method multiple times
        for _ in range(5):
            obj.fast_method()
            
        metrics = aspect.get_metrics()
        fast_metrics = metrics.get("MockObject.fast_method", {})
        
        assert fast_metrics.get("call_count") == 5
        assert fast_metrics.get("average_time") > 0
        
    def test_slow_method_alert(self):
        """Test alerting for slow methods"""
        alerts = []
        
        # Create aspect with custom alert handler
        class TestPerformanceAspect(PerformanceAspect):
            def get_pointcut(self) -> str:
                return "MockObject.*"
                
            def after(self, join_point):
                """Override to capture alerts"""
                super().after(join_point)
                # Check if any new alerts were added
                if self.alerts:
                    last_alert = self.alerts[-1]
                    alerts.append(f"{last_alert['method']} took {last_alert['duration_ms']:.2f}ms")
        
        aspect = TestPerformanceAspect(alert_threshold_ms=5.0)  # 5ms threshold
        obj = MockObject()
        weaver = AspectWeaver()
        weaver.add_aspect(aspect)
        weaver.weave(obj)
        
        # Call slow method
        obj.slow_method()
        
        # Check for alert
        assert len(alerts) == 1
        assert "MockObject.slow_method" in alerts[0]
        assert "took" in alerts[0]
        
    def test_get_slow_methods(self):
        """Test getting slow methods"""
        class TestPerformanceAspect(PerformanceAspect):
            def get_pointcut(self) -> str:
                return "MockObject.*"
        
        aspect = TestPerformanceAspect(alert_threshold_ms=5.0)  # 5ms threshold
        obj = MockObject()
        weaver = AspectWeaver()
        weaver.add_aspect(aspect)
        weaver.weave(obj)
        
        # Call methods
        obj.fast_method()
        obj.slow_method()  # This should be slow
        
        slow_methods = aspect.get_slow_methods()
        assert len(slow_methods) >= 1
        # get_slow_methods returns list of tuples (method_sig, avg_time_ms)
        assert any("slow_method" in method[0] for method in slow_methods)
        
    def test_reset_metrics(self):
        """Test resetting metrics"""
        aspect = PerformanceAspect()
        
        # Add some metrics
        join_point = JoinPoint(
            target=MockObject(),
            method_name="test_method",
            args=(MockObject(),),
            kwargs={}
        )
        join_point.metadata['perf_start_time'] = time.perf_counter() - 0.001
        aspect.after(join_point)
        
        assert len(aspect.get_metrics()) > 0
        
        # Reset
        aspect.reset_metrics()
        assert len(aspect.get_metrics()) == 0
        
    def test_exception_handling(self):
        """Test performance tracking with exceptions"""
        class TestPerformanceAspect(PerformanceAspect):
            def get_pointcut(self) -> str:
                return "MockObject.*"
        
        aspect = TestPerformanceAspect()
        obj = MockObject()
        weaver = AspectWeaver()
        weaver.add_aspect(aspect)
        weaver.weave(obj)
        
        # Call method that throws exception
        with pytest.raises(ValueError):
            obj.failing_method()
            
        # Metrics should still be recorded
        metrics = aspect.get_metrics()
        assert "MockObject.failing_method" in metrics
        assert metrics["MockObject.failing_method"]["call_count"] == 1
        
    def test_performance_statistics(self):
        """Test calculating performance statistics"""
        class TestPerformanceAspect(PerformanceAspect):
            def get_pointcut(self) -> str:
                return "MockObject.*"
        
        aspect = TestPerformanceAspect()
        obj = MockObject()
        weaver = AspectWeaver()
        weaver.add_aspect(aspect)
        weaver.weave(obj)
        
        # Call method with varying delays
        delays = [0.001, 0.002, 0.003, 0.004, 0.005]
        for delay in delays:
            obj.variable_method(delay)
            
        metrics = aspect.get_metrics()
        var_metrics = metrics.get("MockObject.variable_method", {})
        
        assert var_metrics["call_count"] == 5
        assert var_metrics["min_time"] < var_metrics["max_time"]
        # Average should be around 3ms
        assert 0.002 < var_metrics["average_time"] < 0.004
        
    def test_disable_aspect(self):
        """Test disabling the aspect"""
        class TestPerformanceAspect(PerformanceAspect):
            def get_pointcut(self) -> str:
                return "MockObject.*"
        
        aspect = TestPerformanceAspect()
        obj = MockObject()
        weaver = AspectWeaver()
        weaver.add_aspect(aspect)
        weaver.weave(obj)
        
        # Call with aspect enabled
        obj.fast_method()
        assert len(aspect.get_metrics()) == 1
        
        # Disable and call again
        aspect.set_enabled(False)
        obj.fast_method()
        
        # Should still have only 1 call recorded
        metrics = aspect.get_metrics()
        assert metrics["MockObject.fast_method"]["call_count"] == 1