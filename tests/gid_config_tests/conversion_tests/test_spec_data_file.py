import pytest
from pathlib import Path
from gidapptools.gid_config.conversion.spec_data import SpecFile, AdvancedDict, AdvancedDictError, EntryTypus, SpecVisitor
from pprint import pprint

THIS_FILE_DIR = Path(__file__).parent.absolute()

simple_spec_file = THIS_FILE_DIR.joinpath("example_spec_file.json")


def test_spec_data_file_init():
    spec = SpecFile(simple_spec_file, visitor=SpecVisitor())
    assert spec.spec_name == "example_spec_file"


def test_load():
    spec = SpecFile(simple_spec_file, visitor=SpecVisitor())
    assert spec._data == None
    assert spec.last_size is None
    spec.load()
    assert spec.data != None
    assert spec.last_size is not None
    assert set(spec.data) == {"first_section", "second_section", "third_section"}
    assert isinstance(spec['first_section']['first_key'], EntryTypus)
    all_end_values = []
    for section, entries in spec.items():
        for key, value in entries.items():
            all_end_values.append(value)
    assert all(isinstance(item, EntryTypus) for item in all_end_values)
