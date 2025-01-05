from aionui.models.base import BaseModel
from .config import Config
from typing import Optional
from playwright.sync_api import Playwright, Browser, Page, BrowserContext, sync_playwright
from playwright.async_api import (
    Playwright as AsyncPlaywright,
    Browser as AsyncBrowser,
    Page as AsyncPage,
    BrowserContext as AsyncBrowserContext,
)
from .utils.logger import get_logger

default_logger = get_logger()


class AiOnUI:
    config: Config
    _playwright: Optional[Playwright] = None
    _browser: Optional[Browser] = None
    _page: Optional[Page] = None
    _context: Optional[BrowserContext] = None
    _outer_playwright: bool = False

    def __init__(self, config_path: Optional[str] = None, playwright: Optional[Playwright] = None) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.config = Config(config_path)
        if playwright is not None:
            self._playwright = playwright
            self._outer_playwright = True

    def load_config(self, config_path: str) -> None:
        """
        Loads the config from a YAML file.
        """
        self.config.load_config(config_path)

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
