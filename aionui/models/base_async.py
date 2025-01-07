from abc import ABC, abstractmethod
from typing import Literal

from playwright.async_api import Locator, Page
from ..config.config import Config
from ..exceptions import BotDetectedException
import os
import codecs


class BaseAsyncModel(ABC):
    url: str
    page: Page
    config: Config

    def __init__(self, config: Config, page: Page):
        self.config = config
        self.page = page

    async def new_conversation(self):
        """
        Starts a new conversation asynchronously.
        """
        await self.page.goto(self.url, wait_until="networkidle")
        await self.page.wait_for_timeout(1000)
        if "just a moment" in (await self.page.title()).lower():
            raise BotDetectedException("Cloudflare detected")
        await self.init_instructions()

    async def init_instructions(self):
        """
        Initializes the instructions for the AI model asynchronously.
        """
        template = "For my requests, please proceed as follows:\n"
        template += "- Only respond to what is requested, do not add any descriptions or explanations.\n"
        template += "- Return in a code block for JSON and code, while text remains in normal format.\n"
        template += "- Search for any additional information on the internet if needed.\n"
        await self.chat(template)

    async def fill_message(self, message: str):
        """
        Fills the message into the input field asynchronously.
        """
        input_field = await self.get_input_field()
        await input_field.fill(message)

    async def text_as_file(self, text: str, file_name: str = "attachment.txt"):
        """
        Converts text to a file and attaches it asynchronously.

        Args:
            text (str): The text content to write to the file
            file_name (str, optional): The name of the file to create. Defaults to "attachment.txt"
        """
        path = os.path.abspath(file_name)

        if os.path.exists(path):
            os.remove(path)

        with codecs.open(path, "w", encoding="utf-8") as file:
            file.write(text)

        await self.attach_file(path)
        os.remove(path)

    @abstractmethod
    async def get_input_field(self) -> Locator:
        """
        Gets the input field to type messages asynchronously.
        """
        pass

    @abstractmethod
    async def get_submit_button(self) -> Locator:
        """
        Gets the submit button to send messages asynchronously.
        """
        pass

    @abstractmethod
    async def get_text_response(self) -> str:
        """
        Gets the text response asynchronously.
        """
        pass

    @abstractmethod
    async def get_code_block_response(self) -> str:
        """
        Gets the response in a code block asynchronously.
        """
        pass

    @abstractmethod
    async def get_image_response(self) -> str:
        """
        Gets the image response asynchronously.

        Returns:
            str: Image url.
        """
        pass

    @abstractmethod
    async def chat(self, message: str, expected_result: Literal["text", "image", "code", "json"] = "text") -> str:
        """
        Sends a message to the AI model and returns the response asynchronously.

        Args:
            message (str): The message to send to the AI model.
            expected_result (Literal["text", "image", "code", "json"], optional): The expected result type.
                Can be "text", "image", "code", or "json". Defaults to "text".

        Returns:
            str: The response from the AI model. The format depends on expected_result:
                - "text": Plain text response
                - "image": URL to generated image
                - "code": Code block response
                - "json": JSON response as string

        Raises:
            BotDetectedException: If bot detection (e.g. Cloudflare) blocks the request.
        """
        pass

    @abstractmethod
    async def attach_file(self, file_path: str):
        """
        Attaches a file to the AI model asynchronously.

        Args:
            file_path (str): The path to the file to attach.
        """
        pass

    @abstractmethod
    async def wait_for_response(self):
        """
        Waits until the response is complete asynchronously.
        """
        pass

    @abstractmethod
    async def handle_on_error(self, error: Exception):
        """
        Handles when chat fails asynchronously.

        Args:
            error (Exception): The exception that was raised during chat.
        """
        pass
