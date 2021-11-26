import win32gui
import string
import easygui

from typing import Union


def contains_any(text: str, checks: list[str]):
    for check in checks:
        if check in text:
            return True
    return False


def is_capitalised(text: str):
    artist = text.split(" - ")[0]
    return artist == string.capwords(artist)


def handler(hwnd, windows: list[tuple[str, int]]):
    text = win32gui.GetWindowText(hwnd)

    if text not in ["", "Default IME", "MSCTFIME UI"]:
        windows.append((text, hwnd))


def identify_window(message_box:bool=False, hwnd=True, window_name=False) -> Union[tuple[int, str], int, str]:
    windows = []

    win32gui.EnumWindows(handler, windows)

    windows = dict(windows)

    if message_box:
        _hwnd = windows[easygui.choicebox("Select Spotify Window", choices=[k for k in windows.keys()])]

        print(f"Window name: {win32gui.GetWindowText(_hwnd)}")
        print(f"Window hwnd: {_hwnd}")

        return _hwnd

    window = list(windows[0])

    return window[1]

    # if all([hwnd, window_name]):
    #     return tuple(window)

    # if not window_name:
    #     del window[1]

    # if not hwnd:
    #     del window[0]

    # return tuple(window)[0]
