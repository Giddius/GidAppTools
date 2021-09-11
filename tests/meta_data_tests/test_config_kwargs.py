import pytest
from gidapptools.meta_data.config_kwargs import ConfigKwargs, NamedMetaPath
from pathlib import Path
from pprint import pprint


def fake_kwargs_function(first, second, bool_kwarg=False):
    return first, second, bool_kwarg


def fake_multi_kwarg_function(first, second: int = 2, **kwargs):
    return tuple([first, second] + [v for v in kwargs.values()])


def fake_no_arg_function():
    return ('no_args',)


class FakeKwargsClass:

    def __init__(self, first: str, second: int = 1, bool_kwarg: bool = False) -> None:
        self.first = first
        self.second = second
        self.bool_kwarg = bool_kwarg

    @property
    def all_attrs(self):
        return self.first, self.second, self.bool_kwarg


def test_if_not_singleton(config_kwargs_item: ConfigKwargs):
    new = ConfigKwargs({'this': 'that'})
    assert config_kwargs_item is not new
    assert config_kwargs_item != new
    assert config_kwargs_item.data != new.data
    assert config_kwargs_item._path_overwrites != new._path_overwrites


def test_get_kwargs_for_func(config_kwargs_item: ConfigKwargs):
    assert config_kwargs_item.get_kwargs_for(fake_kwargs_function) == {'first': 'is_first_kwarg', 'second': 2, 'bool_kwarg': True}
    assert fake_kwargs_function(**config_kwargs_item.get_kwargs_for(fake_kwargs_function)) == ('is_first_kwarg', 2, True)

    assert config_kwargs_item.get_kwargs_for(fake_multi_kwarg_function) == {'first': 'is_first_kwarg', 'second': 2}

    assert config_kwargs_item.get_kwargs_for(fake_no_arg_function) == {}

    config_kwargs_item.pop('bool_kwarg')

    assert config_kwargs_item.get_kwargs_for(fake_kwargs_function) == {'first': 'is_first_kwarg', 'second': 2}
    assert fake_kwargs_function(**config_kwargs_item.get_kwargs_for(fake_kwargs_function)) == ('is_first_kwarg', 2, False)

    config_kwargs_item.pop('second')

    assert config_kwargs_item.get_kwargs_for(fake_kwargs_function) == {'first': 'is_first_kwarg'}

    with pytest.raises(TypeError):
        fake_kwargs_function(**config_kwargs_item.get_kwargs_for(fake_kwargs_function))


def test_get_kwargs_for_class(config_kwargs_item: ConfigKwargs):

    assert config_kwargs_item.get_kwargs_for(FakeKwargsClass) == {'first': 'is_first_kwarg', 'second': 2, 'bool_kwarg': True}

    assert fake_kwargs_function(**config_kwargs_item.get_kwargs_for(fake_kwargs_function)) == ('is_first_kwarg', 2, True)


def test_get_kwargs_for_func_w_defaults(config_kwargs_item: ConfigKwargs):
    defaults = {'second': 14}
    config_kwargs_item.pop('second')
    assert config_kwargs_item.get_kwargs_for(fake_kwargs_function, defaults=defaults) == {'first': 'is_first_kwarg', 'second': 14, 'bool_kwarg': True}


def test_get_kwargs_for_func_w_overwrites(config_kwargs_item: ConfigKwargs):
    overwrites = {'second': 14}

    assert config_kwargs_item.get_kwargs_for(fake_kwargs_function, overwrites=overwrites) == {'first': 'is_first_kwarg', 'second': 14, 'bool_kwarg': True}


def test_get_kwargs_for_func_w_excludes(config_kwargs_item: ConfigKwargs):
    excludes = ['bool_kwarg']

    assert config_kwargs_item.get_kwargs_for(fake_kwargs_function, exclude=excludes) == {'first': 'is_first_kwarg', 'second': 2}


def test_get_path_overwrites(config_kwargs_item: ConfigKwargs):
    assert config_kwargs_item.get('path_overwrites') == {NamedMetaPath.DATA: Path(r"C:\Windows")}
    with pytest.raises(KeyError, match='Not allowed to set path_overwrites this way, use "add_path_overwrite"'):
        config_kwargs_item['path_overwrites'] = 'this'
