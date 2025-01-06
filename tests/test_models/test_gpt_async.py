import json
import re
from pathlib import Path
from playwright.async_api import expect, Playwright
import pytest
from aionui.models import GPTAsync
from aionui.enums import ExpectedResult
from aionui.config import Config
from playwright.async_api import async_playwright
import pytest_asyncio


@pytest_asyncio.fixture
async def gpt_async(config_file: str):
    async with async_playwright() as playwright:
        config = Config(config_file)
        browser = await playwright.chromium.connect_over_cdp(f"http://localhost:{config.debug_port}")
        context = browser.contexts[0]
        page = await context.new_page()
        await page.goto("https://chatgpt.com", wait_until="networkidle")
        gpt = GPTAsync(config, page)
        yield gpt
        await page.close()


@pytest.mark.asyncio
async def test_init_instructions(gpt_async: GPTAsync):
    await gpt_async.init_instructions()
    await expect(gpt_async.page.locator("article .sr-only").last).to_have_text(
        re.compile("ChatGPT said:", re.IGNORECASE)
    )


@pytest.mark.asyncio
async def test_get_input_field(gpt_async: GPTAsync):
    input_field = await gpt_async.get_input_field()
    await expect(input_field).to_be_visible()


@pytest.mark.asyncio
async def test_fill_message(gpt_async: GPTAsync):
    await gpt_async.fill_message("Hello")
    await expect(await gpt_async.get_input_field()).to_have_text(re.compile("Hello", re.IGNORECASE))


@pytest.mark.asyncio
async def test_get_submit_button(gpt_async: GPTAsync):
    submit_button = await gpt_async.get_submit_button()
    await expect(submit_button).to_be_visible()


@pytest.mark.asyncio
async def test_attach_file(gpt_async: GPTAsync, content_file):
    path = Path(content_file)
    await gpt_async.attach_file(content_file)
    await expect(gpt_async.page.locator("input[type='file']")).to_have_value(
        re.compile(r".*{}".format(path.name), re.IGNORECASE)
    )


@pytest.mark.asyncio
async def test_text_as_file(gpt_async: GPTAsync):
    await gpt_async.text_as_file("Xin chào")
    await expect(gpt_async.page.locator("input[type='file']")).to_have_value(
        re.compile(r".*attachment.txt", re.IGNORECASE)
    )


@pytest.mark.asyncio
async def test_chat_text(gpt_async: GPTAsync):
    result = await gpt_async.chat(
        "Trả lời chính xác từ sau, không thêm bất kỳ thông tin hoặc dấu câu nào khác: `Xin chào`",
    )
    assert result == "Xin chào"


@pytest.mark.asyncio
async def test_chat_code(gpt_async: GPTAsync):
    result = await gpt_async.chat(
        'Trả lời lại chính xác json sau, không thêm bất kỳ thông tin nào khác: `{"message": "Xin chào"}`',
        ExpectedResult.Code,
    )
    dict_result = json.loads(result)
    assert dict_result == {"message": "Xin chào"}
