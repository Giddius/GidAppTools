import pytest
from pathlib import Path
from gidapptools.gid_config.conversion.spec_data import SpecDataFile, AdvancedDict, AdvancedDictError, EntryTypus
from pprint import pprint

THIS_FILE_DIR = Path(__file__).parent.absolute()

simple_spec_file = THIS_FILE_DIR.joinpath("example_spec_file.json")


def test_spec_data_file_init():
    spec = SpecDataFile(simple_spec_file)
    assert spec.spec_name == "example_spec_file"


def test_load():
    spec = SpecDataFile(simple_spec_file)
    assert spec._data == {}
    assert spec.last_size is None
    spec.load()
    assert spec.data != {}
    assert spec.last_size is not None
    assert set(spec.data) == {"first_section", "second_section", "third_section"}
    assert isinstance(spec['first_section']['first_key'], EntryTypus)
    all_end_values = []
    for section, entries in spec.items():
        for key, value in entries.items():
            all_end_values.append(value)
    assert all(isinstance(item, EntryTypus) for item in all_end_values)
