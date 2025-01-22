import pytest
import re
import json
from playwright.async_api import expect
from aionui import AiOnUi
from aionui.models_async import DeepSeekAsync
from pathlib import Path
import pytest_asyncio


@pytest_asyncio.fixture(scope="class", loop_scope="class")
async def deep_seek_async(config_file):
    aionui = AiOnUi(config_file)
    async with aionui.model_async("deep_seek_async") as model:
        yield model


class TestDeepSeekAsync:
    @pytest.mark.asyncio(loop_scope="class")
    async def test_init_instructions(self, deep_seek_async: DeepSeekAsync):
        await deep_seek_async.init_instructions()
        await expect(deep_seek_async.page.locator(selector=".f9bf7997.d7dc56a8.c05b5566").last).to_have_text(
            re.compile(".+")
        )

    @pytest.mark.asyncio(loop_scope="class")
    @pytest.mark.dependency(depends=["test_init_instructions"])
    async def test_chat_text(self, deep_seek_async: DeepSeekAsync):
        result = await deep_seek_async.chat(
            "Trả lời chính xác từ sau, không thêm bất kỳ thông tin hoặc dấu câu nào khác: `Xin chào`",
        )
        assert result == "Xin chào"

    @pytest.mark.asyncio(loop_scope="class")
    @pytest.mark.dependency(depends=["test_chat_text"])
    async def test_chat_code(self, deep_seek_async: DeepSeekAsync):
        result = await deep_seek_async.chat(
            'Trả lời lại chính xác json sau, không thêm bất kỳ thông tin nào khác: `{"message": "Xin chào"}`',
            "code",
        )
        dict_result = json.loads(result)
        assert dict_result == {"message": "Xin chào"}

    @pytest.mark.asyncio(loop_scope="class")
    @pytest.mark.dependency(depends=["test_chat_code"])
    async def test_attach_file(self, deep_seek_async: DeepSeekAsync, content_file):
        await deep_seek_async.page.goto(deep_seek_async.url)
        path = Path(content_file)
        await deep_seek_async.attach_file(content_file)
        assert (
            next(
                (
                    x
                    for x in await deep_seek_async.page.locator(".f3a54b52").all_inner_texts()
                    if path.name.lower() in x.lower()
                ),
                None,
            )
            is not None
        )

    @pytest.mark.asyncio(loop_scope="class")
    @pytest.mark.dependency(depends=["test_attach_file"])
    async def test_text_as_file(self, deep_seek_async: DeepSeekAsync):
        await deep_seek_async.page.goto(deep_seek_async.url)
        await deep_seek_async.text_as_file("Xin chào")
        assert (
            next(
                (
                    x
                    for x in await deep_seek_async.page.locator(".f3a54b52").all_inner_texts()
                    if "attachment.txt" in x.lower()
                ),
                None,
            )
            is not None
        )
