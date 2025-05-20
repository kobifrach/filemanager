import os
import logging

def setup_logger(name: str):
    # Create the 'logs' directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Define the log file location and name
    log_file = os.path.join('logs', 'app.log')

    # Set up the logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Define the log format
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    # Handle logs to file
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handle logs to console (for app runtime display)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Return the logger
    return logger
