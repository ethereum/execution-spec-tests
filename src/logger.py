import logging
import logging.config
import configparser
import os
import sys


class CustomLogger(logging.Logger):
    def error(self, message):
        super().error(message)

    def critical(self, message, exit_code=1):
        super().critical(message)
        sys.exit(exit_code)


def setup_logger(name):
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logger.cfg'))
    logging.config.fileConfig(config, disable_existing_loggers=False)

    # Set the CustomLogger class as the loggerClass for the logging module
    logging.setLoggerClass(CustomLogger)

    logger = logging.getLogger(name)

    return logger
