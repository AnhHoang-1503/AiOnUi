import os
from typing import Optional
from ..enums.platform import Platform
import platform


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
