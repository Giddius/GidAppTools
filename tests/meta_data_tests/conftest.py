import pytest
from gidapptools.meta_data.config_kwargs import ConfigKwargs, NamedMetaPath
from pathlib import Path
import os
import sysconfig
from importlib import reload

from faked_pack_src import call_and_return
import subprocess
VENV_SITE_PACKAGES_PATH = Path(sysconfig.get_path('purelib'))

FAKE_PACKAGES_INIT_PATH = VENV_SITE_PACKAGES_PATH.joinpath("faked_pack_src", "__init__.py")
FAKE_PACKAGE_DIR = Path(r"..\..\misc\faked_pack").resolve()

VENV_PYTHON = Path(r"..\..\.venv\Scripts\python.exe")


FAKE_KWARGS = {'first': 'is_first_kwarg',
               'second': 2,
               'bool_kwarg': True,
               'appname': 'default_test_appname',
               'appauthor': 'default_test_appauthor',
               'name': 'default_test_name',
               'author': 'default_test_author',
               'init_path': FAKE_PACKAGES_INIT_PATH}


@pytest.fixture()
def fake_kwargs():
    yield FAKE_KWARGS


@pytest.fixture()
def config_kwargs_item():
    item = ConfigKwargs(base_configuration=FAKE_KWARGS)
    item.add_path_overwrite(NamedMetaPath.DATA, Path(r"C:\Windows"))
    yield item


@pytest.fixture(scope="function")
def app_meta_instance():
    import gidapptools.meta_data.interface
    reload(gidapptools.meta_data.interface)
    gidapptools.meta_data.interface.app_meta = gidapptools.meta_data.interface.AppMeta()
    call_and_return(gidapptools.meta_data.interface.setup_meta_data)
    yield gidapptools.meta_data.interface.app_meta
    gidapptools.meta_data.interface.app_meta.clean_up(remove_all_paths=True)


@pytest.fixture()
def app_meta_instance_dry_run():
    import gidapptools.meta_data.interface
    reload(gidapptools.meta_data.interface)
    gidapptools.meta_data.interface.app_meta = gidapptools.meta_data.interface.AppMeta()
    call_and_return(gidapptools.meta_data.interface.setup_meta_data)
    yield gidapptools.meta_data.interface.app_meta
    gidapptools.meta_data.interface.app_meta.clean_up(remove_all_paths=True, dry_run=True)
