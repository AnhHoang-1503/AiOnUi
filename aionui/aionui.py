from .models import BaseModel, GPT, Claude, Gemini
from .config import Config
from .enums import AiModel, ExpectedResult
from typing import Optional, TypeVar, Type
from playwright.sync_api import Playwright, Browser, Page, BrowserContext, sync_playwright
from playwright.async_api import (
    Playwright as AsyncPlaywright,
    Browser as AsyncBrowser,
    Page as AsyncPage,
    BrowserContext as AsyncBrowserContext,
)
from .utils.logger import get_logger

T = TypeVar("T", bound=BaseModel)

default_logger = get_logger()


class AiOnUI:
    config: Config
    model: T
    _playwright: Optional[Playwright] = None
    _browser: Optional[Browser] = None
    _page: Optional[Page] = None
    _context: Optional[BrowserContext] = None
    _outer_playwright: bool = False
    _model_type: AiModel

    def __init__(
        self, model_type: AiModel, config_path: Optional[str] = None, playwright: Optional[Playwright] = None
    ) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.config = Config(config_path)
        if playwright is not None:
            self._playwright = playwright
            self._outer_playwright = True

        self._model_type = model_type

    def load_config(self, config_path: str) -> None:
        """
        Loads the config from a YAML file.
        """
        self.config.load_config(config_path)

    def chat(self, message: str, expected_result: ExpectedResult = ExpectedResult.Text):
        """
        Sends a message to the AI model and returns the response.
        """
        return self.model.chat(message, expected_result)

    def attach_file(self, file_path: str):
        """
        Attaches a file to the AI model.
        """
        return self.model.attach_file(file_path)

    def __enter__(self):
        if self._playwright is None:
            self._playwright = sync_playwright().start()

        if self.config.connect_over_cdp:
            self._browser = self._playwright.chromium.connect_over_cdp(f"http://localhost:{self.config.debug_port}")
            self._context = self._browser.contexts[0]
        else:
            self._context = self._playwright.chromium.launch_persistent_context(
                headless=self.config.headless, user_data_dir=self.config.user_data_dir
            )

        self._page = self._context.new_page()

        model_map: dict[AiModel, Type[BaseModel]] = {AiModel.GPT: GPT, AiModel.Claude: Claude, AiModel.Gemini: Gemini}
        model_class = model_map[self._model_type]
        self.model = model_class(self.config, self._page)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self._page is not None:
                self._page.close()
                self._page = None
            if self._context is not None:
                self._context.close()
                self._context = None
            if self._browser is not None and not self._outer_playwright:
                self._browser.close()
                self._browser = None
            if self._playwright is not None and not self._outer_playwright:
                self._playwright.stop()
                self._playwright = None
        except Exception as e:
            self.logger.error(f"Error closing browser or playwright: {e}")
