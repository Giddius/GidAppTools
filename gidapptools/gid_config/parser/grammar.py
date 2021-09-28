"""
WiP.

Soon.
"""

# region [Imports]


from pathlib import Path

import pyparsing as pp
import pyparsing.common as ppc
from gidapptools.gid_config.parser.tokens import Section, Entry, Comment, TokenFactory, Token

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class BaseIniGrammar:
    l_sqr_bracket = pp.Suppress('[')
    r_sqr_bracket = pp.Suppress(']')

    section_name_excluded_chars = ['[', ']', '.']
    section_name_extra_chars = [' ', '\t']

    key_name_exclusion_chars = ['[', ']', '.']
    key_name_extra_chars = [' ']

    value_exclusion_chars = []
    value_extra_chars = [' ', '\t']
    base_chars = {"section": {"exclude": section_name_excluded_chars,
                              "extra": section_name_extra_chars},
                  "key": {"exclude": key_name_exclusion_chars,
                          "extra": key_name_extra_chars},
                  "value": {"exclude": value_exclusion_chars,
                            "extra": value_extra_chars}}

    def __init__(self, value_separator: str = '=', comment_indicator: str = '#', token_factory: TokenFactory = None) -> None:
        self.token_factory = TokenFactory() if token_factory is None else token_factory
        self.raw_value_separator = value_separator
        self.value_seperator = pp.Suppress(self.raw_value_separator)
        self.raw_comment_indicator = comment_indicator
        self.comment_indicator = pp.Suppress(self.raw_comment_indicator)

    def get_chars_for(self, kind: str) -> str:
        exclude = self.base_chars[kind]['exclude'] + [self.raw_value_separator, self.raw_comment_indicator]
        extra = self.base_chars[kind]['extra']
        return ''.join(char for char in pp.printables if char not in exclude) + ''.join(extra)

    @property
    def section_name(self) -> pp.ParserElement:
        section_name = pp.line_start + self.l_sqr_bracket + pp.Word(self.get_chars_for('section')) + self.r_sqr_bracket
        return section_name.set_results_name('section_name')

    @property
    def key(self) -> pp.ParserElement:
        key = pp.line_start + pp.Word(self.get_chars_for('key')) + self.value_seperator
        return key

    @property
    def value(self) -> pp.ParserElement:
        value = pp.OneOrMore(pp.Word(self.get_chars_for('value')), stop_on=self.key | self.section_name | self.comment).set_parse_action(''.join)

        return value

    @property
    def entry(self) -> pp.ParserElement:
        entry = self.key + self.value
        return entry.set_results_name('entry')

    @property
    def comment(self) -> pp.ParserElement:
        comment = pp.line_start + self.comment_indicator + pp.rest_of_line
        return comment.set_results_name('comment')

    def get_grammar(self) -> pp.ParserElement:
        all_elements = pp.MatchFirst([self.section_name, self.entry, self.comment])

        return all_elements.set_parse_action(self.token_factory.parse_action)


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
