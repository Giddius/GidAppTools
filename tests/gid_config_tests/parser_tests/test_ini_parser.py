import pytest
from gidapptools.gid_config.parser.ini_parser import BaseIniParser, Entry, Section, Comment, TrailingCommentError
from pathlib import Path
from pprint import pprint
from typing import Any
from tempfile import TemporaryDirectory
from contextlib import contextmanager
import shutil
THIS_FILE_DIR = Path(__file__).parent.absolute()

SIMPLE_INI_CONFIG_FILE = THIS_FILE_DIR.joinpath("simple_example_config.ini")
SIMPLE_INI_CONFIG_STRIPED_INLINE_COMMENTS_FILE = THIS_FILE_DIR.joinpath("simple_example_config_striped_inline_comments.ini")
SIMPLE_INI_CONFIG_STRIPED_ALL_COMMENTS_FILE = THIS_FILE_DIR.joinpath("simple_example_config_striped_all_comments.ini")
SIMPLE_INI_CONFIG_W_TRAILING_COMMENT = THIS_FILE_DIR.joinpath("simple_example_config_w_trailing_comment.ini")


@pytest.mark.parametrize('in_text, expected_result', [("blah blah # something", "blah blah"),
                                                      ("# a comment", '# a comment'),
                                                      ("something something # inline comment\n# normal comment", "something something\n# normal comment"),
                                                      (SIMPLE_INI_CONFIG_FILE.read_text(encoding='utf-8'), SIMPLE_INI_CONFIG_STRIPED_INLINE_COMMENTS_FILE.read_text(encoding='utf-8'))])
def test_preprocess_comments_inline(in_text: str, expected_result: str):
    parser = BaseIniParser()
    check = '\n'.join([line for line in parser._preprocess_comments(in_text).splitlines() if line.strip()])
    result = '\n'.join([line for line in expected_result.splitlines() if line.strip()])
    assert check == result


@pytest.mark.parametrize('in_text, expected_result', [("blah blah # something", "blah blah"),
                                                      ("# a comment", ''),
                                                      ("something something # inline comment\n# normal comment", "something something\n"),
                                                      (SIMPLE_INI_CONFIG_FILE.read_text(encoding='utf-8'), SIMPLE_INI_CONFIG_STRIPED_ALL_COMMENTS_FILE.read_text(encoding='utf-8'))])
def test_preprocess_comments_all(in_text: str, expected_result: str):
    parser = BaseIniParser(remove_all_comments=True)
    check = [line for line in parser._preprocess_comments(in_text).splitlines() if line]
    result = [line for line in expected_result.splitlines() if line]
    assert check == result


@pytest.mark.parametrize('in_text, resulting_exception', [('# a trailing commment', TrailingCommentError),
                                                          (SIMPLE_INI_CONFIG_W_TRAILING_COMMENT.read_text(encoding='utf-8'), TrailingCommentError)])
def test_verify(in_text, resulting_exception):
    parser = BaseIniParser()
    with pytest.raises(resulting_exception):
        parser._verify(in_text)


@contextmanager
def example_config_file_simple():
    with TemporaryDirectory() as temp_folder:
        new_path = shutil.copy(SIMPLE_INI_CONFIG_FILE, temp_folder)
        yield Path(new_path)


@contextmanager
def example_config_2():
    with TemporaryDirectory() as temp_folder:
        new_path = shutil.copy(THIS_FILE_DIR.parent.joinpath('example_config_2.ini'), temp_folder)
        yield Path(new_path)


@pytest.mark.parametrize("config_func, expected_data_length", [(example_config_file_simple, 4),
                                                               (example_config_2, 5)])
def test_ini_parser_parse(config_func, expected_data_length: int):
    with config_func() as config_file:
        parser = BaseIniParser()
        text = config_file.read_text()
        data = parser.parse(text)
        pprint(data)

        assert len(data) == expected_data_length
        assert isinstance(data, list) is True
        assert all(isinstance(item, Section) for item in data)


simple_ini_parsed_sections_expected_data = [{'name': 'general_settings', 'len': 4, 'len_comments': 1},
                                            {'name': 'debug', 'len': 1, 'len_comments': 3},
                                            {'name': 'this', 'len': 2, 'len_comments': 0}]

simple_ini_parsed_sections_expected_data = [(idx, item) for idx, item in enumerate(simple_ini_parsed_sections_expected_data)]


@pytest.mark.parametrize('section_number, expected', simple_ini_parsed_sections_expected_data)
def test_simple_ini_parsed_sections(simple_example_config_data: list[Section], section_number: int, expected: dict[str, Any]):
    check_section = simple_example_config_data[section_number]

    assert check_section.name == expected.get('name')
    assert len(check_section) == expected.get('len')
    assert len(check_section.comments) == expected.get("len_comments")
