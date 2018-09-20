from logging import Logger, getLogger, shutdown
from logging.config import dictConfig

from nanohttp import settings


def configure():
    dictConfig(dict(settings.logging))


def get_logger(logger_name: str = 'main') -> Logger:
    return getLogger(logger_name)


def close():
    """ Close all logging handlers """
    shutdown()


def warning(message: str):
    get_logger().warning(message)


def info(message: str):
    get_logger().info(message)


def critical(message: str):
    get_logger().critical(message)


def debug(message: str):
    get_logger().debug(message)


def error(message: str):
    get_logger().error(message)


def exception(message: str):
    get_logger().exception(message)
