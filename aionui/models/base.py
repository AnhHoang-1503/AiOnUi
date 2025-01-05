from abc import ABC, abstractmethod
from ..enums import ExpectedResult
from playwright.sync_api import Page
from ..config.config import Config


class BaseModel(ABC):
    url: str
    page: Page

    def __init__(self, config: Config, page: Page):
        self._config = config
        self.page = page

    def init_instructions(self):
        """
        Initializes the instructions for the AI model.
        """
        template = "For my requests, please proceed as follows:\n"
        template += "- Only respond to what is requested, do not add any descriptions or explanations.\n"
        template += "- Return in a code block for JSON and code, while text remains in normal format.\n"
        template += "- Search for any additional information on the internet if needed.\n"
        self.chat(template)

    def new_conversation(self):
        """
        Starts a new conversation.
        """
        self.page.goto(self.url)
        self.init_instructions()

    @abstractmethod
    def get_input_field(self):
        """
        Gets the input field to type messages.
        """
        pass

    @abstractmethod
    def get_submit_button(self):
        """
        Gets the submit button to send messages.
        """
        pass

    @abstractmethod
    def get_response(self):
        """
        Gets the response.
        """
        pass

    @abstractmethod
    def get_code_block_response(self):
        """
        Gets the response in a code block.
        """
        pass

    @abstractmethod
    def chat(self, message: str, expected_result: ExpectedResult = ExpectedResult.Text):
        """Sends a message to the AI model and returns the response.

        Args:
            message (str): The message to send to the AI model.
            expected_result (ExpectedResult, optional): The expected result of the response. Defaults to ExpectedResult.Text.
        """
        pass

    @abstractmethod
    def attach_file(self, file_path: str):
        """Attaches a file to the AI model.

        Args:
            file_path (str): The path to the file to attach.
        """
        pass

    @abstractmethod
    def wait_for_response(self):
        """
        Waits until the response is complete.
        """
        pass
