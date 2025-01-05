import json
import re
from pathlib import Path
from playwright.sync_api._generated import Playwright
import pytest
from aionui import AiOnUI, AiModel, GPTTool
from aionui.models import GPT
from aionui.enums import ExpectedResult
from aionui.config import Config
from playwright.sync_api import expect


@pytest.fixture
def gpt(config_file, playwright: Playwright):
    config = Config(config_file)
    browser = playwright.chromium.connect_over_cdp(f"http://localhost:{config.debug_port}")
    context = browser.contexts[0]
    page = context.new_page()
    page.goto("https://chatgpt.com", wait_until="networkidle")
    yield GPT(config, page)
    page.close()


class TestGPT:
    def test_init_instructions(self, gpt: GPT):
        gpt.init_instructions()
        expect(gpt.page.locator("article .sr-only").last).to_have_text(re.compile("ChatGPT said:", re.IGNORECASE))

    def test_get_input_field(self, gpt: GPT):
        input_field = gpt.get_input_field()
        expect(input_field).to_be_visible()

    def test_fill_message(self, gpt: GPT):
        gpt.fill_message("Hello")
        expect(gpt.get_input_field()).to_have_text(re.compile("Hello", re.IGNORECASE))

    def test_get_submit_button(self, gpt: GPT):
        submit_button = gpt.get_submit_button()
        expect(submit_button).to_be_visible()

    def test_attach_file(self, gpt: GPT, content_file):
        path = Path(content_file)
        gpt.attach_file(content_file)
        expect(gpt.page.locator("input[type='file']")).to_have_value(
            re.compile(r".*{}".format(path.name), re.IGNORECASE)
        )

    def test_text_as_file(self, gpt: GPT):
        gpt.text_as_file("Xin chào")
        expect(gpt.page.locator("input[type='file']")).to_have_value(re.compile(r".*attchment.txt", re.IGNORECASE))

    def test_chat_text(self, gpt: GPT):
        result = gpt.chat(
            "Trả lời chính xác từ sau, không thêm bất kỳ thông tin hoặc dấu câu nào khác: `Xin chào`",
        )
        assert result == "Xin chào"

    def test_chat_code(self, gpt: GPT):
        result = gpt.chat(
            'Trả lời lại chính xác json sau, không thêm bất kỳ thông tin nào khác: `{"message": "Xin chào"}`',
            ExpectedResult.Code,
        )
        dict_result = json.loads(result)
        assert dict_result == {"message": "Xin chào"}
