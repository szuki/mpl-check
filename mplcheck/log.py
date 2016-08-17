import logging

LOG_FORMAT = "%(asctime)s %(name)s:%(lineno)d %(levelname)s %(message)s"
DEFAULT_LEVEL = logging.DEBUG


def setup_handler(log_format=LOG_FORMAT):
    console_log_handler = logging.StreamHandler()
    console_log_handler.setFormatter(logging.Formatter(log_format))
    return console_log_handler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.addHandler(LOG_HANDLER)
    logger.setLevel(DEFAULT_LEVEL)
    return logger

LOG_HANDLER = setup_handler()
