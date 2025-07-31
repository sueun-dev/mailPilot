"""Tests for the logging configuration module."""
import unittest
import logging
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.utils.logging_config import (
    get_logger,
    configure_logging,
    SensitiveDataFilter,
    StructuredFormatter,
    DevelopmentFormatter,
    LogPerformance,
    add_context
)


class TestSensitiveDataFilter(unittest.TestCase):
    """Test the sensitive data redaction filter."""
    
    def setUp(self):
        self.filter = SensitiveDataFilter()
    
    def test_redact_api_key(self):
        """Test API key redaction."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Using api_key=sk-1234567890abcdef",
            args=(),
            exc_info=None
        )
        
        self.filter.filter(record)
        self.assertIn("api_key=***REDACTED***", record.msg)
        self.assertNotIn("sk-1234567890abcdef", record.msg)
    
    def test_redact_password(self):
        """Test password redaction."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Login with password='super_secret_123'",
            args=(),
            exc_info=None
        )
        
        self.filter.filter(record)
        self.assertIn("password=***REDACTED***", record.msg)
        self.assertNotIn("super_secret_123", record.msg)
    
    def test_redact_email(self):
        """Test email redaction."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Sending email to user@example.com",
            args=(),
            exc_info=None
        )
        
        self.filter.filter(record)
        self.assertIn("use***@***", record.msg)
        self.assertNotIn("user@example.com", record.msg)
    
    def test_multiple_redactions(self):
        """Test multiple sensitive data redactions."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Auth with token=abc123 for user test@example.com with client_secret=xyz789",
            args=(),
            exc_info=None
        )
        
        self.filter.filter(record)
        self.assertIn("token=***REDACTED***", record.msg)
        self.assertIn("tes***@***", record.msg)
        self.assertIn("client_secret=***REDACTED***", record.msg)


class TestStructuredFormatter(unittest.TestCase):
    """Test the JSON structured formatter."""
    
    def setUp(self):
        self.formatter = StructuredFormatter()
    
    def test_basic_formatting(self):
        """Test basic JSON formatting."""
        record = logging.LogRecord(
            name="test.module",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        output = self.formatter.format(record)
        data = json.loads(output)
        
        self.assertEqual(data["level"], "INFO")
        self.assertEqual(data["logger"], "test.module")
        self.assertEqual(data["message"], "Test message")
        self.assertEqual(data["line"], 42)
        self.assertIn("timestamp", data)
    
    def test_exception_formatting(self):
        """Test exception info formatting."""
        try:
            raise ValueError("Test error")
        except ValueError:
            import sys
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=1,
                msg="Error occurred",
                args=(),
                exc_info=sys.exc_info()
            )
        
        output = self.formatter.format(record)
        data = json.loads(output)
        
        self.assertIn("exception", data)
        self.assertIn("ValueError: Test error", data["exception"])
    
    def test_extra_fields(self):
        """Test extra fields are included."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test",
            args=(),
            exc_info=None
        )
        record.user_id = "123"
        record.request_id = "abc-def"
        
        output = self.formatter.format(record)
        data = json.loads(output)
        
        self.assertEqual(data["user_id"], "123")
        self.assertEqual(data["request_id"], "abc-def")


class TestLoggerFactory(unittest.TestCase):
    """Test the logger factory."""
    
    def test_get_logger(self):
        """Test getting a logger."""
        logger = get_logger("test.module")
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test.module")
    
    def test_logger_caching(self):
        """Test that loggers are cached."""
        logger1 = get_logger("test.cached")
        logger2 = get_logger("test.cached")
        self.assertIs(logger1, logger2)
    
    @patch.dict(os.environ, {"MAILPILOT_ENV": "production"})
    def test_production_environment(self):
        """Test production environment configuration."""
        from src.utils.logging_config import LoggerFactory
        factory = LoggerFactory()
        self.assertEqual(factory.environment, "production")
    
    @patch.dict(os.environ, {"MAILPILOT_ENV": "development"})
    def test_development_environment(self):
        """Test development environment configuration."""
        from src.utils.logging_config import LoggerFactory
        factory = LoggerFactory()
        self.assertEqual(factory.environment, "development")


class TestLogPerformance(unittest.TestCase):
    """Test the performance logging context manager."""
    
    def test_successful_operation(self):
        """Test logging successful operation."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)
        
        with self.assertLogs("test", level="DEBUG") as cm:
            with LogPerformance(logger, "test operation"):
                # Simulate some work
                pass
        
        self.assertEqual(len(cm.output), 2)
        self.assertIn("Starting test operation", cm.output[0])
        self.assertIn("test operation completed in", cm.output[1])
    
    def test_failed_operation(self):
        """Test logging failed operation."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.ERROR)
        
        with self.assertLogs("test", level="ERROR") as cm:
            try:
                with LogPerformance(logger, "failing operation"):
                    raise ValueError("Test error")
            except ValueError:
                pass
        
        self.assertIn("failing operation failed after", cm.output[0])
        self.assertIn("ValueError: Test error", cm.output[0])


class TestAddContext(unittest.TestCase):
    """Test the context adding utility."""
    
    def test_add_context(self):
        """Test adding context to logger."""
        base_logger = logging.getLogger("test")
        logger = add_context(base_logger, user_id="123", session_id="abc")
        
        # Create a handler to capture the output
        handler = MagicMock()
        handler.level = logging.DEBUG  # Set the level attribute
        base_logger.addHandler(handler)
        
        logger.info("Test message")
        
        # Check that handle was called with extra context
        self.assertTrue(handler.handle.called)
        record = handler.handle.call_args[0][0]
        self.assertEqual(record.user_id, "123")
        self.assertEqual(record.session_id, "abc")


class TestIntegration(unittest.TestCase):
    """Integration tests for the logging system."""
    
    def test_full_logging_flow(self):
        """Test complete logging flow with all components."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Configure logging for test
            configure_logging(
                environment="test",
                log_dir=temp_dir,
                log_level="DEBUG"
            )
            
            # Get a logger and log some messages
            logger = get_logger("test.integration")
            
            # Add context
            context_logger = add_context(logger, request_id="test-123")
            
            # Log various levels
            context_logger.debug("Debug message")
            context_logger.info("Info with sensitive api_key=secret123")
            context_logger.warning("Warning message")
            
            # Log with performance
            with LogPerformance(logger, "test operation"):
                context_logger.info("Operation in progress")
            
            # Try to log an error
            try:
                raise ValueError("Test error")
            except ValueError:
                context_logger.error("Error occurred", exc_info=True)
            
            # Check that log files were created
            log_files = os.listdir(temp_dir)
            self.assertIn("mailpilot.log", log_files)
            self.assertIn("mailpilot_errors.log", log_files)


class TestLogFunctionDecorator(unittest.TestCase):
    """Test the log_function_call decorator."""
    
    def test_log_function_call_success(self):
        """Test decorator logs successful function calls."""
        from src.utils.logging_config import log_function_call
        
        # The decorator uses func.__module__ before decoration, so we need to set it before decorating
        def test_function(a, b=1):
            return a + b
        
        test_function.__module__ = 'test.module'
        decorated_function = log_function_call(test_function)
        
        with self.assertLogs('test.module', level='DEBUG') as cm:
            result = decorated_function(2, b=3)
        
        self.assertEqual(result, 5)
        self.assertEqual(len(cm.output), 2)
        self.assertIn("Calling test_function", cm.output[0])
        self.assertIn("args=(2,)", cm.output[0])
        self.assertIn("kwargs={'b': 3}", cm.output[0])
        self.assertIn("test_function returned: 5", cm.output[1])
    
    def test_log_function_call_exception(self):
        """Test decorator logs exceptions."""
        from src.utils.logging_config import log_function_call
        
        def failing_function():
            raise ValueError("Test error")
        
        failing_function.__module__ = 'test.module'
        decorated_function = log_function_call(failing_function)
        
        with self.assertLogs('test.module', level='ERROR') as cm:
            with self.assertRaises(ValueError):
                decorated_function()
        
        self.assertIn("failing_function raised exception: Test error", cm.output[0])


if __name__ == "__main__":
    unittest.main()