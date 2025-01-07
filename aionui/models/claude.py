import os
import time
from pathlib import Path
from typing import Literal, override
from playwright.sync_api import Locator
from .base import BaseModel
import pyperclip


class Claude(BaseModel):
    url: str = "https://claude.ai/new"

    @override
    def get_input_field(self) -> Locator:
        input_field = self.page.locator('[contenteditable="true"]')
        if input_field.count() > 0:
            return input_field.first
        raise ValueError("Input field not found")

    @override
    def get_submit_button(self) -> Locator:
        send_button = self.page.locator('[aria-label="Send Message"]')
        if send_button.count() > 0:
            return send_button.first

        raise ValueError("Submit button not found")

    @override
    def get_text_response(self):
        if self.page.locator(".font-claude-message").count() <= 0:
            raise ValueError("No response found")

        response = self.page.locator(".font-claude-message").last.inner_text()
        if response == "":
            raise ValueError("No response found")

        return response

    @override
    def get_code_block_response(self) -> str:
        if self.page.locator(".font-claude-message").count() <= 0:
            raise ValueError("No response found")

        last_response = self.page.locator(".font-claude-message").last
        copy_button = last_response.locator("button")
        if copy_button.count() <= 0:
            raise ValueError("Copy button not found")

        pyperclip.copy("")
        copy_button.click()
        result = pyperclip.paste()

        if result == "":
            raise ValueError("No response found")

        return result

    @override
    def get_image_response(self) -> str:
        pass

    @override
    def chat(
        self,
        message: str,
        expected_result: Literal["text", "image", "code", "json"] = "text",
    ) -> str:
        if "claude" not in self.page.url.lower():
            self.page.goto(self.url)
            self.page.wait_for_load_state("networkidle")
            time.sleep(2)

        if expected_result == "code" or expected_result == "json":
            if "return in code block" not in message.lower():
                message += "\nReturn in code block."
        self.get_input_field()
        self.fill_message(message)
        self.get_submit_button().click()
        self.wait_for_response()
        if expected_result == "code" or expected_result == "json":
            return self.get_code_block_response()
        else:
            return self.get_text_response()

    @override
    def attach_file(self, file_path: str):
        path = Path(file_path)
        file_name = path.name
        file_input = self.page.locator('input[data-testid="file-upload"]')
        file_input.set_input_files(file_path)
        self.page.wait_for_load_state("networkidle")
        if Path(file_input.input_value()).name != file_name:
            raise ValueError("File could not be attached")

    @override
    def wait_for_response(self):
        time.sleep(2)
        self.page.wait_for_load_state("networkidle")

    @override
    def handle_on_error(self, error: Exception):
        return super().handle_on_error(error)
