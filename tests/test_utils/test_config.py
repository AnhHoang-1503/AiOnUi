import pytest
import os
from aionui.config import Config
from aionui.enums import Platform


def test_config_load(tmp_path):
    config_content = """
connect_over_cdp: true
user_data_dir: "user_data_dir"
chrome_binary_path: "chrome_binary_path"
headless: true
debug_port: 9222
"""
    config_path = os.path.join(tmp_path, "test_config.yaml")
    with open(config_path, "w") as f:
        f.write(config_content)
    config_file = str(config_path)
    config = Config(config_file)
    assert config.debug_port == 9222
    assert config.user_data_dir == "user_data_dir"
    assert config.chrome_binary_path == "chrome_binary_path"


def test_config_platform_detection():
    config = Config()
    assert isinstance(config.platform, Platform)
