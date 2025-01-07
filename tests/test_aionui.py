from typing import Literal
import pytest
import os
from aionui import AiOnUi
from aionui.models import GPT, Claude, Gemini, GPTAsync, ClaudeAsync, GeminiAsync
from playwright.sync_api import Page, Browser, BrowserContext, Playwright
from playwright.async_api import (
    Page as AsyncPage,
    Browser as AsyncBrowser,
    BrowserContext as AsyncBrowserContext,
    Playwright as AsyncPlaywright,
)
from unittest.mock import Mock, AsyncMock, patch


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


@pytest.fixture
def mock_page_async(mocker):
    return AsyncMock(spec=AsyncPage, title=AsyncMock(return_value="ChatGPT"))


@pytest.fixture
def mock_context_async(mocker, mock_page_async):
    mock = AsyncMock(spec=AsyncBrowserContext)
    mock.new_page = AsyncMock(return_value=mock_page_async)
    return mock


@pytest.fixture
def mock_browser_async(mocker, mock_context_async):
    mock = AsyncMock(spec=AsyncBrowser)
    mock.contexts = [mock_context_async]
    return mock


@pytest.fixture
def mock_playwright_async(mocker, mock_browser_async):
    mock = AsyncMock(spec=AsyncPlaywright)
    mock.chromium.connect_over_cdp = AsyncMock(return_value=mock_browser_async)
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


class TestAiOnUiAsync:
    @pytest.mark.parametrize("model_type", ["gpt"])
    @pytest.mark.asyncio(loop_scope="class")
    async def test_async_model(self, mock_page_async: AsyncMock, model_type: Literal["gpt", "claude", "gemini"]):
        aionui = AiOnUi(page=mock_page_async)
        async with aionui.model_async(model_type) as model:
            assert model is not None
            assert model.page == mock_page_async
            if model_type == "gpt":
                assert isinstance(model, GPTAsync)
            elif model_type == "claude":
                assert isinstance(model, ClaudeAsync)
            elif model_type == "gemini":
                assert isinstance(model, GeminiAsync)

    @pytest.mark.asyncio(loop_scope="class")
    async def test_clean_up_page(self, mock_page_async):
        aionui = AiOnUi(page=mock_page_async)
        async with aionui.model_async("gpt") as model:
            assert model.page == mock_page_async

    @pytest.mark.asyncio(loop_scope="class")
    async def test_clean_up_context(self, mock_context_async, mock_page_async):
        aionui = AiOnUi(context=mock_context_async)
        async with aionui.model_async("gpt") as model:
            assert model.page == mock_page_async
        assert mock_context_async.new_page.await_count == 1
        assert mock_page_async.close.await_count == 1

    @pytest.mark.asyncio(loop_scope="class")
    async def test_clean_up_browser(self, mock_browser_async, mock_page_async, mock_context_async):
        aionui = AiOnUi(browser=mock_browser_async)
        async with aionui.model_async("gpt") as model:
            assert model.page == mock_page_async
        assert mock_context_async.new_page.await_count == 1
        assert mock_page_async.close.await_count == 1

    @pytest.mark.asyncio(loop_scope="class")
    async def test_clean_up_playwright(
        self, mock_playwright_async, mock_page_async, mock_context_async, mock_browser_async
    ):
        aionui = AiOnUi(playwright=mock_playwright_async)
        async with aionui.model_async("gpt") as model:
            assert model.page == mock_page_async
        assert mock_playwright_async.chromium.connect_over_cdp.await_count == 1
        assert mock_page_async.close.await_count == 1
        assert mock_context_async.close.await_count == 1
        assert mock_browser_async.close.await_count == 1

    @pytest.mark.asyncio(loop_scope="class")
    async def test_clean_up_no_args(
        self, monkeypatch, mock_page_async, mock_context_async, mock_browser_async, mock_playwright_async
    ):
        mock_popen = Mock()
        monkeypatch.setattr("subprocess.Popen", mock_popen)

        mock_playwright_async.chromium.connect_over_cdp.side_effect = [ConnectionError, mock_browser_async]

        with patch("aionui.aionui.async_playwright") as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__.return_value = mock_playwright_async

            aionui = AiOnUi()
            async with aionui.model_async("gpt") as model:
                assert model.page == mock_page_async

            assert mock_popen.call_count == 1
            assert mock_page_async.close.await_count == 1
            assert mock_context_async.close.await_count == 1
            assert mock_browser_async.close.await_count == 1
