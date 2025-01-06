import time
from .models import BaseModel, GPT, Claude, Gemini, GPTAsync, ClaudeAsync, GeminiAsync, BaseAsyncModel
from .exceptions import BotDetectedException
from .config import Config
from .enums import AiModel, ExpectedResult
from typing import Optional, TypeVar, Type
from playwright.sync_api import Playwright, Browser, Page, BrowserContext, sync_playwright
from playwright.async_api import (
    Playwright as AsyncPlaywright,
    Browser as AsyncBrowser,
    Page as AsyncPage,
    BrowserContext as AsyncBrowserContext,
    async_playwright,
)
from .utils.logger import get_logger
import nest_asyncio
import subprocess

nest_asyncio.apply()

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
        try:
            return self.model.chat(message, expected_result)
        except BotDetectedException:
            self.logger.error("Bot detected")
            self.handle_bot_detected()
            time.sleep(10)
            return self.chat(message, expected_result)

    def attach_file(self, file_path: str):
        """
        Attaches a file to the AI model.
        """
        try:
            return self.model.attach_file(file_path)
        except BotDetectedException:
            self.logger.error("Bot detected")
            self.handle_bot_detected()
            time.sleep(10)
            return self.attach_file(file_path)

    def handle_bot_detected(self):
        """
        Handles the bot detected exception.
        """
        self.close_browser()
        self._page.goto(self.model.url, wait_until="networkidle")
        if self._page.locator("input[type='checkbox']").count() > 0:
            self._page.locator("input[type='checkbox']").first.check()
        self.set_up_browser()

    def __enter__(self):
        if self._playwright is None:
            self._playwright = sync_playwright().start()

        self.set_up_browser()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_browser()
        if self._playwright is not None and not self._outer_playwright:
            self._playwright.stop()
            self._playwright = None

    def set_up_browser(self):
        try:
            self._browser = self._playwright.chromium.connect_over_cdp(f"http://localhost:{self.config.debug_port}")
        except Exception as e:
            subprocess.Popen([self.config.chrome_binary_path, f"--remote-debugging-port={self.config.debug_port}"])
            time.sleep(10)
            self._browser = self._playwright.chromium.connect_over_cdp(f"http://localhost:{self.config.debug_port}")

        self._context = self._browser.contexts[0]
        self._page = self._context.new_page()

        model_map: dict[AiModel, Type[BaseModel]] = {AiModel.GPT: GPT, AiModel.Claude: Claude, AiModel.Gemini: Gemini}
        model_class = model_map[self._model_type]
        self.model = model_class(self.config, self._page)
        self.model.new_conversation()

    def close_browser(self):
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
        except Exception as e:
            self.logger.error(f"Error closing browser or playwright: {e}")


class AiOnUiAsync:
    config: Config
    model: T
    _playwright: Optional[AsyncPlaywright] = None
    _browser: Optional[AsyncBrowser] = None
    _page: Optional[AsyncPage] = None
    _context: Optional[AsyncBrowserContext] = None
    _outer_playwright: bool = False
    _model_type: AiModel

    def __init__(
        self, model_type: AiModel, config_path: Optional[str] = None, playwright: Optional[AsyncPlaywright] = None
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

    async def chat(self, message: str, expected_result: ExpectedResult = ExpectedResult.Text) -> str:
        """
        Sends a message to the AI model and returns the response.
        """
        try:
            return await self.model.chat(message, expected_result)
        except BotDetectedException:
            self.logger.error("Bot detected")
            await self.handle_bot_detected()
            await self._page.wait_for_timeout(10000)
            return await self.chat(message, expected_result)

    async def attach_file(self, file_path: str):
        """
        Attaches a file to the AI model.
        """
        try:
            return await self.model.attach_file(file_path)
        except BotDetectedException:
            self.logger.error("Bot detected")
            await self.handle_bot_detected()
            await self._page.wait_for_timeout(10000)
            return await self.attach_file(file_path)

    async def handle_bot_detected(self):
        """
        Handles the bot detected exception.
        """
        await self.close_browser()
        await self._page.goto(self.model.url, wait_until="networkidle")
        checkbox = self._page.locator("input[type='checkbox']")
        if await checkbox.count() > 0:
            await checkbox.first.check()
        await self.set_up_browser()

    async def __aenter__(self):
        if self._playwright is None:
            self._playwright = await async_playwright().start()
        await self.set_up_browser()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close_browser()
        if self._playwright is not None and not self._outer_playwright:
            await self._playwright.stop()
            self._playwright = None

    async def set_up_browser(self):
        try:
            self._browser = await self._playwright.chromium.connect_over_cdp(
                f"http://localhost:{self.config.debug_port}"
            )
        except Exception as e:
            subprocess.Popen([self.config.chrome_binary_path, f"--remote-debugging-port={self.config.debug_port}"])
            time.sleep(10)
            self._browser = await self._playwright.chromium.connect_over_cdp(
                f"http://localhost:{self.config.debug_port}"
            )

        self._context = self._browser.contexts[0]
        self._page = await self._context.new_page()

        model_map: dict[AiModel, Type[BaseAsyncModel]] = {
            AiModel.GPT: GPTAsync,
            AiModel.Claude: ClaudeAsync,
            AiModel.Gemini: GeminiAsync,
        }
        model_class = model_map[self._model_type]
        self.model = model_class(self.config, self._page)
        await self.model.new_conversation()

    async def close_browser(self):
        try:
            if self._page is not None:
                await self._page.close()
                self._page = None
            if self._context is not None:
                await self._context.close()
                self._context = None
            if self._browser is not None and not self._outer_playwright:
                await self._browser.close()
                self._browser = None
        except Exception as e:
            self.logger.error(f"Error closing browser or playwright: {e}")
