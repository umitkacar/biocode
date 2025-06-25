"""
Centralized logging configuration for BioCode

This module provides consistent logging setup across all BioCode components,
following biological metaphors for log levels and contexts.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional


class BiologicalLogLevel(Enum):
    """Biological metaphor for log levels"""

    CELLULAR = logging.DEBUG  # Detailed cellular operations
    TISSUE = logging.INFO  # Tissue-level events
    ORGAN = logging.WARNING  # Organ-level warnings
    SYSTEM = logging.ERROR  # System-level errors
    CRITICAL = logging.CRITICAL  # Life-threatening events


class BioCodeFormatter(logging.Formatter):
    """Custom formatter with biological context"""

    COLORS = {
        logging.DEBUG: "\033[36m",  # Cyan
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors and sys.stdout.isatty()
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with biological context"""
        # Add biological context if available
        bio_context = []
        if hasattr(record, "cell_id"):
            bio_context.append(f"Cell:{record.cell_id}")
        if hasattr(record, "tissue_name"):
            bio_context.append(f"Tissue:{record.tissue_name}")
        if hasattr(record, "organ_name"):
            bio_context.append(f"Organ:{record.organ_name}")

        context_str = f"[{' > '.join(bio_context)}]" if bio_context else ""

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )[:-3]

        # Build log message
        level_name = record.levelname
        if self.use_colors and record.levelno in self.COLORS:
            level_name = f"{self.COLORS[record.levelno]}{level_name}{self.RESET}"

        message = f"{timestamp} | {level_name:8} | {record.name} {context_str} | {record.getMessage()}"

        # Add exception info if present
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"

        return message


class BioCodeLogger:
    """Factory for creating BioCode loggers"""

    _loggers: Dict[str, logging.Logger] = {}
    _initialized: bool = False
    _log_dir: Optional[Path] = None

    @classmethod
    def setup_logging(
        cls,
        log_level: str = "INFO",
        log_dir: Optional[str] = None,
        enable_file_logging: bool = True,
        enable_console_logging: bool = True,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
    ) -> None:
        """
        Setup global logging configuration

        Args:
            log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files (creates logs/ if not specified)
            enable_file_logging: Whether to log to files
            enable_console_logging: Whether to log to console
            max_file_size: Maximum size of each log file before rotation
            backup_count: Number of backup files to keep
        """
        if cls._initialized:
            return

        # Set log directory
        if log_dir:
            cls._log_dir = Path(log_dir)
        else:
            cls._log_dir = Path.cwd() / "logs"

        if enable_file_logging:
            cls._log_dir.mkdir(parents=True, exist_ok=True)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))

        # Remove existing handlers
        root_logger.handlers.clear()

        # Console handler
        if enable_console_logging:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(BioCodeFormatter(use_colors=True))
            root_logger.addHandler(console_handler)

        # File handlers
        if enable_file_logging:
            # Main log file with rotation
            file_handler = logging.handlers.RotatingFileHandler(
                cls._log_dir / "biocode.log",
                maxBytes=max_file_size,
                backupCount=backup_count,
            )
            file_handler.setFormatter(BioCodeFormatter(use_colors=False))
            root_logger.addHandler(file_handler)

            # Error log file
            error_handler = logging.handlers.RotatingFileHandler(
                cls._log_dir / "biocode_errors.log",
                maxBytes=max_file_size,
                backupCount=backup_count,
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(BioCodeFormatter(use_colors=False))
            root_logger.addHandler(error_handler)

        cls._initialized = True

    @classmethod
    def get_logger(
        cls,
        name: str,
        cell_id: Optional[str] = None,
        tissue_name: Optional[str] = None,
        organ_name: Optional[str] = None,
    ) -> logging.Logger:
        """
        Get a logger with biological context

        Args:
            name: Logger name (usually __name__)
            cell_id: Optional cell identifier
            tissue_name: Optional tissue name
            organ_name: Optional organ name

        Returns:
            Configured logger with biological context
        """
        # Ensure logging is setup
        if not cls._initialized:
            cls.setup_logging()

        # Create or get logger
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        else:
            logger = cls._loggers[name]

        # Create adapter with biological context
        extra = {}
        if cell_id:
            extra["cell_id"] = cell_id
        if tissue_name:
            extra["tissue_name"] = tissue_name
        if organ_name:
            extra["organ_name"] = organ_name

        if extra:
            return logging.LoggerAdapter(logger, extra)
        return logger

    @classmethod
    def get_performance_logger(cls) -> logging.Logger:
        """Get specialized logger for performance metrics"""
        logger = cls.get_logger("biocode.performance")
        # Performance logs only at INFO level and above
        logger.setLevel(logging.INFO)
        return logger

    @classmethod
    def get_security_logger(cls) -> logging.Logger:
        """Get specialized logger for security events"""
        logger = cls.get_logger("biocode.security")

        # Add security-specific file handler if not already added
        if cls._initialized and cls._log_dir:
            security_log = cls._log_dir / "biocode_security.log"
            has_security_handler = any(
                isinstance(h, logging.FileHandler) and h.baseFilename == str(security_log)
                for h in logger.handlers
            )

            if not has_security_handler:
                security_handler = logging.handlers.RotatingFileHandler(
                    security_log, maxBytes=10 * 1024 * 1024, backupCount=10
                )
                security_handler.setFormatter(BioCodeFormatter(use_colors=False))
                logger.addHandler(security_handler)

        return logger


# Convenience functions
def get_logger(name: str, **context: Any) -> logging.Logger:
    """Convenience function to get a logger"""
    return BioCodeLogger.get_logger(name, **context)


def setup_logging(**kwargs: Any) -> None:
    """Convenience function to setup logging"""
    BioCodeLogger.setup_logging(**kwargs)


# Example usage for different components
class LoggingMixin:
    """Mixin to add logging capabilities to BioCode components"""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging for this component"""
        # Determine biological context
        context = {}
        if hasattr(self, "name"):
            if hasattr(self, "cell_type"):
                context["cell_id"] = self.name
            elif hasattr(self, "tissue_name"):
                context["tissue_name"] = self.name
            elif hasattr(self, "organ_name"):
                context["organ_name"] = self.name

        self.logger = get_logger(self.__class__.__module__, **context)


# Specialized log functions for biological events
def log_cell_event(
    logger: logging.Logger, event: str, cell_id: str, **kwargs: Any
) -> None:
    """Log cell-level events"""
    extra = {"cell_id": cell_id, **kwargs}
    logger.debug(f"Cell Event: {event}", extra=extra)


def log_tissue_event(
    logger: logging.Logger, event: str, tissue_name: str, **kwargs: Any
) -> None:
    """Log tissue-level events"""
    extra = {"tissue_name": tissue_name, **kwargs}
    logger.info(f"Tissue Event: {event}", extra=extra)


def log_system_event(logger: logging.Logger, event: str, **kwargs: Any) -> None:
    """Log system-level events"""
    logger.warning(f"System Event: {event}", extra=kwargs)


def log_security_event(
    severity: str, event: str, details: Dict[str, Any], **kwargs: Any
) -> None:
    """Log security-related events"""
    security_logger = BioCodeLogger.get_security_logger()
    log_method = getattr(security_logger, severity.lower(), security_logger.warning)
    log_method(f"Security Event: {event}", extra={"details": details, **kwargs})