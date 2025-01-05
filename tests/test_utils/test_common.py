import pytest
from aionui.utils.common import (
    get_platform,
    clean_text,
    save_image,
    save_image_async,
    get_user_data_dir,
    get_chrome_binary_path,
)
from aionui.enums import Platform
import os
from unittest.mock import patch


def test_get_platform():
    platform = get_platform()
    assert isinstance(platform, Platform)


def test_clean_text():
    text = "<div>Test<script>alert(1)</script></div>"
    cleaned = clean_text(text)
    assert cleaned == "Test"


def test_save_image():
    url = "https://interactive-examples.mdn.mozilla.net/media/cc0-images/grapefruit-slice-332-332.jpg"
    file_path = "test.jpg"
    saved_path = save_image(url, file_path)
    print(saved_path)
    assert os.path.exists(saved_path)
    os.remove(saved_path)


@pytest.mark.asyncio(loop_scope="module")
async def test_save_image_async():
    url = "https://interactive-examples.mdn.mozilla.net/media/examples/lizard.png"
    file_path = "testasync.jpg"
    saved_path = await save_image_async(url, file_path)
    assert os.path.exists(saved_path)
    os.remove(saved_path)


@pytest.mark.parametrize(
    "platform,expected_path",
    [
        (Platform.LINUX, "~/.config/google-chrome"),
        (Platform.MACOS, "~/Library/Application Support/Google/Chrome"),
        (Platform.WINDOWS, "~/AppData/Local/Google/Chrome/User Data"),
        (Platform.OTHER, None),
    ],
)
def test_get_user_data_dir(platform, expected_path):
    with patch("os.path.exists") as mock_exists:
        if platform == Platform.OTHER:
            assert get_user_data_dir(platform) is None
            mock_exists.assert_not_called()
            return

        mock_exists.return_value = True
        result = os.path.normpath(get_user_data_dir(platform))
        expected_full_path = os.path.normpath(os.path.expanduser(expected_path))
        assert result == expected_full_path
        mock_exists.assert_called_once_with(expected_full_path)

        mock_exists.reset_mock()
        mock_exists.return_value = False
        result = get_user_data_dir(platform)
        assert result is None
        mock_exists.assert_called_once_with(expected_full_path)


@pytest.mark.parametrize(
    "platform,expected_paths",
    [
        (
            Platform.WINDOWS,
            [
                os.path.join(os.environ.get("PROGRAMFILES", ""), "Google/Chrome/Application/chrome.exe"),
                os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google/Chrome/Application/chrome.exe"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google/Chrome/Application/chrome.exe"),
            ],
        ),
        (
            Platform.MACOS,
            [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            ],
        ),
        (
            Platform.LINUX,
            [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chrome",
                "/usr/bin/chromium-browser",
                "/snap/bin/chromium",
            ],
        ),
        (Platform.OTHER, None),
    ],
)
def test_get_chrome_binary_path(platform: Platform, expected_paths: list[str] | None):
    with patch("os.path.exists") as mock_exists:
        if expected_paths is None:
            assert get_chrome_binary_path(platform) is None
            mock_exists.assert_not_called()
            return

        mock_exists.return_value = False
        result = get_chrome_binary_path(platform)
        assert result is None
        assert mock_exists.call_count == len(expected_paths)

        mock_exists.reset_mock()
        mock_exists.side_effect = lambda p: p == expected_paths[0]
        result = get_chrome_binary_path(platform)
        assert result == expected_paths[0]
        assert mock_exists.call_count == 1

        mock_exists.reset_mock()
        mock_exists.side_effect = lambda p: p == expected_paths[-1]
        result = get_chrome_binary_path(platform)
        assert result == expected_paths[-1]
        assert mock_exists.call_count == len(expected_paths)
