"""
WiP.

Soon.
"""

# region [Imports]


from abc import ABCMeta
from pathlib import Path
from typing import Any

import pyparsing as pp
from pprint import pprint
import pyparsing.common as ppc
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.gid_config.enums import SpecialTypus
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class Token:

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(" + ', '.join(f"{k}={v!r}" for k, v in vars(self).items()) + ')'


class IniToken(Token, metaclass=ABCMeta):
    spec_data = None

    def add_comment(self, comment: "Comment") -> None:
        self.comments.append(comment.content)


class Comment(Token):
    def __init__(self, content: str) -> None:
        self.content = content.strip()
        self.comment_indicator: str = '#'

    def __str__(self) -> str:
        return self.content

    def as_text(self, **kwargs) -> str:
        return f"{self.comment_indicator} {self}"


class Section(IniToken):

    def __init__(self, name: str) -> None:
        self.name = name
        self.comments = []
        self.entries = {}

    def add_entry(self, entry: "Entry") -> None:
        self.entries[entry.key] = entry

    def __getitem__(self, key: str) -> "Entry":
        return self.entries[key]

    def get(self, key, default=None) -> Any:
        try:
            return self[key].get_value()
        except KeyError:
            return default

    def __len__(self) -> int:
        return len(self.entries)

    def as_dict(self) -> dict[str, dict[str, str]]:
        data = {self.name: {}}
        for entry in self.entries.values():
            data[self.name] |= entry.as_dict()
        return data

    def as_text(self, **kwargs) -> str:
        lines = []
        lines += [comment.as_text(**kwargs) for comment in self.comments]
        lines.append(f"[{self.name}]")
        lines += ['' for i in range(kwargs.get("section_header_newlines", 1))]
        lines += [entry.as_text(**kwargs) for entry in self.entries.values()]
        lines += ['' for i in range(kwargs.get("extra_section_newlines", 2))]
        return '\n'.join(lines)


class Entry(IniToken):

    def __init__(self, key: str, value: str) -> None:
        self.key = key.strip()
        self.value = value.lstrip()
        self.key_value_separator = '='
        self.comments = []

    def get_value(self) -> Any:
        return self.value

    def as_dict(self) -> dict[str, str]:
        return {self.key: self.value}

    def as_text(self, **kwargs) -> str:
        lines = [comment.as_text() for comment in self.comments]
        lines.append(f"{self.key} {self.key_value_separator} {self.get_value()}")
        lines += ['' for i in range(kwargs.get("extra_entry_newlines", 0))]
        return '\n'.join(lines)


class TokenFactory:

    def __init__(self, token_map: dict[str, type] = None) -> None:
        self.token_map = {'comment': Comment,
                          'section_name': Section,
                          'entry': Entry}
        if token_map is not None:
            self.token_map |= token_map

    def parse_action(self, tokens: pp.ParseResults) -> Token:
        name = tokens.get_name()
        token_class = self.token_map[name]
        return token_class(*tokens)

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
