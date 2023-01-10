"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import TYPE_CHECKING, Optional
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
import PySide6
from PySide6.QtWidgets import QWidget, QApplication

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    pass

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


class ApplicationInfoWidget(QWidget):

    def __init__(self, app: QApplication, parent: Optional[PySide6.QtWidgets.QWidget] = None) -> None:
        self.app = app
        super().__init__(parent)

        # region [Main_Exec]
if __name__ == '__main__':
    pass

# endregion [Main_Exec]
