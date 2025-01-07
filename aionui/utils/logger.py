from logging import getLogger
import logging
import sys
import traceback
from types import TracebackType
from typing import Mapping, Optional
from .singleton import SingletonMeta


class ColorFormatter(logging.Formatter):
    """
    Custom formatter adding colors to log levels
    """

    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    purple = "\x1b[35m"
    green = "\x1b[32m"

    FORMATS = {
        logging.DEBUG: f"{purple}%(asctime)s{reset} - {green}%(name)s{reset} - "
        f"{grey}%(levelname)s{reset} - {grey}[Line %(lineno)d] - %(message)s{reset}",
        logging.INFO: f"{purple}%(asctime)s{reset} - {green}%(name)s{reset} - "
        f"{blue}%(levelname)s{reset} - {blue}[Line %(lineno)d] - %(message)s{reset}",
        logging.WARNING: f"{purple}%(asctime)s{reset} - {green}%(name)s{reset} - "
        f"{yellow}%(levelname)s{reset} - {yellow}[Line %(lineno)d] - %(message)s{reset}",
        logging.ERROR: f"{purple}%(asctime)s{reset} - {green}%(name)s{reset} - "
        f"{red}%(levelname)s{reset} - {red}[Line %(lineno)d] - %(message)s\n%(traceback)s{reset}",
        logging.CRITICAL: f"{purple}%(asctime)s{reset} - {green}%(name)s{reset} - "
        f"{bold_red}%(levelname)s{reset} - {bold_red}[Line %(lineno)d] - %(message)s\n%(traceback)s{reset}",
    }

    def format(self, record):
        if record.levelno in (logging.ERROR, logging.CRITICAL, logging.DEBUG):
            if record.exc_info:
                exc_type, exc_value, exc_traceback = record.exc_info
                record.traceback = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                record.exc_info = None
                record.exc_text = None
            else:
                record.traceback = "".join(traceback.format_stack())

        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

    def formatException(self) -> str:
        return ""


class CustomLogger(logging.Logger):
    def error(
        self,
        msg: object,
        *args: object,
        exc_info: Optional[bool | tuple[type[BaseException], BaseException, TracebackType] | BaseException] = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Optional[Mapping[str, object]] = None,
    ) -> None:
        exc_info = exc_info or True
        return super().error(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )

    def critical(
        self,
        msg: object,
        *args: object,
        exc_info: Optional[bool | tuple[type[BaseException], BaseException, TracebackType] | BaseException] = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Optional[Mapping[str, object]] = None,
    ) -> None:
        exc_info = exc_info or True
        return super().critical(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )


class LoggerManager(metaclass=SingletonMeta):
    def __init__(self):
        self._loggers = {}
        self._original_logger_class = logging.getLoggerClass()

    def setup_logger(self, name: str = "aionui", log_level: int = logging.INFO) -> logging.Logger:
        if name in self._loggers:
            return self._loggers[name]

        logging.setLoggerClass(CustomLogger)
        logger = getLogger(f"aionui.{name}")
        logging.setLoggerClass(self._original_logger_class)

        logger.handlers.clear()
        logger.setLevel(log_level)
        logger.propagate = False

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(ColorFormatter())
        logger.addHandler(console_handler)

        self._loggers[name] = logger
        return logger

    def get_logger(self, name: str = "aionui") -> logging.Logger:
        """Get an existing logger or create a new one"""
        if name not in self._loggers:
            return self.setup_logger(name)
        return self._loggers[name]


logger_manager: LoggerManager = LoggerManager()
get_logger = logger_manager.get_logger
setup_logger = logger_manager.setup_logger
