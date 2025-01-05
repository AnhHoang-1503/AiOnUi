import pytest
from aionui.utils.logger import get_logger


def test_logger_creation():
    logger = get_logger("test")
    assert logger is not None
    assert logger.name == "aionui.test"
