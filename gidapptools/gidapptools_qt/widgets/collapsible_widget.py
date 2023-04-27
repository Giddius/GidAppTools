"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import TYPE_CHECKING
from pathlib import Path
from enum import Enum, auto
# * Qt Imports --------------------------------------------------------------------------------------->
import PySide6
from PySide6.QtCore import Qt, QEvent, QSize
from PySide6.QtWidgets import QWidget, QGroupBox, QGridLayout, QSizePolicy

from PySide6 import (QtCore, QtGui, QtWidgets, Qt3DAnimation, Qt3DCore, Qt3DExtras, Qt3DInput, Qt3DLogic, Qt3DRender, QtAxContainer, QtBluetooth,
                     QtCharts, QtConcurrent, QtDataVisualization, QtDesigner, QtHelp, QtMultimedia, QtMultimediaWidgets, QtNetwork, QtNetworkAuth,
                     QtOpenGL, QtOpenGLWidgets, QtPositioning, QtPrintSupport, QtQml, QtQuick, QtQuickControls2, QtQuickWidgets, QtRemoteObjects,
                     QtScxml, QtSensors, QtSerialPort, QtSql, QtStateMachine, QtSvg, QtSvgWidgets, QtTest, QtUiTools, QtWebChannel, QtWebEngineCore,
                     QtWebEngineQuick, QtWebEngineWidgets, QtWebSockets, QtXml)

from PySide6.QtCore import (QByteArray, QCoreApplication, QDate, QDateTime, QEvent, QLocale, QMetaObject, QModelIndex, QModelRoleData, QMutex,
                            QMutexLocker, QObject, QPoint, QRect, QRecursiveMutex, QRunnable, QSettings, QSize, QThread, QThreadPool, QTime, QUrl,
                            QWaitCondition, Qt, QAbstractItemModel, QAbstractListModel, QAbstractTableModel, Signal, Slot, QMargins)

from PySide6.QtGui import (QAction, QBrush, QColor, QPaintEvent, QConicalGradient, QCursor, QFont, QFontDatabase, QFontMetrics, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform)

from PySide6.QtWidgets import (QApplication, QBoxLayout, QCheckBox, QColorDialog, QColumnView, QComboBox, QDateTimeEdit, QDialogButtonBox,
                               QDockWidget, QDoubleSpinBox, QFontComboBox, QFormLayout, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
                               QLCDNumber, QLabel, QLayout, QLineEdit, QListView, QListWidget, QMainWindow, QMenu, QMenuBar, QMessageBox,
                               QProgressBar, QProgressDialog, QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QStackedLayout, QStackedWidget,
                               QStatusBar, QStyledItemDelegate, QSystemTrayIcon, QTabWidget, QTableView, QTextEdit, QTimeEdit, QToolBox, QTreeView,
                               QVBoxLayout, QWidget, QAbstractItemDelegate, QAbstractItemView, QAbstractScrollArea, QRadioButton, QFileDialog, QButtonGroup, QWidgetItem, QLayoutItem)

# * Gid Imports ----------------------------------------------------------------------------------------->


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


class EmptyPlaceholderWidget(QWidget):

    @property
    def has_content(self) -> bool:
        return False


class CollapsibleGroupBox(QGroupBox):
    _expand_prefix = "▼"
    _collapse_prefix = "▲"
    _expand_text = "show"
    _collapse_text = "hide"
    _no_content_text = ""
    _no_content_prefix = ""

    def __init__(self,
                 text: str = None,
                 content: QWidget = None,
                 start_expanded: bool = True,
                 parent=None):
        super().__init__(parent=parent)
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        self.setLayout(QGridLayout())
        self.layout.setAlignment(Qt.AlignCenter)
        self.setFlat(True)
        self.setAlignment(Qt.AlignCenter)
        self.no_content_prefix = str(self._no_content_prefix)
        self.no_content_text = str(self._no_content_text)
        self.expand_prefix = str(self._expand_prefix)
        self.collapse_prefix = str(self._collapse_prefix)
        self.expand_text = str(self._expand_text)
        self.collapse_text = str(self._collapse_text)
        self.text = text
        self.content = content or EmptyPlaceholderWidget()
        self.layout.addWidget(self.content)
        self.expanded = True
        self.setTitle(self.full_text)
        self.original_cursor = self.cursor()
        self.current_cursor = self.cursor()
        if start_expanded is False:
            self.set_expanded(False)

    @property
    def has_content(self) -> bool:
        return getattr(self.content, "has_content", self.content is not None)

    @property
    def full_text(self) -> str:

        if self.has_content is False:
            text = self.no_content_text
            prefix = self.no_content_prefix

        elif self.expanded is True:
            text = self.text or self.collapse_text
            prefix = self.collapse_prefix + " "

        else:
            text = self.text or self.expand_prefix
            prefix = self.expand_prefix + " "
        return f"{prefix}{text}"

    @ property
    def layout(self) -> QGridLayout:
        return super().layout()

    def mousePressEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        if not self.contentsRect().contains(event.position().toPoint()):
            self.on_title_clicked()

    def event(self, event: PySide6.QtCore.QEvent) -> bool:
        if event.type() == QEvent.HoverMove:
            if self.has_content is True and not self.contentsRect().contains(event.position().toPoint()) and self.current_cursor is not Qt.PointingHandCursor:
                self.setCursor(Qt.PointingHandCursor)
            elif self.contentsRect().contains(event.position().toPoint()) and self.current_cursor is not self.original_cursor:
                self.setCursor(self.original_cursor)

        return super().event(event)

    def leaveEvent(self, event: PySide6.QtCore.QEvent) -> None:
        self.setCursor(self.original_cursor)
        return super().leaveEvent(event)

    def on_title_clicked(self):
        if self.has_content:
            self.set_expanded(not self.expanded)

    def set_expanded(self, value: bool):
        self.expanded = value
        self.content.setVisible(value)
        self.setTitle(self.full_text)

    def set_content(self, content: QWidget) -> None:
        if self.has_content is True:
            self.layout.removeWidget(self.content)
        self.content = content
        self.layout.addWidget(self.content)
        self.setTitle(self.full_text)

        if self.has_content is False and self.expanded is True:
            self.set_expanded(False)


# region [Main_Exec]

if __name__ == '__main__':
    from gidapptools.gidapptools_qt.helper.misc import batch_modify_widget
    x = QApplication()
    w = QMainWindow()
    cont_wid = QTextEdit()
    batch_modify_widget(cont_wid, setFontItalic=True, setFontPointSize=(10.5,), paste=...)
    # cont_wid.setText("sadfsdfgsfsedfsefdsdfsdf\nasdfasdasdasdasda\nsadfsdfsdfsdfsdf")
    wid = CollapsibleGroupBox(text="wuff", content=cont_wid)
    w.setCentralWidget(wid)
    w.show()
    x.exec()

# endregion [Main_Exec]
