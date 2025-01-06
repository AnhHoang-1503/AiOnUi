from _pytest._py.path import LocalPath
import pytest
import pytest_asyncio
import codecs
import asyncio
from playwright.async_api import async_playwright


@pytest.fixture(scope="session")
def config_file(tmpdir_factory: pytest.TempdirFactory):
    config_content = """
user_data_dir: C:\\Users\\vutri\\AppData\\Local\\Google\\Chrome\\User Data
headless: false
"""
    config_path: LocalPath = tmpdir_factory.mktemp("test_config").join("test_config.yaml")
    with open(config_path, "w") as f:
        f.write(config_content)
    return str(config_path.strpath)


@pytest.fixture(scope="session")
def content_file(tmpdir_factory: pytest.TempdirFactory):
    file_path = tmpdir_factory.mktemp("test_content").join("test.txt")
    with codecs.open(file_path, "w", encoding="utf-8") as f:
        f.write("Xin chào")
    return str(file_path.strpath)
