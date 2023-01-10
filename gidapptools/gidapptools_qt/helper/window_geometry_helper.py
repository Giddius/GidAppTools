"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import sys
from typing import TYPE_CHECKING
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QWidget, QApplication

if sys.version_info >= (3, 11):
    pass
else:
    pass
# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    ...

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


def move_to_center_of_screen(widget: QWidget, screen: QScreen = None) -> None:
    screen = screen or QApplication.instance().screenAt(widget.cursor().pos())

    screen_center = screen.availableGeometry().center()
    widget_geometry = widget.geometry()
    widget_geometry.moveCenter(screen_center)
    widget.setGeometry(widget_geometry)


# region [Main_Exec]

if __name__ == '__main__':
    pass

# endregion [Main_Exec]
