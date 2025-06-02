import asyncio
from typing import Literal
import re
from datetime import datetime, timedelta
from pathlib import Path

import pyperclip
from playwright.async_api import Locator
from tenacity import retry, stop_after_attempt, wait_exponential

from ..enums import Platform, KeyboardCommand
from ..utils.logger import get_logger
from ..utils.common import clean_text
from .base_async import BaseAsyncModel

logger = get_logger(__name__)


class GPTAsync(BaseAsyncModel):
    url: str = "https://chatgpt.com"

    async def get_input_field(self) -> Locator:
        input_field = self.page.locator("#prompt-textarea")
        if (await input_field.count()) > 0:
            return input_field.first
        raise ValueError("Input field not found")

    async def get_submit_button(self) -> Locator:
        send_button = self.page.locator('[data-testid="send-button"]:not([disabled])')
        if await send_button.count() > 0:
            return send_button.first

        speech_button = self.page.locator('[data-testid="composer-speech-button"]')
        if await speech_button.count() > 0:
            return speech_button.first

        raise ValueError("Submit button not found")

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=15))
    async def get_text_response(self) -> str:
        pyperclip.copy("")
        # await self.page.keyboard.press(self.get_key_board_shortcut(KeyboardCommand.CopyLastArticle))
        await self.page.wait_for_selector('[data-testid="copy-turn-action-button"]')
        await self.page.locator('[data-testid="copy-turn-action-button"]').click()

        result = pyperclip.paste()
        if result == "":
            raise ValueError("No response found")
        return clean_text(result)

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=15))
    async def get_code_block_response(self) -> str:
        pyperclip.copy("")
        await self.page.keyboard.press(self.get_key_board_shortcut(KeyboardCommand.CopyLastCode))
        await self.page.wait_for_timeout(200)
        result = pyperclip.paste()
        if result == "":
            raise ValueError("No response found")
        return result

    async def get_image_response(self) -> str:
        src = await self.page.locator("article").last.locator("img").first.get_attribute("src")
        if not src:
            raise Exception("Image generation failed")
        return src

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=15))
    async def chat(
        self,
        message: str,
        expected_result: Literal["text", "image", "code", "json"] = "text",
        tools: list[Literal["search_the_web"]] = [],
    ) -> str:
        if "gpt" not in self.page.url.lower():
            await self.page.goto(self.url)
            await self.page.wait_for_timeout(3000)

        if expected_result == "code" or expected_result == "json":
            if "return in code block" not in message.lower():
                message += "\nReturn in code block."

        await self.get_input_field()
        await self.get_submit_button()
        await self.fill_message(message)
        await self.activate_tools(tools)

        submit_button = await self.get_submit_button()
        await submit_button.click()

        await self.wait_for_response()

        if expected_result == "image":
            return await self.get_image_response()
        elif expected_result == "code" or expected_result == "json":
            return await self.get_code_block_response()
        else:
            return await self.get_text_response()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15))
    async def attach_file(self, file_path: str):
        path = Path(file_path)
        file_name = path.name
        file_input = self.page.locator('input[type="file"]').first
        await file_input.set_input_files(file_path)
        await self.page.wait_for_timeout(3000)

        if Path(await file_input.input_value()).name != file_name:
            raise ValueError("File could not be attached")

    async def wait_for_response(self):
        await self.page.wait_for_timeout(3000)

        continue_btn = self.page.locator("text=Continue generating")
        if await continue_btn.count() > 0:
            await continue_btn.click()
            logger.info("Continuing generation...")
            return await self.wait_for_response()

        articles = self.page.locator("article").last
        if await articles.count() <= 0:
            return await self.wait_for_response()

        copy_btn = self.page.locator('[data-testid="copy-turn-action-button"]')
        if await copy_btn.count() <= 0:
            return await self.wait_for_response()

        last_article = articles.last
        if await last_article.locator(".sr-only").last.text_content() == "You said:":
            return await self.wait_for_response()

        if await last_article.locator('[data-testid="copy-turn-action-button"]').count() <= 0:
            return await self.wait_for_response()

    async def handle_on_error(self):
        await self.page.reload()
        time_element = self.page.locator(r"text=/[0-9]{1,2}:[0-9]{2}\s(?:AM|PM)/")

        if await time_element.count() > 0:
            text = await time_element.inner_text()
            time_reset = re.search(r"([0-9]{1,2}:[0-9]{2}\s(?:AM|PM))", text).group(1)
            await self.sleep_until_time(time_reset)

    def get_key_board_shortcut(self, command: KeyboardCommand) -> str:
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

    async def activate_tools(self, tools: list[Literal["search_the_web"]]):
        """Activates the tools for the GPT model."""
        if "search_the_web" in tools:
            search_btn = self.page.locator('[aria-label="Search the web"][aria-pressed="false"]')
            if await search_btn.count() > 0:
                await search_btn.first.click()

    async def sleep_until_time(self, time_str: str):
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
        await self.page.wait_for_timeout(sleep_time * 1000)
