from gidapptools.meta_data.meta_paths.meta_paths_item import MetaPaths, NamedMetaPath, UnknownMetaPathIdentifier, NotImplementedMetaPath
from gidapptools.meta_data.interface import AppMeta
from pathlib import Path
import os
import pytest

import platform

from pytest import param


@pytest.mark.parametrize(["in_app_meta_instance", "name", "suffix", "result"],
                         [param(pytest.lazy_fixture("app_meta_instance"), "wuff", None, {"full_name": "wuff"}),
                         param(pytest.lazy_fixture("app_meta_instance"), "wuff", "extra", {"full_name": "wuff_extra"})])
def test_get_temp_dir(in_app_meta_instance: AppMeta, name: str, suffix: str, result: dict[str, object]):
    meta_paths: MetaPaths = in_app_meta_instance['meta_paths']
    new_temp_dir = meta_paths.get_new_temp_dir(suffix=suffix, name=name)
    assert new_temp_dir.name == result["full_name"]
    assert new_temp_dir.is_dir() is True

    another_new_temp_dir = meta_paths.get_new_temp_dir(name=name, suffix=suffix)
    assert another_new_temp_dir.name != result["full_name"]
    assert os.fspath(another_new_temp_dir) != os.fspath(new_temp_dir)
    assert another_new_temp_dir != new_temp_dir
    assert another_new_temp_dir.is_dir() is True

    meta_paths.clean_all_temp()
    assert new_temp_dir.exists() is False
    assert another_new_temp_dir.exists() is False

    third_new_temp_dir = meta_paths.get_new_temp_dir(name=name, suffix=suffix)
    assert third_new_temp_dir.name == result["full_name"]
    assert third_new_temp_dir.is_dir() is True

    meta_paths.clean_all_temp()

    with meta_paths.context_new_temp_dir(suffix=suffix, name=name) as context_temp_dir:
        stored_context_dir = Path(context_temp_dir)
        assert context_temp_dir.name == result["full_name"]
        assert context_temp_dir.is_dir() is True

    assert stored_context_dir.exists() is False


def test_get_path(app_meta_instance: AppMeta):

    meta_paths: MetaPaths = app_meta_instance["meta_paths"]

    cache_dir_identifier = NamedMetaPath.CACHE

    raw_cache_dir_path = meta_paths._paths.get(cache_dir_identifier)

    assert raw_cache_dir_path is not None

    assert raw_cache_dir_path.exists() is False

    cache_dir = meta_paths.cache_dir

    assert cache_dir.exists() is True

    assert cache_dir.is_dir() is True

    assert raw_cache_dir_path.exists() is True

    assert os.fspath(raw_cache_dir_path) == os.fspath(cache_dir)
    assert raw_cache_dir_path == cache_dir
    with pytest.raises(UnknownMetaPathIdentifier):
        meta_paths.get_path("This is not an identifier")

    default_path = meta_paths.get_path(NamedMetaPath._ONLY_FOR_TESTING, default=cache_dir.joinpath("a_default"))
    assert default_path.is_dir() is True
    assert default_path.name == "a_default"
    assert default_path == cache_dir.joinpath("a_default")

    with pytest.raises(NotImplementedMetaPath):
        meta_paths.get_path(NamedMetaPath._ONLY_FOR_TESTING)
