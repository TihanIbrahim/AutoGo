import logging

def setup_logger(name=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO) 

    if not logger.hasHandlers():  
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        logger.addHandler(ch)

    return logger         





