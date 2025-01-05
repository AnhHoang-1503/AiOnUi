import pytest
from aionui import AiOnUI, AiModel
import codecs


@pytest.fixture
def config_file(tmp_path):
    config_content = """
connect_over_cdp: true
"""
    config_path = tmp_path / "test_config.yaml"
    with open(config_path, "w") as f:
        f.write(config_content)
    return str(config_path)


@pytest.fixture
def content_file(tmp_path):
    file_path = tmp_path / "test.txt"
    with codecs.open(file_path, "w", encoding="utf-8") as f:
        f.write("Xin chào")
    return str(file_path)
