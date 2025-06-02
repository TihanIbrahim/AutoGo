import logging

def setup_logger(name=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)  # Set log level to INFO

    # Only add handler if there isn't one already to avoid duplicates
    if not logger.hasHandlers():
        ch = logging.StreamHandler()  # Create console handler
        ch.setLevel(logging.INFO)  # Set console handler log level

        # Define log message format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)  # Apply format to console handler

        logger.addHandler(ch)  # Add console handler to logger

    return logger  # Return configured logger



