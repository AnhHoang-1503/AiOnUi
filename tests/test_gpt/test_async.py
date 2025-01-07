import pytest
import json
import re
from pathlib import Path
from playwright.async_api import expect
import pytest
from aionui.models_async import GPTAsync
import pytest_asyncio
from aionui import AiOnUi


@pytest_asyncio.fixture(scope="class", loop_scope="class")
async def gpt_async(config_file: str):
    aionui = AiOnUi(config_file)
    async with aionui.model_async("gpt") as model:
        yield model


class TestGPTAsync:
    @pytest.mark.asyncio(loop_scope="class")
    @pytest.mark.dependency(depends=["test_init_instructions"])
    async def test_init_instructions(self, gpt_async: GPTAsync):
        await gpt_async.init_instructions()
        await expect(gpt_async.page.locator("article .sr-only").last).to_have_text(
            re.compile("ChatGPT said:", re.IGNORECASE)
        )

    @pytest.mark.asyncio(loop_scope="class")
    @pytest.mark.dependency(depends=["test_init_instructions"])
    async def test_chat_text(self, gpt_async: GPTAsync):
        result = await gpt_async.chat(
            "Trả lời chính xác từ sau, không thêm bất kỳ thông tin hoặc dấu câu nào khác: `Xin chào`",
        )
        assert result == "Xin chào"

    @pytest.mark.asyncio(loop_scope="class")
    @pytest.mark.dependency(depends=["test_chat_text"])
    async def test_chat_code(self, gpt_async: GPTAsync):
        result = await gpt_async.chat(
            'Trả lời lại chính xác json sau, không thêm bất kỳ thông tin nào khác: `{"message": "Xin chào"}`',
            "code",
        )
        dict_result = json.loads(result)
        assert dict_result == {"message": "Xin chào"}

    @pytest.mark.asyncio(loop_scope="class")
    @pytest.mark.dependency(depends=["test_chat_code"])
    async def test_attach_file(self, gpt_async: GPTAsync, content_file):
        await gpt_async.page.goto(gpt_async.url)
        path = Path(content_file)
        await gpt_async.attach_file(content_file)
        await expect(gpt_async.page.locator("input[type='file']")).to_have_value(
            re.compile(r".*{}".format(path.name), re.IGNORECASE)
        )

    @pytest.mark.asyncio(loop_scope="class")
    @pytest.mark.dependency(depends=["test_attach_file"])
    async def test_text_as_file(self, gpt_async: GPTAsync):
        await gpt_async.page.goto(gpt_async.url)
        await gpt_async.text_as_file("Xin chào")
        await expect(gpt_async.page.locator("input[type='file']")).to_have_value(
            re.compile(r".*attachment.txt", re.IGNORECASE)
        )
