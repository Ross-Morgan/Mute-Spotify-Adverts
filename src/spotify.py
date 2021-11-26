# Module imports
import sewar.full_ref as image_similarity
import win32gui
import win32ui
import ctypes
import cv2

from threading import Thread
from typing import Union
from PIL import Image

# File imports
from window import identify_window


class ReturnThread(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        # print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def screenshot_app(hwnd: int = None):
    if hwnd is None:
        hwnd = identify_window(message_box=True)

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bottom - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

    saveDC.SelectObject(saveBitMap)

    result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    bbox = (1820, 1000, 93, 4)

    im = im.crop((bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]))

    if result == 1:
        im.save("..\\Images\\current_volume.png")


def is_identical_to(image0: str, image1: str):
    image0 = cv2.imread(image0)
    image1 = cv2.imread(image1)

    return image_similarity.mse(image0, image1)


def get_volume(hwnd: int = None) -> int:
    """:return: [integer or multiple of 1.6] in range [0 - 16]"""
    screenshot_app(hwnd)

    threads: list[Union[ReturnThread, float]] = []

    for i in range(17):
        threads.append(ReturnThread(target=is_identical_to, args=("..\\Images\\current_volume.png", f"..\\Images\\volume-{i * 10}.png")))
        threads[i].start()

    for i in range(8):
        threads.append(ReturnThread(target=is_identical_to, args=("..\\Images\\current_volume.png", f"..\\Images\\volume-{(i + 1) * 16}.png")))
        threads[17 + i].start()

    for val in threads:
        print(val)

    print()


    for i in range(len(threads)):
        threads[i] = threads[i].join()


    for val in threads:
        print(val)

    # Get index of matching image
    idx = threads.index(min(threads))

    vol = {
        17: 1.6,
        18: 3.2,
        19: 4.8,
        20: 6.4,
        21: 8,
        22: 9.6,
        23: 11.2,
        24: 12.8,
        25: 14.4,
    }

    if idx < 17:
        return round(idx)
    return round(vol[idx])
