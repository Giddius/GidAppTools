import pytest
from gidapptools.meta_data.config_kwargs import ConfigKwargs, NamedMetaPath
from pathlib import Path
import sysconfig
from gidapptools.meta_data.interface import app_meta, setup_meta_data
from faked_pack_src import call_and_return

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
def fake_kwargs():
    yield FAKE_KWARGS


@pytest.fixture()
def config_kwargs_item():
    item = ConfigKwargs(base_configuration=FAKE_KWARGS)
    item.add_path_overwrite(NamedMetaPath.DATA, Path(r"C:\Windows"))
    yield item


@pytest.fixture()
def app_meta_instance():
    call_and_return(setup_meta_data)
    yield app_meta
    app_meta.clean_up(remove_all_paths=True)


@pytest.fixture()
def app_meta_instance_dry_run():
    call_and_return(setup_meta_data)
    yield app_meta
    app_meta.clean_up(remove_all_paths=True, dry_run=True)
