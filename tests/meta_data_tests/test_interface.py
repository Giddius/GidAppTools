from gidapptools.meta_data.interface import AppMeta, setup_meta_data, get_meta_info, get_meta_paths, get_meta_item
from gidapptools.meta_data.meta_info.meta_info_item import MetaInfo
from gidapptools.meta_data.meta_info.meta_info_factory import MetaInfoFactory
from gidapptools.meta_data.meta_paths.meta_paths_item import MetaPaths
from gidapptools.meta_data.meta_paths.meta_paths_factory import MetaPathsFactory

from gidapptools.errors import NotSetupError, MetaItemNotFoundError
from typing import Any
from pathlib import Path
import pytest
from pprint import pprint
from faked_pack_src.plugin import FakeFactory

pytestmark = pytest.mark.random_order(disabled=True)


# def test_not_setup_errors():
#     with pytest.raises(NotSetupError):
#         meta_info = get_meta_info()

#     with pytest.raises(NotSetupError):
#         meta_paths = get_meta_paths()

#     with pytest.raises(NotSetupError):
#         item = get_meta_item('something')


def test_get_meta_item(app_meta_instance: AppMeta):
    assert app_meta_instance.is_setup is True
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
    assert app_meta_instance.get() == {'meta_paths': app_meta_instance['meta_paths'], 'meta_info': app_meta_instance["meta_info"]}
    assert isinstance(app_meta_instance['meta_paths'], MetaPaths)
    assert isinstance(app_meta_instance['meta_info'], MetaInfo)

    item = app_meta_instance.get(MetaInfo)
    assert isinstance(item, MetaInfo)
    assert hasattr(item, "pretty_started_at")
    with pytest.raises(MetaItemNotFoundError):
        item = app_meta_instance['not_existing_item']


def test_all_names(app_meta_instance: AppMeta):
    assert set(app_meta_instance.all_item_names) == {'meta_paths', 'meta_info'}


def test_all_items(app_meta_instance: AppMeta):
    for item in app_meta_instance.all_items:
        assert any(isinstance(item, compare_class) for compare_class in [MetaInfo, MetaPaths])


def test_plugin(app_meta_instance: AppMeta):
    assert set(app_meta_instance.factories) == {MetaInfoFactory, MetaPathsFactory, FakeFactory}
