# Module imports
from typing import Callable
import threading
import win32com.client
import win32gui
import time
import os

# File imports
from window import identify_window
from spotify import get_volume


class Waiter:
    def __init__(self, init_value, func: Callable = lambda x:x, ab: tuple[bool, bool] = (True, True)) -> None:
        self.var = init_value
        self.var_mutex = threading.Lock()
        self.var_event = threading.Event()

        assert callable(func)

        self.func_a = func if ab[0] else lambda x:x
        self.func_b = func if ab[1] else lambda x:x

    def wait_until(self, value) -> None:
        while True:
            self.var_mutex.acquire()
            if self.func_a(self.var) == self.func_b(value):
                self.var_mutex.release()
                return # Done waiting

            self.var_mutex.release()
            self.var_event.wait(1)

    def wait_until_change(self) -> None:
        original = self.func_a(self.var)
        while True:
            self.var_mutex.acquire()
            if self.func_b(self.var) != original:
                self.var_mutex.release()
                return # Done waiting
            self.var_mutex.release()
            self.var_event.wait(1)

    def set(self, value) -> None:
        self.var_mutex.acquire()
        self.var = value
        self.var_mutex.release()
        self.var_event.set()
        self.var_event.clear()


class Volume:
    DOWN = r"^{DOWN}"
    UP = r"^{UP}"


class AppHandler:
    """Handle interaction through Dispatch and win32 api"""
    def __init__(self, app:str, hwnd:int):
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.shell.AppActivate(app)
        self.hwnd = hwnd

    def send_keys(self, keys):
        self.shell.SendKeys(keys, 0)


def on_advert(app: AppHandler):
    waiter = Waiter(app.hwnd, win32gui.GetWindowText, (True, True))
    volume = get_volume(app.hwnd)

    print(f"{volume=}")

    for _ in range(volume):
        app.send_keys(Volume.DOWN)
        time.sleep(0.25)
        print(f"  {volume=}")

    waiter.wait_until_change()

    for _ in range(volume):
        app.send_keys(Volume.UP)
        time.sleep(0.25)
        print(f"  {volume=}")


def main():
    app = AppHandler("Spotify", identify_window(True))

    while True:
        waiter = Waiter(app.hwnd, win32gui.GetWindowText, (True, False))
        print("Waiting...")

        waiter.wait_until("Advertisement")

        on_advert(app)


def set_env():
    print("Checking environment variables...")
    if not os.getenv("Spotify"):
        print("Environment variable not found\n")

        spotify_path = input("Spotify installation path: ")
        if os.path.exists(spotify_path):
            os.system(f'SETX Spotify "{spotify_path}"')
        print("Set environment variable successfully!")
    else:
        print("Environment variable exists!")


if __name__ == "__main__":
    set_env()
    main()
