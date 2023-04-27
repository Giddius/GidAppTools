"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from enum import Enum, auto
from typing import TYPE_CHECKING, Union, Optional
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6 import QtGui
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import QFrame, QLabel, QWidget, QGroupBox, QGridLayout, QHBoxLayout, QSizePolicy, QVBoxLayout, QStackedWidget, QDialogButtonBox

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.string_helper import StringCase, StringCaseConverter

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


class SelectorPosition(Enum):
    TOP = auto()
    Bottom = auto()
    LEFT = auto()
    RIGHT = auto()


class CategoryPicture(QFrame):
    clicked = Signal(int)

    def __init__(self, text: str, picture: Optional[QPixmap], category_page_number: int, parent=None) -> None:
        super().__init__(parent=parent)
        self.raw_text = text
        self.raw_picture = picture
        self.text: QLabel = None
        self.picture: QLabel = None
        self.category_page_number = category_page_number
        self.base_style = QFrame.Raised | QFrame.Panel

    def setup(self) -> "CategoryPicture":
        self.setLayout(QVBoxLayout(self))
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setContentsMargins(0, 0, 0, 1)
        self.setFrameStyle(self.base_style)
        self.setMidLineWidth(3)
        self.setLineWidth(3)

        self.setup_text()
        self.setup_picture()
        return self

    def setup_text(self):
        self.setToolTip(self.raw_text)
        self.text = QLabel(text=self.raw_text, parent=self)
        self.text.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.text.setTextFormat(Qt.AutoText)

        self.layout.addWidget(self.text)

    def setup_picture(self):
        self.picture = QLabel(self)
        if self.raw_picture:
            picture = self.raw_picture.scaled(60, 60, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.picture.setPixmap(picture)
        self.picture.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.picture)

    def sizeHint(self) -> QSize:
        width = self.text.sizeHint().width() + self.picture.sizeHint().width()
        height = self.text.sizeHint().height() + self.picture.sizeHint().height()
        return QSize(w=width, h=height)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.setFrameStyle(QFrame.Sunken | QFrame.Panel)


    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.setFrameStyle(self.base_style)
        self.clicked.emit(self.category_page_number)

    @property
    def layout(self) -> QVBoxLayout:
        return super().layout()

    def __repr__(self) -> str:
        """
        Basic Repr
        !REPLACE!
        """
        return f'{self.__class__.__name__}'


class PictureCategorySelector(QGroupBox):

    def __init__(self, content_widget: QStackedWidget, parent: QStackedWidget = None, position: SelectorPosition = SelectorPosition.LEFT):
        super().__init__(parent=parent)
        self.position = position
        self.content_widget = content_widget
        self._set_layout()
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.layout.setAlignment(Qt.AlignCenter)
        self.setFlat(True)
        # self.setTitle("Categories")
        self.categories: dict[str, CategoryPicture] = {}

    def _set_layout(self):
        if self.position in {SelectorPosition.TOP, SelectorPosition.Bottom}:
            layout_class = QHBoxLayout
        elif self.position in {SelectorPosition.LEFT, SelectorPosition.RIGHT}:
            layout_class = QVBoxLayout

        self.setLayout(layout_class(self))

    @property
    def layout(self) -> Union[QHBoxLayout, QVBoxLayout]:
        return super().layout()

    def add_category(self, name: str, picture: Optional[QPixmap], category_page_number: int, verbose_name: str = None):
        verbose_name = verbose_name or StringCaseConverter.convert_to(name, StringCase.SPLIT, clean_in_string=True).title()

        category = CategoryPicture(verbose_name, picture, category_page_number, self).setup()

        self.layout.addWidget(category)
        self.categories[name] = category

        category.clicked.connect(self.content_widget.setCurrentIndex)
        self.resize_categories()

    def sizeHint(self) -> QSize:
        width = max(c.sizeHint().width() for c in self.categories.values())
        height = sum(c.height() for c in self.categories.values())
        return QSize(w=width, h=int(height * 1.25))

    def resize_categories(self):
        widths = []
        heights = []
        for category in self.categories.values():
            widths.append(category.sizeHint().width())
            heights.append(category.height())

        max_width = max(widths)
        max_heights = max(heights)
        for category in self.categories.values():
            category.resize(max_width, max_heights)
        self.repaint()

    def __repr__(self) -> str:
        """
        Basic Repr
        !REPLACE!
        """
        return f'{self.__class__.__name__}'


class ContentStackedwidget(QStackedWidget):

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)
        self.pages: dict[str, QWidget] = {}
        self.setFrameShape(QFrame.WinPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(2)
        self.setMidLineWidth(2)

    def addWidget(self, w: QWidget, name: str = None) -> int:
        name = name or w.category_name
        self.pages[name] = w
        return super().addWidget(w)

    def __repr__(self) -> str:
        """
        Basic Repr
        !REPLACE!
        """
        return f'{self.__class__.__name__}'


class CategorySelectWidget(QWidget):
    _available_selector_positions = {SelectorPosition.TOP, SelectorPosition.LEFT}

    def __init__(self, selector_position: SelectorPosition = SelectorPosition.LEFT, parent=None) -> None:
        super().__init__(parent=parent, f=Qt.Dialog)
        self.selector_position = selector_position
        if self.selector_position not in self._available_selector_positions:
            raise ValueError(f"Selector Posiotion {self.selector_position!r} is not available, only {', '.join(repr(i) for i in self._available_selector_positions)}")
        self.main_layout: QGridLayout = None
        self.buttons: QDialogButtonBox = None
        self.selection_box: PictureCategorySelector = None
        self.content_widget: ContentStackedwidget = None

    def setup(self) -> "CategorySelectWidget":

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        self.setup_buttons()
        self.setup_content_widget()
        self.setup_selection_box()
        return self

    def setup_buttons(self) -> None:
        self.buttons = QDialogButtonBox(self)
        self.buttons.setOrientation(Qt.Horizontal)
        self.buttons.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        if self.selector_position is SelectorPosition.TOP:
            self.main_layout.addWidget(self.buttons, 2, 0, 1, 1, Qt.AlignBottom)
        elif self.selector_position is SelectorPosition.LEFT:
            self.main_layout.addWidget(self.buttons, 1, 1, 1, 1, Qt.AlignBottom)
        self.buttons.rejected.connect(self.on_cancelled)
        self.buttons.accepted.connect(self.on_accepted)

    def setup_content_widget(self) -> None:
        self.content_widget = ContentStackedwidget(self)
        if self.selector_position is SelectorPosition.TOP:
            self.main_layout.addWidget(self.content_widget, 1, 0, 1, 1)
        elif self.selector_position is SelectorPosition.LEFT:
            self.main_layout.addWidget(self.content_widget, 0, 1, 1, 1)

    def setup_selection_box(self) -> None:
        self.selection_box = PictureCategorySelector(self.content_widget, position=self.selector_position)
        if self.selector_position is SelectorPosition.TOP:
            self.main_layout.addWidget(self.selection_box, 0, 0, 1, 1, Qt.AlignTop)
        elif self.selector_position is SelectorPosition.LEFT:
            self.main_layout.addWidget(self.selection_box, 0, 0, 1, 1, Qt.AlignLeft | Qt.AlignTop)

    def add_category(self, content_widget: QWidget):
        try:
            name = content_widget.name
        except AttributeError:
            name = content_widget.objectName()
            if not name:
                name = str(content_widget)

        try:
            picture = content_widget.category_picture
        except AttributeError:
            picture = None
        page_number = self.content_widget.addWidget(content_widget, name=name)
        self.selection_box.add_category(name, picture, page_number)

    def change_page(self, current_item, previous_item):
        self.content_widget.setCurrentIndex(current_item.page_number)

    def on_cancelled(self):
        self.close()

    def on_accepted(self):
        self.close()

    def __repr__(self) -> str:
        """
        Basic Repr
        !REPLACE!
        """
        return f'{self.__class__.__name__}'

# region [Main_Exec]


if __name__ == '__main__':
    # app = QApplication()

    # select_widget = CategorySelectWidget(selector_position=SelectorPosition.LEFT).setup()
    # content = QTextEdit()
    # content.name = "first"
    # content.category_picture = QPixmap(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\docs\source\_images\broca_progs_logo.png")
    # content.setText("osdfolijsdolpfjlsdfjlksdjflksdjfljsd psdjfpöosdjfpdsfj \n\n sdfosidfjlpsdjfoljsdflsdf")
    # content2 = QDoubleSpinBox()
    # content2.name = "second"

    # content2.category_picture = QPixmap(r"D:\Dropbox\hobby\Modding\Ressources\Icons\To_Sort_Icons\png_icons\document(1).png")
    # select_widget.add_category(content_widget=content)
    # select_widget.add_category(content_widget=content2)
    # select_widget.show()
    # app.exec()
    pass

# endregion [Main_Exec]
