"""
Unit tests for Logging Aspect - Proper Implementation
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import pytest
import logging
from io import StringIO
from src.biocode.aspects import LoggingAspect, AspectWeaver, JoinPoint


class MockObject:
    """Mock object for testing"""
    
    def simple_method(self):
        return "result"
        
    def method_with_args(self, x, y):
        return x + y
        
    def failing_method(self):
        raise ValueError("Test exception")


class TestLoggingAspect:
    """Test LoggingAspect functionality - PROPER VERSION"""
    
    def test_aspect_creation(self):
        """Test creating logging aspect"""
        logger = logging.getLogger("test")
        aspect = LoggingAspect(logger=logger)
        
        assert aspect.logger == logger
        assert aspect.log_args is True
        assert aspect.log_result is True
        assert aspect.max_arg_length == 100
        
    def test_aspect_configuration(self):
        """Test aspect configuration options"""
        aspect = LoggingAspect(
            log_args=False,
            log_result=False,
            max_arg_length=50
        )
        
        assert aspect.log_args is False
        assert aspect.log_result is False
        assert aspect.max_arg_length == 50
        
    def test_before_logging(self):
        """Test logging before method execution"""
        # Set up logger with string handler
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("test_before")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        
        aspect = LoggingAspect(logger=logger)
        join_point = JoinPoint(
            target=MockObject(),
            method_name="method_with_args",
            args=(MockObject(), 10, 20),  # Note: first arg is 'self'
            kwargs={}
        )
        
        aspect.before(join_point)
        
        log_output = log_stream.getvalue()
        assert ">>> Entering MockObject.method_with_args" in log_output
        assert "10" in log_output  # Args should be logged
        assert "20" in log_output
        
    def test_after_returning_logging(self):
        """Test logging after successful method execution"""
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("test_after")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        
        aspect = LoggingAspect(logger=logger)
        join_point = JoinPoint(
            target=MockObject(),
            method_name="simple_method",
            args=(MockObject(),),  # 'self' as first arg
            kwargs={},
            result="result"  # Using 'result' not 'return_value'
        )
        # Set start time for duration calculation
        join_point.metadata['start_time'] = time.time()
        
        aspect.after_returning(join_point)
        
        log_output = log_stream.getvalue()
        assert "<<< Exiting MockObject.simple_method" in log_output
        assert "result" in log_output
        assert "ms)" in log_output  # Duration should be included
        
    def test_exception_logging(self):
        """Test logging exceptions"""
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("test_exception")
        logger.setLevel(logging.ERROR)
        logger.addHandler(handler)
        
        aspect = LoggingAspect(logger=logger)
        join_point = JoinPoint(
            target=MockObject(),
            method_name="failing_method",
            args=(MockObject(),),
            kwargs={},
            exception=ValueError("Test error")
        )
        # Set start time for duration calculation
        join_point.metadata['start_time'] = time.time()
        
        aspect.after_throwing(join_point)
        
        log_output = log_stream.getvalue()
        assert "!!! Exception in MockObject.failing_method" in log_output
        assert "ValueError: Test error" in log_output
        assert "ms)" in log_output  # Duration should be included
        
    def test_weaving_logging_aspect(self):
        """Test weaving logging aspect into object"""
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("test_weave")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        
        obj = MockObject()
        
        # Create aspect with custom pointcut for MockObject
        class TestLoggingAspect(LoggingAspect):
            def get_pointcut(self) -> str:
                return "MockObject.*"  # Match all MockObject methods
        
        aspect = TestLoggingAspect(logger=logger)
        weaver = AspectWeaver()
        
        weaver.add_aspect(aspect)
        weaver.weave(obj)
        
        # Call method
        result = obj.simple_method()
        
        log_output = log_stream.getvalue()
        
        assert ">>> Entering MockObject.simple_method" in log_output
        assert "<<< Exiting MockObject.simple_method" in log_output
        assert result == "result"
        
    def test_disable_arg_logging(self):
        """Test disabling argument logging"""
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("test_no_args")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        
        aspect = LoggingAspect(logger=logger, log_args=False)
        join_point = JoinPoint(
            target=MockObject(),
            method_name="method_with_args",
            args=(MockObject(), 10, 20),
            kwargs={"test": "value"}
        )
        
        aspect.before(join_point)
        
        log_output = log_stream.getvalue()
        assert ">>> Entering MockObject.method_with_args" in log_output
        assert "10" not in log_output  # Args should not be logged
        assert "test" not in log_output  # Kwargs should not be logged
        assert "with args:" not in log_output  # Args section should not appear
        
    def test_disable_result_logging(self):
        """Test disabling return value logging"""
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("test_no_result")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        
        aspect = LoggingAspect(logger=logger, log_result=False)
        join_point = JoinPoint(
            target=MockObject(),
            method_name="simple_method",
            args=(MockObject(),),
            kwargs={},
            result="Secret value"
        )
        join_point.metadata['start_time'] = time.time()
        
        aspect.after_returning(join_point)
        
        log_output = log_stream.getvalue()
        assert "<<< Exiting MockObject.simple_method" in log_output
        assert "Secret value" not in log_output  # Return value should not be logged
        assert "with result:" not in log_output  # Result section should not appear
        
    def test_excluded_methods(self):
        """Test excluding methods from logging"""
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("test_exclude")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        
        aspect = LoggingAspect(logger=logger)
        aspect.add_excluded_method("__str__")
        
        join_point = JoinPoint(
            target=MockObject(),
            method_name="__str__",
            args=(MockObject(),),
            kwargs={}
        )
        
        aspect.before(join_point)
        aspect.after_returning(join_point)
        
        log_output = log_stream.getvalue()
        assert log_output == ""  # Nothing should be logged


import time  # Import for duration calculation