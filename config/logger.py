import logging
import sys
from pathlib import Path
from config.settings import settings

def setup_logger():
    """
    Configures the root logging level, console handler, and file handler.
    Ensures that all logs from the application are formatted consistently
    and written to stdout and logs/cortexweb.log.
    """
    log_dir = settings.get_absolute_logs_dir()
    log_file = log_dir / "cortexweb.log"

    # Detailed log format with timestamp, level, name/module, and message
    log_format = "%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Get root logger
    root_logger = logging.getLogger()
    
    # Remove any pre-existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set root logger level from settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger.setLevel(log_level)

    # Standard Output (Console) Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    root_logger.addHandler(console_handler)

    # File Handler for persistence
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    root_logger.addHandler(file_handler)

    # Mute verbose logs from dependencies unless in DEBUG mode
    if log_level > logging.DEBUG:
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)
        logging.getLogger("playwright").setLevel(logging.WARNING)

    logging.info(f"Logging initialized. Level: {settings.LOG_LEVEL}, Output: {log_file}")

# Setup logging immediately on import of this helper module
setup_logger()
