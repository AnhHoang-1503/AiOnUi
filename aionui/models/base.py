from abc import ABC, abstractmethod
from playwright.sync_api import Page
from ..config.config import Config


class BaseModel(ABC):
    url: str

    def __init__(self, config: Config):
        self._config = config

    @abstractmethod
    def get_input_field(self, page: Page):
        pass

    @abstractmethod
    def get_submit_button(self, page: Page):
        pass

    @abstractmethod
    def get_response(self, page: Page):
        pass

    @abstractmethod
    def get_code_block_response(self, page: Page):
        pass
