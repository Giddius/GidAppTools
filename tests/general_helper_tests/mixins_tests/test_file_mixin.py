import pytest
from pathlib import Path
from gidapptools.general_helper.mixins.file_mixin import FileMixin


def test_init(check_file_path: Path):
    file = FileMixin(file_path=check_file_path)
    assert file.file_name == check_file_path.name.casefold()
    assert file.file_path == check_file_path
    assert file.last_size is None
    assert file.last_changed_time is None
    assert file.last_file_hash is None
    assert file.has_changed is True


def test_has_changed(check_file_path: Path):
    file = FileMixin(file_path=check_file_path)
    assert file.has_changed is True
    file._update_changed_data()
    assert file.last_size is not None
    assert file.last_file_hash is None
    assert file.last_changed_time is None
    assert file.has_changed is False
    file.write('this is to change it')
    assert file.has_changed is True
    file.set_changed_parameter('file_hash')
    file._update_changed_data()
    assert file.last_file_hash is not None
    file.set_changed_parameter('all')
    file._update_changed_data()
    assert file.last_size is not None
    assert file.last_file_hash is not None
    assert file.last_changed_time is not None
