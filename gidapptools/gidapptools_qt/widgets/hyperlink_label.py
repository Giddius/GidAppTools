"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6.QtGui import QPalette, QMouseEvent, QDesktopServices
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QLabel, QApplication, QMainWindow, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout
from validators import url as validate_url
import requests
from time import perf_counter
# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


class HyperlinkLabel(QLabel):

    def __init__(self, link: str = None, validate: bool = False, parent=None):
        super().__init__(parent=parent)
        self.validate = validate
        self._link: str = None
        if link:
            self.set_link(link)
        self._set_link_color()

    @property
    def link(self) -> str:
        return self._link

    def get_link(self) -> str:
        return self._link

    def get_link_as_QUrl(self) -> QUrl:
        return QUrl(self._link)

    def _validate_link(self, link: str):
        result = validate_url(link)
        if not result:
            raise result

    def _modify_link(self, link: str) -> str:
        return link

    def set_link(self, link: str):
        link = self._modify_link(link)
        if self.validate is True:
            self._validate_link(link)
        self._link = link
        self.setText(link)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _set_link_color(self):
        link_color = QApplication.instance().palette().color(QPalette.Button.Link)
        r = link_color.red()
        g = link_color.green()
        b = link_color.blue()
        self.setStyleSheet(f"color: rgb({', '.join(str(i) for i in [r,g,b])})")
        self.setCursor(Qt.PointingHandCursor)

    def _open_link(self):
        QDesktopServices.openUrl(self._link)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if ev.button() == Qt.LeftButton:
            self._open_link()
        else:
            super().mousePressEvent(ev)
# region [Main_Exec]


if __name__ == '__main__':
    x = QApplication()
    w = QMainWindow()
    cont_wid = HyperlinkLabel("https://example.com/", validate=True)

    cent_wid = QWidget()
    cent_wid.setLayout(QVBoxLayout())
    lab = QLabel("blah")

    cent_wid.layout().addWidget(cont_wid)

    w.setCentralWidget(cent_wid)
    url = cont_wid.get_link_as_QUrl()

    w.show()
    x.exec()

# endregion [Main_Exec]
