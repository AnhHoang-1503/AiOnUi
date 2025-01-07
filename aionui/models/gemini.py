import time
from pathlib import Path
from typing import Literal, override
from playwright.sync_api import Locator
from .base import BaseModel
import pyperclip


class Gemini(BaseModel):
    url: str = "https://gemini.google.com/u/3/app"

    @override
    def get_input_field(self) -> Locator:
        input_field = self.page.locator('[contenteditable="true"]')
        if input_field.count() > 0:
            return input_field.first
        raise ValueError("Input field not found")

    @override
    def get_submit_button(self) -> Locator:
        send_button = self.page.locator(".send-button")
        if send_button.count() > 0:
            return send_button.first

        speech_button = self.page.locator("speech_dictation_mic_button")
        if speech_button.count() > 0:
            return speech_button.first

        raise ValueError("Submit button not found")

    @override
    def get_text_response(self):
        if self.page.locator("model-response").count() <= 0:
            raise ValueError("No response found")

        response = self.page.locator("model-response").last.inner_text()
        if response == "":
            raise ValueError("No response found")

        return response

    @override
    def get_code_block_response(self) -> str:
        if self.page.locator("model-response").count() <= 0:
            raise ValueError("No response found")

        last_response = self.page.locator("model-response").last
        copy_button = last_response.locator(".copy-button")
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
        if self.page.locator("model-response").count() <= 0:
            raise ValueError("No response found")

        src = ""
        for _ in range(5):
            time.sleep(2)
            last_response = self.page.locator("model-response").last
            img = last_response.locator("generated-image img").last
            if img.count() > 0:
                src = img.get_attribute("src")
                if src != "":
                    break

        if src is None or src == "":
            raise ValueError("Image not found")

        return src

    @override
    def chat(
        self,
        message: str,
        expected_result: Literal["text", "image", "code", "json"] = "text",
    ) -> str:
        if "gemini" not in self.page.url.lower():
            self.page.goto(self.url)
            time.sleep(2)

        if expected_result == "code" or expected_result == "json":
            if "return in code block" not in message.lower():
                message += "\nReturn in code block."

        self.fill_message(message)
        self.get_submit_button().click()
        self.wait_for_response()

        if expected_result == "image":
            return self.get_image_response()
        elif expected_result == "code" or expected_result == "json":
            return self.get_code_block_response()
        else:
            return self.get_text_response()

    @override
    def attach_file(self, file_path: str):
        path = Path(file_path)
        file_name = path.name

        if self.page.locator('input[name="Filedata"]').count() <= 0:

            self.page.on("filechooser", lambda file_chooser: file_chooser)

            if self.page.locator(".upload-card-button").count() <= 0:
                raise ValueError("Upload button not found")
            self.page.locator(".upload-card-button").click()

            if self.page.locator("#file-uploader-local").count() <= 0:
                raise ValueError("File uploader not found")
            self.page.locator("#file-uploader-local").click()

        file_input = self.page.locator('input[name="Filedata"]').first
        file_input.set_input_files(file_path)

        time.sleep(2)
        if self.page.locator(f'[data-test-id="file-name"][title="{file_name}"]').count() <= 0:
            raise ValueError("File could not be attached")

    @override
    def wait_for_response(self):
        time.sleep(3)

        if self.page.locator("model-response").count() <= 0:
            return self.wait_for_response()

        if self.page.locator("model-response").last.locator("sensitive-memories-banner").count() <= 0:
            return self.wait_for_response()

    @override
    def handle_on_error(self, error: Exception):
        return super().handle_on_error(error)

    @override
    def fill_message(self, message: str):
        input_field = self.get_input_field()
        input_field.fill("")
        list_message = message.split("\n")
        for message in list_message:
            input_field.type(message)
            input_field.press("Shift+Enter")

        self.page.wait_for_timeout(3000)
