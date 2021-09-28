"""
WiP.

Soon.
"""

# region [Imports]


import re


from pprint import pprint
from pathlib import Path

import pyparsing as pp
import pyparsing.common as ppc
from gidapptools.gid_config.parser.tokens import Section, Entry, Comment, TokenFactory, Token
from gidapptools.gid_config.parser.grammar import BaseIniGrammar
from gidapptools.gid_config.parser.config_data import ConfigData
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class BaseIniParser:
    comment_regex = re.compile(r'#.*')

    def __init__(self,
                 config_data_item: ConfigData,
                 grammar_class: BaseIniGrammar = None,
                 token_factory: TokenFactory = None,
                 value_separator: str = '=',
                 comment_indicator: str = '#',
                 remove_comments: bool = False) -> None:
        self.config_data = config_data_item
        grammar_class = BaseIniGrammar if grammar_class is None else grammar_class

        self.grammar_item = grammar_class(value_separator=value_separator, comment_indicator=comment_indicator, token_factory=token_factory)
        self.remove_comments = remove_comments

        self.grammar: pp.ParserElement = None

    def _strip_comments(self, text: str) -> str:
        text = self.comment_regex.sub('', text)
        return text

    def pre_process(self, text: str) -> str:
        if self.remove_comments is True:
            text = self._strip_comments(text)
        return text

    def _parse(self, text: str) -> list[Token]:
        temp_comments = []
        temp_sections = []
        self.config_data.clear_sections()

        for tokens in self.grammar.search_string(text):

            token = tokens[0]

            if isinstance(token, Section):
                token.comments += temp_comments
                temp_comments = []
                temp_sections.append(token)
                self.config_data.add_section(token)

            elif isinstance(token, Entry):
                token.comments += temp_comments
                temp_comments = []
                temp_sections[-1].entries.append(token)

            elif isinstance(token, Comment):
                temp_comments.append(token)

        return self.config_data

    def parse(self, text: str) -> dict[str, str]:
        if self.grammar is None:
            self.grammar = self.grammar_item.get_grammar()
        text = self.pre_process(text)
        return self._parse(text)


# region[Main_Exec]


if __name__ == '__main__':
    pass
# endregion[Main_Exec]
