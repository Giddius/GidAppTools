from gidapptools.general_helper.dispatch_table import BaseDispatchTable, dispatch_mark
import pytest
from tempfile import TemporaryDirectory
from pathlib import Path


class CheckDispatchTable(BaseDispatchTable):

    @dispatch_mark(dispatch_mark.DEFAULT)
    def _the_default(self, argument):
        return ("default", argument)

    @dispatch_mark(str)
    def _on_string_type(self, argument):
        return (str, argument)

    @dispatch_mark('something')
    def _on_something(self, argument):
        return ('something', argument)

    @dispatch_mark(1)
    def _on_1(self, argument):
        return (1, argument)

    @dispatch_mark('callable_key_conversion')
    def _on_callable_key_conversion(self, argument):
        return ("callable_key_conversion", argument)


@pytest.fixture
def check_dispatch_table():
    yield CheckDispatchTable()


@pytest.fixture
def mod_key_check_dispatch_table():
    yield CheckDispatchTable(key_conversion={"callable_key_conversion": "modified_callable_key_conversion"})


FILE_HELPER_FILE_CONTENT_1 = """

this is the first line
this is the second line

after an empty line, this is the third one
this is the last line

"""

FILE_HELPER_FILE_CONTENT_2 = FILE_HELPER_FILE_CONTENT_1.strip()


FILE_HELPER_FILE_CONTENT_3 = """

asdasd
asdasdasd
asdasd

asd
\n"""

print(f"'{FILE_HELPER_FILE_CONTENT_3}'")

FILE_HELPER_FILE_CONTENT_4 = """

asdasd
asdasdasd
asdasd

asd
\t"""


@pytest.fixture
def file_helper_file_1() -> Path:
    with TemporaryDirectory() as temp_folder:
        path = Path(temp_folder, "file_helper_file_1.txt")
        path.write_text(FILE_HELPER_FILE_CONTENT_1, encoding='utf-8', errors='ignore')
        yield path


@pytest.fixture
def file_helper_file_2() -> Path:
    with TemporaryDirectory() as temp_folder:
        path = Path(temp_folder, "file_helper_file_2.txt")
        path.write_text(FILE_HELPER_FILE_CONTENT_2, encoding='utf-8', errors='ignore')
        yield path


@pytest.fixture
def file_helper_file_3() -> Path:
    with TemporaryDirectory() as temp_folder:
        path = Path(temp_folder, "file_helper_file_3.txt")
        path.write_text(FILE_HELPER_FILE_CONTENT_3, encoding='utf-8', errors='ignore')
        yield path


@pytest.fixture
def file_helper_file_4() -> Path:
    with TemporaryDirectory() as temp_folder:
        path = Path(temp_folder, "file_helper_file_4.txt")
        path.write_text(FILE_HELPER_FILE_CONTENT_4, encoding='utf-8', errors='ignore')
        yield path
