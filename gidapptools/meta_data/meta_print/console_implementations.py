"""
WiP.

Soon.
"""

# region [Imports]


from pathlib import Path
from typing import Any, Union
from collections import deque
from collections import deque

from rich.console import Console as RichConsole, HighlighterType, RichCast, ConsoleRenderable
from rich.align import AlignMethod
from rich.text import TextType
from rich.rule import Rule
from rich.theme import Theme
from rich.style import StyleType, Style
from rich.emoji import EmojiVariant
from rich._log_render import FormatTimeCallable
import attr
from attr.converters import default_if_none
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

NEW_DEFAULT_CONSOLE_KWARGS = {'soft_wrap': True}


@ attr.s(auto_attribs=True, auto_detect=True)
class ExtraConsoleConfiguration:
    use_output_numbering: bool = attr.ib(converter=default_if_none(False))
    use_rule_seperator: bool = attr.ib(converter=default_if_none(False))
    use_extra_newline_pre: bool = attr.ib(converter=default_if_none(False))
    use_extra_newline_post: bool = attr.ib(converter=default_if_none(False))
    use_prefix: bool = attr.ib(converter=default_if_none(False))

    output_numbering_template: str = attr.ib(converter=default_if_none("Output No. {number}"))
    rule_seperator_char: str = attr.ib(converter=default_if_none('-'))
    prefix: str = attr.ib(converter=default_if_none('-->'))
    multiline_indent: int = attr.ib(converter=default_if_none(0))

    @property
    def actual_mutlitline_indent(self) -> int:
        return len(self.prefix) + 2 + self.multiline_indent

    @classmethod
    def from_console_kwargs(cls, console_kwargs: dict[str, Any]) -> tuple["ExtraConsoleConfiguration", dict[str, Any]]:
        extra_kwargs = {}
        for field in attr.fields(cls):
            extra_kwargs[field.name] = console_kwargs.pop(field.name, None)
        return cls(**extra_kwargs), console_kwargs

    def as_dict(self) -> dict[str, Any]:
        return attr.asdict(self)


class GidPrintFormater:
    output_number: int = 0

    def __init__(self, extra_config: ExtraConsoleConfiguration) -> None:
        self.extra_config = extra_config

    def increment_output_number(self):
        self.output_number += 1

    def _handle_multiline_item(self, text_part: Union[str, Rule]) -> Union[str, Rule]:
        if not isinstance(text_part, str):
            return text_part
        if '\n' not in text_part:
            return text_part
        _indent = ' ' * self.extra_config.actual_mutlitline_indent
        return _indent.join(sub_part for sub_part in text_part.splitlines(keepends=True))

    def format(self, *print_args) -> str:
        self.increment_output_number()

        text_parts = deque(print_args)

        if self.extra_config.use_prefix is True:
            text_parts = deque(self._handle_multiline_item(part) for part in text_parts)

            text_parts.appendleft(self.extra_config.prefix)

        if self.extra_config.use_extra_newline_pre is True:
            text_parts.appendleft('\n')
        if self.extra_config.use_extra_newline_post is True:
            text_parts.append('\n')

        title = ''
        if self.extra_config.use_output_numbering is True:
            title = self.extra_config.output_numbering_template.format(number=self.output_number)

        if self.extra_config.use_rule_seperator is True:
            rule = Rule(title=title, characters=self.extra_config.rule_seperator_char)
            text_parts.appendleft(rule)

        elif title != '':
            text_parts.appendleft('\n')
            text_parts.appendleft(title)

        return text_parts


class GidRichConsole(RichConsole):
    output_number: int = 0

    def __init__(self, **console_kwargs):
        console_kwargs = NEW_DEFAULT_CONSOLE_KWARGS | console_kwargs
        self.extra_config, console_kwargs = ExtraConsoleConfiguration.from_console_kwargs(console_kwargs)
        self.formatter = GidPrintFormater(self.extra_config)
        self.console_kwargs = console_kwargs

        super().__init__(**self.console_kwargs)

    def print(self, *args, **kwargs) -> None:
        text_parts = self.formatter.format(*args)
        super().print(*text_parts, **kwargs)

# region[Main_Exec]


if __name__ == '__main__':
    pass
# endregion[Main_Exec]
