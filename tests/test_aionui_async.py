import pytest
import pytest_asyncio
from aionui import AiModel, AiOnUiAsync
from aionui.models import GPTAsync
import re
from playwright.async_api import expect as async_expect


@pytest_asyncio.fixture(scope="class", loop_scope="class")
async def aionui_gpt_async_instance(config_file):
    async with AiOnUiAsync(AiModel.GPT, config_file) as ai:
        yield ai


class TestAiOnUIAsync:
    @pytest.mark.asyncio(loop_scope="class")
    async def test_aionui_async_initialization(self, config_file):
        async with AiOnUiAsync(AiModel.GPT, config_file) as ai:
            assert ai._playwright is not None
            assert ai._browser is not None
            assert ai._context is not None
            assert ai._page is not None
            assert ai.config is not None
            assert ai._model_type == AiModel.GPT
            assert isinstance(ai.model, GPTAsync)

        assert ai._page is None
        assert ai._context is None

    @pytest.mark.asyncio(loop_scope="class")
    async def test_aionui_async_chat(self, aionui_gpt_async_instance: AiOnUiAsync):
        result = await aionui_gpt_async_instance.chat(
            "Trả lời chính xác từ sau, không thêm bất kỳ thông tin hoặc dấu câu nào khác: `Xin chào`",
        )
        assert result == "Xin chào"

    @pytest.mark.asyncio(loop_scope="class")
    async def test_aionui_async_attach_file(self, aionui_gpt_async_instance: AiOnUiAsync, content_file: str):
        await aionui_gpt_async_instance.attach_file(content_file)
        await async_expect(aionui_gpt_async_instance._page.locator("input[type='file']")).to_have_value(
            re.compile(r".*test.txt", re.IGNORECASE)
        )
