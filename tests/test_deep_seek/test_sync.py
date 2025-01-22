import pytest
import re
import json
from playwright.sync_api import expect
from aionui import AiOnUi
from aionui.models import DeepSeek
from pathlib import Path


@pytest.fixture(scope="class")
def deep_seek(config_file):
    aionui = AiOnUi(config_file)
    with aionui.model_sync("deep_seek") as model:
        yield model


class TestDeepSeek:
    def test_init_instructions(self, deep_seek: DeepSeek):
        deep_seek.init_instructions()
        expect(deep_seek.page.locator(selector=".f9bf7997.d7dc56a8.c05b5566").last).to_have_text(re.compile(".+"))

    @pytest.mark.dependency(depends=["test_init_instructions"])
    def test_chat_text(self, deep_seek: DeepSeek):
        result = deep_seek.chat(
            "Trả lời chính xác từ sau, không thêm bất kỳ thông tin hoặc dấu câu nào khác: `Xin chào`",
        )
        assert result == "Xin chào"

    @pytest.mark.dependency(depends=["test_chat_text"])
    def test_chat_code(self, deep_seek: DeepSeek):
        result = deep_seek.chat(
            'Trả lời lại chính xác json sau, không thêm bất kỳ thông tin nào khác: `{"message": "Xin chào"}`',
            "code",
        )
        dict_result = json.loads(result)
        assert dict_result == {"message": "Xin chào"}

    @pytest.mark.dependency(depends=["test_chat_code"])
    def test_attach_file(self, deep_seek: DeepSeek, content_file):
        deep_seek.page.goto(deep_seek.url)
        path = Path(content_file)
        deep_seek.attach_file(content_file)

        assert (
            next(
                (x for x in deep_seek.page.locator(".f3a54b52").all_inner_texts() if path.name.lower() in x.lower()),
                None,
            )
            is not None
        )

    @pytest.mark.dependency(depends=["test_attach_file"])
    def test_text_as_file(self, deep_seek: DeepSeek):
        deep_seek.page.goto(deep_seek.url)
        deep_seek.text_as_file("Xin chào")
        assert (
            next(
                (x for x in deep_seek.page.locator(".f3a54b52").all_inner_texts() if "attachment.txt" in x.lower()),
                None,
            )
            is not None
        )
