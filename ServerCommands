import os
import shutil
import subprocess
import pyautogui
import glob

IMAGE_PATH = 'screen.jpg'
VALID_COMMANDS = ("exit", "update commands", "dir", "delete", "copy", "execute", "take_screenshot", "send_photo")


def dir_cmd(path) -> bytes:
    items = glob.glob(path + r"\*.*")
    return ''.join(items).encode()


def delete_cmd(path):
    os.remove(path)


def copy_cmd(copy_from, copy_to):
    shutil.copy(copy_from, copy_to)


def execute_cmd(path):
    subprocess.call(path)


def take_screenshot_cmd():
    image = pyautogui.screenshot()
    image.save(IMAGE_PATH)


def send_photo_cmd() -> bytes:
    with open(IMAGE_PATH, 'rb') as photo:
        image_bytes = photo.read()
    return image_bytes

