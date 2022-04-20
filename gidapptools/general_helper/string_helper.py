"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import re
import inspect
from typing import Union, Literal, Mapping, Callable, Iterable
from pathlib import Path
from string import ascii_uppercase, ascii_lowercase, ascii_letters
from textwrap import dedent

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.enums import StringCase
import pyparsing as ppa
import pyparsing.common as ppc

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]

# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion[Constants]

STRING_CASE_FUNC_TYPE = Callable[[Iterable[str]], str]


# TODO: Rewrite as normal class/Module-Singleton
class StringCaseConverter:
    SNAKE = StringCase.SNAKE
    SCREAMING_SNAKE = StringCase.SCREAMING_SNAKE
    CAMEL = StringCase.CAMEL
    PASCAL = StringCase.PASCAL
    KEBAP = StringCase.KEBAP
    SPLIT = StringCase.SPLIT
    CLASS = StringCase.CLASS
    TITLE = StringCase.TITLE
    BLOCK_UPPER = StringCase.BLOCK_UPPER

    _split_grammar: ppa.ParserElement = None
    split_pascal_case_regex = re.compile(r"(?<!\_)(\B[A-Z])")
    snake_case_to_pascal_case_regex = re.compile(r"(_|^)(\w)")
    _word_list_split_chars = {'-', '_', ' '}
    _word_list_split_regex = re.compile(r'|'.join(list(_word_list_split_chars) + [r"(?=[A-Z])"]))

    _dispatch_table: dict[str, STRING_CASE_FUNC_TYPE] = None

    @classmethod
    @property
    def dispatch_table(cls) -> dict[StringCase, STRING_CASE_FUNC_TYPE]:
        if cls._dispatch_table is None:
            cls._dispatch_table = {}
            for meth_name, meth_obj in inspect.getmembers(cls):
                if meth_name.startswith('_to_') and meth_name.endswith('_case'):
                    key_name = meth_name.removeprefix('_to_').removesuffix('_case')
                    cls._dispatch_table[StringCase(key_name)] = meth_obj
        return cls._dispatch_table

    @classmethod
    @property
    def split_grammar(cls):

        if cls._split_grammar is None:
            underscore = ppa.Literal('_').suppress()
            dash = ppa.Literal("-").suppress()
            all_upper_word = ppa.Regex(r"[A-Z]+(?![a-z])")
            all_lower_word = ppa.Word(ascii_lowercase, ascii_lowercase)
            title_word = ppa.Regex(r"[A-Z][a-z]+")
            number = ppa.Word(ppa.nums)
            words = (title_word | all_upper_word | all_lower_word | number).set_parse_action(lambda x: x[0].casefold())
            grammar = words | underscore | dash
            cls._split_grammar = ppa.OneOrMore(grammar)
        return cls._split_grammar

    @classmethod
    def _to_word_list(cls, in_string: str) -> Iterable[str]:
        parts = cls.split_grammar.parse_string(in_string, parse_all=True)

        return [word for word in parts if word]

    @staticmethod
    def _to_block_upper_case(word_list: Iterable[str]) -> str:
        return ''.join(word.upper() for word in word_list)

    @staticmethod
    def _to_snake_case(word_list: Iterable[str]) -> str:
        return '_'.join(word_list).casefold()

    @staticmethod
    def _to_camel_case(word_list: Iterable[str]) -> str:
        return word_list[0].casefold() + ''.join(item.title() for item in word_list[1:])

    @staticmethod
    def _to_pascal_case(word_list: Iterable[str]) -> str:
        return ''.join(item.title() for item in word_list)

    @staticmethod
    def _to_kebap_case(word_list: Iterable[str]) -> str:
        return '-'.join(word_list)

    @staticmethod
    def _to_screaming_snake_case(word_list: Iterable[str]) -> str:
        return '_'.join(word_list).upper()

    @staticmethod
    def _to_split_case(word_list: Iterable[str]) -> str:
        return ' '.join(word_list)

    @staticmethod
    def _to_title_case(word_list: Iterable[str]) -> str:
        return ' '.join(word.title() for word in word_list)

    @staticmethod
    def _to_upper_case(word_list: Iterable[str]) -> str:
        return ' '.join(word.upper() for word in word_list)

    @classmethod
    def convert_to(cls, in_string: str, target_case: Union[str, StringCase]) -> str:
        target_case = StringCase(target_case) if isinstance(target_case, str) else target_case
        word_list = cls._to_word_list(in_string)
        return cls.dispatch_table.get(target_case)(word_list)


_ = StringCaseConverter.dispatch_table
_ = StringCaseConverter.split_grammar


def replace_by_dict(in_string: str, in_dict: dict[str, str]) -> str:
    mod_string = in_string
    for key, value in in_dict.items():
        mod_string = mod_string.replace(key, value)
    return mod_string


def extract_by_map(in_string: str, extract_data: Union[Iterable[str], Mapping[str, str]]) -> Iterable[str]:
    parts = []
    re_pattern = re.compile(r'|'.join(extract_data))
    for match in re_pattern.finditer(in_string):
        matched_str = match.group()
        parts.append(matched_str)
    if isinstance(extract_data, Mapping):
        return [extract_data.get(part) for part in parts]
    return parts


SPACE_CLEANING_REGEX = re.compile(r" +")
NEWLINE_CLEANING_REGEX = re.compile(r"\n+")


def clean_whitespace(in_text: str, replace_newline: bool = False) -> str:
    cleaned_text = SPACE_CLEANING_REGEX.sub(' ', in_text)
    if replace_newline is True:
        cleaned_text = NEWLINE_CLEANING_REGEX.sub(' ', cleaned_text)
    return cleaned_text


def shorten_string(in_text: str, max_length: int, shorten_side: Literal["right", "left"] = "right", placeholder: str = '...', clean_before: bool = True, ensure_space_around_placeholder: bool = False, split_on: str = '\s|\n') -> str:
    max_length = int(max_length)
    if shorten_side.casefold() not in {"left", "right"}:
        raise ValueError(shorten_side)

    if clean_before is True:
        in_text = clean_whitespace(in_text, replace_newline=False)

    if len(in_text) <= max_length:
        return in_text

    if ensure_space_around_placeholder is True:
        placeholder = f" {placeholder.strip()}" if shorten_side == "right" else f"{placeholder.strip()} "

    max_length = max_length - len(placeholder)

    new_text = in_text[:max_length] if shorten_side == 'right' else in_text[-max_length:]
    if split_on == "any":
        split_on = r"."
    find_regex = re.compile(split_on)
    last_space_position = list(find_regex.finditer(new_text))

    return new_text[:last_space_position[-1].span()[0]].strip() + placeholder if shorten_side == 'right' else placeholder + new_text[last_space_position[0].span()[0]:].strip()


def split_quotes_aware(text: str, split_chars: Iterable[str] = None, quote_chars: Iterable[str] = None, strip_parts: bool = True) -> list[str]:
    """
    Splits a string on but not if the separator char is inside of quotes.

    Args:
        text (str): The string to split.
        split_chars (Iterable[str], optional): The characters to split on. Defaults to `,`.
        quote_chars (Iterable[str], optional): The quote chars that should be considered real quotes. Defaults to `"` and `'`.
        strip_parts (bool, optional): If each found substrin should be striped of preceding and trailing whitespace in the result. Defaults to True.

    Returns:
        list[str]: The found sub-parts.
    """
    split_chars = {','} if split_chars is None else set(split_chars)
    quote_chars = {"'", '"'} if quote_chars is None else set(quote_chars)
    parts = []
    temp_chars = []
    inside_quotes: str = None

    def _add_part():
        nonlocal parts
        nonlocal temp_chars
        part = ''.join(temp_chars)
        if strip_parts is True:
            part = part.strip()
        for quote_char in quote_chars:
            if part.startswith(quote_char) and part.endswith(quote_char):
                part = part.strip(quote_char)
        if part:
            parts.append(part)
        temp_chars.clear()

    for char in text:
        if char in split_chars and inside_quotes is None:
            _add_part()
        else:
            temp_chars.append(char)

            if char in quote_chars and inside_quotes is None:
                inside_quotes = char
            elif char in quote_chars and inside_quotes == char:
                inside_quotes = None

    if temp_chars:
        _add_part()

    return parts


def make_attribute_name(in_string: str) -> str:

    # Remove invalid characters
    in_string = re.sub(r'-', '_', in_string)
    in_string = re.sub('[^0-9a-zA-Z_]', '', in_string)

    # Remove leading characters until we find a letter or underscore
    in_string = re.sub('^[^a-zA-Z_]+', '', in_string)

    return in_string.casefold()


def fix_multiple_quotes(_text: str) -> str:

    def _replace_function(match: re.Match):
        return match.group()[0]

    return re.sub(r"""(\"+)|(\'+)""", _replace_function, _text)


def deindent(in_text: str, ignore_first_line: bool = False) -> str:
    if in_text == "":
        return in_text
    pre_whitespace_regex = re.compile(r"\s*")
    lines = in_text.splitlines()
    white_space_levels = []
    if ignore_first_line is True:
        _first_line = lines.pop(0)
    for line in lines:
        if not line:
            continue
        if match := pre_whitespace_regex.match(line):
            ws = match.group()
            if len(ws) == len(line):
                continue
            white_space_levels.append(len(match.group()))
        else:

            white_space_levels.append(0)

    try:
        min_ws_level = min(white_space_levels) if len(white_space_levels) > 1 else white_space_levels[0]
    except IndexError:
        min_ws_level = 0
    combined = '\n'.join(line[min_ws_level:] for line in lines)
    if ignore_first_line is True:
        combined = '\n' + combined if combined else ""
        combined = _first_line + combined
    return combined


def multi_line_dedent(in_text: str, strip_pre_lines: bool = True, strip_post_lines: bool = True) -> str:
    text = dedent(in_text)

    if strip_pre_lines is True:
        lines = text.splitlines()
        while lines[0] == "":
            lines.pop(0)
        text = '\n'.join(lines)
    if strip_post_lines is True:
        text = text.rstrip()
    return text


def strip_only_wrapping_empty_lines(in_text: str) -> str:
    empty_line_pattern = re.compile(r"(^\s*)|(\s*$)")
    return empty_line_pattern.sub("", in_text)


def string_strip(in_string: str, chars: str = None) -> str:
    return in_string.strip(chars)


def remove_chars(in_string: str, *chars) -> str:
    return ''.join(char for char in in_string if char not in set(chars))
# region[Main_Exec]


if __name__ == '__main__':
    pass
# endregion[Main_Exec]
