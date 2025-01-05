import pytest
from aionui import AiOnUI, AiModel, ExpectedResult, GPTTool
from aionui.models import GPT
import re
from playwright.sync_api import expect


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
