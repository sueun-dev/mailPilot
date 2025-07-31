"""Centralized logging configuration for mailPilot.

This module provides a comprehensive logging solution with:
- Environment-aware configuration (dev/test/prod)
- Structured logging with JSON format
- Security-conscious log sanitization
- Performance-optimized handlers
- Log rotation and retention
- Context injection for tracing
"""
import logging
import logging.handlers
import os
import re
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Union
from functools import lru_cache

# Import app configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.app_config import (
    ENV_LOG_LEVELS as CONFIG_ENV_LOG_LEVELS,
    LOG_DIR, MAIN_LOG_FILE, ERROR_LOG_FILE, SECURITY_LOG_FILE,
    LOG_FILE_MAX_BYTES, SECURITY_LOG_MAX_BYTES,
    LOG_BACKUP_COUNT, SECURITY_LOG_BACKUP_COUNT,
    THIRD_PARTY_LOG_LEVELS, SENSITIVE_PATTERNS as CONFIG_SENSITIVE_PATTERNS
)

# Convert string log levels to logging constants
ENV_LOG_LEVELS = {
    env: getattr(logging, level)
    for env, level in CONFIG_ENV_LOG_LEVELS.items()
}

# Convert sensitive patterns from config format
SENSITIVE_PATTERNS = [
    (pattern, f'{label}=***REDACTED***')
    for pattern, label in CONFIG_SENSITIVE_PATTERNS
]


class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive information from logs."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Redact sensitive data from log messages."""
        if hasattr(record, 'msg'):
            record.msg = self._sanitize_message(str(record.msg))
        
        # Sanitize any additional args
        if hasattr(record, 'args') and record.args:
            record.args = tuple(self._sanitize_message(str(arg)) for arg in record.args)
        
        return True
    
    def _sanitize_message(self, message: str) -> str:
        """Apply all sanitization patterns to a message."""
        for pattern, replacement in SENSITIVE_PATTERNS:
            if callable(replacement):
                message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
            else:
                message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        return message


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        # Save original values
        original_msg = record.msg
        original_args = record.args
        
        try:
            # Safely format the message
            if record.args:
                record.msg = SafeMessageAdapter.safe_format(record.msg, record.args)
                record.args = None  # Clear args after formatting
            
            log_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "thread": record.thread,
                "thread_name": record.threadName,
                "process": record.process,
            }
            
            # Add exception info if present
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            
            # Add any extra fields
            for key, value in record.__dict__.items():
                if key not in log_data and not key.startswith('_'):
                    try:
                        # Ensure the value is JSON serializable
                        json.dumps(value)
                        log_data[key] = value
                    except (TypeError, ValueError):
                        log_data[key] = str(value)
            
            return json.dumps(log_data)
        finally:
            # Restore original values
            record.msg = original_msg
            record.args = original_args


class SafeMessageAdapter:
    """Adapter to safely format log messages with mixed formatting styles."""
    
    @staticmethod
    def safe_format(msg, args):
        """Safely format message with args, handling both % and {} styles."""
        if not args:
            return str(msg)
        
        try:
            # First try % formatting (used by OpenAI/httpx)
            if '%' in str(msg):
                # Handle both single values and tuples
                if isinstance(args, tuple) and len(args) == 1:
                    return str(msg) % args[0]
                return str(msg) % args
        except (TypeError, ValueError):
            pass
        
        try:
            # Try {} formatting
            if '{' in str(msg) and '}' in str(msg):
                if isinstance(args, tuple):
                    return str(msg).format(*args)
                else:
                    return str(msg).format(args)
        except (TypeError, ValueError, IndexError):
            pass
        
        # Fallback: just concatenate
        return f"{msg} {args}"


class DevelopmentFormatter(logging.Formatter):
    """Human-readable formatter for development."""
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format with colors for development."""
        # Save original values
        original_msg = record.msg
        original_args = record.args
        
        try:
            # Safely format the message
            if record.args:
                record.msg = SafeMessageAdapter.safe_format(record.msg, record.args)
                record.args = None  # Clear args after formatting
            
            levelname = record.levelname
            if levelname in self.COLORS:
                levelname_color = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
                record.levelname = levelname_color
            
            # Format the timestamp
            timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
            
            # Build the log message
            message = f"{timestamp} | {record.levelname} | {record.name} | {record.getMessage()}"
            
            # Add exception info if present
            if record.exc_info:
                message += f"\n{self.formatException(record.exc_info)}"
            
            return message
        finally:
            # Restore original values
            record.msg = original_msg
            record.args = original_args


class LoggerFactory:
    """Factory for creating configured loggers."""
    
    _instance = None
    _loggers: Dict[str, logging.Logger] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.environment = os.getenv("MAILPILOT_ENV", "development").lower()
        self.log_dir = Path(os.getenv("MAILPILOT_LOG_DIR", "logs"))
        self.log_dir.mkdir(exist_ok=True)
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Configure the root logger."""
        root_logger = logging.getLogger()
        root_logger.setLevel(ENV_LOG_LEVELS.get(self.environment, logging.INFO))
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # Add appropriate handlers based on environment
        if self.environment == "development":
            self._add_console_handler(root_logger)
        else:
            self._add_file_handlers(root_logger)
            if self.environment == "test":
                self._add_console_handler(root_logger, structured=True)
        
        # Configure third-party library logging levels to reduce noise
        self._configure_third_party_loggers()
    
    def _configure_third_party_loggers(self):
        """Configure logging levels for third-party libraries."""
        # Suppress noisy third-party library logs
        third_party_loggers = {
            "openai": logging.WARNING,
            "httpx": logging.WARNING,
            "httpcore": logging.WARNING,
            "urllib3": logging.WARNING,
            "google": logging.WARNING,
            "google.auth": logging.WARNING,
            "google.api_core": logging.WARNING,
            "googleapiclient": logging.WARNING,
            "googleapiclient.discovery": logging.WARNING,
            "googleapiclient.discovery_cache": logging.ERROR,
        }
        
        for logger_name, level in third_party_loggers.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)
            # Ensure they use our safe formatters
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
    
    def _add_console_handler(self, logger: logging.Logger, structured: bool = False):
        """Add console handler to logger."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        if structured:
            console_handler.setFormatter(StructuredFormatter())
        else:
            console_handler.setFormatter(DevelopmentFormatter())
        
        # Add sensitive data filter
        console_handler.addFilter(SensitiveDataFilter())
        logger.addHandler(console_handler)
    
    def _add_file_handlers(self, logger: logging.Logger):
        """Add rotating file handlers for different log levels."""
        # General application log
        app_handler = logging.handlers.RotatingFileHandler(
            Path(MAIN_LOG_FILE),
            maxBytes=LOG_FILE_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT
        )
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(StructuredFormatter())
        app_handler.addFilter(SensitiveDataFilter())
        logger.addHandler(app_handler)
        
        # Error log
        error_handler = logging.handlers.RotatingFileHandler(
            Path(ERROR_LOG_FILE),
            maxBytes=LOG_FILE_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        error_handler.addFilter(SensitiveDataFilter())
        logger.addHandler(error_handler)
        
        # Security/Audit log
        security_handler = logging.handlers.RotatingFileHandler(
            Path(SECURITY_LOG_FILE),
            maxBytes=SECURITY_LOG_MAX_BYTES,
            backupCount=SECURITY_LOG_BACKUP_COUNT
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(StructuredFormatter())
        # Don't filter security logs - we want to see attempts
        logger.addHandler(security_handler)
    
    @lru_cache(maxsize=128)
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the given name."""
        if name not in self._loggers:
            logger = logging.getLogger(name)
            # Logger inherits configuration from root
            self._loggers[name] = logger
        
        return self._loggers[name]


# Global logger factory instance
logger_factory = LoggerFactory()


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger for the given module name.
    
    Args:
        name: Logger name, typically __name__ from the calling module
    
    Returns:
        Configured logger instance
    
    Example:
        >>> from utils.logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    return logger_factory.get_logger(name)


def configure_logging(
    environment: Optional[str] = None,
    log_dir: Optional[str] = None,
    log_level: Optional[Union[str, int]] = None
):
    """Configure logging for the application.
    
    Args:
        environment: Override environment (development/test/production)
        log_dir: Override log directory
        log_level: Override log level
    """
    if environment:
        os.environ["MAILPILOT_ENV"] = environment
    
    if log_dir:
        os.environ["MAILPILOT_LOG_DIR"] = log_dir
    
    # Reinitialize the logger factory
    global logger_factory
    logger_factory = LoggerFactory()
    
    if log_level:
        root_logger = logging.getLogger()
        if isinstance(log_level, str):
            log_level = getattr(logging, log_level.upper())
        root_logger.setLevel(log_level)


def log_function_call(func):
    """Decorator to log function calls with arguments and return values."""
    logger = get_logger(func.__module__)
    
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func_name} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"{func_name} raised exception: {e}", exc_info=True)
            raise
    
    return wrapper


def add_context(logger: logging.Logger, **context):
    """Add context to all logs from this logger.
    
    Example:
        >>> logger = get_logger(__name__)
        >>> add_context(logger, user_id="123", session_id="abc")
        >>> logger.info("User action")  # Will include user_id and session_id
    """
    class ContextAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            for key, value in self.extra.items():
                kwargs.setdefault('extra', {})[key] = value
            return msg, kwargs
    
    return ContextAdapter(logger, context)


# Performance monitoring utilities
class LogPerformance:
    """Context manager for logging performance metrics."""
    
    def __init__(self, logger: logging.Logger, operation: str, level: int = logging.DEBUG):
        self.logger = logger
        self.operation = operation
        self.level = level
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log(self.level, f"Starting {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        if exc_type:
            self.logger.error(
                f"{self.operation} failed after {duration:.3f}s: {exc_val}",
                exc_info=True
            )
        else:
            self.logger.log(
                self.level,
                f"{self.operation} completed in {duration:.3f}s"
            )