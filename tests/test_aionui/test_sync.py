from typing import Literal
import pytest
import os
from aionui import AiOnUi
from aionui.models import GPT, Claude, Gemini
from playwright.sync_api import Page, Browser, BrowserContext, Playwright
from unittest.mock import Mock, patch


@pytest.fixture
def mock_page(mocker):
    mock = Mock(spec=Page)
    mock.title.return_value = "ChatGPT"
    return mock


@pytest.fixture
def mock_context(mocker, mock_page):
    mock = Mock(spec=BrowserContext)
    mock.new_page.return_value = mock_page
    return mock


@pytest.fixture
def mock_browser(mocker, mock_context):
    mock = Mock(spec=Browser)
    mock.new_context.return_value = mock_context
    mock.contexts = [mock_context]
    return mock


@pytest.fixture
def mock_playwright(mocker, mock_browser):
    mock = Mock(spec=Playwright)
    mock.chromium.connect_over_cdp.return_value = mock_browser
    return mock


class TestAiOnUiConfig:
    def test_custom_config(self, tmp_path):
        config_content = """
        debug_port: 9223
        user_data_dir: "user_data_dir"
        chrome_binary_path: "chrome_binary_path"
        """
        config_path = os.path.join(tmp_path, "test_config.yaml")
        with open(config_path, "w") as f:
            f.write(config_content)

        aionui = AiOnUi()
        aionui.load_config(config_path)
        assert aionui.config.debug_port == 9223
        assert aionui.config.user_data_dir == "user_data_dir"
        assert aionui.config.chrome_binary_path == "chrome_binary_path"


class TestAiOnUiSync:
    @pytest.mark.parametrize("model_type", ["gpt"])  # TODO: Add other models
    def test_sync_model(self, mock_page: Mock, model_type: Literal["gpt", "claude", "gemini"]):
        aionui = AiOnUi(page=mock_page)
        with aionui.model_sync(model_type) as model:
            assert model is not None
            assert model.page == mock_page
            if model_type == "gpt":
                assert isinstance(model, GPT)
            elif model_type == "claude":
                assert isinstance(model, Claude)
            elif model_type == "gemini":
                assert isinstance(model, Gemini)

    def test_clean_up_page(self, mock_page):
        aionui = AiOnUi(page=mock_page)
        with aionui.model_sync("gpt") as model:
            assert model.page == mock_page

    def test_clean_up_context(self, mock_context, mock_page):
        aionui = AiOnUi(context=mock_context)
        with aionui.model_sync("gpt") as model:
            assert model.page == mock_page
        assert mock_context.new_page.call_count == 1
        assert mock_page.close.call_count == 1

    def test_clean_up_browser(self, mock_browser, mock_page, mock_context):
        aionui = AiOnUi(browser=mock_browser)
        with aionui.model_sync("gpt") as model:
            assert model.page == mock_page
        assert mock_context.new_page.call_count == 1
        assert mock_page.close.call_count == 1

    def test_clean_up_playwright(self, mock_playwright, mock_page, mock_context, mock_browser):
        aionui = AiOnUi(playwright=mock_playwright)
        with aionui.model_sync("gpt") as model:
            assert model.page == mock_page
        assert mock_playwright.chromium.connect_over_cdp.call_count == 1
        assert mock_page.close.call_count == 1
        assert mock_context.close.call_count == 1
        assert mock_browser.close.call_count == 1

    def test_clean_up_no_args(self, monkeypatch, mock_page, mock_context, mock_browser, mock_playwright):
        mock_popen = Mock()
        monkeypatch.setattr("subprocess.Popen", mock_popen)

        mock_playwright.chromium.connect_over_cdp.side_effect = [ConnectionError, mock_browser]

        with patch("aionui.aionui.sync_playwright") as mock_sync_playwright:
            mock_sync_playwright.return_value.__enter__.return_value = mock_playwright

            aionui = AiOnUi()
            with aionui.model_sync("gpt") as model:
                assert model.page == mock_page

            assert mock_popen.call_count == 1
            assert mock_page.close.call_count == 1
            assert mock_context.close.call_count == 1
            assert mock_browser.close.call_count == 1
