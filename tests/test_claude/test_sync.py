import pytest
import re
import json
from playwright.sync_api import expect
from aionui import AiOnUi
from aionui.models import Claude
from pathlib import Path


@pytest.fixture(scope="class")
def claude(config_file):
    aionui = AiOnUi(config_file)
    with aionui.model_sync("claude") as model:
        yield model


class TestClaude:
    def test_init_instructions(self, claude: Claude):
        claude.init_instructions()
        expect(claude.page.locator(selector=".font-claude-message").last).to_have_text(re.compile(".+"))

    @pytest.mark.dependency(depends=["test_init_instructions"])
    def test_chat_text(self, claude: Claude):
        result = claude.chat(
            "Trả lời chính xác từ sau, không thêm bất kỳ thông tin hoặc dấu câu nào khác: `Xin chào`",
        )
        assert result == "Xin chào"

    @pytest.mark.dependency(depends=["test_chat_text"])
    def test_chat_code(self, claude: Claude):
        result = claude.chat(
            'Trả lời lại chính xác json sau, không thêm bất kỳ thông tin nào khác: `{"message": "Xin chào"}`',
            "code",
        )
        dict_result = json.loads(result)
        assert dict_result == {"message": "Xin chào"}

    @pytest.mark.dependency(depends=["test_chat_code"])
    def test_attach_file(self, claude: Claude, content_file):
        claude.page.goto("https://claude.ai/new", wait_until="networkidle")
        path = Path(content_file)
        claude.attach_file(content_file)
        expect(claude.page.locator(f'[data-testid="{path.name}"]')).to_be_visible()

    @pytest.mark.dependency(depends=["test_attach_file"])
    def test_text_as_file(self, claude: Claude):
        claude.page.goto("https://claude.ai/new", wait_until="networkidle")
        claude.text_as_file("Xin chào")
        expect(claude.page.locator(f'[data-testid="attachment.txt"]')).to_be_visible()
