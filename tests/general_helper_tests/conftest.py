from gidapptools.general_helper.dispatch_table import BaseDispatchTable, dispatch_mark
import pytest


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
