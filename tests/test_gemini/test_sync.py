import pytest
import re
import json
from playwright.sync_api import expect
from aionui import AiOnUi
from aionui.models import Gemini
from pathlib import Path
from aionui.utils.common import save_image


@pytest.fixture(scope="class")
def gemini(config_file):
    aionui = AiOnUi(config_file)
    with aionui.model_sync("gemini") as model:
        yield model


class TestGemini:
    def test_init_instructions(self, gemini: Gemini):
        gemini.init_instructions()
        expect(gemini.page.locator("model-response").last).to_have_text(re.compile(".+"))

    @pytest.mark.dependency(depends=["test_init_instructions"])
    def test_chat_text(self, gemini: Gemini):
        result = gemini.chat(
            "Trả lời chính xác như sau, không thêm bất kỳ thông tin hoặc dấu câu nào khác: `Xin chào`",
        )
        assert result == "Xin chào"

    @pytest.mark.dependency(depends=["test_chat_text"])
    def test_chat_code(self, gemini: Gemini):
        result = gemini.chat(
            'Trả lời lại chính xác json sau, không thêm bất kỳ thông tin nào khác: `{"message": "Xin chào"}`',
            "code",
        )
        dict_result = json.loads(result)
        assert dict_result == {"message": "Xin chào"}

    @pytest.mark.dependency(depends=["test_chat_code"])
    def test_attach_file(self, gemini: Gemini, content_file):
        path = Path(content_file)
        gemini.attach_file(content_file)
        expect(gemini.page.locator(f'[data-test-id="file-name"][title="{path.name}"]')).to_be_visible()

    @pytest.mark.dependency(depends=["test_attach_file"])
    def test_text_as_file(self, gemini: Gemini):
        gemini.text_as_file("Xin chào")
        expect(gemini.page.locator(f'[data-test-id="file-name"][title="attachment.txt"]')).to_be_visible()
