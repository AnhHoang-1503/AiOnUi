from pathlib import Path
from typing import Literal, override
from playwright.async_api import Locator
from .base_async import BaseAsyncModel
import pyperclip


class GeminiAsync(BaseAsyncModel):
    url: str = "https://gemini.google.com/u/3/app"

    @override
    async def get_input_field(self) -> Locator:
        input_field = self.page.locator('[contenteditable="true"]')
        if await input_field.count() > 0:
            return input_field.first
        raise ValueError("Input field not found")

    @override
    async def get_submit_button(self) -> Locator:
        send_button = self.page.locator(".send-button")
        if await send_button.count() > 0:
            return send_button.first

        speech_button = self.page.locator("speech_dictation_mic_button")
        if await speech_button.count() > 0:
            return speech_button.first

        raise ValueError("Submit button not found")

    @override
    async def get_text_response(self) -> str:
        if await self.page.locator("model-response").count() <= 0:
            raise ValueError("No response found")

        response = await self.page.locator("model-response").last.inner_text()
        if response == "":
            raise ValueError("No response found")

        return response

    @override
    async def get_code_block_response(self) -> str:
        if await self.page.locator("model-response").count() <= 0:
            raise ValueError("No response found")

        last_response = self.page.locator("model-response").last
        copy_button = last_response.locator(".copy-button")
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
        if await self.page.locator("model-response").count() <= 0:
            raise ValueError("No response found")

        src = ""
        for _ in range(5):
            await self.page.wait_for_timeout(2000)
            last_response = self.page.locator("model-response").last
            img = last_response.locator("generated-image img")
            if await img.count() > 0:
                src = await img.get_attribute("src")
                if src != "":
                    break

        if src is None or src == "":
            raise ValueError("Image not found")

        return src

    @override
    async def chat(
        self,
        message: str,
        expected_result: Literal["text", "image", "code", "json"] = "text",
    ) -> str:
        if "gemini" not in self.page.url.lower():
            await self.page.goto(self.url)
            await self.page.wait_for_timeout(2000)

        if expected_result == "code" or expected_result == "json":
            if "return in code block" not in message.lower():
                message += "\nReturn in code block."

        await self.fill_message(message)
        submit_button = await self.get_submit_button()
        await submit_button.click()
        await self.wait_for_response()

        if expected_result == "image":
            return await self.get_image_response()
        elif expected_result == "code" or expected_result == "json":
            return await self.get_code_block_response()
        else:
            return await self.get_text_response()

    @override
    async def attach_file(self, file_path: str):
        path = Path(file_path)
        file_name = path.name

        if await self.page.locator('input[name="Filedata"]').count() <= 0:

            self.page.on("filechooser", lambda file_chooser: file_chooser)

            if await self.page.locator(".upload-card-button").count() <= 0:
                raise ValueError("Upload button not found")
            await self.page.locator(".upload-card-button").click()

            if await self.page.locator("#file-uploader-local").count() <= 0:
                raise ValueError("File uploader not found")
            await self.page.locator("#file-uploader-local").click()

        file_input = self.page.locator('input[name="Filedata"]').first
        await file_input.set_input_files(file_path)

        await self.page.wait_for_timeout(2000)
        if await self.page.locator(f'[data-test-id="file-name"][title="{file_name}"]').count() <= 0:
            raise ValueError("File could not be attached")

    @override
    async def wait_for_response(self):
        await self.page.wait_for_timeout(3000)

        if await self.page.locator("model-response").count() <= 0:
            return await self.wait_for_response()

        if await self.page.locator("model-response").last.locator("sensitive-memories-banner").count() <= 0:
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
