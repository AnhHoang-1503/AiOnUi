import pytest
from aionui import AiOnUI, AiModel
from aionui.models import GPT
import re
from playwright.sync_api import expect


@pytest.fixture(scope="class")
def aionui_gpt_instance(config_file):
    with AiOnUI(AiModel.GPT, config_file) as ai:
        yield ai


class TestAiOnUI:
    def test_aionui_initialization(self, config_file):
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

    def test_aionui_chat(self, aionui_gpt_instance):
        result = aionui_gpt_instance.chat(
            "Trả lời chính xác từ sau, không thêm bất kỳ thông tin hoặc dấu câu nào khác: `Xin chào`",
        )
        assert result == "Xin chào"

    def test_aionui_attach_file(self, aionui_gpt_instance, content_file):
        aionui_gpt_instance.attach_file(content_file)
        expect(aionui_gpt_instance._page.locator("input[type='file']")).to_have_value(
            re.compile(r".*test.txt", re.IGNORECASE)
        )
