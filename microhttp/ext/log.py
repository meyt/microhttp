from logging import Logger, getLogger
from logging.config import dictConfig
from nanohttp import settings
from microhttp import bus
bus.ext.log.logger = getLogger()


def configure():
    dictConfig(dict(settings.logging))
    bus.ext.log.logger = getLogger('main')


def get_logger() -> Logger:
    return bus.ext.log.logger


def close():
    """ Close all logging handlers """
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
