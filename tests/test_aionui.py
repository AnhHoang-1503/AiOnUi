import pytest
from aionui import AiOnUI, AiModel, AiOnUiAsync
from aionui.models import GPT, GPTAsync
import re
from playwright.sync_api import expect
from playwright.async_api import expect as async_expect, Playwright as AsyncPlaywright, async_playwright


def test_aionui_initialization(config_file):
    with AiOnUI(AiModel.GPT, config_file) as ai:
        assert ai._playwright is not None
        assert ai._browser is not None
        assert ai._context is not None
        assert ai._page is not None
        assert ai.config is not None
        assert ai._model_type == AiModel.GPT
        assert isinstance(ai.model, GPT)

    assert ai._page is None
    assert ai._context is None
    assert ai._browser is None
    assert ai._playwright is None


def test_aionui_chat(config_file, playwright):
    with AiOnUI(AiModel.GPT, config_file, playwright) as ai:
        result = ai.chat(
            "Trả lời chính xác từ sau, không thêm bất kỳ thông tin hoặc dấu câu nào khác: `Xin chào`",
        )
        assert result == "Xin chào"


def test_aionui_attach_file(config_file, playwright, content_file):
    with AiOnUI(AiModel.GPT, config_file, playwright) as ai:
        ai.attach_file(content_file)
        expect(ai._page.locator("input[type='file']")).to_have_value(re.compile(r".*test.txt", re.IGNORECASE))


@pytest.mark.asyncio(loop_scope="module")
async def test_aionui_async_initialization(config_file):
    async with async_playwright() as playwright:
        async with AiOnUiAsync(AiModel.GPT, config_file, playwright) as ai:
            assert ai._playwright is not None
            assert ai._browser is not None
            assert ai._context is not None
            assert ai._page is not None
            assert ai.config is not None
            assert ai._model_type == AiModel.GPT
            assert isinstance(ai.model, GPTAsync)

        assert ai._page is None
        assert ai._context is None


@pytest.mark.asyncio(loop_scope="module")
async def test_aionui_async_chat(config_file):
    async with async_playwright() as playwright:
        async with AiOnUiAsync(AiModel.GPT, config_file, playwright) as ai:
            result = await ai.chat(
                "Trả lời chính xác từ sau, không thêm bất kỳ thông tin hoặc dấu câu nào khác: `Xin chào`",
            )
            assert result == "Xin chào"


@pytest.mark.asyncio(loop_scope="module")
async def test_aionui_async_attach_file(config_file, content_file):
    async with async_playwright() as playwright:
        async with AiOnUiAsync(AiModel.GPT, config_file, playwright) as ai:
            await ai.attach_file(content_file)
            await async_expect(ai._page.locator("input[type='file']")).to_have_value(
                re.compile(r".*test.txt", re.IGNORECASE)
            )
