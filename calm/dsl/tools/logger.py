import logging

from colorlog import ColoredFormatter
import time
import sys

# Used for looking at verbose level
VERBOSE_LEVEL = 20


class StdOutFilter(logging.Filter):
    """Filter for Stdout stream handler"""

    def filter(self, rec):
        return rec.levelno <= logging.WARNING


class StdErrFilter(logging.Filter):
    """Filter for Stderr stream handler"""

    def filter(self, rec):
        return rec.levelno > logging.WARNING


class CustomLogging:
    """
    customization on logging module.

    custom logger with following log levels with appropriate color codes and
    custom formatting for messages::“

        * LOG.debug     - [DEBUG]
        * LOG.info      - [INFO]
        * LOG.warn      - [WARNING]
        * LOG.error     - [ERROR]
        * LOG.critical  - [CRITICAL]
        * LOG.exception - [ERROR]

    """

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __init__(self, name):
        """
        Build CustomLogger based on logging module

        Args:
            name(str): name of the module/logger

        Returns:
           None
        """

        # create console and file handler
        self._ch1 = logging.StreamHandler(sys.stdout)
        self._ch1.addFilter(StdOutFilter())

        self._ch2 = logging.StreamHandler()
        self._ch2.addFilter(StdErrFilter())

        # add custom formatter to console handler
        self.__addCustomFormatter(self._ch1)
        self.__addCustomFormatter(self._ch2)

        # create custom logger
        self._logger = logging.getLogger(name)

        # add console to logger
        self._logger.addHandler(self._ch1)
        self._logger.addHandler(self._ch2)

    def get_logger(self):
        self.set_logger_level(VERBOSE_LEVEL)
        return self._logger

    def get_logging_levels(self):
        return [
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]

    def set_logger_level(self, lvl):
        """sets the logger verbose level"""
        self._logger.setLevel(lvl)

    def info(self, msg):
        """
        info log level

        Args:
            msg (str): message to log

        Returns:
            None
        """
        logger = self.get_logger()
        return logger.info(msg)

    def warning(self, msg):
        """
        warning log level

        Args:
            msg (str): message to log

        Returns:
            None
        """

        logger = self.get_logger()
        return logger.warning(msg)

    def error(self, msg):
        """
        error log level

        Args:
            msg (str): message to log

        Returns:
            None
        """

        logger = self.get_logger()
        return logger.error(msg)

    def exception(self, msg):
        """
        exception log level

        Args:
            msg (str): message to log

        Returns:
            None
        """

        logger = self.get_logger()
        return logger.exception(msg)

    def critical(self, msg):
        """
        critical log level

        Args:
            msg (str): message to log

        Returns:
            None
        """

        logger = self.get_logger()
        return logger.critical(msg)

    def debug(self, msg):
        """
        debug log level

        Args:
            msg (str): message to log

        Returns:
            None
        """

        logger = self.get_logger()
        return logger.debug(msg)

    def __addCustomFormatter(self, ch):
        """
        add ColorFormatter with custom colors for each log level

        Args:
            None

        Returns
            None
        """

        fmt = (
            "\n[%(asctime)s %(name)s "
            "[%(log_color)s%(levelname)s%(reset)s] %(message)s"
        )

        formatter = ColoredFormatter(
            fmt,
            datefmt="%Y-%m-%d %H:%M:%S",
            reset=True,
            log_colors={
                "DEBUG": "purple",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            },
        )
        formatter.converter = time.gmtime

        # add formatter to console handler
        ch.setFormatter(formatter)


def get_logging_handle(name):
    """returns the CustomLogging object"""

    logging_handle = CustomLogging(name)
    return logging_handle


def set_verbose_level(verbose_level):
    global VERBOSE_LEVEL
    VERBOSE_LEVEL = verbose_level
