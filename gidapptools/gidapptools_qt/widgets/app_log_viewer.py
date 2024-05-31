"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import logging.handlers
from typing import Optional, NamedTuple
from pathlib import Path
import logging
import math
import re
# * Third Party Imports --------------------------------------------------------------------------------->
from pyparsing.exceptions import ParseBaseException

# * Qt Imports --------------------------------------------------------------------------------------->
import PySide6
from PySide6 import QtGui, QtWidgets, QtCore
from PySide6.QtGui import QFont, QColor, QPalette, QBrush, QTextCharFormat, QSyntaxHighlighter, QPainter
from PySide6.QtCore import Qt, Slot, Signal, QSize
from PySide6.QtWidgets import QLabel, QWidget, QStyle, QApplication, QStyleOption, QStyleOptionViewItem, QSizePolicy, QGroupBox, QTextEdit, QFormLayout, QStyledItemDelegate, QGridLayout, QPushButton, QTableView, QTableWidget, QTableWidgetItem, QAbstractItemView

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.gid_logger.logger import get_main_logger
from gidapptools.gid_logger.handler import GidStoringHandler
from gidapptools.general_helper.conversion import bytes2human
from gidapptools.general_helper.string_helper import StringCaseConverter, StringCase
from gidapptools.gid_parsing.py_log_parsing import GeneralGrammar

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]


THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion [Constants]


class AppLogHighlighter(QSyntaxHighlighter):
    grammar = GeneralGrammar()
    level_regex = re.compile(r"(?P<level>(DEBUG)|(INFO)|(WARN(ING)?)|(CRITICAL)|(ERROR))")
    line_number_regex = re.compile(r"\| *(?P<line_number>\d+) *\|")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.formats: dict[str, QTextCharFormat] = {}
        self.setup_formats()

    def setup_formats(self):
        self.base_format = QTextCharFormat()

        date_format = QTextCharFormat()
        date_format.setForeground(QColor(0, 0, 0, 255))
        date_format.setTextOutline(QColor(255, 255, 255, 50))
        date_format.setFontWeight(1000)
        self.formats["time_stamp"] = date_format

        line_number_format = QTextCharFormat()
        line_number_format.setForeground(QColor(0, 0, 0, 255))
        line_number_format.setTextOutline(QColor(255, 255, 255, 50))
        line_number_format.setFontWeight(1000)
        self.formats["line_number"] = line_number_format

        level_format = QTextCharFormat()
        level_format.setFontWeight(1000)
        level_format.setFontUnderline(True)
        self.formats["level"] = level_format

        debug_format = QTextCharFormat()
        debug_format.setBackground(QColor(144, 238, 144, 75))
        self.formats["debug"] = debug_format

        info_format = QTextCharFormat()
        info_format.setBackground(QColor(173, 216, 230, 75))
        self.formats["info"] = info_format

        critical_format = QTextCharFormat()
        critical_format.setBackground(QColor(255, 165, 0, 75))
        self.formats["critical"] = critical_format

        error_format = QTextCharFormat()
        error_format.setBackground(QColor(220, 20, 60, 100))
        self.formats["error"] = error_format

        message_format = QTextCharFormat()
        message_format.setFontWeight(1000)
        self.formats["message"] = message_format

        thread_format = QTextCharFormat()
        self.formats["thread"] = thread_format

        module_format = QTextCharFormat()
        self.formats["module"] = module_format

        function_format = QTextCharFormat()
        self.formats["function"] = function_format

    def highlightBlock(self, text: str) -> None:

        # try:
        #     tokens = self.grammar(text)
        #     background_fmt = self.formats[tokens["level"].log_level.casefold()]
        #     self.setFormat(0, len(text), background_fmt)
        #     for name, token in tokens.items():
        #         fmt = self.formats.get(name, self.base_format)
        #         fmt.setBackground(background_fmt.background())
        #         self.setFormat(token.start, token.span, fmt)

        # except ParseBaseException as e:
        # print(f"{e=} | {e.args=}", flush=True)
        if match := self.line_number_regex.search(text):
            self.setFormat(match.start("line_number"), match.end("line_number") - match.start("line_number"), self.formats["line_number"])

        if match := self.level_regex.search(text):
            self.setFormat(0, len(text), self.formats.get(match.group("level").casefold(), self.base_format))

    # def highlightBlock(self, text: str) -> None:
    #     try:
    #         backgrounds = {"debug": QColor(0, 200, 0, 50),
    #                        "info": QColor(0, 0, 255, 50),
    #                        "critical": QColor(255, 200, 0, 50),
    #                        "error": QColor(255, 0, 0, 100)}
    #         if not text.strip():
    #             return
    #         parts = text.split("|")

    #         level_part = parts[2]

    #         start = text.find(level_part)
    #         background = backgrounds.get(level_part.strip().casefold(), QColor(0, 0, 0, 0))
    #         format_item = QTextCharFormat()
    #         format_item.setBackground(background)
    #         self.setFormat(0, text.find("||-->"), format_item)

    #         date_part = parts[0].strip()
    #         start = text.find(date_part)
    #         fmt = self.formats["date"]
    #         fmt.setBackground(background)
    #         self.setFormat(start, len(date_part), fmt)

    #         line_number_part = parts[1].strip()
    #         start = text.find(line_number_part)
    #         fmt = self.formats["line_number"]
    #         fmt.setBackground(background)
    #         self.setFormat(start, len(line_number_part), fmt)

    #         message_start = text.find("||--> ") + 6
    #         self.setFormat(message_start, len(text) - message_start, self.formats["message"])
    #     except IndexError:
    #         pass


class MetaBox(QGroupBox):

    def __init__(self, log_file: Path, parent=None):
        super().__init__(parent=parent)
        self.log_file = log_file
        self.setLayout(QFormLayout())

        self.setTitle("Meta Data")
        self.widgets = {}

        self.setup()

    def _gather_meta_data(self) -> dict[str, str]:
        data = {}
        data["Name"] = self.log_file.name
        data["Path"] = self.log_file.as_posix()
        data["Size"] = bytes2human(self.log_file.stat().st_size)
        data["Lines"] = len(self.log_file.read_text(encoding='utf-8', errors='ignore').splitlines())

        return data

    def setup(self):
        for k, v in self._gather_meta_data().items():
            value_widget = QLabel()
            value_widget.setText(str(v))
            self.layout.addRow(k, value_widget)
            self.widgets[k] = value_widget

    @property
    def layout(self) -> QFormLayout:
        return super().layout()

    def update_size(self):
        size_widget = self.widgets["Size"]
        size_widget.setText(bytes2human(self.log_file.stat().st_size))
        size_widget.repaint()

        line_amount_widget = self.widgets["Lines"]
        line_amount_widget.setText(str(len(self.log_file.read_text(encoding='utf-8', errors='ignore').splitlines())))
        line_amount_widget.repaint()


class FileAppLogViewer(QWidget):

    def __init__(self, log_file: Path, parent=None) -> None:
        super().__init__(parent=parent)
        self.log_file = Path(log_file).resolve()
        self.file_size = None
        self.timer_id = None

    def setup(self) -> "FileAppLogViewer":
        self.setLayout(QGridLayout())
        self.setWindowTitle("Application Log")

        self.setup_widgets()
        self.set_content()
        # self.file_watcher = QFileSystemWatcher(self)
        # self.file_watcher.addPath(str(self.log_file))
        # self.file_watcher.fileChanged.connect(self.set_content)
        # self.file_watcher.fileChanged.connect(self.set_content)
        self.timer_id = self.startTimer(500, Qt.CoarseTimer)
        return self

    def setup_widgets(self):
        self.meta_box = MetaBox(self.log_file)
        self.layout.addWidget(self.meta_box)

        self.text_widget = QTextEdit(self)
        self.text_widget.setReadOnly(True)
        self.text_widget.setLineWrapMode(QTextEdit.NoWrap)
        font: QFont = self.text_widget.font()
        font.setStyleHint(QFont.Monospace)
        font.setFamily("Consolas")
        self.text_widget.setFont(font)

        self.layout.addWidget(self.text_widget)
        self.highlighter = AppLogHighlighter()
        self.highlighter.setDocument(self.text_widget.document())

    def set_content(self):
        self.file_size = self.log_file.stat().st_size
        content = self.log_file.read_text(encoding='utf-8', errors='ignore')
        self.text_widget.setPlainText(content)
        self.resize_to_content()
        self.text_widget.verticalScrollBar().setValue(self.text_widget.verticalScrollBar().maximum())
        self.text_widget.update()
        self.text_widget.repaint()

    def resize_to_content(self):
        height = self.size().height()
        width = min(2000, self.text_widget.document().size().toSize().width())
        self.resize(width, height)

    def check_file(self):
        if self.log_file.stat().st_size != self.file_size:
            self.set_content()
            self.meta_box.update_size()

    def timerEvent(self, event: PySide6.QtCore.QTimerEvent) -> None:
        self.check_file()
        return super().timerEvent(event)

    @property
    def layout(self) -> QGridLayout:
        return super().layout()

    def closeEvent(self, event: PySide6.QtGui.QCloseEvent) -> None:
        if self.timer_id is not None:
            self.killTimer(self.timer_id)
        event.accept()


class StoredAppLogViewer(QWidget):

    def __init__(self, logger: logging.Logger, parent: Optional[PySide6.QtWidgets.QWidget] = None, storage_handler: GidStoringHandler = None) -> None:
        super().__init__(parent)
        self.logger = logger
        self.storage_handler: GidStoringHandler = storage_handler or self._try_find_storage_handler()
        self.last_len = 0
        self.timer_id = None

    def _try_find_storage_handler(self) -> logging.Handler:
        logger = self.logger

        while len(logger.handlers) <= 0:
            logger = logging.getLogger(logger.name.rsplit(".", 1)[0])

        all_handlers = list(logger.handlers)

        for _handler in tuple(all_handlers):
            if isinstance(_handler, logging.handlers.QueueHandler):
                for qued_listener in _handler.listener:
                    for qued_handler in qued_listener.handlers:
                        all_handlers.append(qued_handler)

        for handler in tuple(all_handlers):
            if isinstance(handler, GidStoringHandler):
                return handler

        raise ValueError("no storing handler found.")

    def setup(self) -> "StoredAppLogViewer":
        self.setLayout(QGridLayout())
        self.setWindowTitle("Application Log")

        self.setup_widgets()
        self.gather_content()

        self.timer_id = self.startTimer(int(0.5 * 1000), Qt.CoarseTimer)

        return self

    def setup_widgets(self):
        self.text_widget = QTextEdit(self)
        self.text_widget.setReadOnly(True)
        self.text_widget.setLineWrapMode(QTextEdit.NoWrap)
        font: QFont = self.text_widget.font()
        font.setStyleHint(QFont.Monospace)
        font.setFamily("Consolas")
        font.setPointSizeF(font.pointSizeF() * 1.25)
        self.text_widget.setFont(font)
        self.highlighter = AppLogHighlighter()
        self.highlighter.setDocument(self.text_widget.document())
        self.layout.addWidget(self.text_widget)

        self.clear_button = QPushButton("Clear")
        self.clear_button.pressed.connect(self.on_clear_pressed)
        self.layout.addWidget(self.clear_button)
        self.clear_button = QPushButton("Clear")
        self.clear_button.pressed.connect(self.on_clear_pressed)
        self.layout.addWidget(self.clear_button)

    @Slot()
    def on_clear_pressed(self, checked: bool = False):
        self.storage_handler.clear()
        self.gather_content()

    @property
    def layout(self) -> QGridLayout:
        return super().layout()

    def gather_content(self):
        if len(self.storage_handler) != self.last_len:
            all_messages = []
            for message_tuple in self.storage_handler.get_stored_messages().values():
                for raw_message in message_tuple:
                    all_messages.append(raw_message)
            all_messages = sorted(all_messages, key=lambda x: (x.created, x.msecs))
            text = ""
            for msg in all_messages:
                text += self.storage_handler.format(msg) + '\n'
            h_scroll_value = self.text_widget.horizontalScrollBar().value()
            self.text_widget.setPlainText(text)
            self.text_widget.verticalScrollBar().setValue(self.text_widget.verticalScrollBar().maximum())
            self.text_widget.horizontalScrollBar().setValue(h_scroll_value)

            self.last_len = len(self.storage_handler)

    def timerEvent(self, event: PySide6.QtCore.QTimerEvent) -> None:
        self.gather_content()
        return super().timerEvent(event)

    def closeEvent(self, event: PySide6.QtGui.QCloseEvent) -> None:
        if self.timer_id is not None:
            self.killTimer(self.timer_id)
        event.accept()


class HighlightDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = QtGui.QTextDocument(self.parent())
        self._highlight_data: list[tuple[QtCore.QRegularExpression, QtGui.QTextCharFormat]] = []

    def paint(self, painter, option, index):
        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        self.doc.setDefaultFont(options.font)
        self.doc.setPlainText(options.text)

        palette: QPalette = options.palette

        bkgrnd_color = index.data(Qt.ItemDataRole.BackgroundRole)
        if bkgrnd_color:

            palette.setColor(QPalette.ColorRole.Base, bkgrnd_color.color())

        foreground_color = index.data(Qt.ItemDataRole.ForegroundRole)
        if foreground_color:
            palette.setColor(QPalette.ColorRole.Text, foreground_color.color())

        self.apply_highlight()
        options.text = ""
        style = QtWidgets.QApplication.style() if options.widget is None else options.widget.style()
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, options, painter)

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
        if option.state & QtWidgets.QStyle.State_Selected:
            ctx.palette.setColor(QtGui.QPalette.Text, option.palette.color(
                QtGui.QPalette.Active, QtGui.QPalette.HighlightedText))
        else:
            ctx.palette.setColor(QtGui.QPalette.Text, option.palette.color(
                QtGui.QPalette.Active, QtGui.QPalette.Text))

        textRect = style.subElementRect(
            QtWidgets.QStyle.SE_ItemViewItemText, options)

        if index.column() != 0:
            textRect.adjust(5, 0, 0, 0)

        the_constant = 4
        margin = (option.rect.height() - options.fontMetrics.height()) // 2
        margin = margin - the_constant
        textRect.setTop(textRect.top() + margin)

        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        self.doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def apply_highlight(self):
        for regex, fmt in self._highlight_data:
            cursor = QtGui.QTextCursor(self.doc)
            cursor.beginEditBlock()
            highlightCursor = QtGui.QTextCursor(self.doc)
            while not highlightCursor.isNull() and not highlightCursor.atEnd():
                highlightCursor = self.doc.find(regex, highlightCursor)
                if not highlightCursor.isNull():
                    highlightCursor.mergeCharFormat(fmt)
            cursor.endEditBlock()

    def add_format_item(self, regex: QtCore.QRegularExpression, fmt: QtGui.QTextFormat) -> None:
        self._highlight_data.append((regex, fmt))

    def copy(self, parent=None) -> "HighlightDelegate":
        new_highlight_delegate = self.__class__(parent)

        new_highlight_delegate._highlight_data = list(self._highlight_data)

        return new_highlight_delegate


class ColumnDataItem:

    __slots__ = ("_attr_name",
                 "_display_name",
                 "_alignment",
                 "_delegate")

    def __init__(self,
                 attr_name: str,
                 display_name: str | None = None,
                 alignment: Qt.AlignmentFlag = None,
                 delegate: QStyledItemDelegate | None = None) -> None:
        self._attr_name = attr_name
        self._display_name = display_name if display_name is not None else self._get_auto_display_name()
        self._alignment = alignment
        self._delegate = delegate

    @property
    def attr_name(self) -> str:
        return self._attr_name

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def alignment(self) -> Qt.AlignmentFlag | None:
        return self._alignment

    @property
    def delegate(self) -> QStyledItemDelegate | None:
        return self._delegate

    def _get_auto_display_name(self) -> str:
        return StringCaseConverter.convert_to(self.attr_name, StringCase.TITLE)


def get_date_style_delegate(parent=None):
    highlight_delegate = HighlightDelegate(parent)

    date_regex = QtCore.QRegularExpression(r"\d+\-\d+\-\d+")

    date_fmt = QtGui.QTextCharFormat()

    date_fmt.setForeground(QApplication.palette().dark())
    date_fmt.setFontWeight(500)

    highlight_delegate.add_format_item(date_regex, date_fmt)

    time_regex = QtCore.QRegularExpression(r"\d+\:\d+\:\d+\.\d*")

    time_fmt = QtGui.QTextCharFormat()
    QApplication.style
    time_fmt.setForeground(QApplication.palette().placeholderText())

    time_fmt.setFontUnderline(True)

    highlight_delegate.add_format_item(time_regex, time_fmt)

    return highlight_delegate


# _DATE_STYLE_DELEGATE = get_date_style_delegate()


def get_message_style_delegate(parent=None):
    highlight_delegate = HighlightDelegate(parent)

    string_regex = QtCore.QRegularExpression(r"(?P<quotes>\'|\").*?(?P=quotes)")

    string_fmt = QtGui.QTextCharFormat()

    string_fmt.setForeground(QApplication.palette().link())

    string_fmt.setFontItalic(True)

    highlight_delegate.add_format_item(string_regex, string_fmt)

    return highlight_delegate


class StoredAppLogTableViewer(StoredAppLogViewer):

    def __init__(self,
                 logger: logging.Logger,
                 parent=None,
                 storage_handler: GidStoringHandler = None) -> None:
        super().__init__(parent=parent, logger=logger, storage_handler=storage_handler)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)

        self.error_background_color = QColor(Qt.GlobalColor.red)
        self.error_background_color.setAlpha(50)

        self.critical_background_color = QColor.fromRgb(255, 165, 0)
        self.critical_background_color.setAlpha(50)

        self.warning_background_color = QColor(Qt.GlobalColor.blue)
        self.warning_background_color.setAlpha(50)

        self.debug_background_color = QColor(Qt.GlobalColor.gray)
        self.debug_background_color.setAlpha(50)

        self.debug_foreground_color = QColor(Qt.GlobalColor.darkGray)

    def _get_color_map(self):
        return {"background": {"error": ...,
                               "critical": ...,
                               "warning": ...,
                               "info": ...,
                               "debug": ...},
                "foregorund": {"error": ...}}

    def setup_widgets(self):
        self.table_widget = QTableWidget(self)

        self.column_data = (ColumnDataItem(attr_name="asctime"),
                            ColumnDataItem(attr_name="levelname", display_name="Level Name", alignment=Qt.AlignmentFlag.AlignCenter),
                            ColumnDataItem(attr_name="name", alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                            ColumnDataItem(attr_name="lineno", display_name="Line Number", alignment=Qt.AlignmentFlag.AlignCenter),
                            ColumnDataItem(attr_name="funcName", alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                            ColumnDataItem(attr_name="message", alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))

        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setColumnCount(len(self.column_data))
        self.table_widget.setHorizontalHeaderLabels([item.display_name for item in self.column_data])
        self.table_widget.horizontalHeader().setMinimumSectionSize(100)
        self.table_widget.verticalHeader().setMinimumSectionSize(25)
        self.table_widget.setWordWrap(False)
        self.table_widget.setTextElideMode(Qt.TextElideMode.ElideNone)
        for column, column_data in enumerate(self.column_data):
            if column_data.delegate is not None:
                column_data.delegate.setParent(self.table_widget)
                self.table_widget.setItemDelegateForColumn(column, column_data.delegate)

        font: QFont = self.table_widget.font()
        font.setStyleHint(QFont.Monospace)
        font.setFamily("Consolas")
        font.setPointSizeF(font.pointSizeF() * 1.25)
        self.table_widget.setFont(font)

        self.layout.addWidget(self.table_widget)

        self.clear_button = QPushButton("Clear")
        self.clear_button.pressed.connect(self.on_clear_pressed)
        self.layout.addWidget(self.clear_button)

    def gather_content(self):
        if len(self.storage_handler) != self.table_widget.rowCount():
            self.table_widget.clearContents()

            all_messages = list(self.storage_handler.get_all_messages(formatted=True))

            h_scroll_value = self.table_widget.horizontalScrollBar().value()

            self.table_widget.setRowCount(len(all_messages))

            for row, msg in enumerate(all_messages):

                for column, column_data in enumerate(self.column_data):
                    if column_data.attr_name == "asctime":
                        item = QTableWidgetItem(self.storage_handler.formatter.formatTime(msg))

                    elif column_data.attr_name == "message":
                        item = QTableWidgetItem(msg.message + (f"\n{msg.exc_text}" if msg.exc_text else ""))
                    else:
                        value = getattr(msg, column_data.attr_name)

                        text = "" if value is None else str(value)

                        item = QTableWidgetItem(text)

                    if column_data.alignment is not None:
                        item.setTextAlignment(column_data.alignment)

                    _pathname = Path(msg.pathname).resolve()
                    if msg.exc_text:
                        item.setToolTip(f"{_pathname.as_posix()!r}\n\n{msg.exc_text}")

                    else:
                        item.setToolTip(f"{_pathname.as_posix()!r}")

                    match msg.levelname.casefold():
                        case "error":

                            item.setBackground(self.error_background_color)

                        case "critical":

                            item.setBackground(self.critical_background_color)

                        case "warning" | "warn":

                            item.setBackground(self.warning_background_color)

                        case "debug":

                            item.setBackground(self.debug_background_color)

                            item.setForeground(self.debug_foreground_color)

                        case "info":
                            pass

                    self.table_widget.setItem(row, column, item)
                if msg.exc_text:
                    self.table_widget.resizeRowToContents(row)
                    # self.table_widget.setRowHeight(row, self.table_widget.fontMetrics().h)

            self.table_widget.verticalScrollBar().setValue(self.table_widget.verticalScrollBar().maximum())
            self.table_widget.horizontalScrollBar().setValue(h_scroll_value)

            self.last_len = self.table_widget.rowCount()

            if self.table_widget.rowCount() > 0:
                self.table_widget.resizeColumnsToContents()
                self.table_widget.resizeRowsToContents()


# region [Main_Exec]
if __name__ == '__main__':
    pass

# endregion [Main_Exec]
