"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path
from typing import TypeVar
from collections.abc import Mapping, Iterable
# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QWidget, QApplication

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


def center_window(window: QWidget, allow_window_resize: bool = True) -> QWidget:
    app = QApplication.instance()
    if allow_window_resize is True:
        window.resize(window.sizeHint())

    screen = app.primaryScreen()
    screen_geo = QScreen.availableGeometry(screen)
    screen_center = screen_geo.center()

    window_geo = window.frameGeometry()
    window_geo.moveCenter(screen_center)
    window.move(window_geo.topLeft())
    return window


T_WIDGET = TypeVar("T_WIDGET", bound=QWidget)


def batch_modify_widget(widget: T_WIDGET, **kwargs) -> T_WIDGET:
    for method_name, method_arguments in kwargs.items():
        method = getattr(widget, method_name)

        if isinstance(method_arguments, Mapping):
            method(**method_arguments)

        elif isinstance(method_arguments, Iterable) and not isinstance(method_arguments, str):
            method(*method_arguments)

        elif method_arguments is ...:
            method()

        else:
            method(method_arguments)

    return widget

# region [Main_Exec]


if __name__ == '__main__':
    pass

# endregion [Main_Exec]
