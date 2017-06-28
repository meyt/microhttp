from nanohttp import settings
from microhttp import bus
from logging.config import dictConfig
import logging
bus.ext.log.logger = logging.getLogger()


def configure():
    logging.config.dictConfig(dict(settings.logging))
    bus.ext.log.logger = logging.getLogger('main')


def get_logger() -> logging.Logger:
    return bus.ext.log.logger


def close():
    for handler in get_logger().handlers:
        handler.close()


def warning(message: str):
    bus.ext.log.logger.warning(message)


def info(message: str):
    bus.ext.log.logger.info(message)


def critical(message: str):
    bus.ext.log.logger.critical(message)


def debug(message: str):
    bus.ext.log.logger.debug(message)


def error(message: str):
    bus.ext.log.logger.error(message)


def exception(message: str):
    bus.ext.log.logger.exception(message)
