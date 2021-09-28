"""
WiP.

Soon.
"""

# region [Imports]


from abc import ABCMeta
from pathlib import Path
from typing import Any

import pyparsing as pp
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

    def __str__(self) -> str:
        return self.content


class Section(IniToken):

    def __init__(self, name: str) -> None:
        self.name = name
        self.comments = []
        self.entries = {}

    def add_entry(self, entry: "Entry") -> None:
        self.entries[entry.key] = entry

    def get(self, key, default=None) -> Any:
        try:
            return self.entries[key].get_value()
        except KeyError:
            return default

    def as_dict(self) -> dict[str, dict[str, str]]:
        data = {self.name: {}}
        for entry in self.entries.values():
            data[self.name] |= entry.as_dict()
        return data


class Entry(IniToken):

    def __init__(self, key: str, value: str) -> None:
        self.key = key.strip()
        self.value = value.lstrip()
        self.comments = []

    def get_value(self) -> Any:
        return self.value

    def as_dict(self) -> dict[str, str]:
        return {self.key: self.value}


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
