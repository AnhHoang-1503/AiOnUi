import pytest
import re
import json
from playwright.async_api import expect
from aionui import AiOnUi
from aionui.models_async import GeminiAsync
from pathlib import Path
import pytest_asyncio


@pytest_asyncio.fixture(scope="class", loop_scope="class")
async def gemini_async(config_file):
    aionui = AiOnUi(config_file)
    async with aionui.model_async("gemini") as model:
        yield model


class TestClaudeAsync:
    @pytest.mark.asyncio(loop_scope="class")
    async def test_init_instructions(self, gemini_async: GeminiAsync):
        await gemini_async.init_instructions()
        await expect(gemini_async.page.locator("model-response").last).to_have_text(re.compile(".+"))

    @pytest.mark.asyncio(loop_scope="class")
    @pytest.mark.dependency(depends=["test_init_instructions"])
    async def test_chat_text(self, gemini_async: GeminiAsync):
        result = await gemini_async.chat(
            "Trả lời chính xác từ sau, không thêm bất kỳ thông tin hoặc dấu câu nào khác: `Xin chào`",
        )
        assert result == "Xin chào"

    @pytest.mark.asyncio(loop_scope="class")
    @pytest.mark.dependency(depends=["test_chat_text"])
    async def test_chat_code(self, gemini_async: GeminiAsync):
        result = await gemini_async.chat(
            'Trả lời lại chính xác json sau, không thêm bất kỳ thông tin nào khác: `{"message": "Xin chào"}`',
            "code",
        )
        dict_result = json.loads(result)
        assert dict_result == {"message": "Xin chào"}

    @pytest.mark.asyncio(loop_scope="class")
    @pytest.mark.dependency(depends=["test_chat_code"])
    async def test_attach_file(self, gemini_async: GeminiAsync, content_file):
        await gemini_async.page.goto(gemini_async.url, wait_until="networkidle")
        path = Path(content_file)
        await gemini_async.attach_file(content_file)
        await expect(gemini_async.page.locator(f'[data-testid="{path.name}"]')).to_be_visible()

    @pytest.mark.asyncio(loop_scope="class")
    @pytest.mark.dependency(depends=["test_attach_file"])
    async def test_text_as_file(self, gemini_async: GeminiAsync):
        await gemini_async.page.goto(gemini_async.url, wait_until="networkidle")
        await gemini_async.text_as_file("Xin chào")
        await expect(gemini_async.page.locator(f'[data-testid="attachment.txt"]')).to_be_visible()
