import os
import requests
from typing import Optional
from ..enums.platform import Platform
import platform
import re
import aiohttp


def get_platform() -> Platform:
    """Get current platform"""
    system = platform.system().lower()

    if system == "windows":
        return Platform.WINDOWS
    elif system == "darwin":
        return Platform.MACOS
    elif system == "linux":
        return Platform.LINUX
    else:
        return Platform.OTHER


def get_user_data_dir(platform: Platform) -> Optional[str]:
    """Get default chrome user data dir"""
    if platform == Platform.LINUX:
        path = os.path.join(os.path.expanduser("~"), ".config", "google-chrome")
    elif platform == Platform.MACOS:
        path = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Google", "Chrome")
    elif platform == Platform.WINDOWS:
        path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "User Data")
    else:
        return None

    if not os.path.exists(path):
        return None
    return path


def get_chrome_binary_path(platform: Platform) -> Optional[str]:
    """Get default chrome binary path"""
    if platform == Platform.WINDOWS:
        paths = [
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Google/Chrome/Application/chrome.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google/Chrome/Application/chrome.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google/Chrome/Application/chrome.exe"),
        ]

    elif platform == Platform.MACOS:
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ]

    elif platform == Platform.LINUX:
        paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chrome",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ]
    else:
        return None

    for path in paths:
        if os.path.exists(path):
            return path

    return None


def clean_text(text: str):
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"\{.*?\}", " ", text)
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def save_image(url: str, file_path: str):
    """Save image to file"""
    content = requests.get(url).content
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path


async def save_image_async(url: str, file_path: str) -> str:
    """Save image to file asynchronously"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                with open(file_path, "wb") as f:
                    f.write(content)
    return file_path
