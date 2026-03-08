import logging
import sys

def setup_logging(log_level: str = "INFO"):
    """
    Configure standard logging for the application.
    Outputs to stdout as expected by 12-factor apps and Docker.
    """
    logging.basicConfig(
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Optional: Suppress extra chatty libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger = logging.getLogger("krishi_saathi")
    logger.info("Logging configured successfully.")
    return logger

# Global instance configured initially
logger = setup_logging()
