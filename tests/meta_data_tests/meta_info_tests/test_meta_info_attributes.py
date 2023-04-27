# region [Imports]

import pytest
from pytest import param
from pytest_lazyfixture import lazy_fixture
import os
from pathlib import Path
from gidapptools.meta_data.interface import AppMeta
from gidapptools.meta_data.meta_info.meta_info_item import MetaInfo, ManualMetaInfoItem

# endregion [Imports]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


def test_pretty_is_dev(app_meta_instance: AppMeta):
    meta_info = app_meta_instance.get(MetaInfo)

    assert meta_info.pretty_is_dev in ("Yes", "No")

    if meta_info.is_dev is True:
        assert meta_info.pretty_is_dev == "Yes"

    else:
        assert meta_info.pretty_is_dev == "No"

    manual_meta_info = ManualMetaInfoItem(is_dev=False)
    assert manual_meta_info.is_dev is False
    assert manual_meta_info.pretty_is_dev == "No"


def test_pretty_author_name(app_meta_instance: AppMeta):
    meta_info = app_meta_instance.get(MetaInfo)

    assert meta_info.pretty_app_author == "Fake Author"


def test_pretty_app_name(app_meta_instance: AppMeta):
    meta_info = app_meta_instance.get(MetaInfo)

    assert meta_info.pretty_app_name == "Faked Pack Src"


def test_is_frozen_app(app_meta_instance: AppMeta):
    meta_info = app_meta_instance.get(MetaInfo)

    assert meta_info.is_frozen_app is False
