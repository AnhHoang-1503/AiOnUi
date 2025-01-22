import json
from pathlib import Path
from typing import Literal, override
from playwright.sync_api import Locator
from .base_async import BaseAsyncModel
import pyperclip


class DeepSeekAsync(BaseAsyncModel):
    url: str = "https://chat.deepseek.com/"

    @override
    async def get_input_field(self) -> Locator:
        input_field = self.page.locator('textarea[id="chat-input"]')
        if await input_field.count() > 0:
            return input_field.first
        raise ValueError("Input field not found")

    @override
    async def get_submit_button(self) -> Locator:
        send_button = self.page.locator('.f6d670[role="button"]')
        if await send_button.count() > 0:
            return send_button.first

        raise ValueError("Submit button not found")

    @override
    async def get_text_response(self):
        if await self.page.locator(".f9bf7997.d7dc56a8.c05b5566").count() <= 0:
            raise ValueError("No response found")

        response = await self.page.locator(
            ".f9bf7997.d7dc56a8.c05b5566 .ds-markdown.ds-markdown--block"
        ).last.inner_text()
        if response == "":
            raise ValueError("No response found")

        return response

    @override
    async def get_code_block_response(self) -> str:
        if await self.page.locator(".f9bf7997.d7dc56a8.c05b5566").count() <= 0:
            raise ValueError("No response found")

        last_response = self.page.locator(".f9bf7997.d7dc56a8.c05b5566").last
        copy_button = last_response.locator(".ds-markdown-code-copy-button")
        if await copy_button.count() <= 0:
            raise ValueError("Copy button not found")

        pyperclip.copy("")
        await copy_button.click()
        result = pyperclip.paste()

        if result == "":
            raise ValueError("No response found")

        return result

    @override
    async def get_image_response(self) -> str:
        pass

    @override
    async def chat(
        self,
        message: str,
        expected_result: Literal["text", "image", "code", "json"] = "text",
        tools: list[Literal["search", "deep_think"]] = [],
    ) -> str:
        if "deepseek" not in self.page.url.lower():
            await self.page.goto(self.url)
            await self.page.wait_for_timeout(3000)

        if expected_result == "code" or expected_result == "json":
            if "return in code block" not in message.lower():
                message += "\nReturn in code block."

        await self.fill_message(message)
        await self.activate_tools(tools)
        submit_button = await self.get_submit_button()
        await submit_button.click()

        await self.wait_for_response()
        if expected_result == "code" or expected_result == "json":
            return await self.get_code_block_response()
        else:
            return await self.get_text_response()

    @override
    async def attach_file(self, file_path: str):
        path = Path(file_path)
        file_name = path.name
        file_input = self.page.locator('input[type="file"]')
        await file_input.set_input_files(file_path)
        await self.page.wait_for_timeout(3000)
        if await self.page.locator(".f3a54b52").count() <= 0:
            raise ValueError("File could not be attached")

        if (
            next(
                (x for x in await self.page.locator(".f3a54b52").all_inner_texts() if file_name.lower() in x.lower()),
                None,
            )
            is None
        ):
            raise ValueError("File could not be attached")

    @override
    async def wait_for_response(self):
        await self.page.wait_for_timeout(3000)

        if await self.page.locator(".f9bf7997.d7dc56a8.c05b5566").count() <= 0:
            return await self.wait_for_response()

        if await self.page.locator(".f9bf7997.c05b5566").count() <= 0:
            return await self.wait_for_response()

        if await self.page.locator(".f9bf7997.d7dc56a8.c05b5566").last.locator(".ds-icon-button").count() < 4:
            return await self.wait_for_response()

    @override
    async def handle_on_error(self, error: Exception):
        return await super().handle_on_error(error)

    @override
    async def fill_message(self, message: str):
        input_field = await self.get_input_field()
        await input_field.fill("")
        list_message = message.split("\n")
        for message in list_message:
            await input_field.type(message)
            await input_field.press("Shift+Enter")
        await self.page.wait_for_timeout(3000)

    async def activate_tools(self, tools: list[Literal["search", "deep_think"]]):
        need_click_search = False
        try:
            search_enabled = await self.page.evaluate("localStorage.getItem('searchEnabled')")
            if "search" in tools and (search_enabled is None or json.loads(search_enabled)["value"] == False):
                need_click_search = True
            elif "search" not in tools and (json.loads(search_enabled)["value"] == True):
                need_click_search = True
        except Exception as e:
            need_click_search = True

        if need_click_search and await self.page.locator(".ad0c98fd").locator("text=Search").count() > 0:
            await self.page.locator(".ad0c98fd").locator("text=Search").first.click()

        need_click_thinking = False
        try:
            deep_think_enabled = await self.page.evaluate("localStorage.getItem('thinkingEnabled')")
            if "deep_think" in tools and (
                deep_think_enabled is None or json.loads(deep_think_enabled)["value"] == False
            ):
                need_click_thinking = True
            elif "deep_think" not in tools and (json.loads(deep_think_enabled)["value"] == True):
                need_click_thinking = True
        except Exception as e:
            need_click_thinking = True

        if need_click_thinking and await self.page.locator(".ad0c98fd").locator("text=DeepThink").count() > 0:
            await self.page.locator(".ad0c98fd").locator("text=DeepThink").first.click()
