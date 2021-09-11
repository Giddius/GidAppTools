import pytest
from gidapptools.meta_data.config_kwargs import ConfigKwargs, NamedMetaPath
from pathlib import Path
import sysconfig

VENV_SITE_PACKAGES_PATH = Path(sysconfig.get_path('purelib'))

FAKE_PACKAGES_INIT_PATH = VENV_SITE_PACKAGES_PATH.joinpath("faked_pack_src", "__init__.py")

FAKE_KWARGS = {'first': 'is_first_kwarg',
               'second': 2,
               'bool_kwarg': True,
               'appname': 'default_test_appname',
               'appauthor': 'default_test_appauthor',
               'name': 'default_test_name',
               'author': 'default_test_author',
               'init_path': FAKE_PACKAGES_INIT_PATH}


@pytest.fixture()
def config_kwargs_item():
    item = ConfigKwargs(base_configuration=FAKE_KWARGS)
    item.add_path_overwrite(NamedMetaPath.DATA, Path(r"C:\Windows"))
    yield item
