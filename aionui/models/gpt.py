import re
import time
from datetime import datetime, timedelta
from typing import Literal, override
from pathlib import Path

import pyperclip
from playwright.sync_api import Locator
from tenacity import retry, stop_after_attempt, wait_exponential, RetryCallState

from .base import BaseModel
from ..enums import Platform, KeyboardCommand
from ..utils.logger import get_logger
from ..utils.common import clean_text

logger = get_logger(__name__)


def handle_reload(state: RetryCallState):
    self: GPT = state.args[0]
    self.page.reload()
    time.sleep(3)


class GPT(BaseModel):
    url: str = "https://chatgpt.com"

    @override
    def get_input_field(self) -> Locator:
        input_field = self.page.locator("#prompt-textarea")
        if input_field.count() > 0:
            return input_field.first
        raise ValueError("Input field not found")

    @override
    def fill_message(self, message: str):
        input_field = self.get_input_field()
        input_field.fill(message)

    @override
    def get_submit_button(self):
        send_button = self.page.locator('[data-testid="send-button"]:not([disabled])')
        if send_button.count() > 0:
            return send_button.first

        speech_button = self.page.locator('[data-testid="composer-speech-button"]')
        if speech_button.count() > 0:
            return speech_button.first

        raise ValueError("Submit button not found")

    @override
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=15))
    def get_text_response(self):
        pyperclip.copy("")
        # self.page.keyboard.press(self.get_key_board_shortcut(KeyboardCommand.CopyLastArticle))
        self.page.wait_for_selector('[data-testid="copy-turn-action-button"]')
        self.page.locator('[data-testid="copy-turn-action-button"]').click()
        result = pyperclip.paste()
        if result == "":
            raise ValueError("No response found")
        return clean_text(result)

    @override
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=15))
    def get_code_block_response(self):
        pyperclip.copy("")
        self.page.keyboard.press(self.get_key_board_shortcut(KeyboardCommand.CopyLastCode))
        result = pyperclip.paste()
        if result == "":
            raise ValueError("No response found")
        return result

    @override
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=15))
    def get_image_response(self):
        src = (
            self.page.locator('article[data-testid^="conversation-turn"]')
            .last.locator("img")
            .first.get_attribute("src")
        )
        if not src:
            raise Exception("Image generation failed")
        return src

    @override
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=15), before_sleep=handle_reload)
    def chat(
        self,
        message: str,
        expected_result: Literal["text", "image", "code", "json"] = "text",
        tools: list[Literal["search_the_web"]] = [],
    ):
        if "gpt" not in self.page.url.lower():
            self.page.goto(self.url)
            time.sleep(3)

        if expected_result == "code" or expected_result == "json":
            if "return in code block" not in message.lower():
                message += "\nReturn in code block."
        self.get_input_field()
        self.get_submit_button()
        self.fill_message(message)
        self.activate_tools(tools)
        self.get_submit_button().click()
        self.wait_for_response()
        if expected_result == "image":
            return self.get_image_response()
        elif expected_result == "code" or expected_result == "json":
            return self.get_code_block_response()
        else:
            return self.get_text_response()

    @override
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15))
    def attach_file(self, file_path: str):
        path = Path(file_path)
        file_name = path.name
        file_input = self.page.locator('input[type="file"]').first
        file_input.set_input_files(file_path)
        time.sleep(3)
        if Path(file_input.input_value()).name != file_name:
            raise ValueError("File could not be attached")

    @override
    def wait_for_response(self):
        time.sleep(3)
        if self.page.locator("text=Continue generating").count() > 0:
            self.page.click("text=Continue generating")
            logger.info("Continuing generation...")
            return self.wait_for_response()

        if self.page.locator("article").count() <= 0:
            return self.wait_for_response()

        if self.page.locator('[data-testid="copy-turn-action-button"]').count() <= 0:
            return self.wait_for_response()

        last_article = self.page.locator("article").last
        if last_article.locator(".sr-only").last.text_content() == "You said:":
            return self.wait_for_response()

        if last_article.locator('[data-testid="copy-turn-action-button"]').count() <= 0:
            return self.wait_for_response()

        if not last_article.locator('[data-testid="copy-turn-action-button"]').last.is_visible():
            return self.wait_for_response()

    @override
    def handle_on_error(self):
        self.page.reload()
        if self.page.locator(r"text=/[0-9]{1,2}:[0-9]{2}\s(?:AM|PM)/").count() > 0:
            text = self.page.locator(r"text=/[0-9]{1,2}:[0-9]{2}\s(?:AM|PM)/").inner_text()
            time_reset = re.search(r"([0-9]{1,2}:[0-9]{2}\s(?:AM|PM))", text).group(1)
            self.sleep_until_time(time_reset)

    def get_key_board_shortcut(self, command: KeyboardCommand):
        MACOS = {
            KeyboardCommand.Enter: "Enter",
            KeyboardCommand.CopyLastArticle: "Meta+Shift+C",
            KeyboardCommand.CopyLastCode: "Meta+Shift+;",
            KeyboardCommand.FocusChatInput: "Shift+Escape",
        }

        WINDOWS = {
            KeyboardCommand.Enter: "Enter",
            KeyboardCommand.CopyLastArticle: "Control+Shift+C",
            KeyboardCommand.CopyLastCode: "Control+Shift+;",
            KeyboardCommand.FocusChatInput: "Shift+Escape",
        }

        return MACOS[command] if self.config.platform == Platform.MACOS else WINDOWS[command]

    def activate_tools(self, tools: list[Literal["search_the_web"]]):
        """Activates the tools for the GPT model."""
        if "search_the_web" in tools:
            if self.page.locator('[aria-label="Search the web"][aria-pressed="false"]').count() > 0:
                self.page.locator('[aria-label="Search the web"][aria-pressed="false"]').first.click()

    def sleep_until_time(self, time_str: str):
        """Sleep until specified time"""
        now = datetime.now()
        time_format = "%I:%M %p"
        reset_datetime = datetime.strptime(time_str, time_format)

        reset_datetime = now.replace(
            hour=reset_datetime.time().hour,
            minute=reset_datetime.time().minute,
            second=0,
            microsecond=0,
        )

        if reset_datetime.time() < now.time():
            reset_datetime += timedelta(days=1)

        reset_datetime += timedelta(minutes=5)

        sleep_time = (reset_datetime - now).total_seconds()
        if sleep_time < 0:
            sleep_time = -sleep_time

        logger.info(f"Waiting {sleep_time} seconds for limit reset")
        time.sleep(sleep_time)
