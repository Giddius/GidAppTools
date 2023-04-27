from ._checks import check_has_data_set_methods, check_is_widget

from .standard_types import DefaultValueWidget, TextValueWidget, NumberValueWidget

from PySide6.QtWidgets import QWidget


DEFAULT_VALUE_WIDGET = DefaultValueWidget


WIDGET_MAP: dict[type:QWidget] = {}


def determine_value_widget(value: object) -> QWidget:

    return WIDGET_MAP.get(value.__class__, DEFAULT_VALUE_WIDGET)


for widget in (DefaultValueWidget, TextValueWidget, NumberValueWidget):
    widget.determine_value_widget_func = determine_value_widget
    assert check_is_widget(widget) is True
    assert check_has_data_set_methods(widget) is True
    for typus in widget.value_types:
        WIDGET_MAP[typus] = widget
