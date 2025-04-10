from pathlib import Path
import os
from functools import cache
from gidapptools.errors import MissingOptionalDependencyError

try:
    from PySide6.QtGui import QIcon, QPixmap

    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False


IMAGES_DIR = Path(__file__).parent.absolute()


class StoredImage:
    allowed_extensions: frozenset[str] = frozenset(["png", "jpg", "jpeg"])

    def __init__(self, path: Path):
        self.path = path.resolve()
        self.name = self.path.stem
        self._bytes: bytes = None

    @property
    def bytes(self) -> bytes:
        if self._bytes is None:
            self._bytes = self.path.read_bytes()
        return self._bytes

    def as_qicon(self):
        if PYSIDE_AVAILABLE:
            return QIcon(str(self.path))

        raise NotImplementedError()

    def as_qpixmap(self):
        if PYSIDE_AVAILABLE:
            return QPixmap(self.path)

        raise NotImplementedError()


@cache
def get_image(name: str) -> StoredImage:
    cleaned_name = name.casefold().rsplit(".", 1)[0]
    for dirname, folderlist, filelist in os.walk(IMAGES_DIR):
        for file in filelist:
            if file.rsplit(".", 1)[-1] in StoredImage.allowed_extensions and file.casefold().rsplit(".", 1)[0] == cleaned_name:
                path = Path(dirname, file)
                return StoredImage(path)
    raise FileNotFoundError(f"No gif with name {name!r} found.")
