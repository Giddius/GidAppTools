from gidapptools.meta_data.interface import AppMeta, setup_meta_data, get_meta_info, get_meta_paths, get_meta_item
from gidapptools.meta_data.meta_info.meta_info_holder import MetaInfo
from gidapptools.meta_data.meta_paths.meta_paths_holder import MetaPaths
from gidapptools.errors import NotSetupError, MetaItemNotFoundError
from typing import Any
from pathlib import Path
import pytest
from pprint import pprint


def test_not_setup_errors():
    with pytest.raises(NotSetupError):
        meta_info = get_meta_info()

    with pytest.raises(NotSetupError):
        meta_paths = get_meta_paths()

    with pytest.raises(NotSetupError):
        item = get_meta_item('something')


def test_get_meta_item(app_meta_instance: AppMeta):
    meta_info = get_meta_info()
    assert isinstance(meta_info, MetaInfo)
    meta_paths = get_meta_paths()
    x = meta_paths.data_dir

    assert isinstance(meta_paths, MetaPaths)

    with pytest.raises(MetaItemNotFoundError):
        item = get_meta_item('not_existing_item')


def test_contains(app_meta_instance: AppMeta):
    assert 'meta_paths' in app_meta_instance
    assert 'meta_info' in app_meta_instance


def test_get(app_meta_instance: AppMeta):
    assert app_meta_instance.get() == {'meta_paths': app_meta_instance.meta_paths, 'meta_info': app_meta_instance.meta_info}
    assert app_meta_instance['meta_paths'] == app_meta_instance.meta_paths
    assert app_meta_instance['meta_info'] == app_meta_instance.meta_info

    with pytest.raises(MetaItemNotFoundError):
        item = app_meta_instance['not_existing_item']
