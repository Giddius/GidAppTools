from pathlib import Path
import os

from PySide6.QtGui import QMovie, QPixmap

GIFS_DIR = Path(__file__).parent.absolute()


def get_gif(name: str) -> QMovie:
    cleaned_name = name.casefold().rsplit(".", 1)[0]
    for dirname, folderlist, filelist in os.walk(GIFS_DIR):
        for file in filelist:
            if file.casefold().rsplit(".", 1)[0] == cleaned_name:
                path = Path(dirname, file)
                return QMovie(str(path))
    raise FileNotFoundError(f"No gif with name {name!r} found.")
