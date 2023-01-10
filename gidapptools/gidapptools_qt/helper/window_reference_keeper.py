"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path
from threading import RLock

# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6.QtGui import Qt, QCloseEvent
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QApplication

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


class SecondaryWindow(QWidget):
    close_signal = Signal(QWidget)

    def __init__(self, parent: QWidget = None, f: Qt.WindowFlags = None, name: str = None) -> None:
        super().__init__(*[i for i in [parent, f] if i is not None])
        self.is_closed: bool = False
        if name is not None:
            self.setObjectName(name)
            self.setWindowTitle(name)

    @property
    def app(self) -> QApplication:
        return QApplication.instance()

    def closeEvent(self, event: QCloseEvent) -> None:
        super().closeEvent(event)
        self.close_signal.emit(self)
        self.is_closed = True

    def __repr__(self) -> str:

        return f'{self.__class__.__name__}'


class WindowReferenceKeeper:

    def __init__(self) -> None:
        self.lock = RLock()
        self._open_windows: list[SecondaryWindow] = []

    def show(self, window: SecondaryWindow) -> SecondaryWindow:
        if not isinstance(window, SecondaryWindow):
            raise TypeError(f"{self.__class__.__name__!r} can only handle windows that are a subclass of {SecondaryWindow.__name__!r}.")
        with self.lock:
            if window not in self._open_windows:
                self._open_windows.append(window)
            window.close_event.connect(self.on_window_close)
            window.show()
            return window

    def on_window_close(self, window: SecondaryWindow) -> None:
        with self.lock:
            try:
                self._open_windows.remove(window)
            except ValueError:
                pass

    def remove_already_closed(self) -> None:
        with self.lock:
            self._open_windows = [w for w in self._open_windows if w.is_closed is False]


# region [Main_Exec]
if __name__ == '__main__':
    pass

# endregion [Main_Exec]
