"""
WiP.

Soon.
"""

# region [Imports]


import re


import inspect

from pathlib import Path
from typing import Callable, Iterable, Mapping, Union
from gidapptools.utility.enums import BaseGidEnum
from gidapptools.general_helper.enums import StringCase
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]

# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion[Constants]

STRING_CASE_FUNC_TYPE = Callable[[Iterable[str]], str]


class StringCaseConverter:
    SNAKE = StringCase.SNAKE
    SCREAMING_SNAKE = StringCase.SCREAMING_SNAKE
    CAMEL = StringCase.CAMEL
    PASCAL = StringCase.PASCAL
    KEBAP = StringCase.KEBAP
    SPLIT = StringCase.SPLIT
    CLASS = StringCase.CLASS

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

    @staticmethod
    def _snake_to_pascal_replacer(match: re.Match) -> str:
        return match.group(2).upper()

    @classmethod
    def _to_word_list(cls, in_string: str) -> Iterable[str]:
        in_string = in_string.strip()
        if in_string.isupper():
            in_string = in_string.casefold()

        return [word.casefold() for word in cls._word_list_split_regex.split(in_string) if word]

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


def shorten_string(in_text: str, max_length: int, shorten_side: str = "right", placeholder: str = '...', clean_before: bool = True, ensure_space_around_placeholder: bool = False, split_on: str = '\s|\n') -> str:
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
    find_regex = re.compile(split_on)
    last_space_position = list(find_regex.finditer(new_text))

    return new_text[:last_space_position[-1].span()[0]].strip() + placeholder if shorten_side == 'right' else placeholder + new_text[last_space_position[0].span()[0]:].strip()

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
