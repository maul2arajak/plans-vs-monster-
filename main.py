from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys


REQUIRED_PACKAGES = (
    ("pygame", "pygame>=2.5.0"),
    ("pytmx", "pytmx>=3.32"),
    ("cv2", "opencv-python>=4.8.0"),
)

def ensure_dependencies() -> None:

    missing = [package for module, package in REQUIRED_PACKAGES if importlib.util.find_spec(module) is None]
    if not missing:
        return

    print("Dependency game belum lengkap. Memasang: " + ", ".join(missing))
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
    except (OSError, subprocess.CalledProcessError) as exc:
        print("Gagal memasang dependency game.")
        print("Jalankan perintah berikut secara manual:")
        print(f'  "{sys.executable}" -m pip install -r requirements.txt')
        print(f"Detail error: {exc}")
        try:
            input("Tekan ENTER untuk keluar...")
        except EOFError:
            pass
        raise SystemExit(1) from exc


def relaunch_supported_python() -> bool:
    if sys.version_info < (3, 14):
        return False

    try:
        subprocess.run(
            ["py", "-3.11", "-c", "import pygame, pytmx, cv2"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        try:
            subprocess.check_call(["py", "-3.11", "-m", "pip", "install", "-r", str(Path(__file__).with_name("requirements.txt"))])
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            print("Python 3.11 diperlukan, tetapi tidak dapat menyiapkannya.")
            print("Pasang Python 3.11 lalu jalankan: py -3.11 main.py")
            raise SystemExit(1) from exc

    try:
        return_code = subprocess.call(["py", "-3.11", str(Path(__file__).resolve())])
    except OSError:
        return_code = 1
    raise SystemExit(return_code)


if __name__ == "__main__":
    relaunch_supported_python()
    ensure_dependencies()
    from src.game import Game

    Game().run()
