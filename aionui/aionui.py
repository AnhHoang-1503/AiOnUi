from contextlib import asynccontextmanager, contextmanager
from typing import Optional, overload, Union, Literal, Any, Generator, AsyncGenerator
import subprocess
import time
import asyncio
import nest_asyncio
from playwright.async_api import (
    Playwright as AsyncPlaywright,
    Browser as AsyncBrowser,
    Page as AsyncPage,
    BrowserContext as AsyncBrowserContext,
    async_playwright,
)
from playwright.sync_api import (
    Playwright as SyncPlaywright,
    Browser as SyncBrowser,
    Page as SyncPage,
    BrowserContext as SyncBrowserContext,
    sync_playwright,
)
from .config import Config
from .utils.logger import get_logger
from .models import GPT, Claude, Gemini, DeepSeek
from .models_async import GPTAsync, ClaudeAsync, GeminiAsync, DeepSeekAsync

nest_asyncio.apply()
default_logger = get_logger()


class AiOnUi:
    config: Config
    _playwright_sync: Optional[SyncPlaywright] = None
    _playwright_async: Optional[AsyncPlaywright] = None
    _browser_sync: Optional[SyncBrowser] = None
    _browser_async: Optional[AsyncBrowser] = None
    _context_sync: Optional[SyncBrowserContext] = None
    _context_async: Optional[AsyncBrowserContext] = None
    _page_sync: Optional[SyncPage] = None
    _page_async: Optional[AsyncPage] = None

    @overload
    def __init__(
        self,
        config_path: Optional[str] = None,
        playwright: Optional[SyncPlaywright] = None,
        browser: Optional[SyncBrowser] = None,
        context: Optional[SyncBrowserContext] = None,
        page: Optional[SyncPage] = None,
    ) -> None:
        """Initialize AiOnUi with synchronous Playwright components.

        Args:
            config_path: Optional path to config file
            playwright: Optional SyncPlaywright instance
            browser: Optional synchronous Browser instance
            context: Optional synchronous BrowserContext instance
            page: Optional synchronous Page instance
        """
        ...

    @overload
    def __init__(
        self,
        config_path: Optional[str] = None,
        playwright: Optional[AsyncPlaywright] = None,
        browser: Optional[AsyncBrowser] = None,
        context: Optional[AsyncBrowserContext] = None,
        page: Optional[AsyncPage] = None,
    ) -> None:
        """Initialize AiOnUi with asynchronous Playwright components.

        Args:
            config_path: Optional path to config file
            playwright: Optional AsyncPlaywright instance
            browser: Optional asynchronous Browser instance
            context: Optional asynchronous BrowserContext instance
            page: Optional asynchronous Page instance
        """
        ...

    def __init__(
        self,
        config_path: Optional[str] = None,
        playwright: Optional[Union[SyncPlaywright, AsyncPlaywright]] = None,
        browser: Optional[Union[SyncBrowser, AsyncBrowser]] = None,
        context: Optional[Union[SyncBrowserContext, AsyncBrowserContext]] = None,
        page: Optional[Union[SyncPage, AsyncPage]] = None,
    ) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.config = Config(config_path)

        if isinstance(playwright, AsyncPlaywright):
            self._playwright_async = playwright
        else:
            self._playwright_sync = playwright
        if isinstance(browser, AsyncBrowser):
            self._browser_async = browser
        else:
            self._browser_sync = browser
        if isinstance(context, AsyncBrowserContext):
            self._context_async = context
        else:
            self._context_sync = context
        if isinstance(page, AsyncPage):
            self._page_async = page
        else:
            self._page_sync = page

    def load_config(self, config_path: str) -> None:
        """
        Loads the config from a YAML file.
        """
        self.config.load_config(config_path)

    # region Async Api
    @overload
    @asynccontextmanager
    async def model_async(self, model: Literal["gpt"]) -> AsyncGenerator[GPTAsync, None]: ...

    @overload
    @asynccontextmanager
    async def model_async(self, model: Literal["claude"]) -> AsyncGenerator[ClaudeAsync, None]: ...

    @overload
    @asynccontextmanager
    async def model_async(self, model: Literal["gemini"]) -> AsyncGenerator[GeminiAsync, None]: ...

    @overload
    @asynccontextmanager
    async def model_async(self, model: Literal["deep_seek"]) -> AsyncGenerator[DeepSeekAsync, None]: ...

    @overload
    @asynccontextmanager
    async def model_async(
        self, model: Literal["gpt", "claude", "gemini", "deep_seek"]
    ) -> AsyncGenerator[Union[GPTAsync, ClaudeAsync, GeminiAsync, DeepSeekAsync], None]: ...

    @asynccontextmanager
    async def model_async(
        self, model: Literal["gpt", "claude", "gemini", "deep_seek"]
    ) -> AsyncGenerator[Union[GPTAsync, ClaudeAsync, GeminiAsync, DeepSeekAsync], None]:
        async with self.get_page_async() as page:
            if model == "gpt":
                yield GPTAsync(self.config, page)
            elif model == "claude":
                yield ClaudeAsync(self.config, page)
            elif model == "gemini":
                yield GeminiAsync(self.config, page)
            elif model == "deep_seek":
                yield DeepSeekAsync(self.config, page)

    @asynccontextmanager
    async def get_page_async(self) -> AsyncGenerator[AsyncPage, None]:
        if self._page_async is not None:
            yield self._page_async
        elif self._context_async is not None:
            page = await self._context_async.new_page()
            yield page
            await page.close()
        elif self._browser_async is not None:
            context = self._browser_async.contexts[0]
            page = await context.new_page()
            yield page
            await page.close()
        elif self._playwright_async is not None:
            try:
                browser = await self._playwright_async.chromium.connect_over_cdp(
                    f"http://localhost:{self.config.debug_port}"
                )
            except:
                subprocess.Popen([self.config.chrome_binary_path, f"--remote-debugging-port={self.config.debug_port}"])
                await asyncio.sleep(3)
                browser = await self._playwright_async.chromium.connect_over_cdp(
                    f"http://localhost:{self.config.debug_port}"
                )
            context = browser.contexts[0]
            page = await context.new_page()
            yield page
            await page.close()
            await context.close()
            await browser.close()
        else:
            async with async_playwright() as playwright:
                try:
                    browser = await playwright.chromium.connect_over_cdp(f"http://localhost:{self.config.debug_port}")
                except:
                    subprocess.Popen(
                        [self.config.chrome_binary_path, f"--remote-debugging-port={self.config.debug_port}"]
                    )
                    await asyncio.sleep(3)
                    browser = await playwright.chromium.connect_over_cdp(f"http://localhost:{self.config.debug_port}")
                context = browser.contexts[0]
                page = await context.new_page()
                yield page
                await page.close()
                await context.close()
                await browser.close()

    # endregion

    # region Sync Api
    @overload
    @contextmanager
    def model_sync(self, model: Literal["gpt"]) -> Generator[GPT, None, None]: ...

    @overload
    @contextmanager
    def model_sync(self, model: Literal["claude"]) -> Generator[Claude, None, None]: ...

    @overload
    @contextmanager
    def model_sync(self, model: Literal["gemini"]) -> Generator[Gemini, None, None]: ...

    @overload
    @contextmanager
    def model_sync(self, model: Literal["deep_seek"]) -> Generator[DeepSeek, None, None]: ...

    @overload
    @contextmanager
    def model_sync(
        self, model: Literal["gpt", "claude", "gemini", "deep_seek"]
    ) -> Generator[Union[GPT, Claude, Gemini, DeepSeek], None, None]: ...

    @contextmanager
    def model_sync(
        self, model: Literal["gpt", "claude", "gemini", "deep_seek"]
    ) -> Generator[Union[GPT, Claude, Gemini, DeepSeek], None, None]:
        with self.get_page_sync() as page:
            if model == "gpt":
                yield GPT(self.config, page)
            elif model == "claude":
                yield Claude(self.config, page)
            elif model == "gemini":
                yield Gemini(self.config, page)
            elif model == "deep_seek":
                yield DeepSeek(self.config, page)

    @contextmanager
    def get_page_sync(self) -> Generator[SyncPage, None, None]:
        if self._page_sync is not None:
            yield self._page_sync
        elif self._context_sync is not None:
            page = self._context_sync.new_page()
            yield page
            page.close()
        elif self._browser_sync is not None:
            context = self._browser_sync.contexts[0]
            page = context.new_page()
            yield page
            page.close()
        elif self._playwright_sync is not None:
            try:
                browser = self._playwright_sync.chromium.connect_over_cdp(f"http://localhost:{self.config.debug_port}")
            except:
                subprocess.Popen([self.config.chrome_binary_path, f"--remote-debugging-port={self.config.debug_port}"])
                time.sleep(3)
                browser = self._playwright_sync.chromium.connect_over_cdp(f"http://localhost:{self.config.debug_port}")
            context = browser.contexts[0]
            page = context.new_page()
            yield page
            page.close()
            context.close()
            browser.close()
        else:
            with sync_playwright() as playwright:
                try:
                    browser = playwright.chromium.connect_over_cdp(f"http://localhost:{self.config.debug_port}")
                except:
                    subprocess.Popen(
                        [self.config.chrome_binary_path, f"--remote-debugging-port={self.config.debug_port}"]
                    )
                    time.sleep(3)
                    browser = playwright.chromium.connect_over_cdp(f"http://localhost:{self.config.debug_port}")
                context = browser.contexts[0]
                page = context.new_page()
                yield page
                page.close()
                context.close()
                browser.close()

    # endregion
