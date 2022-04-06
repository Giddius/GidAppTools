"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Optional, Union, TYPE_CHECKING, Any
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
import PySide6
from PySide6 import (QtCore, QtGui, QtWidgets, Qt3DAnimation, Qt3DCore, Qt3DExtras, Qt3DInput, Qt3DLogic, Qt3DRender, QtAxContainer, QtBluetooth,
                     QtCharts, QtConcurrent, QtDataVisualization, QtDesigner, QtHelp, QtMultimedia, QtMultimediaWidgets, QtNetwork, QtNetworkAuth,
                     QtOpenGL, QtOpenGLWidgets, QtPositioning, QtPrintSupport, QtQml, QtQuick, QtQuickControls2, QtQuickWidgets, QtRemoteObjects,
                     QtScxml, QtSensors, QtSerialPort, QtSql, QtStateMachine, QtSvg, QtSvgWidgets, QtTest, QtUiTools, QtWebChannel, QtWebEngineCore,
                     QtWebEngineQuick, QtWebEngineWidgets, QtWebSockets, QtXml)

from PySide6.QtCore import (QByteArray, QCoreApplication, QDate, QDateTime, QEvent, QLocale, QMetaObject, QModelIndex, QModelRoleData, QMutex,
                            QMutexLocker, QObject, QPoint, QRect, QRecursiveMutex, QRunnable, QSettings, QSize, QThread, QThreadPool, QTime, QUrl,
                            QWaitCondition, Qt, QAbstractItemModel, QAbstractListModel, QAbstractTableModel, Signal, Slot)

from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QFontMetrics, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform)

from PySide6.QtWidgets import (QApplication, QStyle, QBoxLayout, QCheckBox, QColorDialog, QColumnView, QComboBox, QDateTimeEdit, QDialogButtonBox,
                               QDockWidget, QDoubleSpinBox, QFontComboBox, QFormLayout, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
                               QLCDNumber, QLabel, QLayout, QLineEdit, QListView, QListWidget, QMainWindow, QMenu, QMenuBar, QMessageBox,
                               QProgressBar, QProgressDialog, QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QStackedLayout, QStackedWidget,
                               QStatusBar, QStyledItemDelegate, QSystemTrayIcon, QTabWidget, QTableView, QTextEdit, QTimeEdit, QToolBox, QTreeView,
                               QVBoxLayout, QWidget, QAbstractItemDelegate, QAbstractItemView, QAbstractScrollArea, QRadioButton, QFileDialog, QButtonGroup)
from gidapptools.errors import ApplicationNotExistingError
if TYPE_CHECKING:
    from gidapptools.gidapptools_qt.basics.application import GidQtApplication
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class BaseMenuBar(QMenuBar):
    general_disabled_action_names: frozenset[str] = frozenset()

    def __init__(self, parent: Optional[QWidget] = None, auto_connect_standard_actions: bool = True) -> None:
        super().__init__(parent=parent)
        self.auto_connect_standard_actions = auto_connect_standard_actions
        self.menus: list[QMenu] = []
        self.all_actions: dict[str, QAction] = {}

    def setup(self) -> "BaseMenuBar":
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setup_default_menus()
        self.setup_extra_menus()

        self.handle_temp_disabled()

    def handle_temp_disabled(self) -> None:
        for action_name in self.general_disabled_action_names:
            action = self.all_actions.get(action_name)
            if action is not None:
                action.setEnabled(False)

    def setup_extra_menus(self):
        pass

    def setup_default_menus(self) -> None:
        self.file_menu = self.add_new_menu("File")
        self.exit_action = self.add_new_action(self.file_menu, "Exit")
        self.edit_menu = self.add_new_menu("Edit")

        self.view_menu = self.add_new_menu("View")
        self.windows_menu = self.add_new_menu("Windows", parent_menu=self.view_menu)

        self.settings_menu = self.add_new_menu("Settings")

        self.help_menu = self.add_new_menu("Help")
        self.help_menu.addSeparator()
        self.help_separator = self.help_menu.addSeparator()
        self.add_action(self.help_menu, self.help_separator)
        self.about_action = self.add_new_action(self.help_menu, "About", icon=self.style().standardIcon(QStyle.SP_MessageBoxInformation))
        self.about_action.setMenuRole(QAction.AboutRole)

        self.about_qt_action = self.add_new_action(self.help_menu, "About Qt®", icon=self.style().standardIcon(QStyle.SP_TitleBarMenuButton))
        self.about_qt_action.setMenuRole(QAction.AboutQtRole)
        if self.auto_connect_standard_actions is True:
            self.about_action.triggered.connect(self.app.show_about)
            self.about_qt_action.triggered.connect(self.app.show_about_qt)
            if self.parent() is not None:
                self.exit_action.triggered.connect(self.parent().close)

    @property
    def app(self) -> "GidQtApplication":
        app = QApplication.instance()
        if app is None:
            raise ApplicationNotExistingError()
        return app

    def add_new_menu(self, menu_title: str, icon: QIcon = None, add_before=None, parent_menu: QMenu = None) -> QMenu:
        menu = QMenu(self)
        menu.setEnabled(False)
        menu.setTitle(menu_title)
        if icon is not None:
            menu.setIcon(icon)

        target_menu = parent_menu or self
        if add_before is not None:
            if isinstance(add_before, QMenu):
                add_before = add_before.menuAction()
            target_menu.insertMenu(add_before, menu)
        else:
            target_menu.addMenu(menu)

        target_menu.setEnabled(True)
        return menu

    def add_new_action(self, menu: QMenu, action_name: str, action_title: str = None, icon: Union[QPixmap, QIcon] = None, add_before=None, action_klass: type[QAction] = QAction):
        action_title = action_title or action_name
        action_name = action_name.casefold().replace(' ', '_')
        action = action_klass(parent=menu)
        if icon:
            action.setIcon(icon)

        action.setText(action_title)
        if add_before is not None:
            if isinstance(add_before, QMenu):
                add_before = add_before.menuAction()
            menu.insertAction(add_before, action)
        else:
            menu.addAction(action)

        if not hasattr(menu, action_name + '_action'):
            setattr(menu, action_name + '_action', action)
        menu.setEnabled(True)
        self.all_actions[action_name] = action
        return action

    def add_action(self, menu: QMenu, action: QAction, add_before=None):

        if add_before is not None:
            if isinstance(add_before, QMenu):
                add_before = add_before.menuAction()
            menu.insertAction(add_before, action)
        else:
            menu.addAction(action)

        if not hasattr(menu, action.text() + '_action'):
            setattr(menu, action.text() + '_action', action)
        menu.setEnabled(True)
        return action

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(auto_connect_standard_actions={self.auto_connect_standard_actions!r})"


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
