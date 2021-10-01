import pytest
from gidapptools.gid_signal.interface import get_signal, Signal, SignalRegistry, signal_registry


@pytest.mark.parametrize('name', [('first_signal_name'), ('second_signal_name'), ('name_with_spaces')])
def test_get_signal(name: str):
    signal_1 = get_signal(name)
    signal_2 = get_signal(name)
    assert signal_1 is signal_2
    signal_3 = get_signal('other_signal_name')
    assert signal_1 is not signal_3
    assert signal_2 is not signal_3
    assert len(signal_registry) == 2


check_list = []


def add_it(to_add):
    check_list.append(to_add)


class CheckClass:

    def __init__(self) -> None:
        self._value = None

    def set_value(self, value):
        self._value = value


check_class = CheckClass()


def test_signal():
    signal = get_signal('a_signal')

    signal.connect(check_class.set_value)
    signal.connect(add_it)

    signal.emit(1)

    assert check_list == [1]
    assert check_class._value == 1
    signal.emit(2)
    assert check_list == [1, 2]
    assert check_class._value == 2
    from inspect import isbuiltin


def test_valdate():
    signal = get_signal('a_signal')
    with pytest.raises(TypeError):
        signal.connect(check_list.append)
