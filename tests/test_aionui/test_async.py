import pytest
from aionui.models_async import GPTAsync, ClaudeAsync, GeminiAsync
from playwright.async_api import (
    Page as AsyncPage,
    Browser as AsyncBrowser,
    BrowserContext as AsyncBrowserContext,
    Playwright as AsyncPlaywright,
)
from typing import Literal
from aionui import AiOnUi
from unittest.mock import Mock, AsyncMock, patch


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
