"""
Example demonstrating BioCode's centralized logging system
"""

import asyncio
import logging
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.enhanced_codecell import EnhancedCodeCell
from src.core.advanced_codetissue import AdvancedCodeTissue
from src.utils.logging_config import setup_logging, get_logger


async def demonstrate_logging():
    """Demonstrate the logging features"""
    
    # Setup logging with custom configuration
    setup_logging(
        log_level="DEBUG",
        log_dir="logs/demo",
        enable_console_logging=True,
        enable_file_logging=True
    )
    
    # Get a logger for the demo
    logger = get_logger(__name__)
    logger.info("Starting BioCode logging demonstration")
    
    # Create a tissue
    tissue = AdvancedCodeTissue("LoggingDemoTissue")
    tissue.register_cell_type(EnhancedCodeCell)
    
    # Grow some cells
    logger.info("Growing cells in tissue...")
    cell1 = tissue.grow_cell("demo_cell_1", "EnhancedCodeCell")
    cell2 = tissue.grow_cell("demo_cell_2", "EnhancedCodeCell")
    
    # Perform some operations
    logger.info("Performing cell operations...")
    try:
        result = await cell1.perform_operation("process_data", energy_cost=5)
        logger.debug(f"Operation result: {result}")
    except Exception as e:
        logger.error(f"Operation failed: {e}")
    
    # Demonstrate cell lifecycle events
    logger.info("Demonstrating cell lifecycle...")
    
    # Cell infection
    cell1.infect(Exception("Demo infection"))
    
    # Cell healing
    cell1.heal()
    
    # Cell division
    daughter_cell = cell1.divide()
    if daughter_cell:
        logger.info(f"Cell division successful: {daughter_cell.name}")
    
    # Trigger apoptosis
    logger.info("Triggering apoptosis...")
    cell2.trigger_apoptosis()
    
    # Demonstrate different log levels
    logger.debug("This is a DEBUG level message - detailed cellular operations")
    logger.info("This is an INFO level message - tissue-level events")
    logger.warning("This is a WARNING level message - organ-level warnings")
    logger.error("This is an ERROR level message - system-level errors")
    logger.critical("This is a CRITICAL level message - life-threatening events")
    
    # Get tissue diagnostics
    diagnostics = tissue.get_tissue_diagnostics()
    logger.info(f"Tissue diagnostics: {diagnostics}")


def demonstrate_security_logging():
    """Demonstrate security-specific logging"""
    from src.utils.logging_config import log_security_event
    
    # Log various security events
    log_security_event(
        "warning",
        "Unauthorized access attempt",
        {"cell_id": "suspicious_cell", "action": "data_access", "result": "blocked"}
    )
    
    log_security_event(
        "error",
        "Security breach detected",
        {"tissue": "critical_tissue", "threat_level": "high", "response": "quarantine"}
    )


def demonstrate_performance_logging():
    """Demonstrate performance logging"""
    from src.utils.logging_config import BioCodeLogger
    
    perf_logger = BioCodeLogger.get_performance_logger()
    
    # Log performance metrics
    perf_logger.info("Performance metric", extra={
        "metric": "memory_usage",
        "value": 256.5,
        "unit": "MB"
    })
    
    perf_logger.info("Performance metric", extra={
        "metric": "operation_latency",
        "value": 15.3,
        "unit": "ms"
    })


def main():
    """Main demonstration"""
    print("=" * 60)
    print("BioCode Logging System Demonstration")
    print("=" * 60)
    
    # Run async demonstration
    asyncio.run(demonstrate_logging())
    
    print("\n" + "=" * 60)
    print("Security Logging Demonstration")
    print("=" * 60)
    demonstrate_security_logging()
    
    print("\n" + "=" * 60)
    print("Performance Logging Demonstration")
    print("=" * 60)
    demonstrate_performance_logging()
    
    print("\n" + "=" * 60)
    print("Check the logs/ directory for log files:")
    print("- logs/demo/biocode.log - All logs")
    print("- logs/demo/biocode_errors.log - Error logs only")
    print("- logs/demo/biocode_security.log - Security events")
    print("=" * 60)


if __name__ == "__main__":
    main()